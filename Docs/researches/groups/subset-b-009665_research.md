# Research Report: subset-b-009665

This grouped report covers the libtirpc source files assigned to `subset-b-009665`. Each section preserves the original source path so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authunix_prot.c -->
## sources/user-network-fs/libtirpc/src/authunix_prot.c

Purpose: Implements the XDR codec for legacy AUTH_UNIX/AUTH_SYS authentication parameters. The single exported routine, `xdr_authunix_parms(XDR *xdrs, struct authunix_parms *p)`, serializes or deserializes timestamp, machine name, uid, gid, and supplementary groups.

Important APIs and control flow: The function asserts non-null inputs, then chains `xdr_u_long`, `xdr_string`, `xdr_u_int`, and `xdr_array` calls. The group array is capped by `NGRPS` and uses `xdr_int` for each element. The function returns `TRUE` only if every XDR operation succeeds.

State and persistence: No persistent state is owned here. In decode/free modes, allocation and release behavior are delegated to XDR primitives, especially `xdr_string` and `xdr_array`.

Dependencies and integration: Depends on `<rpc/auth_unix.h>` and the common XDR runtime. It is exported in `libtirpc.map.in` and is consumed by AUTH_UNIX credential creation/validation paths.

Risks and test signals: Risks are bounded by the XDR length caps. Tests should round-trip AUTH_UNIX credentials, exercise `NGRPS` boundaries, and verify decode/free behavior under malformed lengths and null-assert builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authunix_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/binddynport.c -->
## sources/user-network-fs/libtirpc/src/binddynport.c

Purpose: Provides `__binddynport(int fd)`, a libtirpc internal helper that binds an unbound IPv4/IPv6 socket to a random dynamic/private port in the RFC 6335 range 49152-65534 while avoiding Linux locally reserved ports.

Important APIs and control flow: `is_reserved` and `set_reserved` maintain a compact bitset for the dynamic range. `parse_reserved_ports` reads `/proc/sys/net/ipv4/ip_local_reserved_ports`, accepts comma-separated singleton/range syntax, and marks excluded ports. `__binddynport` first returns success for already-bound sockets, then under `port_lock` calls `getsockname`, finds the port field by address family, seeds `rand_r`, builds the reserved-port bitset, and iterates through candidate ports until `bind` succeeds or a non-`EADDRINUSE` failure occurs.

State and persistence: Uses a static pseudo-random seed and reads live kernel configuration on each call. It does not persist bindings outside the socket state.

Dependencies and integration: Depends on `__rpc_sockisbound`, POSIX sockets, `/proc`, syslog, and the shared `port_lock` from `mt_misc.c`. It complements `bindresvport_sa` for non-privileged client sockets.

Risks and test signals: Linux `/proc` parsing failures prevent binding. The random seed is not cryptographic. Tests should cover empty/reserved-port files, range wraparound, already-bound sockets, IPv4/IPv6 family handling, and concurrent callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/binddynport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/bindresvport.c -->
## sources/user-network-fs/libtirpc/src/bindresvport.c

Purpose: Implements BSD-compatible reserved-port binding for RPC clients that need privileged source ports. `bindresvport` delegates to `bindresvport_sa`.

Important APIs and control flow: On Linux, the implementation scans ports 600 through 1023, below `IPPORT_RESERVED`, while skipping entries loaded from `/etc/bindresvport.blacklist`. `load_blacklist` parses comments, whitespace, decimal or base-detected port values, and ignores out-of-range entries. `bindresvport_sa` accepts `sockaddr_in`, optionally `sockaddr_in6`, or a null address, determines the socket family with `getsockname` when needed, randomizes/rotates the static start port, binds under `port_lock`, and treats `EADDRINUSE`, `EADDRNOTAVAIL`, and similar retryable errors as signals to continue scanning.

State and persistence: Maintains static blacklist storage and a static starting port across calls. External persistence is limited to the system blacklist file and the bound socket.

Dependencies and integration: Used by `clnt_tli_create` for sockets opened by the generic client path. Relies on privilege/CAP_NET_BIND_SERVICE semantics and shared `port_lock`.

Risks and test signals: Behavior is platform-conditional and privilege-sensitive. Tests should verify blacklist parsing, concurrent calls, port wraparound, IPv4/IPv6 sockaddr updates, and no mutation beyond the port field.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/bindresvport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_bcast.c -->
## sources/user-network-fs/libtirpc/src/clnt_bcast.c

Purpose: Implements RPC broadcast discovery through `rpc_broadcast_exp` and `rpc_broadcast`, sending `RPCBPROC_CALLIT` requests over datagram transports and invoking a caller callback for each reply.

Important APIs and control flow: `__rpc_getbroadifs` enumerates active interfaces with `getifaddrs`, finds the sunrpc service port via `getaddrinfo`, and builds a TAILQ of IPv4 broadcast or IPv6 multicast destinations. `rpc_broadcast_exp` selects `datagram_n` by default, iterates `__rpc_setconf` results, opens sockets, builds RPCB and optionally legacy PMAP call packets, then repeatedly sends to each broadcast address and polls for replies with expanding waits. Matching replies are decoded with `xdr_replymsg`; successful responses are converted from universal address to `netbuf` and passed to `eachresult`.

State and persistence: Owns only stack arrays and temporary buffers; `__rpc_lowvers` globally controls whether only old portmapper broadcasts are sent.

Dependencies and integration: Integrates with netconfig, rpcbind XDR, optional PORTMAP compatibility, `authunix_create_default`, and debug logging.

Risks and test signals: Broadcast storms, duplicate rpcbind/portmap replies, address-family fixups, and callback-controlled early exit are key risks. Tests should mock datagram sockets, malformed replies, IPv6-v4 fixup, callback false/true behavior, and cleanup of all sockets/interface lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_bcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_dg.c -->
## sources/user-network-fs/libtirpc/src/clnt_dg.c

Purpose: Implements the connectionless datagram RPC `CLIENT` transport used for UDP-style netconfig entries.

Important APIs and control flow: `clnt_dg_create` creates a `CLIENT`, allocates one private `cu_data` block containing input/output buffers, pre-marshals the static call header, enables nonblocking I/O, optionally enables Linux `IP_RECVERR`, and attaches per-fd locking from `clnt_fd_locks.h`. `clnt_dg_call` serializes procedure/auth/arguments, increments XID, sends with `sendto` or a connected socket, polls for replies, retransmits on retry timeout until total timeout, filters replies by XID unless async mode is enabled, decodes reply status, validates/unpacks auth, and refreshes credentials up to two times except for RPCSEC_GSS.

State and persistence: Per-client state tracks fd, remote address, retry/total timeouts, async/connect flags, cached error, and pre-marshalled XDR position. Global `dg_fd_locks` serializes all handles sharing a file descriptor.

Dependencies and integration: Used by `clnt_tli_create` for `NC_TPI_CLTS`. Depends on `authnone_create`, XDR, poll, socket APIs, `clnt_fd_lock`, and optional GSS.

Risks and test signals: The fd lock is held across full RPC/retransmission. Tests should cover timeout math, XID mismatch filtering, async mode, `CLSET_*` controls, IP error queue handling, destroy while operations are pending, and shared-fd serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_dg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_fd_locks.h -->
## sources/user-network-fs/libtirpc/src/clnt_fd_locks.h

Purpose: Provides inline support for per-file-descriptor client locks shared by datagram and virtual-circuit transports, ensuring multiple `CLIENT` handles over the same fd do not concurrently read/write interleaved RPC records.

Important APIs and control flow: Defines `fd_lock_t` with `active`, `pending`, and condition variable fields. Without `MAX_FDLOCKS_PREALLOC`, `fd_locks_t` is a TAILQ of `fd_lock_item_t` nodes keyed by fd and refcounted. With preallocation, low-numbered fds are mapped into an array sized by `__rpc_dtbsize` and `MAX_FDLOCKS_PREALLOC`; higher fds still use the TAILQ. `fd_locks_init`, `fd_locks_destroy`, `fd_lock_create`, and `fd_lock_destroy` allocate, reuse, refcount, and clean up locks.

State and persistence: The header owns no global instance; each transport has its own static `fd_locks_t *`. Lock state persists for the lifetime of active client handles.

Dependencies and integration: Requires callers to hold the global `clnt_fd_lock` around create/destroy and active/pending changes.

Risks and test signals: Preallocated locks do not increment refs and may outlive individual clients. TAILQ destroy uses `TAILQ_FOREACH` while freeing, which is sensitive to implementation. Tests should cover shared fd refcounts, high fd allocation, pending wait/cleanup, and preallocation boundary behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_fd_locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_generic.c -->
## sources/user-network-fs/libtirpc/src/clnt_generic.c

Purpose: Implements high-level RPC client creation APIs that hide netconfig selection, rpcbind lookup, version negotiation, socket creation, and transport-specific client construction.

Important APIs and control flow: `clnt_create` and `clnt_create_timed` iterate netconfig entries for a nettype via `__rpc_setconf`, trying `clnt_tp_create_timed` until one succeeds while preserving more useful errors than final name-translation failures. `clnt_create_vers_timed` probes `NULLPROC`, adjusts version ranges from `RPC_PROGVERSMISMATCH`, and returns the highest supported version. `clnt_tp_create_timed` resolves service address with `__rpcb_findaddr_timed`, reuses a returned client when possible, or calls `clnt_tli_create`. `clnt_tli_create` opens/binds fds, raises low descriptors, verifies address family, then chooses `clnt_vc_create` or `clnt_dg_create` from netconfig semantics.

State and persistence: Uses global `rpc_createerr`/thread-specific create errors and `__rpc_minfd`. Created clients own sockets when opened internally.

Dependencies and integration: Connects netconfig, rpcbind, reserved-port binding, TCP_NODELAY, fd raising, and the dg/vc transports.

Risks and test signals: `__rpc_raise_fd` unexpectedly calls `fsync` on duplicated fds. Tests should cover version fallback, error preservation, fd ownership flags, address-family mismatches, nettype length rejection, and all netconfig semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_perror.c -->
## sources/user-network-fs/libtirpc/src/clnt_perror.c

Purpose: Formats and prints RPC client and client-creation errors for legacy libtirpc APIs.

Important APIs and control flow: `_buf` lazily allocates one process-global 256-byte buffer. `clnt_sperror` fetches `CLNT_GETERR`, appends the base `clnt_sperrno` string, and adds status-specific detail for errno, version ranges, auth errors, or unknown low bits. `clnt_perror`, `clnt_perrno`, and `clnt_pcreateerror` print to stderr. `clnt_spcreateerror` formats `rpc_createerr`, including nested pmap failure details. `auth_errmsg` maps `enum auth_stat` values.

State and persistence: The static buffer is reused for all callers and is not thread-safe. It persists until process exit.

Dependencies and integration: Used by pmap helpers and applications calling traditional SunRPC error APIs. Depends on global or macro-resolved `rpc_createerr`.

Risks and test signals: Shared buffer reuse, truncation handling, and enum-range mismatches are the main risks. Tests should check every `enum clnt_stat`, auth-error detail, pmap/system errno formatting, null input handling, and concurrent callers if thread safety matters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_perror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_raw.c -->
## sources/user-network-fs/libtirpc/src/clnt_raw.c

Purpose: Implements an in-process memory-backed RPC client used with raw service transports for tests and microbenchmarks without kernel networking.

Important APIs and control flow: `clnt_raw_create` lazily allocates one global `clntraw_private`, initializes `__rpc_rawcombuf`, pre-marshals the call header, and returns a singleton `CLIENT` using `authnone`. `clnt_raw_call` writes request data into the shared XDR memory stream, invokes `svc_getreq_common(FD_SETSIZE)` directly to let the in-process server handle it, then decodes the reply from the same buffer. It handles partial decode cleanup and auth refresh retry. `clnt_raw_freeres` switches the shared XDR stream to `XDR_FREE`.

State and persistence: Singleton private state and raw buffer persist for the process lifetime. `clnt_raw_destroy` is intentionally a no-op.

Dependencies and integration: Integrates with `svc_raw_create`/raw service machinery through `__rpc_rawcombuf` and `svc_getreq_common`.

Risks and test signals: The singleton design means no independent raw clients. Tests should cover raw client/server round trips, auth refresh, decode failure cleanup, XDR free paths, and lock behavior under concurrent raw calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_simple.c -->
## sources/user-network-fs/libtirpc/src/clnt_simple.c

Purpose: Provides `rpc_call`, the simplified one-shot RPC API that internally caches a client handle for repeated calls to the same host/program/version/nettype.

Important APIs and control flow: `rpc_call` creates a thread-specific `rpc_call_private` key on first use, then reuses the cached `CLIENT` only if pid, program, version, host, and nettype still match. On cache miss it destroys the old client, calls `clnt_create`, sets a 5-second retry timeout, marks the fd close-on-exec, stores identity fields when they fit fixed buffers, and calls `CLNT_CALL` with a 25-second total timeout. Failures invalidate the cache.

State and persistence: Cache is thread-specific and pid-aware to avoid reuse after fork. The destructor destroys the cached client at key cleanup.

Dependencies and integration: Wraps `clnt_create`, `CLNT_CONTROL`, and `CLNT_CALL`. Defaults empty nettype to `netpath`.

Risks and test signals: Fixed host/nettype buffers only cache short values. Tests should cover cache hit/miss, fork pid change, failure invalidation, close-on-exec flag, default netpath, and thread-local isolation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_vc.c -->
## sources/user-network-fs/libtirpc/src/clnt_vc.c

Purpose: Implements connection-oriented RPC `CLIENT` transport for TCP/local stream-style netconfig entries using XDR record streams.

Important APIs and control flow: `clnt_vc_create` allocates `CLIENT` and `ct_data`, creates/reuses an fd lock, connects the socket when needed, copies the remote `netbuf`, pre-marshals a static call header with a process-global `disrupt` component in the XID, and initializes `xdrrec_create` with `read_vc`/`write_vc`. `clnt_vc_call` serializes a call into the record stream, supports batched calls when no results and zero timeout are requested, then skips records until the matching XID is decoded. It validates auth, unwraps results, and may refresh credentials. `clnt_vc_control` exposes timeout, fd, address, XID, program, and version controls.

State and persistence: Per-client state tracks fd ownership, timeout, remote address, cached error, pre-marshalled header, and XDR record stream. Shared static fd locks serialize handles on the same fd.

Dependencies and integration: Selected by `clnt_tli_create` for connection-oriented netconfig semantics. Uses poll/read/write, XDR records, auth APIs, `ops_lock`, `disrupt_lock`, and optional GSS.

Risks and test signals: Full-call fd locking limits concurrency. Tests should cover batching, timeout propagation to `read_vc`, mismatched XID skipping, control mutation of header fields, destroy pending waits, and short writes/EOF.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/clnt_vc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/crypt_client.c -->
## sources/user-network-fs/libtirpc/src/crypt_client.c

Purpose: Implements `_des_crypt_call`, a client-side RPC wrapper for talking to a local `crypt` service when hardware or external DES support is requested.

Important APIs and control flow: The routine opens a netconfig session, selects the first loopback transport, creates a `CRYPT_PROG`/`CRYPT_VERS` client, populates `desargs` from caller buffer and `desparams`, calls generated `des_crypt_1`, then copies returned encrypted/decrypted data and IV back to the caller for `DESERR_NONE` or `DESERR_NOHWDEVICE`. It frees RPC results and destroys the client.

State and persistence: No cached state; each call opens netconfig and creates a client. External state is the local crypt service and loopback transport database.

Dependencies and integration: Depends on rpcsvc crypt generated interfaces, netconfig iteration, and `clnt_tp_create`. Complements the software DES implementation in `des_crypt.c`/`des_impl.c`.

Risks and test signals: Failing to find loopback or crypt service returns hardware error. Tests should cover no loopback transport, client creation failure, null result, successful data/IV copy, and result freeing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/crypt_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/debug.c -->
## sources/user-network-fs/libtirpc/src/debug.c

Purpose: Provides global debug-level and logging behavior for libtirpc.

Important APIs and control flow: `libtirpc_set_debug(char *name, int level, int use_stderr)` clamps negative levels to zero, chooses stderr or syslog, optionally calls `openlog`, stores the global level, and emits a level-1 startup message via `LIBTIRPC_DEBUG`. `libtirpc_log_dbg` formats variadic messages to stderr with newline or to syslog `LOG_NOTICE`.

State and persistence: `libtirpc_debug_level` and `log_stderr` are process-global mutable variables. They are not protected by a lock.

Dependencies and integration: Used by broadcast, public-key, key, and netname helper code through the macro in `debug.h`. Exported privately in `libtirpc.map.in`.

Risks and test signals: Races are possible if debug settings change while other threads log. Tests should verify negative clamp, stderr/syslog selection, message thresholding through the macro, and format handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/debug.h -->
## sources/user-network-fs/libtirpc/src/debug.h

Purpose: Declares libtirpc debugging globals/functions and defines the `LIBTIRPC_DEBUG` conditional logging macro.

Important APIs and control flow: Exposes `libtirpc_debug_level`, `log_stderr`, `libtirpc_log_dbg`, and `libtirpc_set_debug`. `LIBTIRPC_DEBUG(level, msg)` evaluates the call tuple only when the requested level is enabled. The inline `vlibtirpc_log_dbg` variant accepts a `va_list` and mirrors stderr/syslog routing.

State and persistence: References global state owned by `debug.c`; no storage is created by the header except inline function code in each translation unit.

Dependencies and integration: Included by files that want debug output without taking a hard dependency on syslog details. The macro's tuple style requires callers to write `LIBTIRPC_DEBUG(1, ("format", arg))`.

Risks and test signals: Macro argument style is easy to misuse. The inline function uses `vfprintf` but this header includes `stdarg.h` and `syslog.h`, not `stdio.h`, so transitive include assumptions matter. Tests/builds should compile debug callers with strict warnings and verify disabled logs avoid formatting side effects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/des_crypt.c -->
## sources/user-network-fs/libtirpc/src/des_crypt.c

Purpose: Provides public DES encryption entry points `cbc_crypt` and `ecb_crypt` over libtirpc's software DES backend.

Important APIs and control flow: `cbc_crypt` sets `des_mode` to CBC, copies the IV into `desparams`, calls `common_crypt`, and copies the updated IV back. `ecb_crypt` uses ECB mode. `common_crypt` validates the buffer length is an 8-byte multiple and no larger than `DES_MAXDATA`, sets encrypt/decrypt direction from `DES_DIRMASK`, copies the 8-byte key, calls `_des_crypt`, and returns `DESERR_NONE` for requested software mode or `DESERR_NOHWDEVICE` when a hardware device was requested but software was used.

State and persistence: No persistent state. The caller's buffer and CBC IV are mutated in place.

Dependencies and integration: Uses `_des_crypt` from `des_impl.c` and DES constants/types from RPC headers. Export is conditional through map placeholders.

Risks and test signals: DES is legacy/weak cryptography. Tests should cover ECB/CBC known-answer vectors, invalid lengths, DES_HW fallback status, IV update semantics, and encrypt/decrypt round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/des_crypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/des_impl.c -->
## sources/user-network-fs/libtirpc/src/des_impl.c

Purpose: Contains the table-driven software DES implementation used by `des_crypt.c`.

Important APIs and control flow: Large static lookup tables `des_SPtrans` and `des_skb` implement S-box/permutation work. `des_set_key` converts the 8-byte key into a 32-word key schedule using DES key permutations and the `shifts2` rotation plan. `des_encrypt` applies initial permutation, 16 Feistel rounds using the schedule in forward or reverse order, then final permutation. `_des_crypt` prepares the schedule, walks the caller buffer in 8-byte blocks, applies CBC XOR chaining when requested, encrypts or decrypts in place, updates the IV to the final ciphertext/plaintext dependency, clears temporaries and the schedule, and returns success.

State and persistence: Static tables are read-only. The buffer and `desparams->des_ivec` are mutable caller state.

Dependencies and integration: Called only by `common_crypt`. Uses DES layout macros and `struct desparams`.

Risks and test signals: Table correctness, endian conversion macros, and 32-bit masking on 64-bit `unsigned long` are critical. Tests should use standard DES vectors for ECB/CBC, multi-block IV chaining, decrypt inverse, and sanitizer checks for unaligned buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/des_impl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/des_soft.c -->
## sources/user-network-fs/libtirpc/src/des_soft.c

Purpose: Provides `des_setparity`, the DES key utility that forces odd parity in each of the eight key bytes.

Important APIs and control flow: A static `partab[128]` maps the low seven bits of a byte to the corresponding odd-parity byte. `des_setparity(char *p)` loops over eight bytes and replaces each with `partab[*p & 0x7f]`.

State and persistence: The lookup table is process read-only; the caller's key buffer is modified in place.

Dependencies and integration: Used by callers that need DES-compatible key parity before `cbc_crypt`, `ecb_crypt`, or AUTH_DES operations.

Risks and test signals: The function ignores the input high bit by masking with `0x7f`. Tests should verify all output bytes have odd parity, exactly eight bytes are touched, known parity conversions hold, and signed-char inputs behave as intended through the mask.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/des_soft.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/epoll_sub.c -->
## sources/user-network-fs/libtirpc/src/epoll_sub.c

Purpose: Supplies direct syscall wrappers for `epoll_create`, `epoll_ctl`, and `epoll_wait` on systems/builds where libc lacks these entry points.

Important APIs and control flow: Defines syscall numbers `254`, `255`, and `256`, then each public function simply calls `syscall` with the corresponding number and arguments.

State and persistence: No local state. Kernel epoll instances and interest lists are managed by the returned file descriptors and syscalls.

Dependencies and integration: Depends on Linux syscall numbering for a specific architecture family and `<sys/epoll.h>` structures. It is a portability shim rather than RPC logic.

Risks and test signals: Hard-coded syscall numbers are architecture-sensitive. Tests should compile only on intended targets, compare wrapper behavior to libc epoll when available, verify errno propagation, and guard builds for unsupported architectures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/epoll_sub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getnetconfig.c -->
## sources/user-network-fs/libtirpc/src/getnetconfig.c

Purpose: Implements `/etc/netconfig` access APIs: `setnetconfig`, `getnetconfig`, `endnetconfig`, `getnetconfigent`, `freenetconfigent`, `nc_sperror`, and `nc_perror`.

Important APIs and control flow: A global `netconfig_info` cache stores parsed entries and a shared file pointer protected by `nc_db_lock`. `setnetconfig` opens `NETCONFIG`, increments a reference count, and returns a session handle. `getnetconfig` returns cached entries or reads/skips comments, allocates a list node and `struct netconfig`, then parses fields with `parse_ncp`. `endnetconfig` decrements references and frees the cache/file when the final handle closes. `getnetconfigent` searches the cache or scans the file for one netid and returns a duplicated independent entry.

State and persistence: Persistent process cache mirrors `/etc/netconfig` until all sessions end. Error state is thread-specific via `nc_key`, with static fallback.

Dependencies and integration: Netconfig drives transport selection in client creation, broadcasts, key/crypt clients, and netpath.

Risks and test signals: Parser mutates line buffers and has complex ownership rules. Tests should cover malformed lines, lookup-list parsing, multiple nested sessions, thread-specific errors, `getnetconfigent` duplication/freeing, and cache teardown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getnetconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getnetpath.c -->
## sources/user-network-fs/libtirpc/src/getnetpath.c

Purpose: Implements `NETPATH` iteration APIs that select visible netconfig transports in caller-preferred order.

Important APIs and control flow: `setnetpath` allocates a session and opens `setnetconfig`. If the environment variable `NETPATH` is set, it copies it and closes the netconfig session until individual entries are needed. `getnetpath` either iterates visible netconfig entries when `NETPATH` is unset, or tokenizes the copied `NETPATH` string by colon, ignores invalid netids, and returns `getnetconfigent` results tracked in a session allocation chain. `endnetpath` closes any netconfig handle, frees the copied `NETPATH`, frees all allocated netconfig entries, and releases the session. `_get_next_token` null-terminates tokens while handling backslash escapes.

State and persistence: Per-session mutable cursor state. External persistence is the environment and `/etc/netconfig`.

Dependencies and integration: Used by generic client paths when nettype defaults to `netpath`.

Risks and test signals: `_get_next_token` uses overlapping `strcpy`, noted in comments. Tests should cover unset NETPATH, escaped delimiters/backslashes, invalid netids, cleanup chains, and nested sessions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getnetpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getpeereid.c -->
## sources/user-network-fs/libtirpc/src/getpeereid.c

Purpose: Provides a fallback `getpeereid` implementation when the platform does not supply one.

Important APIs and control flow: Under `!HAVE_GETPEEREID`, `getpeereid(int s, uid_t *euid, gid_t *egid)` calls `getsockopt(SOL_SOCKET, SO_PEERCRED)` into `struct ucred`, then copies `uc.uid` and `uc.gid` to outputs.

State and persistence: No persistent state. It reads peer credential state maintained by the kernel for a connected Unix-domain socket.

Dependencies and integration: Used by local transport authentication paths needing peer uid/gid. Linux-specific `SO_PEERCRED` semantics are assumed.

Risks and test signals: Output pointers are not checked for null. Tests should use socketpairs with known credentials, verify error propagation on invalid sockets, and confirm compile guards exclude this implementation where libc provides `getpeereid`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getpeereid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getpublickey.c -->
## sources/user-network-fs/libtirpc/src/getpublickey.c

Purpose: Implements public-key lookup for AUTH_DES/Secure RPC from `/etc/publickey` with optional NIS fallback.

Important APIs and control flow: `getpublickey` dispatches to `__getpublickey_LOCAL` when set, otherwise `__getpublickey_real`. The real path calls `getpublicandprivatekey`, splits the returned `public:private` record at `:`, copies `HEXKEYBYTES` of public key, and terminates it. `getpublicandprivatekey` scans `/etc/publickey`, skipping comments, honoring `+` NIS inclusion when compiled with YP, parsing key/value fields with `strsep`, and copying the matched value to `ret`.

State and persistence: Global function pointer hook allows local server overrides. External state is `/etc/publickey` and optional NIS maps.

Dependencies and integration: Used by key/auth DES code and exported in newer map versions.

Risks and test signals: Uses `strcpy` into caller-provided buffers and assumes adequate size. Tests should cover local hook, missing file, malformed records, NIS-disabled `+`, exact key matching, public/private split, and buffer sizing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getpublickey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getrpcent.c -->
## sources/user-network-fs/libtirpc/src/getrpcent.c

Purpose: Supplies fallback implementations for RPC database functions when libc lacks them: `getrpcbynumber`, `getrpcbyname`, `setrpcent`, `endrpcent`, and `getrpcent`.

Important APIs and control flow: A process-global `rpcdata` structure holds the `/etc/rpc` file, stay-open flag, aliases, current line, and optional YP state. Lookup by number/name rewinds with `setrpcent`, iterates `getrpcent`, and closes with `endrpcent`. `getrpcent` reads a line or YP record and passes it to `interpret`, which strips comments/newlines, parses service name, numeric program, and aliases into static storage.

State and persistence: Global static `rpcdata` is reused and not thread-specific. File handle persistence is controlled by `stayopen`.

Dependencies and integration: Supports `getrpcport` and applications needing RPC program database lookup.

Risks and test signals: Non-thread-safe static result storage and recursive skip of malformed/comment lines are important. Tests should cover comments, aliases, malformed lines, stayopen behavior, YP fallback guards, and repeated calls overwriting previous results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getrpcent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getrpcport.c -->
## sources/user-network-fs/libtirpc/src/getrpcport.c

Purpose: Implements the legacy `getrpcport` convenience wrapper that resolves a host and asks portmapper for a program/version/protocol port.

Important APIs and control flow: The function asserts a non-null host, resolves it with `gethostbyname`, initializes an IPv4 `sockaddr_in`, copies at most the address field size from `hostent`, and calls `pmap_getport`.

State and persistence: No persistent local state. It depends on resolver state and remote portmapper registration state.

Dependencies and integration: Uses IPv4-only legacy name resolution and the pmap compatibility layer. It is exported in the base map.

Risks and test signals: IPv6 is unsupported and `gethostbyname` returns static resolver storage. Tests should cover unknown host returning 0, long `h_length` truncation, successful pmap delegation, and protocol value pass-through.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/getrpcport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/key_call.c -->
## sources/user-network-fs/libtirpc/src/key_call.c

Purpose: Implements Secure RPC keyserver client functions for setting secrets, encrypting/decrypting session keys, generating DES keys, storing netname key material, checking secret-key presence, and deriving conversation keys.

Important APIs and control flow: Public wrappers build `key_prot` argument/result structs and call the internal `key_call`. `key_call` first honors local override hooks for keyserver-internal AUTH_DES recursion, chooses keyserver protocol version 1 or 2 by procedure, obtains a cached loopback client from `getkeyserv_handle`, and performs `clnt_call` with a 30-second timeout. `getkeyserv_handle` keeps a thread-specific client, rebuilds after fork or effective uid change, searches loopback netconfig entries preferring `NC_TPI_COTS_ORD`, sets AUTH_SYS credentials for the effective uid, sets retry timeout, and marks the fd close-on-exec.

State and persistence: Thread-specific `key_call_private` caches a client by pid and euid. Global function pointers provide local implementations for keyserver use.

Dependencies and integration: Depends on netconfig, uname nodename, authsys, key_prot XDR, and client generic APIs.

Risks and test signals: Secret material is copied through stack/result structs; `key_secretkey_is_set` explicitly wipes the private key field. Tests should cover uid/pid cache invalidation, local hook dispatch, version selection, loopback fallback, auth recreation, and status-to-return mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/key_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/key_prot_xdr.c -->
## sources/user-network-fs/libtirpc/src/key_prot_xdr.c

Purpose: Contains rpcgen-generated XDR routines for keyserver protocol types.

Important APIs and control flow: The file encodes/decodes `keystatus`, fixed `keybuf`, netname strings, `cryptkeyarg`, `cryptkeyarg2`, discriminated `cryptkeyres`, Unix credentials, `getcredres`, `key_netstarg`, and discriminated `key_netstres`. Union result routines first serialize status and only process payload arms on `KEY_SUCCESS`.

State and persistence: No local state. In decode/free modes, dynamic memory is owned by XDR routines for strings, arrays, and netobjs.

Dependencies and integration: Used by `key_call.c`, keyserv-compatible code, and exported as part of the 0.3.2 ABI set.

Risks and test signals: Generated code assumes protocol constants such as `HEXKEYBYTES`, `MAXNETNAMELEN`, and `MAXGIDS`. Tests should round-trip each structure, verify failure arms do not touch success payloads, and exercise XDR_FREE after partial decodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/key_prot_xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/libtirpc.map.in -->
## sources/user-network-fs/libtirpc/src/libtirpc.map.in

Purpose: Defines the ELF symbol version map for libtirpc, controlling public ABI, private exports, and conditional symbol insertion.

Important APIs and control flow: `TIRPC_0.3.0` exports core RPC, XDR, auth, client, service, netconfig, pmap, and rpcbind symbols, with placeholders for GSS, DES, and RPC database symbols. Later versions add key/netname APIs (`TIRPC_0.3.2`), local key/publickey hooks and `xdr_sizeof` (`TIRPC_0.3.3`), and selected credential APIs (`TIRPC_1.3.7`). `TIRPC_PRIVATE` exports `__libc_clntudp_bufcreate`, `__svc_clean_idle`, `svc_auth_none`, and `libtirpc_set_debug`.

State and persistence: No runtime state; it shapes link-time and dynamic-loader symbol visibility.

Dependencies and integration: Consumed by the build system, with `@...@` placeholders substituted by configure/meson logic depending on enabled features.

Risks and test signals: ABI regressions occur if symbols move versions or are omitted. Tests should inspect `readelf --dyn-syms --version-info`, build with feature combinations, and verify consumers link against expected versions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/libtirpc.map.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/mt_misc.c -->
## sources/user-network-fs/libtirpc/src/mt_misc.c

Purpose: Centralizes libtirpc global synchronization primitives, thread-specific-data keys, and thread-safe access to `rpc_createerr`.

Important APIs and control flow: The file initializes many mutexes/rwlocks used across service lists, fd sets, auth caches, client fd locks, raw transports, netconfig, port binding, and ops initialization. It declares TSD keys for broadcast, `rpc_call`, TCP/UDP, netconfig errors, rpc create errors, netgroups, and key calls. `__rpc_createerr` lazily creates the `rce_key`, allocates a per-thread `struct rpc_createerr`, installs it, and falls back to the global `rpc_createerr` on allocation/key failure. `tsd_key_delete` deletes initialized pthread keys.

State and persistence: This file is almost entirely process-global state. Per-thread create-error storage persists until key destructor/free.

Dependencies and integration: Every major transport/auth/service module relies on these locks by extern declaration.

Risks and test signals: `tsd_key_delete` appears to delete `rce_key` when checking `rg_key`, likely a typo. Tests should cover per-thread `rpc_createerr` isolation, lock symbol linkage, repeated key creation, and cleanup behavior under sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/mt_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/netname.c -->
## sources/user-network-fs/libtirpc/src/netname.c

Purpose: Converts local Unix user/host identities into Secure RPC network names.

Important APIs and control flow: `getnetname` chooses `host2netname` for effective uid 0 and `user2netname` otherwise. `user2netname` obtains the default NIS/RPC domain if none is supplied, checks the formatted length against `MAXNETNAMELEN`, and writes `unix.<uid>@<domain>`. `host2netname` similarly defaults domain and hostname, then writes `unix.<host>@<domain>`.

State and persistence: No owned persistent state. It reads effective uid, hostname, and default domain state from system/RPC helpers.

Dependencies and integration: Complements `netnamer.c` reverse mapping and key/publickey lookup. Uses `__rpc_get_default_domain`.

Risks and test signals: Uses `sprintf` after manual length checks. Tests should cover root/user branch, explicit/default domain, default hostname, maximum name lengths, and domain lookup failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/netname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/netnamer.c -->
## sources/user-network-fs/libtirpc/src/netnamer.c

Purpose: Converts Secure RPC network names back to Unix credentials or hostnames, using `/etc/netid`, optional NIS, and local passwd/group databases.

Important APIs and control flow: `netname2user` first tries `getnetid`; a matching record yields uid, gid, and supplementary groups from colon/comma-separated fields. If no netid entry exists, it parses `unix.<uid>@<domain>`, verifies the default domain, looks up passwd by uid, and derives groups via `_getgroups`. `netname2host` similarly honors netid host records beginning with `0:`, otherwise parses `unix.<host>@<domain>`. `getnetid` scans `/etc/netid`, supports `+` NIS inclusion when built with YP, and returns copied map values.

State and persistence: No long-lived local state. It reads `/etc/netid`, passwd/group databases, default domain, and optional NIS maps on demand.

Dependencies and integration: Reverse side of `netname.c`; used by AUTH_DES credential mapping.

Risks and test signals: Fixed 1024-byte buffers and `strcpy` assume map values fit. Tests should cover netid records, fallback parsing, wrong domain rejection, duplicate group filtering, too many groups, host records, and YP-disabled `+`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/netnamer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/nis.h -->
## sources/user-network-fs/libtirpc/src/nis.h

Purpose: Provides a minimal internal subset of NIS/NIS+ type definitions so libtirpc can compile without relying on glibc SunRPC/libnsl headers.

Important APIs and types: Defines `NIS_PK_NONE`, `nis_attr`, `nis_name`, `endpoint`, and `nis_server`. `nis_server` contains a server name, variable-length endpoint array, key type, and public key `netobj`.

State and persistence: Header-only type definitions; no runtime state.

Dependencies and integration: Supplies structures needed by AUTH_DES/NIS-related code that references NIS server metadata.

Risks and test signals: Type layout must stay compatible with expected external NIS definitions. Tests should compile consumers with and without system NIS headers, verify struct sizes/field access where ABI matters, and ensure include guards prevent duplicate definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/nis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_clnt.c -->
## sources/user-network-fs/libtirpc/src/pmap_clnt.c

Purpose: Implements legacy portmapper registration wrappers over rpcbind APIs.

Important APIs and control flow: `pmap_set` accepts only UDP or TCP, obtains the corresponding inet netconfig via `__rpc_getconfip`, formats a universal address `0.0.0.0.high.low` from the requested port, converts it to a transport address with `uaddr2taddr`, and calls `rpcb_set`. `pmap_unset` attempts `rpcb_unset` for both UDP and TCP inet netconfigs and returns true if either succeeds for backward compatibility.

State and persistence: No local persistent state; it mutates remote/local rpcbind registration state.

Dependencies and integration: Bridges PMAP v2 compatibility APIs to rpcbind registration. Depends on netconfig conversion helpers.

Risks and test signals: Only IPv4 inet UDP/TCP are handled. Tests should cover invalid protocol rejection, netconfig lookup failure, universal-address conversion failure, cleanup of netconfig/netbuf, and partial unset success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_clnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_getmaps.c -->
## sources/user-network-fs/libtirpc/src/pmap_getmaps.c

Purpose: Implements `pmap_getmaps`, retrieving the full legacy portmapper map list from a host.

Important APIs and control flow: The function asserts a non-null IPv4 address, sets its port to `PMAPPORT`, creates a TCP client with `clnttcp_create`, calls `PMAPPROC_DUMP` with `xdr_pmaplist` and a 60-second timeout, prints RPC errors on failure, destroys the client, resets the caller address port to zero, and returns the decoded linked list head.

State and persistence: No local persistent state. The returned `pmaplist` is caller-owned XDR-allocated data.

Dependencies and integration: Uses legacy TCP client compatibility, pmap protocol XDR, and `clnt_perror`.

Risks and test signals: Mutates the input address port temporarily. Tests should cover successful dump/free, RPC failure logging, client creation failure, address port restoration, and caller ownership of returned list.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_getmaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_getport.c -->
## sources/user-network-fs/libtirpc/src/pmap_getport.c

Purpose: Implements `pmap_getport`, querying a host's legacy portmapper for a program/version/protocol port.

Important APIs and control flow: The function sets the target IPv4 address port to `PMAPPORT`, creates a UDP client with small buffers and a 5-second retry timeout, sends `PMAPPROC_GETPORT` with an `xdr_pmap` argument and `xdr_u_short` result under a 60-second total timeout, records `RPC_PMAPFAILURE` plus nested client error on RPC failure, records `RPC_PROGNOTREGISTERED` for a zero result, destroys the client, restores address port to zero, and returns the port.

State and persistence: No local persistent state; it updates global/thread `rpc_createerr` on failure.

Dependencies and integration: Used by `getrpcport` and older RPC clients. Depends on UDP client compatibility and pmap XDR.

Risks and test signals: IPv4/UDP only and mutates input sockaddr. Tests should cover success, zero-port unregistered, RPC transport failure, client creation failure, timeout constants, and port restoration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_getport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_prot.c -->
## sources/user-network-fs/libtirpc/src/pmap_prot.c

Purpose: Provides the XDR codec for the legacy `struct pmap` registration/query record.

Important APIs and control flow: `xdr_pmap(XDR *xdrs, struct pmap *regs)` asserts non-null inputs and serializes program, version, protocol, and port as unsigned longs in order. It returns `FALSE` at the first failed XDR primitive.

State and persistence: No local state. Decode/free behavior is entirely primitive scalar handling.

Dependencies and integration: Used by `pmap_getport`, pmap dump list XDR, and compatibility portmapper calls.

Risks and test signals: Legacy protocol uses `u_long`, so ABI width and XDR's fixed external representation matter. Tests should round-trip boundary values, malformed/truncated streams, and interoperate with `xdr_pmaplist`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_prot2.c -->
## sources/user-network-fs/libtirpc/src/pmap_prot2.c

Purpose: Implements XDR for linked lists of legacy portmapper records.

Important APIs and control flow: `xdr_pmaplist` encodes/decodes/frees a `struct pmaplist **` as an XDR recursive optional list but implements the recursion iteratively. Each loop emits or reads a boolean `more_elements`; when true it uses `xdr_reference` to process the current node's `struct pmap` with `xdr_pmap`, then advances to `pml_next`. In `XDR_FREE`, it saves the next pointer before freeing the current node. `xdr_pmaplist_ptr` is a compatibility wrapper with a historical pointer signature.

State and persistence: No static state. Decode allocates list nodes through XDR reference handling; free releases them.

Dependencies and integration: Used by `pmap_getmaps` and exported ABI.

Risks and test signals: Pointer casting in `xdr_pmaplist_ptr` is compatibility-sensitive. Tests should cover empty list, multi-node encode/decode/free, malformed boolean streams, and leak-free cleanup after partial decode failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_prot2.c -->
