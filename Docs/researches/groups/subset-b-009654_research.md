# Research Group subset-b-009654

This grouped report covers the high-level libnfs client implementation files under `sources/user-network-fs/libnfs/lib`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/libnfs-sync.c -->
# sources/user-network-fs/libnfs/lib/libnfs-sync.c

## Purpose

`libnfs-sync.c` implements the blocking, POSIX-like libnfs API on top of the library's asynchronous NFS and RPC operations. It lets callers use functions such as `nfs_mount`, `nfs_open`, `nfs_read`, `nfs_write`, `nfs_stat64`, `nfs_opendir`, `nfs_rename`, and ACL/export discovery helpers without manually polling the RPC file descriptor. The file is mostly a synchronization facade: each synchronous function initializes callback state, starts the corresponding `*_async` operation, waits until the callback marks completion, translates callback data into the caller's output buffers, and returns a libnfs status or negative errno.

## Important APIs, Types, and Functions

The central type is `struct sync_cb_data`, which records `is_finished`, `status`, `offset`, generic `return_data`, integer scratch `return_int`, a call name used in diagnostics, and, when `HAVE_MULTITHREADING` is enabled, a per-call semaphore. `nfs_init_cb_data` initializes this state and, in multithreaded mode, maps the caller to a per-thread `struct nfs_context` clone hanging off `nfsi->thread_ctx`. `cb_data_is_finished` records status and wakes the semaphore. `wait_for_nfs_reply` waits on the NFS context by either blocking on the semaphore when the service thread is active or by polling `nfs_get_fd` and dispatching `nfs_service`. `wait_for_reply` performs the same loop for raw `struct rpc_context` operations such as mount export listing.

The public synchronous wrappers cover mount lifecycle (`nfs_mount`, `nfs_umount`), metadata (`nfs_stat`, `nfs_stat64`, `nfs_lstat64`, `nfs_fstat`, `nfs_fstat64`, `nfs_statvfs`, `nfs_statvfs64`), file handles (`nfs_open`, `nfs_open2`, `nfs_creat`, `nfs_close`), I/O (`nfs_pread`, `nfs_read`, `nfs_preadv`, `nfs_readv`, `nfs_pwrite`, `nfs_write`, `nfs_fsync`), file sizing (`nfs_ftruncate`, `nfs_truncate`), namespace mutation (`nfs_mkdir`, `nfs_mkdir2`, `nfs_rmdir`, `nfs_mknod`, `nfs_unlink`, `nfs_symlink`, `nfs_rename`, `nfs_link`), directory open (`nfs_opendir`), offset/lock operations (`nfs_lseek`, `nfs_lockf`, `nfs_fcntl`), permissions and ownership (`nfs_chmod`, `nfs_lchmod`, `nfs_fchmod`, `nfs_chown`, `nfs_lchown`, `nfs_fchown`), times (`nfs_utimes`, `nfs_lutimes`, `nfs_utime`), access checks (`nfs_access`, `nfs_access2`), symlink reads (`nfs_readlink`, `nfs_readlink2`), and ACL helpers (`nfs3_getacl`, `nfs4_getacl`, `nfs3_acl_free`, `nfs4_acl_free`).

Outside mounted file operations, the file also provides mount daemon export enumeration through `mount_getexports_mountport`, `mount_getexports_timeout`, `mount_getexports`, and `mount_free_export_list`. When `NO_SRV_AUTOSCAN` is not defined, `nfs_find_local_servers` sends UDP portmapper CALLIT probes on broadcast interfaces and returns a deduplicated `nfs_server_list`.

## Control Flow

The common wrapper flow is: fill any `sync_cb_data` output pointers, call `nfs_init_cb_data`, submit the async request, wait for callback completion, destroy the semaphore if present, and return `cb_data.status`. Each callback handles only operation-specific result transfer, such as copying `struct stat`, assigning a returned `struct nfsfh *`, duplicating a readlink string, copying `struct statvfs`, or deep-copying NFSv4 ACL entries.

Mounting uses `_nfs_mount` to submit `nfs_mount_async`, wait, clear `rpc->connect_cb`, and disconnect on failure. Public `nfs_mount` first tries the default NFSv3 path and, if it fails while `default_version` is still set, clears the v3 root file handle, switches `nfsi->version` to `NFS_V4`, disconnects, and retries. `nfs_umount` is similar but treats the expected `-EIO` from the v3 disconnect path as success. `nfs_open` retries up to ten times on `-EIO`, which is a targeted recovery path for reconnectable open failures.

The raw RPC export flow initializes an independent `rpc_context`, optionally sets mount port or timeout, submits `mount_getexports_async`, waits with `wait_for_reply`, destroys the RPC context, and returns a newly allocated linked list. Server discovery binds a UDP RPC context to `0.0.0.0`, enumerates IPv4 broadcast-capable non-loopback interfaces, sends three rounds of portmapper CALLIT probes for the mount program, polls for about one second per round, and appends unique source addresses observed in `callit_cb`.

## State and Persistence Behavior

The file does not persist data outside process memory. Its short-lived state is `sync_cb_data` on the caller's stack plus callback-produced heap allocations returned to the caller. The caller owns `struct nfsfh *`, `struct nfsdir *`, duplicated readlink buffers from `nfs_readlink2`, export lists, server lists, and ACL allocations, and must free them with the corresponding libnfs APIs.

Multithreaded synchronous calls are stateful at the `nfs_context_internal` level. `nfs_init_cb_data` may allocate a `struct nfs_thread_context`, copy the master `nfs_context`, set `master_ctx`, and store per-thread error strings so synchronous callers can block on semaphores while a shared service thread drives the single RPC context. This means context destruction must later release those thread contexts, and errors are deliberately thread-local for callers but RPC transport state remains shared.

## Dependencies and Integration Points

This file depends on `libnfs.c` for public async dispatchers and context utilities, on `nfs_v3.c` and `nfs_v4.c` through the `nfs_*_async` APIs, and on the lower RPC layer for `rpc_get_fd`, `rpc_which_events`, `rpc_service`, `rpc_disconnect`, `rpc_current_time`, and mount/portmapper helpers. Platform integration is through `poll`, socket/interface headers, `ioctl(SIOCGIFCONF/SIOCGIFFLAGS/SIOCGIFBRDADDR)` on Unix-like systems, and `WSAIoctl(SIO_GET_INTERFACE_LIST)` on Windows. `multithreading.c` supplies `nfs_mt_get_tid`, mutexes, and semaphores.

## Risks and Edge Cases

The blocking wait paths depend on callbacks always calling `cb_data_is_finished`; missed callbacks cause synchronous callers to wait until timeout or forever when no timeout applies. In the non-service-thread path, `poll` or `nfs_service` failure maps to `-EIO`, and `wait_for_nfs_reply` also cancels outstanding PDUs on service failure. In the service-thread path, the synchronous caller waits only on the semaphore, so correctness depends on the background thread continuously polling and posting completion.

Several wrappers return immediately with `-1` when async submission fails, but async readonly errors often call the callback with `-EROFS` and return `0`; callers must distinguish submission failure from operation failure. `readlink_cb` uses `strlen(data) > bufsize`, allowing a string exactly equal to `bufsize` to copy `bufsize + 1` bytes including the NUL terminator; boundary tests should cover this. `nfs4_getacl_cb` allocates each ACE name and must free partially built ACLs on allocation failure. `mount_getexports_cb` does not check every allocation result before dereference. Server discovery is IPv4 broadcast-oriented and excludes loopback and non-broadcast interfaces, so it will not discover IPv6-only or routed-only servers.

## Test Signals

Useful signals are integration tests that mount NFSv3 and NFSv4 exports, exercise every synchronous wrapper against success and server-side errno failures, and verify callbacks unblock both poll-driven and service-thread modes. Regression tests should cover v3-to-v4 mount fallback, `nfs_umount` disconnect handling, open retry on transient `-EIO`, readonly operations through the sync layer, short reads across EOF, read/write vector calls, `nfs_readlink` buffer boundaries, ACL allocation/free paths, export-list ownership, and local server discovery with duplicate CALLIT replies. Fault-injection tests should simulate poll failure, socket close, async submission failure, timeout, and allocation failure in ACL/export duplication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/libnfs-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/libnfs-zdr.c -->
# sources/user-network-fs/libnfs/lib/libnfs-zdr.c

## Purpose

`libnfs-zdr.c` provides libnfs's built-in in-memory ZDR/XDR subset and ONC RPC message marshalling helpers. It exists so the project can encode and decode rpcgen-compatible NFS, mount, portmap, and RPCSEC_GSS messages from memory buffers without depending on a platform XDR implementation. It also creates and destroys AUTH credentials for AUTH_NONE, AUTH_UNIX, and, when Kerberos support is compiled in, AUTH_GSS.

## Important APIs, Types, and Functions

The file manages `ZDR` streams with `libnfs_zdrmem_create`, `libnfs_zdr_destroy`, `libnfs_zdr_setpos`, `libnfs_zdr_getpos`, `libnfs_zdr_getsize`, and `libnfs_zdr_getptr`. Decode-time allocations are tracked in a private linked list of `struct zdr_mem`; `zdr_malloc` allocates stream-owned memory and `libnfs_zdr_destroy` releases it.

Primitive codecs include `libnfs_zdr_u_int`, `libnfs_zdr_int`, `libnfs_zdr_uint64_t`, `libnfs_zdr_int64_t`, `libnfs_zdr_bool`, `libnfs_zdr_enum`, `libnfs_zdr_void`, `libnfs_zdr_opaque`, `libnfs_zdr_bytes`, `libnfs_zdr_string`, `libnfs_zdr_pointer`, `libnfs_zdr_array`, and `libnfs_zdr_vector`. RPC envelope helpers are `libnfs_opaque_cred`, `libnfs_opaque_verf`, `libnfs_rpc_call_body`, `libnfs_accepted_reply`, `libnfs_rejected_reply`, `libnfs_rpc_reply_body`, `libnfs_rpc_msg`, `libnfs_zdr_callmsg`, and `libnfs_zdr_replymsg`.

Authentication helpers are `authnone_create`, `libnfs_authunix_create`, `libnfs_authunix_create_default`, `libnfs_auth_destroy`, and the Kerberos-gated `libnfs_authgss_init` and `libnfs_authgss_gen_creds`. The global `_null_auth` is the default empty verifier.

## Control Flow

Primitive encode/decode functions advance `zdrs->pos` through `zdrs->buf` in network byte order. Fixed-width integers check buffer bounds before reading or writing. Variable data first encodes or decodes a 32-bit length, validates a hard 1 GiB clamp, copies or points into the stream buffer, and pads to the next 4-byte XDR boundary. Strings decode in place when the receive buffer already has a trailing NUL byte; otherwise they allocate stream-owned space and append the terminator. Arrays decode by allocating `count * element_size` from `zdr_malloc` after checking multiplication overflow and then invoking the generated element codec for each element.

RPC message processing starts with `libnfs_rpc_msg`, which decodes or encodes the XID and direction, then dispatches to call-body or reply-body helpers. Call bodies marshal RPC version, program, version, procedure, credential, and verifier. Reply bodies dispatch between accepted and denied replies. Accepted replies decode the verifier, accepted status, optional program mismatch bounds, and, for success, invoke the PDU-specific result decode callback.

With `HAVE_LIBKRB5`, verifier and accepted-reply handling add RPCSEC_GSS behavior. Encoding an AUTH_GSS verifier may compute a MIC over bytes already in the ZDR stream. Decoding `krb5p` accepted replies unwraps the protected payload into a GSS output buffer and temporarily repoints the ZDR stream to decrypted data. Decoding `krb5i` skips integrity prefix fields but leaves signature verification as a TODO.

## State and Persistence Behavior

`ZDR` objects are caller-owned, but decode allocations made through `zdr_malloc` are owned by the stream and live until `libnfs_zdr_destroy`. Decode results that point directly into `zdrs->buf` are valid only while the underlying RPC receive buffer remains valid. AUTH objects own `oa_base` buffers for credentials and verifiers and are freed by `libnfs_auth_destroy`. AUTH_UNIX credential data includes a timestamp from `rpc_current_time`, the selected uid/gid, the host string, and up to 16 auxiliary groups.

The implementation keeps no durable filesystem state. Kerberos paths mutate `rpc_context` fields such as GSS sequence number, context handle, credential flavor, and auth data, so the ZDR code participates in transport-session state but does not independently persist it.

## Dependencies and Integration Points

The file integrates with generated raw protocol codecs from `libnfs-raw*.h`, PDU allocation and processing in `pdu.c`, RPC context error reporting in `init.c`, Kerberos helpers in `krb5-wrapper.c`, and the high-level connection setup in `libnfs.c`. It depends on endian conversion (`htonl`, `ntohl`), process credentials (`getuid`, `getgid` where available), and GSSAPI functions when Kerberos is enabled.

## Risks and Edge Cases

The code performs many unaligned casts into `char *` buffers; the `(void *)` casts suppress aliasing warnings but may still rely on architectures tolerating unaligned access. Bounds checks are stronger for integers and bytes than for `libnfs_zdr_opaque`, which assumes callers have already sized the buffer correctly. `libnfs_zdr_string` accepts `maxsize` but does not enforce it directly. `libnfs_zdr_array` rejects multiplication overflow but not a protocol count greater than the caller-provided `maxsize`. `libnfs_zdr_pointer` encodes presence based on the existing pointer value and decodes absent pointers by overwriting `*objp` with `NULL`.

Memory ownership is subtle: bytes and strings may either alias the receive buffer or point to stream-owned allocations, while higher-level callbacks sometimes steal or deep-copy decoded data. RPCSEC_GSS integrity verification is incomplete for `krb5i`, and protected reply decoding repoints the stream buffer, so downstream decode logic must not assume the original buffer pointer remains active. AUTH creation has limited allocation-error checking after allocating nested credential buffers.

## Test Signals

Unit tests should round-trip all primitive codecs across encode and decode, including 4-byte padding, zero-length bytes, strings with and without in-buffer NUL terminators, pointer presence, arrays, vectors, and overflow/size-limit failures. RPC envelope tests should decode accepted success, program mismatch, denied RPC mismatch, and auth error replies. Security-focused tests should cover AUTH_UNIX group-count rejection above 16, allocation failures in auth creation, malformed lengths near 1 GiB, truncated buffers at every field boundary, and Kerberos-enabled builds for MIC, unwrap, and error paths. Integration tests are successful NFSv3/NFSv4 RPC calls through `pdu.c` using this ZDR backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/libnfs-zdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/libnfs.c -->
# sources/user-network-fs/libnfs/lib/libnfs.c

## Purpose

`libnfs.c` is the main high-level asynchronous libnfs client layer. It owns context initialization and destruction, URL parsing, directory cache management, connection setup through portmapper or explicit ports, TLS and Kerberos connection negotiation, public async API dispatch to NFSv3 or NFSv4 backends, read chunking, readonly enforcement, path normalization, configuration setters, error storage, mount export async helpers, and RPC null tasks. The synchronous API in `libnfs-sync.c` wraps the functions defined here.

## Important APIs, Types, and Functions

Lifecycle and state APIs include `nfs_init_context`, `nfs_destroy_context`, `nfs_get_rpc_context`, `nfs_get_server_address`, `nfs_get_server`, `nfs_get_export`, `nfs_get_rootfh`, `nfs_get_fh`, `nfs_umask`, `nfs_set_error`, and `nfs_set_error_locked`. Directory ownership is handled by `nfs_free_nfsdir`, `nfs_dircache_add`, `nfs_dircache_find`, `nfs_dircache_drop`, `nfs_readdir`, `nfs_telldir`, `nfs_seekdir`, `nfs_rewinddir`, and `nfs_closedir`.

URL handling is centered on `nfs_parse_url`, exposed as `nfs_parse_url_full`, `nfs_parse_url_dir`, `nfs_parse_url_incomplete`, and released with `nfs_destroy_url`. URL query parameters are applied through `nfs_set_context_args` and `nfs_set_context_args_no_val`, covering options such as `uid`, `gid`, `timeo`, `retrans`, `debug`, `auto-traverse-mounts`, `dircache`, `autoreconnect`, `version`, `nfsport`, `mountport`, `rsize`, `wsize`, `readdir-buffer`, optional interface binding, TLS `xprtsec`, and Kerberos `sec`.

Connection APIs are `rpc_connect_port_async`, `rpc_connect_program_async`, and callback stages `rpc_connect_program_1_cb` through `rpc_connect_program_6_cb`. They connect first to portmapper when needed, resolve a program port for IPv4 or IPv6, reconnect to the target program, issue a NULL RPC, optionally negotiate RPC-with-TLS using `rpc_null_task_authtls`, and optionally initialize RPCSEC_GSS with `rpc_null_task_gss`.

Public async NFS operations include mount and unmount, stat/lstat/fstat variants, open/open2, chdir, pread/read/preadv/readv, pwrite/write, close, fsync, ftruncate/truncate, mkdir/rmdir/creat/mknod/unlink, opendir, lseek, NFSv4 lockf/fcntl, statvfs/statvfs64, readlink, chmod/lchmod/fchmod, chown/lchown/fchown, utimes/lutimes/utime, access/access2, symlink, rename, and link. Configuration getters/setters include read/write max, uid/gid/auxiliary groups, debug, auto traversal, readonly, dircache, autoreconnect, retrans, version, ports, readdir buffer sizes, poll timeout, timeout, stats/log callbacks, and PDU stats.

## Control Flow

Context initialization allocates `struct nfs_context_internal`, `struct nfs_context`, and an RPC context, sets defaults, initializes optional Kerberos username, sets cwd to `/`, enables auto traversal and directory cache, configures hard-mount-like resiliency defaults, selects NFSv3 as the default version, sets transfer sizes and readdir buffers, seeds NFSv4 verifier and client name, initializes multithreading locks, and ignores SIGPIPE on supported non-Windows platforms. Destruction walks nested mounts and directory cache lists, destroys the RPC context, frees error strings and NFS state, destroys multithreading locks, and releases per-thread contexts.

URL parsing validates the `nfs://` prefix, percent-decodes the server/path string, parses optional server port, splits server/path/file depending on full versus directory mode, applies query options, handles `username@server`, records the selected port, and performs TLS global initialization if `xprtsec=tls` or `xprtsec=mtls` was requested. Path normalization mutates absolute paths in place by collapsing `//`, `/./`, and parent-directory segments while rejecting paths that escape above root.

Most async public functions are dispatchers. They inspect `nfs->nfsi->version` and call the matching `nfs3_*` or `nfs4_*` backend, returning an error for unsupported version/operation combinations. Mutating operations check `nfsi->readonly` and usually complete through the callback with `-EROFS` without starting a backend RPC. File-handle writes and truncates also reject `nfsfh->is_readonly`.

Read chunking uses `struct rw_data`. `_nfs_pread_async` sends a single backend read when the request is smaller than `nfs_get_readmax`; larger requests allocate a continuation object, submit the first chunk, and `r_cb` advances buffer, offset, and remaining count until all bytes are read or a short read indicates EOF. `nfs_read_async` uses `nfsfh->offset` and requests offset updates, while `nfs_pread_async` leaves file position unchanged. Vectored reads dispatch directly to v3/v4 internal preadv helpers.

## State and Persistence Behavior

The durable in-process state is `struct nfs_context` plus `struct nfs_context_internal` and the shared `struct rpc_context`. `nfsi` stores cwd, root file handle, server/export strings, nested mounts, directory cache, NFS version/default-version state, transfer sizes, readonly and cache flags, resiliency defaults, NFSv4 verifier/client name, ports, and optional thread contexts. Directory handles are cached on close when directory caching is enabled and evicted after `MAX_DIR_CACHE` entries. Error strings are heap allocated per context, with special handling for a static out-of-memory string.

No filesystem persistence is performed. Network session persistence is delegated to the RPC context, including connection state, queues, timeouts, auth state, TLS state, and reconnect behavior. Several setters store user choices in `nfsi` until mount completion, when lower layers can apply them to the RPC transport.

## Dependencies and Integration Points

`libnfs.c` is the integration hub for `libnfs.h`, `libnfs-private.h`, raw generated mount/portmap/NFS protocol headers, `nfs_v3.c`, `nfs_v4.c`, RPC socket/PDU/init code, TLS helpers when `HAVE_TLS` is enabled, Kerberos wrapper code when `HAVE_LIBKRB5` is enabled, and multithreading wrappers when `HAVE_MULTITHREADING` is enabled. Its public async functions are the immediate dependency of the synchronous wrappers. The URL parser also integrates with platform-specific interface binding when `HAVE_SO_BINDTODEVICE` is available.

## Risks and Edge Cases

The file has a broad API surface and many feature gates, so regressions often appear as mismatched v3/v4 behavior, missing callback completion, or inconsistent errno conventions. URL parsing is pointer-mutating and has delicate cases around percent-decoding, `server:port`, incomplete URLs, query options, `username@server`, and file-versus-directory splitting. Transfer-size setters clamp and round to 4096-byte units; very small user values are raised to minimums, which can surprise callers. `nfs_set_error` allocates a fixed 1024-byte message and must be used carefully with multithreaded contexts to avoid losing thread-local errors.

Connection setup spans portmapper, target reconnect, NULL RPC validation, TLS negotiation, and optional Kerberos initialization; each stage owns callback data and must free it exactly once. `rpc_null_task` and related functions must free PDUs on queue failure or they risk leaks. Read chunking must handle `readmax == 0`, short reads, callback errors, and offset updates correctly. Directory caching returns an owned cached directory from `nfs_dircache_find`; callers must not double-free cached handles. Several async functions synchronously invoke callbacks for readonly errors, so wrapper code must be reentrant-safe.

## Test Signals

Strong signals are end-to-end async and sync tests for both NFSv3 and NFSv4, including mount/unmount, path resolution, file creation/open/read/write/close, metadata, directory listing and cache reuse, chmod/chown/time changes, link/rename/symlink, statvfs, and NFSv4 lock/fcntl paths. URL parser tests should cover percent escapes, invalid ports, incomplete URLs, query options, TLS/Kerberos options, username extraction, and directory/file modes. Fault tests should cover allocation failures in context and connection callback data, portmapper program-not-found, IPv6 getaddr parsing, TLS handshake rejection, Kerberos init failure, readonly callbacks, transfer-size clamping, read chunking over multiple chunks, and context destruction with cached directories and thread contexts. Build matrix signals should include plain, TLS, Kerberos, Windows, pthread, and no-multithreading configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/libnfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/multithreading.c -->
# sources/user-network-fs/libnfs/lib/multithreading.c

## Purpose

`multithreading.c` provides the optional platform abstraction used when libnfs is built with `HAVE_MULTITHREADING`. It starts and stops the background NFS service thread, identifies the current thread, and wraps mutex and semaphore primitives for Windows, pthread platforms, Apple dispatch semaphores, and POSIX semaphores. The synchronous API uses these primitives to let multiple caller threads issue blocking operations while one service thread drives the shared RPC socket.

## Important APIs, Types, and Functions

The exported helpers are `nfs_mt_get_tid`, `nfs_mt_service_thread_start`, `nfs_mt_service_thread_stop`, `nfs_mt_mutex_init`, `nfs_mt_mutex_destroy`, `nfs_mt_mutex_lock`, `nfs_mt_mutex_unlock`, `nfs_mt_sem_init`, `nfs_mt_sem_destroy`, `nfs_mt_sem_post`, and `nfs_mt_sem_wait`. The internal service routine is `nfs_mt_service_thread`, with a Windows `service_thread_init` adapter for `CreateThread`.

On Windows, thread IDs come from `GetCurrentThreadId`, mutexes and semaphores are implemented with `CreateSemaphoreA`, waits use `WaitForSingleObject`, and the service thread is a Win32 thread handle stored in `nfs->nfsi->service_thread`. On pthread platforms, thread IDs use the best available OS mechanism (`pthread_threadid_np`, `pthread_getthreadid_np`, `getthrid`, `_lwp_self`, or `syscall(SYS_gettid)`). Mutexes are pthread mutexes, with `PTHREAD_MUTEX_ERRORCHECK` enabled under `DEBUG_PTHREAD_LOCKING_VIOLATIONS`. Semaphores use dispatch semaphores on Apple when available or `sem_init`/`sem_wait` elsewhere.

## Control Flow

Starting the service thread creates the platform thread with the `nfs_context` as its argument, then spins until `rpc->multithreading_enabled` becomes nonzero. The service thread sets that flag, then loops while it remains true. Each loop builds a `pollfd` from `nfs_get_fd` and `nfs_which_events`, polls with the RPC poll timeout on pthread platforms or a zero timeout on Windows, maps poll failures to `revents = -1`, and calls `nfs_service` to process socket events. Stop clears `rpc->multithreading_enabled` and joins or waits for the thread to exit.

Mutex and semaphore functions are thin wrappers, so higher layers can use `libnfs_mutex_t` and `libnfs_sem_t` without preprocessor-heavy call sites. In the synchronous facade, each blocking operation initializes a semaphore with value zero and waits for its callback to post; shared structures such as RPC queues, directory cache, and thread-context lists use the mutex wrappers.

## State and Persistence Behavior

The file stores no independent persistent state. It mutates `nfs->rpc->multithreading_enabled` as the service thread run flag and uses `nfs->nfsi->service_thread` to hold the platform thread handle or pthread ID. Mutex and semaphore state lives in caller-owned objects embedded in RPC/NFS contexts or callback data. All state is process-local and must be destroyed by context teardown or per-call cleanup.

## Dependencies and Integration Points

This file depends on `libnfs.h`, `libnfs-raw.h`, `libnfs-private.h`, `poll`, and platform threading APIs. It is used by `libnfs-sync.c` for semaphore-based synchronous waits, by `libnfs.c` for directory cache and error locking, and by lower RPC/PDU/socket/init code for queue and error synchronization. Its API surface is compiled out entirely when `HAVE_MULTITHREADING` is not defined.

## Risks and Edge Cases

The run flag is a plain integer shared between threads; correctness relies on platform memory behavior around thread creation, polling, and join rather than explicit atomics. `nfs_mt_service_thread_start` busy-waits until the service thread sets the flag, so thread startup failure after creation could spin. The Windows service loop polls with timeout zero, which can consume CPU if no socket events are available. Windows `nfs_mt_sem_init` ignores the requested initial value and always creates the semaphore with count zero, which matches current sync-call use but is not a general semaphore implementation.

Pthread builds require one of the supported thread ID APIs; otherwise compilation fails with `#error`. Error-checking mutex initialization may leak the mutex attribute object because it is not destroyed after `pthread_mutex_init`. Semaphore waits do not retry on `EINTR`, so POSIX `sem_wait` interruption can propagate as failure if callers ever inspect the return code. Service-thread shutdown can block indefinitely if `nfs_service` or `poll` does not return.

## Test Signals

Tests should build all supported threading variants where possible: Windows, pthread/Linux, BSD/macOS thread ID paths, Apple dispatch semaphore, POSIX semaphore, and no-multithreading. Runtime tests should start the service thread, issue simultaneous synchronous operations from multiple threads, verify per-thread callback wakeups, exercise mutex-protected directory cache and error paths, and stop the service thread cleanly while no operations are pending. Fault tests should simulate poll errors, service errors, semaphore wait/post failures where injectable, interrupted waits, and rapid start/stop cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libnfs/lib/multithreading.c -->
