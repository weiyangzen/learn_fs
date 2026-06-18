# subset-b-009729 Research

Grouped research for nfs-utils support files. Each section is source-tree aligned and can be split directly into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/tcpwrapper.c -->
# sources/user-network-fs/nfs-utils/support/misc/tcpwrapper.c

Purpose: optional libwrap access-control support for RPC service requests, compiled only when `HAVE_LIBWRAP` is set. It translates caller socket addresses into printable addresses, consults tcp_wrappers through `hosts_access()`, and caches allow/deny decisions per caller/program.

Important APIs and types: `check_default(char *name, struct sockaddr *sap, unsigned long program)` is the exported decision point. Internal `haccess_t` entries are stored in a 1021-bucket `TAILQ` hash table keyed by printable address plus RPC program number. `present_address()`, `good_client()`, `check_files()`, `haccess_add()`, and `haccess_lookup()` support address presentation, libwrap lookup, hosts file change detection, and caching.

Control flow: `check_default()` formats the caller address, checks `/etc/hosts.allow` and `/etc/hosts.deny` mtimes, and returns a cached result if neither file changed. Otherwise local callers are allowed without consulting tcp_wrappers, nonlocal callers go through `request_init()`, `sock_methods()`, and `hosts_access()`, then the cache is updated and a debug log is emitted.

State and persistence: runtime state is the process-local static hash table plus static mtimes for the hosts files. The module reads persistent policy from `/etc/hosts.allow` and `/etc/hosts.deny` but never writes those files.

Dependencies and integration: depends on libwrap headers/functions, RPC sockaddr helpers (`nfs_sockaddr_length()`, `nfs_compare_sockaddr()`, `from_local()`), and `xlog`. It integrates with RPC service setup as a caller authorization filter.

Risks: the cache key includes program but lookup only compares socket address, so different program decisions in the same hash bucket can collide logically. `check_files()` returns unchanged when either hosts file is missing, so policy file creation/removal edge cases deserve scrutiny. No locking protects the global cache, so multithreaded callers could race. `strncpy()` fallback may omit a NUL if buffer sizing changes, though current call uses a sufficiently large fixed buffer.

Test signals: exercise IPv4/IPv6 address formatting, hosts file mtime invalidation, local bypass, remote allow/deny, repeated cached calls, missing hosts files, and concurrent access if used in threaded daemons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/tcpwrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/ucred.c -->
# sources/user-network-fs/nfs-utils/support/misc/ucred.c

Purpose: credential utility routines for export-aware UID/GID handling and temporarily swapping the process effective credentials.

Important APIs and functions: `nfs_ucred_squash_groups()` rewrites root group IDs to the export anonymous GID under root-squash. `nfs_ucred_reload_groups()` reloads supplementary groups for a credential UID using `getpwuid_r()` and `getgrouplist()`, then reapplies squash policy. `nfs_ucred_swap_effective()` captures the current effective credentials and sets effective UID/GID/groups to a supplied `nfs_ucred`.

Control flow: effective credential capture uses `getgroups()`, heap allocation, `geteuid()`, and `getegid()`. Swap first raises effective UID to 0, installs supplementary groups, changes effective GID, then changes effective UID; error paths attempt to restore GID and groups from the saved credential.

State and persistence: no durable state. It mutates process effective credentials and allocates/free group arrays owned by `struct nfs_ucred`.

Dependencies and integration: depends on `exportfs.h` export flags, `nfs_ucred.h` ownership helpers, libc password/group APIs, `setresuid()`, `setresgid()`, `setgroups()`, and `xlog`. It is used by NFS server utilities that need filesystem operations under client/export credentials.

Risks: changing process credentials is global to the thread/process security context and is risky in multithreaded use. `alloca()` uses the system password-buffer size and can still allocate 16 KiB on stack by default. Partial failures during credential swap may leave credentials only partly restored. `nfs_ucred_reload_groups()` returns early for anonymous users under squash policy, which preserves the current group set by design but should be verified against caller expectations.

Test signals: run as root in a controlled test for successful swap/restore, root squash group replacement, all-squash anonymous handling, unknown UID, large group lists, and failure injection around `setgroups()`/`setresgid()`/`setresuid()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/ucred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/workqueue.c -->
# sources/user-network-fs/nfs-utils/support/misc/workqueue.c

Purpose: small synchronous workqueue abstraction used to run operations, especially `chroot()`, in a helper thread with a private filesystem namespace when platform support exists.

Important APIs and types: `struct xthread_workqueue` owns a FIFO queue, mutex, and condition variable. `xthread_workqueue_alloc()`, `xthread_workqueue_shutdown()`, `xthread_work_run_sync()`, and `xthread_workqueue_chroot()` are the public-facing operations. The fallback build uses a dummy singleton and runs work inline.

Control flow: when `HAVE_SCHED_H`, `HAVE_LIBPTHREAD`, and `HAVE_UNSHARE` are available, allocation creates a worker thread and waits until it signals startup. `xthread_work_run_sync()` pushes a stack-allocated work item, signals the worker, and waits on the item condition until the function finishes. `xthread_workqueue_chroot()` runs `unshare(CLONE_FS)` and `chroot(path)` on the worker.

State and persistence: state is process-local queue/thread state. No durable persistence. Shutdown sets a flag and wakes the worker; cleanup frees the queue via pthread cleanup handler.

Dependencies and integration: depends on pthreads, `unshare()`, `chroot()`, `xlog`, and `workqueue.h`. It lets code isolate filesystem-root changes away from the main thread when supported.

Risks: work functions run while the queue mutex remains locked, so nested queue calls or long-running work block all queue activity. The worker thread is not detached or joined visibly here, so lifetime ownership must be clear at call sites. The fallback silently runs work inline except for `chroot`, which only logs an error, so behavior differs substantially by build configuration.

Test signals: verify synchronous completion ordering, shutdown wakeup, chroot success/failure logging, fallback behavior, and deadlock risk if a work function reenters the queue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/workqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/xstat.c -->
# sources/user-network-fs/nfs-utils/support/misc/xstat.c

Purpose: stat wrappers that prefer non-synchronizing `statx()` metadata queries when available and fall back to `fstatat()`, `lstat()`, or `stat()`.

Important APIs and functions: `xlstat()` is lstat-like with `AT_SYMLINK_NOFOLLOW`; `xstat()` is stat-like. `statx_copy()` maps `struct statx` fields into `struct stat`, and `statx_do_stat()` disables future `statx()` attempts after `ENOSYS`.

Control flow: with `HAVE_FSTATAT`, calls first try `statx(..., STATX_BASIC_STATS, AT_STATX_DONT_SYNC | AT_NO_AUTOMOUNT...)`. If unsupported, errno is reset and `fstatat()` is used. Without `HAVE_FSTATAT`, the wrappers directly call libc `lstat()` and `stat()`.

State and persistence: only a static `statx_supported` flag caches kernel/libc support. No persistent state.

Dependencies and integration: depends on Linux statx headers when configured, `sysmacros.h`, `nfslib.h` for `UNUSED`, and `xstat.h`. It is used by code that wants metadata without triggering automounts or remote sync where possible.

Risks: the fallback behavior depends heavily on configure-time feature detection. `statx_copy()` maps only basic fields and ignores birth time, attributes, and masks. Static `statx_supported` is process-global and not synchronized, though the benign race only affects fallback selection.

Test signals: verify symlink and non-symlink paths, automount boundaries, kernels with and without `statx`, `EINVAL` emulation behavior, and parity of key `struct stat` fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/xstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/nfs/Makefile.am

Purpose: Automake manifest for the internal NFS support libraries.

Important build outputs: builds `libnfs.la` from export parsing, rmtab, RPC, socket, service, qword, string, credential, and file-handle-key helpers. Builds `libnfsconf.la` from `conffile.c` and `xlog.c`. `libnfs.la` links `libnfsconf.la` and `-luuid`.

Control flow: conditional `CONFIG_NFSDCTL` adds `nfsdnl.c`, libnl CFLAGS, nfsdctl include paths, and libnl libraries. `MAINTAINERCLEANFILES` removes generated `Makefile.in`.

State and persistence: no runtime state; controls build graph and link dependencies.

Dependencies and integration: integrates `support/reexport`, optional `utils/nfsdctl`, libuuid, libnl3, and libnl-genl. The `libnfsconf` split allows idmap and plugin components to share configuration/logging without pulling every NFS helper.

Risks: source additions must be represented here or downstream utilities silently miss symbols. Conditional netlink dependencies must match configure results. `libnfs_la_CPPFLAGS` contains reexport include paths that couple support/nfs to reexport internals.

Test signals: run `autoreconf`/Automake generation, build with and without `CONFIG_NFSDCTL`, inspect link lines for libuuid/libnl, and verify installed/private library symbol availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/atomicio.c -->
# sources/user-network-fs/nfs-utils/support/nfs/atomicio.c

Purpose: robust read/write loop that attempts to transfer exactly `n` bytes through a supplied I/O function.

Important API: `ssize_t atomicio(ssize_t (*f)(int, void *, size_t), int fd, void *_s, size_t n)` accepts a `read`- or `write`-compatible function pointer and returns bytes transferred, zero, or `-1`.

Control flow: loops until `pos == n`. `EINTR` and `EAGAIN` retry immediately. A zero result or nonretryable error returns a partial count if any bytes were already transferred; otherwise it returns the underlying zero or error.

State and persistence: no state beyond local counters; no persistence.

Dependencies and integration: includes `nfslib.h` and libc `errno`/`unistd` APIs. It is a generic helper for socket or file descriptor protocols requiring complete fixed-size transfers.

Risks: retrying `EAGAIN` without polling can spin on nonblocking descriptors. The callback signature uses `void *`, so direct use with `write()` may require a cast that discards constness. Returning a partial byte count on error requires callers to distinguish partial success from complete success.

Test signals: interrupted I/O, short reads/writes, EOF before any bytes, EOF after partial bytes, nonretryable errno, and nonblocking `EAGAIN` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/atomicio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/cacheio.c -->
# sources/user-network-fs/nfs-utils/support/nfs/cacheio.c

Purpose: qword encoding/decoding helpers for text-based kernel cache upcall channels.

Important APIs: `qword_add()`, `qword_addhex()`, `qword_addint()`, `qword_adduint()`, and `qword_addeol()` append encoded fields to a caller-managed buffer. `qword_get()`, `qword_get_int()`, and `qword_get_uint()` parse encoded fields from a line.

Control flow: text fields encode space, tab, newline, and backslash as octal escapes and append a separating space. Hex fields begin with `\x` and emit two lowercase hex digits per byte. Decoding skips leading spaces, detects hex form, otherwise recognizes `\nnn` octal escapes, stops at space/newline/NUL, updates the input pointer, and NUL-terminates the destination.

State and persistence: no global state. It serializes/deserializes records written elsewhere to kernel cache pseudo-files.

Dependencies and integration: used by NFS cache-channel code. Depends on libc formatting/ctype and `nfslib.h`.

Risks: buffer overflow is avoided by setting remaining length negative, but callers must check the length after building. `qword_addint()` and `qword_adduint()` do not set negative length on truncation; they clamp the returned length and continue. `qword_get()` writes a NUL terminator even after hex decode, so destination buffers must reserve space if the result is treated as a string.

Test signals: round-trip spaces/tabs/newlines/backslashes, hex binary payloads including NUL bytes, truncation paths, malformed octal/hex escapes, empty fields, and integer parse failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/cacheio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/closeall.c -->
# sources/user-network-fs/nfs-utils/support/nfs/closeall.c

Purpose: close all file descriptors greater than or equal to a caller-supplied minimum.

Important API: `void closeall(int min)`.

Control flow: prefers iterating `/proc/self/fd`, parsing numeric directory entries and closing each descriptor except the directory handle itself. If `/proc/self/fd` cannot be opened, it falls back to `sysconf(_SC_OPEN_MAX)` and closes descending descriptors down to `min`.

State and persistence: mutates the process descriptor table; no persistent state.

Dependencies and integration: used during daemonization to close inherited descriptors. Depends on procfs availability for efficient operation.

Risks: closing descriptors while other threads are active is process-wide and can race. The procfs path sees a snapshot during directory iteration, so descriptors opened concurrently may survive. The fallback assumes `sysconf(_SC_OPEN_MAX)` is usable as an integer upper bound.

Test signals: descriptors below/above `min`, procfs unavailable fallback, very high descriptor numbers, and preservation of the `/proc/self/fd` directory fd.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/closeall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/conffile.c -->
# sources/user-network-fs/nfs-utils/support/nfs/conffile.c

Purpose: shared `nfs.conf`/`idmapd.conf` parser, in-memory configuration database, transaction queue, report generator, and targeted config-file writer.

Important APIs and types: public routines include `conf_init_file()`, `conf_cleanup()`, `conf_get_num()`, `conf_get_bool()`, `conf_get_str()`, `conf_get_section()`, `conf_get_entry()`, `conf_get_list()`, `conf_get_tag_list()`, `conf_free_list()`, `conf_begin()`, `conf_remove()`, `conf_remove_section()`, `conf_end()`, `conf_report()`, `conf_write()`, and `conf_decode_base64()`. `struct conf_binding` stores active section/arg/tag/value entries in 256 hash buckets. `struct conf_trans` queues set/remove operations by transaction id.

Control flow: `conf_init_file()` initializes tables, optionally loads `/usr/etc/...` before `/etc/...`, loads the main file, then scans `<file>.d` with `versionsort()` and only `*.conf` entries. `conf_readfile()` locks and reads a whole file. `conf_parse()` splits lines, handles backslash-newline folding, section headers with optional quoted subsection args, assignments with quoted/unquoted values, and recursive `include` or optional `include=-path`. Parsed assignments queue `CONF_SET` operations, then `conf_end(commit=1)` applies them to the hash table.

Mutation and persistence: active configuration lives in process-global hash buckets. Transactions live in a global `TAILQ` until committed or discarded. `conf_write()` opens or creates a config file, takes an exclusive `flock()`, reads content into output queues, updates comments or section/tag assignments in place semantically, truncates the file, and writes the rebuilt content. `modified_by` can append a timestamp comment.

Dependencies and integration: used by NFS support and nfsidmap code for configuration. Depends on `xlog`, BSD queue macros, file locks, `dirname()`, directory scanning, and config constants such as `NFS_CONFFILE`.

Risks: all state is global and unsynchronized. Includes can recurse without explicit cycle detection. `conf_get_section()` expands `$name` through the process environment or `[environment]` section and uses `goto retry`, so cyclic config references can loop. `conf_write()` truncates the original file after building queues but without a temp-file/rename strategy, so write failures can still damage the file despite locks. `conf_get_tag_list()` compares `arg` against `cb->arg` without checking `cb->arg` for NULL when `arg` is non-NULL.

Test signals: parse comments, quoted values, subsections, include and optional include, folded lines, duplicate tags, default-vs-override behavior, directory ordering, transaction rollback, list parsing, base64 validation, env expansion, config write add/update/delete, comments, folded values, and simulated write/truncate failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/conffile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/exports.c -->
# sources/user-network-fs/nfs-utils/support/nfs/exports.c

Purpose: parser and emitter for NFS export entries, including export options, security flavors, transport security, squash lists, fsid/UUID, referrals/replicas, pNFS, and reexport integration.

Important APIs and data: `setexportent()`, `getexportent()`, `putexportent()`, `endexportent()`, `dupexportent()`, `mkexportent()`, `updateexportent()`, `secinfo_addflavor()`, `secinfo_show()`, `xprtsecinfo_show()`, `fix_pseudoflavor_flags()`, and `get_export_features()`. `flav_map` maps `krb5`, `krb5i`, `krb5p`, `unix`, `sys`, `null`, and `none`. Export defaults include read-only, root-squash, gathered writes, and no-subtree-check.

Control flow: `getexportent()` reads the path, optional default options beginning with `-`, then a client token with optional parenthesized options. It initializes defaults, parses options with `parseopts()`, canonicalizes the export path through `nfsd_realpath()`, and returns a static `struct exportent`. `parseopts()` tokenizes comma-separated options, sets/clears flags globally and on active security flavors, parses ID ranges, fsid/UUID, mountpoint, fsloc, `sec=`, `xprtsec=`, and `reexport=`, then normalizes pseudoflavor flags against kernel-supported feature masks.

State and persistence: uses static file name/handle, static returned export entries, and static squash arrays that are moved into export entries. `get_export_features()` caches `/proc/fs/nfsd/export_features`. Persistent input/output is `/etc/exports` or `/proc/fs/nfs/exports` style files via `XFILE`.

Dependencies and integration: depends on export flag definitions, `xio` tokenization, `xmalloc`, `xlog`, pseudoflavor constants, reexport database hooks, and `nfsd_path` realpath handling. It is central to `exportfs`, `mountd`, and kernel export cache population.

Risks: parser state is nonreentrant. `putexportent()` appears to use `e_nsquids` while printing `e_sqgids`, which can omit or overrun group squash ranges when UID and GID range counts differ. Option parsing mutates temporary strings and global squash pointers in ways sensitive to early failures. `fsid=` must precede `reexport=`, which should be documented/tested for user-facing diagnostics.

Test signals: export lines with default options, empty/default clients, missing option warnings, each flag pair, sec flavor grouping, xprtsec modes, squash UID/GID ranges, fsid root/numeric/UUID, reexport strategies, malformed options, path canonicalization, and round-trip `putexportent()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/fh_key_file.c -->
# sources/user-network-fs/nfs-utils/support/nfs/fh_key_file.c

Purpose: derive a deterministic UUID from a file-handle key file by repeatedly applying UUID version-5/SHA1 generation.

Important API: `int hash_fh_key_file(const char *fh_key_file, uuid_t uuid)`.

Control flow: opens the key file, initializes `uuid` from a fixed seed UUID, reads 256-byte blocks, and for each block calls `uuid_generate_sha1(uuid, uuid, buf, sread)`. Read errors are logged and returned as errno or `EIO`.

State and persistence: reads persistent key-file content and writes the resulting UUID into caller-provided storage. No module-global state.

Dependencies and integration: depends on libuuid, `nfslib.h`, and `xlog`. Used where NFS file-handle signing or identity needs a stable UUID derived from local secret/configured content.

Risks: opens in text mode `"r"` instead of binary mode, which is harmless on Linux but conceptually a byte-hash routine. Empty files produce the fixed seed UUID. Sequential UUID chaining is deterministic but not equivalent to hashing the whole file once with explicit domain separation.

Test signals: missing/unreadable file, empty file, one block, multiple blocks, read error injection, and stable output across runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/fh_key_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/getport.c -->
# sources/user-network-fs/nfs-utils/support/nfs/getport.c

Purpose: RPC service discovery helpers for querying local or remote rpcbind/portmapper and verifying service responsiveness.

Important APIs: `nfs_get_proto()`, `nfs_get_netid()`, `nfs_universal2port()`, `nfs_sockaddr2universal()`, `nfs_rpc_ping()`, `nfs_getport()`, `nfs_getport_ping()`, `nfs_getlocalport()`, `nfs_rpcb_getaddr()`, `nfs_pmap_getport()`, and `nfs_probe_statd()`.

Control flow: rpcbind clients are created with `nfs_gp_get_rpcbclient()`, which discovers the rpcbind port from `/etc/services` names or `PMAPPORT`. IPv4 lookups use pmap v2 `PMAPPROC_GETPORT`; IPv6 with TI-RPC uses rpcbind v4 then v3 `RPCBPROC_GETADDR` on the same client. Universal addresses are built from sockaddr plus high/low port components and parsed back by stripping the last two dotted decimal fields. Ping variants set the discovered port and issue an RPC `NULLPROC`.

State and persistence: no durable state. It mutates `rpc_createerr` as the error side channel and may update caller sockaddr ports in `nfs_getport_ping()`. Service-name lookups read system databases such as `/etc/services`, `/etc/rpc`, `/etc/netconfig`, DNS/NSS, and rpcbind state.

Dependencies and integration: depends on TI-RPC when available, legacy SunRPC otherwise, `sockaddr.h`, `nfsrpc.h`, and `nfslib.h`. It integrates with mount/statd probing and service discovery code.

Risks: default timeout uses `tv_sec = -1` as a sentinel interpreted by client creation helpers, so callers must pass initialized timevals. `nfs_sockaddr2universal()` uses `sizeof(struct sockaddr)` to derive AF_LOCAL path length, which is suspicious for longer `sockaddr_un` values. Global `rpc_createerr` makes the APIs non-thread-local. Behavior differs for libtirpc vs non-libtirpc, especially IPv6 and netid support.

Test signals: IPv4 pmap success/failure, IPv6 rpcbind v4 fallback to v3, malformed universal addresses, services database overrides, TCP timeout/refused error mapping, local rpcbind fallback, statd probing, and non-libtirpc unsupported address cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/getport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/mydaemon.c -->
# sources/user-network-fs/nfs-utils/support/nfs/mydaemon.c

Purpose: daemonization helper that lets the parent exit only after the child reports readiness.

Important APIs: `daemon_init(bool fg)` and `daemon_ready()`.

Control flow: foreground mode returns immediately. Background mode creates a pipe, forks, and the parent blocks reading an integer status. The child starts a new session, changes to `/`, moves the readiness pipe to fd 3, redirects stdin/stdout/stderr to `/dev/null`, closes descriptors >=4, and later `daemon_ready()` writes status 0 to the pipe and closes it.

State and persistence: process-global `pipefds[2]` tracks readiness communication. No durable state.

Dependencies and integration: depends on `xlog`, `closeall()`, syslog, fork/session/file descriptor APIs. Used by daemons that want reliable init scripts/system callers to see startup failure.

Risks: parent treats short read as failure, so a child that never calls `daemon_ready()` causes parent failure even if the daemon runs. Error paths call `exit()` directly. Descriptor juggling assumes fd 3 is available after `dup2()`.

Test signals: foreground no-op, successful parent wait, child setup failures, missing `daemon_ready()`, pipe write failure, and descriptor table cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/mydaemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/nfs_mntent.c -->
# sources/user-network-fs/nfs-utils/support/nfs/nfs_mntent.c

Purpose: private mount-entry parser/writer similar to libc `mntent`, with explicit escaping for whitespace and backslashes.

Important APIs: `nfs_setmntent()`, `nfs_endmntent()`, `nfs_addmntent()`, and `nfs_getmntent()`. Internal helpers `mangle()` and `unmangle()` encode/decode `\040`-style octal escapes.

Control flow: opening temporarily sets umask 077. Writing seeks to EOF, records current length, writes escaped fields plus numeric freq/passno, flushes, and truncates back to the previous length on flush failure. Reading skips blank/comment lines, handles missing final newline warnings, unmangles four fields, parses optional numeric freq/passno, and skips malformed lines until an error threshold.

State and persistence: `mntFILE` owns file pointer, path, line number, and soft/hard error counters. `nfs_getmntent()` returns a static `struct mntent` backed by heap strings that are replaced on each call.

Dependencies and integration: used by mount-related nfs-utils code. Depends on `xcommon` allocation/error helpers and NLS `_()` messages.

Risks: returned entries are static and not thread-safe; repeated calls leak or overwrite expectations unless caller understands ownership. Line length is capped at 4096. Parser tolerates trailing data, so corrupted lines may not always fail.

Test signals: escaped spaces/tabs/newlines/backslashes, bad lines and `ERR_MAX`, missing final newline, flush failure rollback, append semantics, and `/proc/mounts`-like files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/nfs_mntent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/nfsdnl.c -->
# sources/user-network-fs/nfs-utils/support/nfs/nfsdnl.c

Purpose: helper for sending nfsd generic-netlink commands with a string attribute.

Important API: `int nfsd_nl_cmd_str(int cmd, int attr, const char *value)`.

Control flow: allocates a libnl socket, connects to generic netlink, sets buffer sizes, resolves `NFSD_FAMILY_NAME`, allocates and fills a generic-netlink message, appends the string attribute, sends it, installs error/finish/ack callbacks, then receives until the callback-controlled return value is no longer positive.

State and persistence: no module-global state. It sends commands to kernel nfsd netlink state and reports kernel/libnl errors.

Dependencies and integration: optional `CONFIG_NFSDCTL` build path. Depends on libnl3/genl, `nfsd_netlink.h` or system kernel header, `nfslib.h`, and `xlog.h`.

Risks: `nla_put_string()` return is not checked. The receive loop ignores the return value of `nl_recvmsgs()`, relying on callbacks to update `ret`. Buffer size is fixed at 4096. Return values are negative errno-style except success 0.

Test signals: missing family, allocation failures, kernel error ack, successful ack, invalid command/attribute, and string values near netlink message limits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/nfsdnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rmtab.c -->
# sources/user-network-fs/nfs-utils/support/nfs/rmtab.c

Purpose: read/write helpers for the NFS remote mount table (`rmtab`) that records client, path, and mount count.

Important APIs: `setrmtabent()`, `fsetrmtabent()`, `getrmtabent()`, `fgetrmtabent()`, `putrmtabent()`, `fputrmtabent()`, `endrmtabent()`, `fendrmtabent()`, `rewindrmtabent()`, and `frewindrmtabent()`. Global `struct state_paths rmtab` supplies the default path.

Control flow: reader parses one `host:path:count` line, converts semicolons back to colons in the client field for IPv6 presentation addresses, defaults missing count to 1, and returns a static `struct rmtabent`. Writer optionally seeks to a supplied position, converts client colons to semicolons, and emits count as fixed-width hex.

State and persistence: global `FILE *rmfp` is the default open table. The durable state is the rmtab file. Static buffers/entries are reused per read.

Dependencies and integration: used by mountd/export utilities tracking remote mounts. Depends on `nfslib.h` and `xlog`.

Risks: colon replacement is lossy for unusual host names containing semicolons. No file locking is performed here. Static buffer and global handle are not reentrant. Path values containing colons are not escaped.

Test signals: IPv4/hostname and IPv6 client round-trip, missing count, malformed line logging/errno, positioned overwrite, long client rejection, and concurrent writers if external locking is expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rmtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rpc_socket.c -->
# sources/user-network-fs/nfs-utils/support/nfs/rpc_socket.c

Purpose: create RPC client handles over AF_LOCAL, UDP, or TCP sockets with bounded connect/request timeouts and optional privileged source ports.

Important APIs: `nfs_get_rpcclient()`, `nfs_get_priv_rpcclient()`, `nfs_getrpcbyname()`, and `nfs_authsys_create()`. Internal helpers cover local sockets, reserved-port binding, nonblocking connect, UDP client creation, and TCP client creation.

Control flow: public client creation validates address family and nonzero network port, clears `rpc_createerr`, then chooses TCP or UDP. UDP and TCP create sockets, optionally bind reserved ports, apply default timeout if `tv_sec == -1`, perform nonblocking connect with `select()`, and create TI-RPC or legacy RPC clients with `CLSET_FD_CLOSE`. UDP clients also set one-second retry timeout.

State and persistence: no durable state; mutates global `rpc_createerr`. `timeout` is an in/out parameter and may be reduced by `select()`.

Dependencies and integration: used by `getport.c` and other RPC callers. Depends on libtirpc when configured, `sockaddr.h`, `nfsrpc.h`, and AUTH_SYS APIs.

Risks: global `rpc_createerr` is not thread-local. `select()` timeout mutation can surprise callers reusing a timeval. Nonblocking connect restores original flags but errors during flag restore are ignored. Reserved ports require privileges and may fail under port exhaustion.

Test signals: TCP/UDP success, refused/timeouts, AF_LOCAL with libtirpc and legacy builds, reserved-port binding, IPv6 support, invalid protocol/address, and `nfs_authsys_create()` group-list minimization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rpc_socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rpcdispatch.c -->
# sources/user-network-fs/nfs-utils/support/nfs/rpcdispatch.c

Purpose: generic server-side RPC dispatcher for table-driven RPC program implementations.

Important API: `rpc_dispatch(struct svc_req *rqstp, SVCXPRT *transp, struct rpc_dtable *dtable, int nvers, void *argp, void *resp)`.

Control flow: validates version range, selects a version table, validates procedure number, fetches the dispatch entry, zeros argument/result storage using configured sizes, decodes arguments with `svc_getargs()`, invokes the handler, sends a reply if the handler returns true and `resp` is non-NULL, then frees decoded arguments.

State and persistence: no module state. It mutates caller-provided argument and response buffers.

Dependencies and integration: depends on RPC service APIs, `rpcmisc.h` table definitions, and `xlog`. Used by generated or hand-written RPC daemons to avoid repetitive dispatch boilerplate.

Risks: caller must pass buffers large enough for the selected table entry. The duplicate procedure bounds checks are harmless. Failure of `svc_freeargs()` exits the process with status 2. Handler return convention must be consistent across services.

Test signals: invalid version, invalid proc, NULL function, decode failure, no-response handlers, send failure, and free-args failure path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rpcdispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rpcmisc.c -->
# sources/user-network-fs/nfs-utils/support/nfs/rpcmisc.c

Purpose: legacy RPC service startup helper with inetd/portmapper awareness and closedown timer behavior.

Important APIs and globals: `rpc_init()` registers UDP/TCP transports for a program/version. Globals `_rpcpmstart`, `_rpcprotobits`, and `_rpcsvcdirty` control inetd mode, enabled protocols, and idle shutdown. Internal `makesock()` binds IPv4 sockets and `closedown()` exits idle portmapper-started services.

Control flow: `rpc_init()` detects whether fd 0 is an inetd-provided socket and sets protocol bits accordingly. Without inetd, it unregisters old mappings and creates UDP/TCP sockets or RPC_ANYSOCK transports. It reuses last UDP/TCP transport for additional versions on the same port, registers each with `svc_register()`, and sets SIGALRM closedown in portmapper-start mode.

State and persistence: process-global protocol/dirty/start flags and static last transports. Registers/unregisters with local portmapper/rpcbind persistent runtime registry.

Dependencies and integration: used when libtirpc `nfs_svc_create()` is unavailable or by legacy service setup. Depends on `svc_socket.c`, `rpcmisc.h`, RPC/pmap APIs, and `nfslib.h`.

Risks: IPv4-only. Signal handling uses `signal()` and `alarm()` with global state. Fatal logging exits on many setup failures. Reusing `last_transp` depends on port equality and can be surprising when protocol bits change.

Test signals: inetd UDP/TCP detection, explicit fixed port, random port, multi-version reuse, protocol-bit filtering, idle closedown with clean/dirty service state, and bind/listen failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/rpcmisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/strlcat.c -->
# sources/user-network-fs/nfs-utils/support/nfs/strlcat.c

Purpose: OpenBSD-compatible `strlcat()` implementation for platforms lacking it.

Important API: `size_t strlcat(char *dst, const char *src, size_t siz)`.

Control flow: scans destination up to `siz`, appends source while leaving space for NUL, always NUL-terminates when there is room, and returns the length it tried to create (`initial_dst_len + strlen(src)`).

State and persistence: no state.

Dependencies and integration: included in `libnfs.la` as a portability shim through `nfslib.h`.

Risks: behavior assumes `dst` points to a valid buffer of `siz` bytes. If `dst` is not NUL-terminated within `siz`, no bytes are appended and return value signals truncation.

Test signals: normal append, exact fit, truncation, zero size, unterminated destination within size, and return-value truncation checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/strlcat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/strlcpy.c -->
# sources/user-network-fs/nfs-utils/support/nfs/strlcpy.c

Purpose: OpenBSD-compatible `strlcpy()` implementation for platforms lacking it.

Important API: `size_t strlcpy(char *dst, const char *src, size_t siz)`.

Control flow: copies up to `siz - 1` bytes, NUL-terminates if `siz != 0`, walks the rest of the source to compute and return `strlen(src)`.

State and persistence: no state.

Dependencies and integration: portability shim included in `libnfs.la`.

Risks: source and destination must not overlap unless the platform semantics permit undefined behavior. Callers must check `return >= siz` for truncation.

Test signals: zero size, one-byte buffer, exact fit, truncation, long source, and return length.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/strlcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/svc_create.c -->
# sources/user-network-fs/nfs-utils/support/nfs/svc_create.c

Purpose: create and register RPC service listeners, using TI-RPC/netconfig when available and falling back to legacy `rpc_init()`.

Important APIs: `nfs_svc_create()` starts listeners for a program/version/dispatch function, and `nfs_svc_unregister()` removes rpcbind/portmap registrations. Internal TI-RPC helpers include `svc_create_bindaddr()`, `svc_create_sock()`, `svc_create_nconf_rand_port()`, `svc_create_nconf_fixed_port()`, and an 8-entry SVCXPRT cache.

Control flow: modern builds ignore SIGPIPE, set `RPC_SVC_CONNMAXREC_SET`, iterate visible netconfig entries, filter by global UDP/TCP protocol bits, choose either configured service port or caller-supplied port, then create/register transports. Random-port mode lets TI-RPC create xprts. Fixed-port mode pre-binds sockets with `SO_REUSEADDR`, IPv6-only when needed, nonblocking mode, and xprt caching so multiple versions can share the same listener. Legacy builds delegate to `rpc_init()`.

State and persistence: caches up to eight service transports in process memory. Registers service mappings with local rpcbind/portmapper. No file persistence.

Dependencies and integration: depends on libtirpc/netconfig, `rpcmisc.h` protocol globals, `svc_socket.c`, `sockaddr.h`, optional `tcpwrapper.h`, and `xlog`.

Risks: xprt cache has a fixed small size and logs only when full. `svc_reg()` may destroy xprts on failure, so cache consistency relies on only caching after successful registration. Fixed-port binding across IPv4/IPv6 depends on `IPV6_V6ONLY`. `rpc_control()` behavior is libtirpc-specific.

Test signals: random and fixed ports, multi-version same-port registration, UDP/TCP protocol filtering, IPv4/IPv6 listeners, cache-full behavior, `svc_reg()` failure, unregister, and legacy non-libtirpc build.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/svc_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/svc_socket.c -->
# sources/user-network-fs/nfs-utils/support/nfs/svc_socket.c

Purpose: legacy helpers for creating nonblocking IPv4 RPC service sockets bound to service ports derived from RPC program numbers.

Important APIs: `getservport()`, `svcsock_nonblock()`, `svctcp_socket()`, and `svcudp_socket()`.

Control flow: `getservport()` maps an RPC program number to an RPC name/aliases and then to a TCP/UDP service port. `svc_socket()` creates AF_INET TCP/UDP sockets, optionally sets `SO_REUSEADDR`, binds to the service port, and marks the socket nonblocking. TCP and UDP wrappers choose socket type/protocol.

State and persistence: no global state; reads NSS databases for RPC/service entries and mutates socket state.

Dependencies and integration: used by legacy `rpcmisc.c`. Depends on `xlog`, `rpcmisc.h`, libc NSS, and socket APIs.

Risks: IPv4-only. If no service port is found, it binds port 0. Nonblocking conversion closes the socket on failure. Test-only `main()` is gated by `TEST`.

Test signals: known program-to-port mappings, aliases, missing service database entries, TCP reuse option, UDP no-reuse path, nonblocking flag, and bind failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/svc_socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/ucred.c -->
# sources/user-network-fs/nfs-utils/support/nfs/ucred.c

Purpose: construct `struct nfs_ucred` values from RPC request authentication credentials and export squash policy.

Important API: `int nfs_ucred_get(struct nfs_ucred **credp, struct svc_req *rqst, const struct exportent *ep)`. Internal helpers initialize credentials from AUTH_UNIX, RPCSEC_GSS, AUTH_DES, or anonymous/null fallback.

Control flow: request auth flavor selects initialization path. AUTH_UNIX copies `authunix_parms`. RPCSEC_GSS calls `rpc_gss_getcred()` when available. AUTH_DES calls `authdes_getucred()` when available. Unknown flavors become anonymous credentials. `nfs_ucred_init_cred()` applies all-squash, root-squash, and root-group squash rules before returning the heap-allocated credential.

State and persistence: allocates a credential and optional group list for the caller to own/free. No persistent state.

Dependencies and integration: depends on RPC request structs, optional tirpc GSS/DES APIs, export flags, and shared `nfs_ucred` helpers from misc. Used by NFS service code needing filesystem credentials corresponding to an RPC caller.

Risks: group arrays are heap allocated and require consistent freeing by callers. Root-squash preserves nonzero primary GID when UID is 0, while group list is anonymous/empty; tests should confirm this matches policy. Unsupported auth flavors silently map to anonymous.

Test signals: AUTH_UNIX user/group/groups, all-squash, root-squash uid 0 with gid 0 and nonzero gid, RPCSEC_GSS success/failure, AUTH_DES success/failure, unknown auth flavor, and allocation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/ucred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/wildmat.c -->
# sources/user-network-fs/nfs-utils/support/nfs/wildmat.c

Purpose: case-insensitive shell-style wildcard matcher supporting `*`, `?`, backslash literals, and bracket character classes.

Important API: `int wildmat(char *text, char *p)`. Internal `DoMatch()` returns true, false, or abort to optimize failing `*` patterns.

Control flow: walks pattern and text; `*` collapses consecutive stars and recursively tests suffixes; `?` matches any character; `[...]` supports ranges and `^` negation; default and escaped characters compare with `toupper()`. A pattern exactly equal to `*` returns true immediately.

State and persistence: no state.

Dependencies and integration: used for export/client matching patterns in NFS utilities via `nfslib.h`.

Risks: file comment warns malformed patterns such as incomplete ranges may not be robust. `toupper()` should be passed unsigned-char-compatible values; current code passes `char` values directly. Matching is case-insensitive, which may not fit all callers.

Test signals: literal, `*`, `?`, escaped metacharacters, classes/ranges/negation, malformed classes, empty strings, 8-bit input, and pathological star patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/wildmat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/xcommon.c -->
# sources/user-network-fs/nfs-utils/support/nfs/xcommon.c

Purpose: shared allocation, string, path, and error helpers imported from mount/util-linux ancestry.

Important APIs and globals: `at_die` optional callback, `xstrndup()`, `xstrconcat2()`, `xstrconcat3()`, `xstrconcat4()`, `nfs_error()`, `canonicalize()`, `die()`, `xmalloc()`, `xrealloc()`, `xfree()`, and `xstrdup()`.

Control flow: allocation wrappers call `die(EX_SYSERR, ...)` on failure except zero-size `xmalloc()` returns NULL. Concatenation helpers treat NULL inputs as empty strings, and the 3/4-argument variants free their first argument when it was non-NULL. `canonicalize()` preserves special pseudo-filesystem names and otherwise returns `realpath()` output or a copy of the original path.

State and persistence: `at_die` is a process-global hook invoked before fatal exit. No durable state.

Dependencies and integration: used by mount/NFS parsing utilities for fail-fast allocation. Depends on NLS `_()` and `xcommon.h`.

Risks: fatal allocation behavior is unsuitable in library paths that should report `ENOMEM`. `xstrconcat3/4()` freeing the first argument is nonobvious and dangerous with string literals or shared ownership. `canonicalize()` returns unresolved paths unchanged, which callers must not confuse with verified canonical paths.

Test signals: allocation failure hooks, NULL string arguments, first-argument ownership in concat helpers, pseudo-filesystem canonicalize exceptions, realpath success/failure, and fatal exit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/xcommon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/xio.c -->
# sources/user-network-fs/nfs-utils/support/nfs/xio.c

Purpose: tokenized file I/O helpers for exports-style configuration files.

Important APIs: `xfopen()`, `xfclose()`, `xflock()`, `xfunlock()`, `xgettok()`, `xgetc()`, `xungetc()`, `xskip()`, and `xskipcomment()`. `XFILE` wraps a `FILE *` and current line number.

Control flow: `xgetc()` handles backslash-newline continuations by returning a space and incrementing the line number. `xgettok()` reads until whitespace or a requested separator unless inside double quotes, decodes octal `\nnn` escapes, and returns 0 for no token, 1 for success, or -1 for overflow/separator mismatch. `xskip()` skips caller-specified chars and comments beginning with `#`.

State and persistence: file position and line number live in `XFILE`. `xflock()` creates/opens lock files and returns an fd whose close releases the fcntl lock.

Dependencies and integration: used by `exports.c` and related parsers. Depends on `xmalloc`, `xlog`, and standard stdio/fcntl APIs.

Risks: token length overflow returns -1 after consuming input. Quote handling toggles on every `"`, with no escape-specific quote semantics. `xflock()` opens read locks with `O_CREAT`, which can create missing lock files even for read mode.

Test signals: quoted tokens, separators, octal decoding, line continuation, comments, line-number pushback, token overflow, and fcntl lock acquisition/release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/xio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/xlog.c -->
# sources/user-network-fs/nfs-utils/support/nfs/xlog.c

Purpose: process-wide logging and debug-facility control for nfs-utils support code.

Important APIs and globals: `xlog_open()`, `xlog_stderr()`, `xlog_syslog()`, `xlog_config()`, `xlog_sconfig()`, `xlog_set_debug()`, `xlog_enabled()`, `xlog_backend()`, `xlog()`, `xlog_warn()`, `xlog_err()`, and `xlog_errno()`. `export_errno` is set for error/general debug calls.

Control flow: `xlog_open()` opens syslog and installs SIGUSR1/SIGUSR2 toggles. SIGUSR1 progressively enables debug masks; SIGUSR2 disables debug logging. `xlog_backend()` filters debug/nonfatal messages, prints to stderr and/or syslog, maps severity to syslog priority, and exits for `L_FATAL`.

State and persistence: global flags control stderr/syslog output, debug mask, program name, pid, and exported error flag. No file persistence except syslog side effects.

Dependencies and integration: widely used by support libraries and daemons. Reads debug config via `conf_get_list(service, "debug")`.

Risks: signal handlers call logging code that is not async-signal-safe. Global mutable logging state is not thread-safe. `va_list` is consumed for stderr and then reused for syslog only if stderr path did not consume it; current code uses `va_copy` for stderr, so syslog still receives the original list. Fatal logging exits from library contexts.

Test signals: stderr/syslog toggles, debug facility parsing, config-driven debug, SIGUSR1/SIGUSR2 behavior, `L_FATAL` exit, and `export_errno` updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfs/xlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/Makefile.am

Purpose: Automake manifest for libnfsidmap and its mapping plugins.

Important build outputs: builds shared `libnfsidmap.la`, plugin modules `nsswitch.la`, `static.la`, `regex.la`, and optional `umich_ldap.la`/`gums.la`. Installs headers `nfsidmap.h` and `nfsidmap_plugin.h`, man pages, and `libnfsidmap.pc`.

Control flow: plugin directory comes from `PATH_PLUGINS` or defaults to `$(libdir)/libnfsidmap`. LDAP, GUMS, and LDAP SASL support are conditional. The core library links `-ldl` and `support/nfs/libnfsconf.la`; plugins that use config also link `libnfsconf.la`.

State and persistence: no runtime state; controls build/install layout and pkg-config metadata generation.

Dependencies and integration: integrates dynamic plugin loading with the core library and config parser. `dist-hook` copies Debian packaging files into release tarballs.

Risks: plugin build flags must match optional dependencies or runtime loading will fail. `gums.la` is built without `nfsidmap_common.c`, unlike other plugins, so it depends on the symbols it actually references being available through headers/libraries. Plugin directory affects runtime search behavior.

Test signals: build all optional combinations, verify plugin install paths, run `pkg-config --libs --cflags libnfsidmap`, and load each plugin through `libnfsidmap.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/gums.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/gums.c

Purpose: optional libnfsidmap plugin that maps SPKM3/X.509/VOMS-authenticated principals to local UID/GID through a GUMS/PRIMA SAML identity mapping service.

Important APIs and data: plugin entry `libnfsidmap_plugin_init()` returns `gums_trans`, whose `.init` is `gums_init()` and `.princ_to_ids` is `gums_gss_princ_to_ids()`. `plugin_config_params conf` holds SAML schema, cert/key, CA directory, GUMS server URL, VOMS directory, and log level.

Control flow: `gums_init()` reads PRIMA config from `nfsidmap_config_get("GUMS", "Conf_File")` or `/etc/grid-security/prima-authz.conf`, extracts server/cert/key/schema/log/CA/VOMS settings, fills defaults, and validates required fields. Mapping accepts only `secname == "spkm3"`, decodes extra X.509 certificate blobs into user cert and chain, retrieves VOMS attributes, initializes PRIMA SAML support, builds a SAML request from server DN and user/VOMS FQANs, queries the mapping service, processes the response into local user/group names, then resolves them with `getpwnam_r()`/`getgrnam_r()`.

State and persistence: process-global `conf` stores plugin configuration. Persistent inputs include PRIMA config, service certificate/key, CA/VOMS directories, user proxy/certificate data, local NSS password/group databases, and the remote GUMS service. Test-program code can use `X509_USER_PROXY`.

Dependencies and integration: depends on OpenSSL X509/BIO APIs, VOMS, PRIMA logger/SOAP/SAML libraries, and libnfsidmap plugin interfaces. It integrates as a GSS-specific translation method.

Risks: `USING_TEST_PROGRAM` is defined in source, which defines `idmap_log_func`, `idmap_verbosity`, and a `main()` test harness in this file; build configuration must prevent conflicts if this is unintended. Several `strdup()` assignments can overwrite existing `conf` pointers on repeated init. External network/certificate/SAML dependencies make error handling and test determinism hard. `queryIdentityMappingService()` returning NULL leaves `local_uid` NULL and then `translate_to_uid(local_uid, ...)` would fail via `getpwnam_r()` expectations; the preceding response branch does not explicitly reject NULL response before translation.

Test signals: missing/malformed PRIMA config, default CA/VOMS dirs, SPKM3-only rejection, DER certificate parsing, VOMS absent vs present, SAML request contents, GUMS response with uid/gid, local NSS lookup failures, cert/key errors, and repeated init/cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/gums.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/idmapd.conf -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/idmapd.conf

Purpose: sample/default configuration file for NFSv4 idmapping.

Important sections and options: `[General]` covers verbosity, NFSv4 domain, no-strip behavior for multi-domain identities, group-name reformatting, and local Kerberos realms. `[Mapping]` defines nobody user/group. `[Translation]` selects ordered mapping plugins via `Method` and optional `GSS-Methods`. `[Static]` provides literal GSS principal-to-local mappings. `[UMICH_SCHEMA]` documents LDAP server, search bases, TLS/SASL options, and schema attribute mappings.

Control flow: the file is consumed by `conffile.c` and `libnfsidmap.c`; comments describe defaults when options are omitted. Plugin modules read their own sections, for example static, LDAP, or GUMS.

State and persistence: persistent administrator configuration, normally installed under `/etc/idmapd.conf`. Values affect process-global libnfsidmap initialization and plugin behavior.

Dependencies and integration: integrates NFSv4 id-to-name mapping with NSS, LDAP, Kerberos realms, and optional static mappings. The sample is also included in distribution by `Makefile.am`.

Risks: most options are commented, so defaults must be kept in sync with code and man pages. LDAP examples include required-looking sample host/base values that should not be mistaken for live defaults. Multi-domain `No-Strip` behavior can alter lookup semantics significantly.

Test signals: parse every documented section, defaults when commented, Method/GSS-Methods lists, Domain omission DNS fallback, Local-Realms handling, No-Strip/Reformat-Group values, and LDAP option retrieval by plugin code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/idmapd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/libnfsidmap.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/libnfsidmap.c

Purpose: core NFSv4 name/id mapping library that initializes configuration, discovers the NFSv4 domain, loads translation plugins, and exposes mapping APIs.

Important APIs and data: public functions include `nfs4_init_name_mapping()`, `nfs4_term_name_mapping()`, `nfs4_get_default_domain()`, `nfs4_uid_to_name()`, `nfs4_gid_to_name()`, `nfs4_uid_to_owner()`, `nfs4_gid_to_group_owner()`, `nfs4_name_to_uid()`, `nfs4_name_to_gid()`, `nfs4_owner_to_uid()`, `nfs4_group_owner_to_gid()`, GSS principal mapping variants, `nfs4_set_debug()`, and `nfsidmap_config_get()`. Global plugin arrays `nfs4_plugins` and `gss_plugins` hold dynamically loaded mapping backends.

Control flow: initialization loads config with `conf_init_file()`, obtains `Domain` or derives it from hostname/DNS `_nfsv4idmapdomain` TXT record, loads local realms, reads `[Translation] Method` or defaults to `nsswitch`, optionally loads `GSS-Methods`, and resolves configured nobody user/group. `load_translation_plugin()` first tries `dlopen("<method>.so")` via the search path, verifies the plugin init symbol, falls back to `PATH_PLUGINS/<method>.so`, calls plugin init and optional plugin `.init`, then stores the handle and function table. The `RUN_TRANSLATIONS` macro initializes lazily and invokes each plugin function until one returns other than `-ENOENT`.

State and persistence: process-global default domain, plugin arrays, nobody UID/GID, logging callback/verbosity, and config path. Persistent inputs are idmapd.conf, DNS/NSS resolver state, plugin shared objects, password/group databases, and plugin-specific backing stores.

Dependencies and integration: depends on `conffile.c`, resolver APIs, `dlopen()`, libnfsidmap plugin ABI, local realm helpers from `nfsidmap_common.c`, and NSS password/group APIs. Used by kernel idmapping helpers and user-space NFSv4 ACL/id conversion.

Risks: global initialization is not synchronized and comments note reload limitations. DNS parsing uses low-level resolver message walking and trusts the first TXT answer. `id_as_chars()` accepts numeric strings with trailing junk because it does not inspect `strtol()` end pointer. Owner/group fallback writes numeric IDs with `sprintf()` without checking the caller buffer length. Plugin unload assumes plugin arrays are complete and can call `dlclose()` while plugin data may still be referenced elsewhere.

Test signals: explicit domain, DNS TXT domain, fallback default domain, Method and GSS-Methods ordering, plugin load fallback path, plugin init failure cleanup, nobody configured/missing, numeric owner fallback, nobody fallback, each mapping API continuing on `-ENOENT`, and term/reinit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/libnfsidmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/libnfsidmap.pc.in -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/libnfsidmap.pc.in

Purpose: pkg-config template for consumers of libnfsidmap.

Important fields: substitutes `prefix`, `exec_prefix`, `libdir`, `includedir`, and `@PACKAGE_VERSION@`; publishes `Name`, `Description`, empty `Requires`, `Libs: -L@libdir@ -lnfsidmap`, and `Cflags: -I@includedir@`.

Control flow: generated by the build system into `libnfsidmap.pc` and installed under `$(libdir)/pkgconfig`.

State and persistence: build-time metadata template only; installed `.pc` file becomes persistent consumer metadata.

Dependencies and integration: used by downstream builds to discover link and include flags for libnfsidmap.

Risks: `Requires` is empty even though the implementation uses runtime plugin loading and may link libdl/config support internally; this is likely intentional for private dependencies but should be checked for static linking. Include path assumes public headers are directly under `includedir`.

Test signals: generated file substitution, `pkg-config --modversion`, `--libs`, `--cflags`, and downstream compile/link of a minimal libnfsidmap consumer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/libnfsidmap.pc.in -->
