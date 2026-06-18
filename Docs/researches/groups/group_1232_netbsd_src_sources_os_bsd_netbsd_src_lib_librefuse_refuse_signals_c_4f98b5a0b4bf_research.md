# Group Research: group_1232_netbsd_src_sources_os_bsd_netbsd_src_lib_librefuse_refuse_signals_c_4f98b5a0b4bf

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_signals.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_signals.c

Read completely: 331 lines.

Implements ReFUSE signal handler registration/removal for FUSE-compatible filesystems. It tracks all `struct fuse *` instances that requested signal handling in a process-global linked list, installs shared handlers for `SIGHUP`, `SIGINT`, and `SIGTERM`, and ignores `SIGPIPE` only when the previous action was default.

The exit handler calls `fuse_exit()` for every tracked filesystem, then chains to the previously installed handler if it was neither default nor ignored. In `MULTITHREADED_REFUSE` builds, it uses a global mutex and temporarily blocks the handled signals while mutating handler/list state.

Removal deletes the matching fuse instance and restores the saved signal actions only after the last tracked instance is gone. Notable risks are deliberate signal-safety compromises: the handler may take a pthread mutex and call non-async-signal-safe code, relying on the signal-blocking discipline around list changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_signals.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/Makefile

Read completely: 28 lines.

Builds NetBSD `libresolv` from resolver support sources shared with libc. It adds libc include/resolver/name-server include paths, defines `_LIBRESOLV`, conditionally enables `INET6`, and sets `.PATH` to libc `net`, `resolv`, and `nameser` directories.

The compiled sources are the dynamic update, TSIG signing/verification, DNS date, zone-cut, DST key, HMAC, and support files in this group plus `ns_samedomain.c`. Commented-out lines document broader libc resolver sources that are intentionally not built into this standalone library.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/dst_api.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/dst_api.c

Read completely: 1058 lines.

Provides the legacy BIND DST API used by TSIG/DNSSEC-era resolver code. `dst_init()` initializes a global algorithm function table and reads `DSTKEYPATH`; this NetBSD build initializes HMAC-MD5 support while leaving hooks for RSA, DSA, SHA1 HMAC, and other historical algorithms.

The file allocates and manages `DST_KEY` objects, compares keys, signs and verifies incrementally through per-algorithm function pointers, converts between DNS KEY RDATA and internal key objects, and reads/writes public/private key files using `K<name>+<alg>+<id>.<suffix>` naming.

For TSIG use, `dst_buffer_to_key()` is the important path: it wraps raw shared-secret bytes in a `DST_KEY`, computes a DNS key id, and hands signing/verification to `hmac_link.c`. The file is global-state heavy, uses legacy file formats, and assumes callers respect fixed buffer sizes such as `RAW_KEY_SIZE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/dst_api.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/dst_internal.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/dst_internal.h

Read completely: 166 lines.

Private DST header defining `DST_KEY`, the `dst_func` algorithm dispatch table, key-file constants, secure-free macros, and internal helper prototypes. It establishes fields for key name, size, protocol, algorithm, DNS flags, key id, opaque algorithm-specific key material, and function table.

The header declares the global algorithm table `dst_t_func`, `dst_path`, algorithm initializers, DNS/key-file conversion helpers, network-byte-order helpers, and optional debug dump support. It is the contract between `dst_api.c`, `hmac_link.c`, and `support.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/dst_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/hmac_link.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/hmac_link.c

Read completely: 472 lines.

Implements the DST algorithm binding for HMAC-MD5. It stores precomputed 64-byte inner and outer pads in an `HMAC_Key`, supports incremental signing and verification over MD5 contexts, converts raw/shared-secret bytes into pad form, and registers these operations in `dst_t_func[KEY_HMAC_MD5]`.

Keys longer than the HMAC block length are first MD5-hashed. File-format conversion emits and parses a `Key: <base64>` line under the generic DST private-key header, while DNS-key conversion extracts the original shared secret from the XORed pad.

Verification requires a 16-byte signature and compares with `memcmp()`. Contexts are heap-allocated for incremental use and freed on finalization; some error paths can leave caller-owned context handling ambiguous, matching the legacy API style.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/hmac_link.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/ns_date.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/ns_date.c

Read completely: 128 lines.

Implements `ns_datetosecs()`, converting DNS date strings in `yyyymmddhhmmss` format to seconds since 1970-01-01 UTC. It validates fixed length, numeric fields, year/month/day/hour/minute/second ranges, and then computes the timestamp manually instead of relying on `timegm()`.

Leap years are handled explicitly. The accepted year range begins at 1990 and extends to 9999, but the return type is `u_int32_t`, so distant future dates wrap modulo 32 bits. The helper `datepart()` leaves an accumulated error flag set if any field fails validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/ns_date.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/ns_sign.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/ns_sign.c

Read completely: 393 lines.

Constructs TSIG records and appends them to DNS messages. `ns_sign()` delegates to `ns_sign2()`, which writes the TSIG owner name, type/class/TTL/RDLEN, algorithm, time signed, fudge, signature, original message id, error, and optional BADTIME other-data fields.

For normal signing, it only accepts `KEY_HMAC_MD5`. The digest covers any query signature for responses, the original message, canonical key name, class/TTL, canonical algorithm name, time/fudge, error, and other-data. Generated signatures are returned to the caller and copied into the TSIG RDATA.

The TCP helpers maintain `ns_tcp_tsig_state`, chaining the previous signature into the next MAC and emitting TSIG records on the first message, every 100 messages, or the final message. Buffer boundary checks return `NS_TSIG_ERROR_NO_SPACE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/ns_sign.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/ns_verify.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/ns_verify.c

Read completely: 485 lines.

Implements TSIG discovery and verification. `ns_find_tsig()` walks the DNS message sections and returns the final additional record only if it is a TSIG. `ns_verify()` parses that record, validates HMAC-MD5 algorithm/key identity, recomputes the MAC over the same canonical fields used by `ns_sign()`, optionally returns the signature, and strips the TSIG from the message unless `nostrip` is set.

Time validation compares the signed time to the local clock within the advertised fudge window. The function distinguishes format errors, missing TSIG, BADKEY, BADSIG, BADTIME, and server-returned TSIG errors.

TCP verification keeps rolling state in `ns_tcp_tsig_state`, accepts unsigned intermediate messages when TSIG is not required, and verifies signed checkpoints/final messages by including the previous signature and current message prefix.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/ns_verify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_findzonecut.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_findzonecut.c

Read completely: 723 lines.

Finds the enclosing DNS zone cut and authoritative server addresses for a name/class. `res_findzonecut()` is the IPv4 wrapper; `res_findzonecut2()` supports `union res_sockaddr_union`, IPv4/IPv6 filtering, and exhaustive glue lookup.

The algorithm canonicalizes the input name, queries for SOA records while stripping labels upward, saves the zone name and SOA MNAME, collects NS records from answer/authority sections, saves additional-section A/AAAA glue, and queries missing A/AAAA glue when necessary. It prefers the SOA MNAME server address, then other NS addresses.

The implementation assumes a functional recursive resolver and does not handle referrals itself. It treats unexpected CNAME/DNAME results as failure or as a signal to continue searching, and manages temporary RRsets with tail queues.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_findzonecut.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_mkupdate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_mkupdate.c

Read completely: 1169 lines.

Builds DNS UPDATE packets from linked `ns_updrec` records. `res_nmkupdate()` initializes a DNS header with update opcode, enforces section ordering beginning with the zone section, applies dynamic-update class/type overloading for prerequisites and updates, compresses owner names, and serializes RR-specific RDATA.

The large RDATA switch supports A, AAAA, CNAME/NS/PTR/DNAME-style names, SOA/MINFO/RP, MX/AFSDB/RT, SRV, PX, WKS, HINFO/TXT/X25/ISDN, NSAP, LOC, SIG, KEY, NXT, CERT, and NAPTR. Helper parsers read whitespace-delimited words, quoted strings with decimal escapes, decimal numbers, and hex numbers from in-memory text buffers.

It also provides `res_mkupdrec()`/`res_freeupdrec()` allocation helpers and cached service/protocol name-number conversion lists. Risks are typical of legacy text-to-wire parsers: many fixed buffers, partial overflow signaling via return codes, and static service/protocol caches without synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_mkupdate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_mkupdate.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_mkupdate.h

Read completely: 27 lines.

Empty public/private compatibility header for resolver update construction. It contains only the include guard and `__BEGIN_DECLS`/`__END_DECLS`, so all effective APIs come from other resolver headers such as `<res_update.h>` and `<resolv.h>`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_mkupdate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_private.h

Read completely: 24 lines.

Defines the private resolver extension structure `__res_state_ext`, containing extended nameserver addresses, resolver sort-list entries for IPv4/IPv6 address/mask pairs, and two suffix buffers. It also declares `res_ourserver_p()`.

This header is a small bridge for code that needs resolver internals beyond the public `res_state` surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_sendsigned.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_sendsigned.c

Read completely: 173 lines.

Implements `res_nsendsigned()`, which signs an outbound DNS message with a TSIG key, sends it through a copied resolver state, and verifies the signed reply. It only accepts `NS_TSIG_ALG_HMAC_MD5`, wraps key bytes with `dst_buffer_to_key()`, appends TSIG using `ns_sign()`, and suppresses resolver debug reply printing on the copied state.

The function chooses TCP if the signed message exceeds `PACKETSZ` or `RES_USEVC` is set; otherwise it sets `RES_IGNTC` and retries over TCP if a truncated UDP response arrives and truncation is not ignored by the original state.

On verification failure it prints resolver-debug diagnostics when requested, maps bad input to `EINVAL` and TSIG failure to `ENOTTY`, and frees the copied state, signed message buffer, and DST key.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_sendsigned.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_update.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_update.c

Read completely: 219 lines.

Implements `res_nupdate()`, the high-level dynamic DNS update sender. It groups input `ns_updrec` records by discovered zone origin and class using `res_findzonecut2()`, prepends a generated SOA zone-section record for each group, marshals the update with `res_nmkupdate()`, and sends to the authoritative nameservers for that zone.

For each zone, it temporarily replaces the resolver state's configured server list with the zone's nameserver addresses, sends either unsigned with `res_nsend()` or signed with `res_nsendsigned()`, counts successful zones when the response rcode is `NOERROR`, and restores the original server list.

Cleanup removes generated zone-section records and frees group objects. Partial success is possible: earlier zones can be updated before a later zone fails, and the function returns the number of zones updated rather than a strict negative error code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/res_update.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/support.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libresolv/support.c

Read completely: 347 lines.

Contains support routines for the DST key subsystem. It verifies string prefixes while advancing parse pointers, computes significant bit counts, calculates DNS key ids/checksums, reads and writes unaligned 16/32-bit network-order integers, and builds/sizes DST key filenames.

`dst_s_build_filename()` creates `K<name>+<alg>+<id>.<suffix>` names while rejecting slash, backslash, and colon. `dst_s_fopen()` prepends the global `dst_path` and optionally applies permissions after opening.

The debug dump helper prints base64 or short length information when enabled. The file is small but central to DST file parsing and DNS KEY id compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libresolv/support.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librmt/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librmt/Makefile

Read completely: 14 lines.

Builds `librmt` from `rmtlib.c` with fortification enabled by default, no PIC, no profiling, and `_REENTRANT` in `CPPFLAGS`. It installs the `rmtops.3` manual and includes the standard NetBSD library make rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librmt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librmt/pathnames.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librmt/pathnames.h

Read completely: 30 lines.

Defines the hardcoded helper paths used by `librmt`: `_PATH_RSH` is `/usr/bin/rsh` and `_PATH_RMT` is `/etc/rmt`. `rmtlib.c` can override the remote-shell command through `RCMD_CMD`, but the remote tape command path comes from this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librmt/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librmt/rmtlib.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librmt/rmtlib.c

Read completely: 896 lines.

Implements a remote tape compatibility library that can replace `open`, `read`, `write`, `lseek`, `ioctl`, and related file operations. Remote devices are detected by paths containing `:/dev/`, opened by forking `rsh` to run `/etc/rmt`, and represented to callers as small internal unit numbers plus `REM_BIAS` 128.

The private protocol helpers send textual remote-tape commands (`O`, `C`, `R`, `W`, `L`, `I`, `S`), parse `A` success and `E`/`F` error replies, ignore `SIGPIPE` around pipe writes, and abort connections on fatal or protocol errors. Up to four remote units are tracked through parent-to-child and child-to-parent pipe arrays.

Public wrappers dispatch local descriptors to normal syscalls and remote descriptors to protocol operations. Some operations such as `dup`, `fstat`, `stat`, `lstat`, and `fcntl` are unsupported remotely and return `EOPNOTSUPP`. The MTIOCGET path reads raw `struct mtget` bytes and contains historical byte-swap logic with acknowledged portability assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librmt/rmtlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librpcsvc/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librpcsvc/Makefile

Read completely: 41 lines.

Builds `librpcsvc` from a set of RPC `.x` interface definitions, generating headers and XDR source files through `bsd.rpc.mk`. Core RPC services include bootparam, KLM, mount, NFS, NLM, rex, rnusers/rusers, rquota, rstat, rwall, sm_inter, and spray.

When `MKYP` is enabled, YP and yppasswd RPC definitions and export symbols are added. The Makefile merges export-symbol fragments with `sort -m`, installs generated headers and `.x` files under `/usr/include/rpcsvc`, and builds the `rpcsvc` library with no manual page.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librpcsvc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librt/Makefile

Read completely: 63 lines.

Builds NetBSD `librt` from `sem.c`, `shm.c`, and `pset.c`, plus generated syscall stubs included from `sys/Makefile.inc`. It disables sanitizers, sets warning level, includes libc internal include handling, and has a powerpc64 workaround adding libc `_errno.c`.

The installed manuals and links cover POSIX AIO, message queues, processor sets, scheduler APIs, shared memory, and semaphores, even though many syscall wrappers are generated assembly rather than C in this directory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/pset.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librt/pset.c

Read completely: 48 lines.

Provides the public `pset_bind()` wrapper for processor sets. It calls the lower-level `_pset_bind()` syscall stub with `P_ALL_LWPS` set to `0`, meaning the operation applies to all LWPs in the selected process/thread scope.

All other processor-set entry points listed in the Makefile are generated syscall stubs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/pset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/sem.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librt/sem.c

Read completely: 435 lines.

Implements POSIX semaphore functions on top of NetBSD `_ksem_*` kernel syscalls. For librt builds, symbols are renamed to `_librt_sem_*` and weak aliases expose the standard `sem_*` names while preserving compatibility with libpthread's copy.

Unnamed non-pshared semaphores allocate a process-local `_sem_st` wrapper containing a kernel semaphore id and magic value. Pshared unnamed semaphores store a specially marked kernel semaphore id directly in `sem_t`, because a heap wrapper would not be shared across processes.

Named semaphores use `_ksem_open()` and a process-local linked list to deduplicate identical kernel ids so repeated opens return the same `sem_t *`. `sem_close()` removes the entry and closes the kernel semaphore; `sem_unlink()` delegates directly. Wait, timedwait, trywait, post, and getvalue are thin wrappers around `_ksem_*`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/sem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/shm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librt/shm.c

Read completely: 141 lines.

Implements POSIX shared-memory object naming over a tmpfs directory. `_shm_check_fs()` verifies `/var/shm` exists, is mounted as tmpfs, and has sticky world-writable directory permissions before caching success in `shm_ok`.

`_shm_get_path()` enforces POSIX-style names beginning with `/` and rejects additional slashes, then maps the name to `/var/shm/.shmobj_<name>`. `shm_open()` opens that path with `O_CLOEXEC | O_NOFOLLOW`, and `shm_unlink()` unlinks it.

If the backing directory is absent or invalid, operations fail with `ENOTSUP`; bad names fail with `EINVAL`; overly long mapped paths fail with `ENAMETOOLONG`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/shm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/librt/sys/Makefile.inc

Read completely: 25 lines.

Generates architecture-specific syscall assembly stubs for AIO, message queue, processor-set, and `_pset_bind` functions. It adds `${.CURDIR}/sys` and `${ARCHDIR}/sys` to `.PATH`, appends generated assembly names to `SRCS`, and removes them during clean.

Generated stubs include `SYS.h` and invoke `RSYSCALL(${.PREFIX})`. The file also adds `cerror.S`, remaps `__cerror` to `__rt_cerror`, includes the libc object directory, and defines `_REENTRANT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librt/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librump/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librump/Makefile

Read completely: 17 lines.

Builds the core `librump` kernel component library from the sys/rump rumpkern makefile. It disables full RELRO, points `RUMPTOP` at `../../sys/rump`, depends on `librumpuser`, uses warning level 3 because kernel code is not ready for stricter sign-compare warnings, and suppresses cast-function-type warnings for selected kernel-derived sources.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librump/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpclient/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpclient/Makefile

Read completely: 40 lines.

Builds shared `librumpclient` from `rumpclient.c` and generated `rump_syscalls.c`, installs `rumpclient.h` under `/usr/include/rump`, and includes the `rumpclient.3` manual. It defines `RUMP_CLIENT`, includes the object directory, current directory, and `librumpuser`, and supports externally supplied dependency libraries via `RUMPCLIENT_EXTERNAL_DPLIBS`.

For non-clean/non-obj builds, it creates a `srcsys` symlink to the kernel `sys/sys` headers. It disables full RELRO and suppresses strict-aliasing for generated syscall code and cast-function-type warnings for `rumpclient.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpclient/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.c

Read completely: 1263 lines.

Implements the client side of the rump syscall proxy protocol. It connects to the server described by `RUMP__PARSEDSERVER` or `RUMP_SERVER`, performs handshakes, sends syscall request frames, waits for responses, and services server callbacks for copyin, copyout, anonymous mmap, and signal delivery.

The transport preserves host syscall access through `dlsym(RTLD_NEXT)` or static fallbacks, so rumphijack can intercept ordinary calls while rumpclient still reaches real host `socket`, `connect`, `poll`/`kevent`, `read`, `sendmsg`, and related functions. On BSD it uses kqueue, on Linux signalfd, and otherwise poll/signal masking to avoid signal handling while holding communication locks.

Connection management includes optional reconnect behavior, generation checks for waiters, a special `holyfd` monitored descriptor, descriptor relocation to avoid stdio collisions, and close-notification handling so intercepted close/dup2/fclosem cannot accidentally destroy the rump connection.

Fork/exec support uses prefork authentication, reconnects the child with `HANDSHAKE_FORK`, preserves state for vfork parent handling, and passes existing connection descriptors through `RUMPCLIENT__EXECFD` during exec. `rumpclient_daemon()` builds on this machinery with a manual daemonization sequence.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.h

Read completely: 123 lines.

Public header for rumpclient. It declares initialization, syscall proxying, prefork/fork/exec/daemon helpers, connection retry configuration, close-notification variants, and the opaque `struct rumpclient_fork`.

It defines retry constants for infinite, once, and die-on-disconnect behavior. The inline `rumpclient__dofork()` wraps `fork` or `vfork`: it obtains prefork state, runs the host fork function, initializes the child connection, cancels on failure, and restores parent state for vfork-style execution.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpdev/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpdev/Makefile

Read completely: 12 lines.

Builds the rump device component library from `${RUMPTOP}/librump/rumpdev/Makefile.rumpdev`. It disables full RELRO, depends on `librump`, uses warning level 3 for kernel-derived code, and otherwise delegates source selection to the sys/rump makefile fragment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumphijack/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librumphijack/Makefile

Read completely: 25 lines.

Builds `librumphijack`, the preload/interposition library that redirects host calls through rumpclient. It disables full RELRO, static library generation, and profiling for dynamic-function use, depends on `libpthread` and `librumpclient`, and installs the `rumphijack.3` manual.

Sources are `hijack.c` and `hijackdlsym.c`. The build defines `_DIAGNOSTIC` and `_REENTRANT`, uses warning level 5, forces `hijackdlsym.c` to `-O0` so stack-frame assumptions hold, and undefines `_FORTIFY_SOURCE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumphijack/Makefile -->