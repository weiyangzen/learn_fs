# subset-b-007017 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc.h -->
# sources/distributed-fs/coda/coda-src/venus/vproc.h

`vproc.h` defines the Venus process abstraction used by the Coda client daemon to service kernel upcalls, background daemons, pathname work, pioctl commands, and VFS operations. Its central type is `class vproc`, an `olink`-managed lightweight process wrapper with an LWP id, per-thread RVM state, retry/interrupt flags, and a public `uarea` holding implicit syscall context such as `u_error`, `u_uid`, current directory fid, `namectxt`, volume lock state, VFS opcode, resolve retry counters, and caller pid/pgid.

Important APIs include `Begin_VFS` and `End_VFS` for volume-level concurrency, the VFS operation methods implemented in `vproc_vfscalls.cc`, `do_ioctl` implemented in `vproc_pioctl.cc`, pathname helpers implemented in `vproc_pathname.cc`, and exported scheduling helpers such as `VprocWait`, `VprocSignal`, `VprocSelect`, `VprocSleep`, `Rtry_Wait`, and `VprocSetRetry`. The `venus_cnode` structure is the small kernel-facing return object carrying a `VenusFid`, cache-file pointer, vnode type, and inconsistency flags. The `MAKE_CNODE` macros convert kernel fids into Venus fids or directly copy Venus fids into output cnodes.

Control flow is deliberately implicit: operation implementations set `u.u_error` instead of returning errors, use `u.u_uid` and `u.u_flags` for authorization/name lookup behavior, and call volume/FSDB helpers according to the declared VFS method. State is mostly transient per-vproc, but it gates persistent cache mutations through FSDB, volume locks, and RVM recovery boundaries in implementation files. Dependencies include LWP, RVM, `venusioctl.h`, `vice.h`, `fso_cachefile.h`, Venus private globals, and local list abstractions.

Integration risks are high because `vproc` is a shared cross-cutting ABI between worker dispatch, vnode methods, pioctl handling, repair, and kernel message conversion. Changes to `uarea`, `venus_cnode`, `VA_IGNORE_*`, or method signatures can break many call paths. Test signals should include kernel upcall smoke tests, pathname and mount-point behavior, pioctl compatibility, interrupted worker requests, retry-loop behavior, and cache consistency after `k_Purge`/`k_Replace`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc_pathname.cc -->
# sources/distributed-fs/coda/coda-src/venus/vproc_pathname.cc

This file implements Venus pathname expansion and validation. `vproc::namev` walks a path relative to `u.u_cdir`, resolving components through `vget`, `lookup`, and `readlink`, then returns a `venus_cnode` for the final object. It accepts lookup flags in `u.u_flags`, handles `FOLLOW_SYMLINKS`, rejects `..` traversal out of the Venus root, and caps symlink expansion with `CODA_MAXSYMLINK`. Absolute symlinks under `venusRoot` are rewritten to Venus-relative paths and restart at `rootfid`; absolute symlinks outside Venus return `ENOENT`; relative symlinks replace the current working path while keeping the current parent.

`GetComponent` and `SkipSlashes` are small parser helpers over mutable path pointers. `vproc::GetPath` reconstructs a full or volume-relative path by walking parent fids upward through FSDB, using `dir_LookupByFid` for reverse component lookup, crossing mount links via `u.mtpoint`, and falling back to `<volname>` when a full mount path cannot be identified. `expansion` recognizes terminal `@cpu` and `@sys` suffixes, and `verifyname` rejects special names, conflict names, and expansion names according to `NAME_NO_DOTS`, `NAME_NO_CONFLICT`, and `NAME_NO_EXPANSION`.

The primary control-flow pattern is a retry-capable VFS loop inside `GetPath`: each step calls `Begin_VFS`, `FSDB->Get`, optional directory reverse lookup, `FSDB->Put`, and `End_VFS(&retry_call)`. `namev` is sequential and uses the vproc's implicit error state to stop on lookup failures, non-directory intermediate objects, symlink loops, or overlong rewritten paths.

State and persistence are limited to `uarea` fields and cache object references, but the routines depend on cached status/data and volume mount metadata. Integration points are FSDB, VDB/volume roots, `venusRoot`, `rootfid`, `namectxt`, and the VFS methods in `vproc_vfscalls.cc`. Risks include mutable fixed-size buffers, path truncation/`strcpy` assumptions after explicit length checks, stale mount metadata during reverse lookup, and subtle semantics around `FOLLOW_SYMLINKS`. Useful tests cover relative and absolute symlinks, symlink loops, root `..`, `@sys`/`@cpu` rejection, conflict-name rejection, mounted volumes, and long-path failure boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc_pathname.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc_pioctl.cc -->
# sources/distributed-fs/coda/coda-src/venus/vproc_pioctl.cc

`vproc_pioctl.cc` implements `vproc::do_ioctl`, the Venus pioctl dispatcher reached from `vproc::ioctl` and ultimately from kernel `CODA_IOCTL` upcalls. The dispatcher partitions commands into object-scoped, inconsistent-object-aware object commands, volume-scoped commands, and filesystem-scoped commands. It converts `ViceIoctl` input/output buffers into ACL operations, mount-point management, repair operations, token management, cache/statistics controls, disconnection controls, and hoard database requests.

Important object APIs include `_VIOCSETAL`, `_VIOCGETAL`, `_VIOCFLUSH`, `_VIOCPREFETCH`, mount point add/delete/stat, `_VIOC_GETPFID`, and `_VIOC_SETVV`. These paths use `Begin_VFS`, `FSDB->Get`, object type and permission checks, lock promotion, FSDB release, kernel purges, and RVM recovery bounds. Inconsistent-object commands such as `_VIOC_ENABLEREPAIR`, `_VIOC_COLLAPSEOBJECT`, `_VIOC_REPAIR`, `_VIOC_FLUSHASR`, and `_VIOC_GETFID` deliberately allow `EINCONS` object access and interact with local repair, fake directories, replicated volumes, version vectors, and realm names.

Volume-scoped handlers obtain a `volent` from `VDB`, enter observing or mutating volume mode, and invoke volume APIs for status, server locations, cache flushing, server statistics, CML checkpoint/purge, write-disconnect, ASR, sync-cache, staging redirection, and repair commands. Filesystem-scoped handlers manage tokens through `REALMDB` and users, probe servers, invalidate callbacks/mount points, toggle debug logging, report Venus stats, flush caches, manipulate HDB state through `HDBD_Request`, resolve paths through `GetPath`, truncate RVM logs, force disconnect/reconnect, and adjust red/yellow cache limits.

State changes span persistent cache state, RVM recovery, CMLs, repair metadata, user tokens, server connections, temp files under `/tmp`, and kernel minicache purges. Dependencies include FSDB, VDB, realm/user/auth layers, RPC2, repair/reintegration classes, HDB, lookaside cache, and worker early-return behavior for prefetch pioctls. Risks concentrate around packed ioctl buffer layouts, short `out_size`, alignment casts into `data->out`, partial validation of variable-length input, temp-file ownership, and lock/retry correctness. Test signals should exercise all pioctl scopes, malformed sizes, replicated versus non-replicated volumes, repair begin/end/check commands, token set/get/unlog, prefetch early return, and cache purges after mount or repair mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc_pioctl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc_vfscalls.cc -->
# sources/distributed-fs/coda/coda-src/venus/vproc_vfscalls.cc

This file implements the main Venus VFS operation surface declared in `vproc.h`. It maps Coda kernel operations onto FSDB object operations while enforcing directory/file type rules, Coda ACL rights, cache-data availability, volume concurrency, repair/inconsistency behavior, and kernel minicache invalidation. The common template is argument validation, `Begin_VFS`, object acquisition via `FSDB->Get`, semantic and protection checks, an `fsobj` method call, cleanup with `FSDB->Put`, then `End_VFS(&retry_call)`.

Read-only or metadata operations include `root`, `statfs`, `vget`, `getattr`, `access`, `lookup`, `readlink`, `fsync`, and VASTRO access-intent reads/mmap. Mutating operations include `open` with write/truncate handling, `close`, `setattr`, `create`, `remove`, `link`, `rename`, `mkdir`, `rmdir`, `symlink`, and VASTRO write tracking. The file uses `verifyname` for component validity, `FTTOVT` for Coda vnode type conversion, and fake vnode/symlink behavior for inconsistent objects so repair state can be surfaced to userspace.

Control flow has several special cases. `vget` and `_VIOCPREFETCH`-like data fetches can return early to workers. `getattr` and `readlink` fabricate attributes or link text for inconsistent objects. `rename` carefully orders parent and child lock promotion, rejects mount-point/root renames, prevents target-descendant loops, and fetches data before dirtying objects to avoid unreachable dirty cache objects. `setattr` fetches data for non-zero truncate or reachable-volume dirtying hazards. `link` forbids cross-volume and cross-directory hardlinks.

State and persistence behavior is broad: operations modify FSDB entries, cache container files, CML state, RVM metadata, kernel minicache entries, active segment tracking for VASTRO, and volume enter/exit state. Dependencies include FSDB, VDB, local repair state, realms, workers, HDB, and `k_Purge`. Risks include lock-order violations explicitly noted by comments, fixed error remapping of `EINCONS`, assumptions about cached data before mutations, and compatibility with historical kernel flag semantics. Tests should cover all VFS ops under connected, disconnected, conflicting, mounted, and interrupted conditions; hardlink/rename corner cases; access-intent notifications; and recovery after retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vproc_vfscalls.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vsg.cc -->
# sources/distributed-fs/coda/coda-src/venus/vsg.cc

`vsg.cc` implements the Venus Volume Storage Group database. A `vsgent` represents a set of replica server addresses for a realm, tracks the number and highest index of populated hosts, and owns a list of multicast group connection entries (`mgrpent`) used by users to communicate with replicated servers. `vsgdb` is the global database of `vsgent` objects, exposed through `VSGDB` and initialized by `VSGDBInit`.

`vsgent::GetMgrp` is the core API. It first searches existing `mgrpent` entries for the same uid and reuses an idle one. If the user already has `MAXMGRPSPERUSER` active groups for this VSG, it waits via `Mgrp_Wait` unless the current vproc has been interrupted. Otherwise it obtains the realm and user, calls `userent::Connect` to form a new RPC2 mgroup handle, constructs a `mgrpent`, adds it to the VSG list, gets a reference, calls `GetHostSet`, and configures the RPC2 multicast info field. `KillMgrps`, `KillUserMgrps`, and `KillMgrpMember` tear down all, per-user, or per-server member state.

`vsgdb::GetVSG` searches by realm id and exact host-array equality, returns a referenced existing entry, or creates and links a new one. State is in-memory reference-counted list state, but it directly controls live RPC2/mgroup communication and therefore affects replicated-volume operations. Dependencies include `mgrp`, `user`, `comm`, `realmdb`, list helpers, and the vproc interruption path.

Risks include non-atomic "InUse" checks if true multithreading is introduced, fairness/starvation around the fixed per-user mgroup cap, exact host-array matching that treats host order as identity, and complex lifetime interactions between `mgrpent::Kill`, list removal, and reference counts. Test signals include repeated concurrent `GetMgrp` calls for the same uid, cap/wait behavior, interrupted waits, realm-specific host sets, server-member kill propagation, user logout cleanup, and debug allocation/deallocation accounting under `VENUSDEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vsg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vsg.h -->
# sources/distributed-fs/coda/coda-src/venus/vsg.h

`vsg.h` declares the Volume Storage Group types used by Venus replicated-volume communication. `class vsgent` privately inherits `RefCountedObject`, is created and owned by `vsgdb`, and is also a friend of `mgrpent` and `Mgrp_Wait` so those components can coordinate connection lifetime and waits. The type stores `nhosts`, `max_vsg`, a fixed `hosts[VSG_MEMBERS]` array, a list of `mgrpent` entries, the owning `RealmId`, and a list hook linking all VSGs.

The public API exposes `Put`, `GetMgrp`, `KillMgrps`, `KillUserMgrps`, `KillMgrpMember`, host count and max-index accessors, `GetHosts`, and `print`. `CmpHosts` compares the full fixed host array with `memcmp`, so callers must keep array ordering and zero-fill conventions stable. `class vsgdb` stores all VSG entries, provides `GetVSG` for lookup/create by host array and realm, provides `KillUserMgrps` for global per-user cleanup, and prints state.

This header is a small but important integration contract between replicated volumes, user authentication, RPC2 mgroup management, and Venus diagnostics. State is in-memory and reference-counted, but instances hold live communication resources through `mgrpent` lists. The exported global `VSGDB` and `VSGDBInit` make initialization order significant for any code that may resolve replicated server groups.

Risks include private inheritance hiding generic refcount operations except through friend classes and `Put`, dependence on `dllist_head` intrusive list discipline, and exact structural host comparison. Any change to `VSG_MEMBERS`, realm identity, or list ownership affects `vsg.cc`, `mgrp`, and replicated volume code. Test signals should check initialization, duplicate `GetVSG` reuse, reference release and destructor cleanup, host copy semantics, per-user mgroup removal, and print output for live diagnostic commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vutil.cc -->
# sources/distributed-fs/coda/coda-src/venus/vutil.cc

This file builds the `vutil` command-line utility used to control a running Venus process. It reads Venus configuration, locates the cache directory, pid file, run-control file, log file, and error log, writes textual control commands, signals Venus, and waits for Venus to consume the control file. Supported commands are shutdown, debug level changes, statistic reset, statistic dump, and log rotation.

Important routines are `usage`, `logrotate`, and `main`. `logrotate` rotates a path through suffixes `.0` through `.9` using `rename`. `main` parses options after stripping one or two leading dashes, loads `venus.conf` through `codaconf_init`, resolves relative `pid_file` and `run_control_file` under `cachedir`, reads the Venus pid, and for each command writes a control string such as `SWAPLOGS`, `DEBUG <venus> <rpc2> <lwp>`, `STATSINIT`, or `STATS`. For shutdown it sends `SIGTERM` directly. For other commands it writes the control file, sends `SIGHUP`, then polls up to 60 seconds for Venus to unlink the control file.

State and persistence are filesystem-based: pid file, control file, rotated logs, and configured log paths. There is no shared memory or RPC path; Venus command handling is signaled through files and Unix signals. Dependencies include `codaconf`, Venus default path constants, standard signal/file APIs, and `venus.private.h`.

Risks include race windows around pid reuse, control-file overwrite if multiple `vutil` instances run, log rotation without fsync or locking, memory allocated for resolved relative paths and intentionally retained for process lifetime, and `strtoul` parsing that uses a shared `errno` pattern. Tests should cover command parsing aliases, relative and absolute config paths, invalid pid safety, log rotation ordering, Venus non-response timeout cleanup, failed `SIGHUP`, and shutdown refusing pid values `<= 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/vutil.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/worker.cc -->
# sources/distributed-fs/coda/coda-src/venus/worker.cc

`worker.cc` implements the Venus worker subsystem that connects the kernel Coda interface to the `vproc` VFS methods. It manages the kernel/device mux fd, message pools, worker LWP creation, request dispatch, mount/unmount, downcalls, interrupts, and per-op marshalling between `union inputArgs` and `union outputArgs`.

The top-level flow starts with `WorkerInit`, which sets worker limits, opens the kernel device or Cygwin IPC socket, checks kernel module version compatibility, purges kernel caches, initializes counters, and registers `WorkerMux` with the message mux. `WorkerMux` reads an upcall using `ReadUpcallMsg`; `DispatchWorker` handles `CODA_SIGNAL` interrupts, limits `_VIOCPREFETCH` concurrency, finds or creates an idle worker, or queues the message. Each `worker::main` loop calls `AwaitRequest`, initializes `uarea`, switches on the kernel opcode, invokes the appropriate `op_coda_*` inline wrapper, stores `u.u_error` in the output header, and calls `Resign`/`Return`.

Important support APIs include `k_Purge` overloads for whole-cache, fid, and user invalidation; `k_Replace` for minicache fid replacement and 9p fid-map updates; `VFSMount` and `VFSUnmount` for platform-specific mount lifecycle; `WorkerCloseMuxfd`; `GetWorkerIdleTime`; and diagnostic printing. Open operations support returning device/inode, file descriptors, or cache paths depending on kernel capability. Access intent operations require kernel version 5 and drive VASTRO read/write/mmap segment tracking.

State spans static worker counts, queues (`FreeMsgs`, `QueuedMsgs`, `ActiveMsgs`), per-worker `msg`, `opcode`, `returned`, `interrupted`, `StoreFid`, kernel module version, mount state, and OS mount tables. Risks include queue/list correctness, partial write handling, signal races, worker-count comments noting missing locks, open-interrupt cleanup via synthetic close, platform mount behavior, and packed offset fields in kernel message structs. Test signals include kernel version negotiation, dispatch saturation, prefetch queue limits, signal interruption of active and queued calls, each opcode wrapper, `CODA_UNLOADKERNEL`, access intents, purge/replace downcalls, and mount failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/worker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/worker.h -->
# sources/distributed-fs/coda/coda-src/venus/worker.h

`worker.h` declares the Venus worker subsystem. It defines defaults for maximum workers and prefetchers, declares kernel message entry and worker types, and exports the kernel downcall/upcall and worker lifecycle functions used across Venus.

`class msgent` is an intrusive-list entry wrapping a `VC_MAXMSGSIZE` message buffer and a `return_fd`. It is shared across free, queued, and active message lists; friend declarations allow dispatch, kernel purge helpers, `fsobj`, `vproc`, and worker internals to access the buffer directly. `msg_iterator` iterates an arbitrary message list. `class worker` derives from `vproc`, adds static mux/queue/counter state, tracks whether a reply has already been returned, stores the active message, opcode, and `StoreFid`, and declares inline handlers for each Coda kernel opcode.

The worker public API consists of construction, `AwaitRequest`, `Resign`, `Return`, and `isReady`, while `main` is the overridden vproc entry point. The exported free functions include message lookup, kernel purge and replace downcalls, VFS mount/unmount, worker initialization, idle worker lookup, dispatch, mux callback, idle-time query, diagnostics, and kernel module version access.

State is mostly process-local but mediates all kernel/Venus communication. Integration points include `vproc.h`, `fso.h`, `vice.h`, `venusioctl.h`, kernel Coda message structures, and FSDB operations reached from opcode handlers. Risks include broad friend access, intrusive list lifetime, static global state initialized by `WorkerInit`, and ABI sensitivity to kernel message layouts. Tests should verify worker initialization under configured limits, message pool reuse, dispatch and queueing, downcall helper behavior when not ready, all opcode handler marshalling, prefetch limits, and clean close of mux fd during unmount or shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/worker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/Makefile.am -->
# sources/distributed-fs/coda/coda-src/vice/Makefile.am

This Automake file defines the build for the Vice server directory when `BUILD_SERVER` is enabled. It declares a private `libviceerror.la` library, installs/links the `codasrv` and `printvrdb` programs, and distributes the `codasrv.8` and `servers.5` manpages plus `server.conf.ex`.

The main source group is `codasrv_SOURCES`, which includes server entry and RPC handling files (`srv.cc`, `srvproc.cc`, `srvproc2.cc`, `codaproc*.cc`), client tracking (`clientproc.cc`), callback handling (`vicecb.cc`), server monitoring (`smon.cc`), cop pending logic, and private headers. `libviceerror_la_SOURCES` isolates `ViceErrorMsg.c`, allowing error formatting to be linked into `codasrv`. `printvrdb_SOURCES` is the smaller VRDB diagnostic program.

`AM_CPPFLAGS` wires the server to generated and source include directories for base, kernel dependencies, utilities, vicedep, directory, ACL/auth, partition, volume, lookaside cache, repair, and resolution code. `codasrv_LDADD` establishes link order across vicedep, volutil, resolution, repair I/O, volume, LKA, VV, auth, partition, AL, directory, util, rwcdb/base, RPC2/RVM libraries, and `LIBKVM`. `printvrdb` links only util and base.

State and persistence here are build-system state rather than runtime state, but the file controls whether server binaries and config/manpage artifacts are produced. Risks include conditional definitions hiding required artifacts when `BUILD_SERVER` is off, strict link-order dependencies among legacy libraries, and missing generated headers from `top_builddir`. Test signals are `autoreconf`/Automake generation, `make V=1` for `codasrv` and `printvrdb`, dependency tracking after touching `ViceErrorMsg.c` or `clientproc.cc`, and install/distcheck behavior with and without `BUILD_SERVER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/ViceErrorMsg.c -->
# sources/distributed-fs/coda/coda-src/vice/ViceErrorMsg.c

`ViceErrorMsg.c` provides one small compatibility function, `ViceErrorMsg`, that converts Vice, RPC2, and Unix error codes into human-readable strings for server logging and diagnostics. Negative error codes are treated as RPC2 errors and delegated to `RPC2_ErrorMsg`. Non-negative values are matched against selected Vice volume and consistency errors, with unknown values falling back to `strerror`.

The explicit mappings include success, volume salvage required, bad vnode number, volume-not-online, volume-exists, no service, offline, already-online, and `EINCONS` as "Inconsistent Object". It depends on RPC2 headers for negative RPC error reporting and on `inconsist.h` for the Coda inconsistency error code. It returns `char *` for historical compatibility, although many returned strings are string literals or library-owned buffers.

Control flow is simple and side-effect free. There is no persistent state. Integration points include server files that log callback/bind failures and any code path that reports Vice or RPC errors to administrators. In this subset, `clientproc.cc` uses it when callback binding or callback checks fail.

Risks are mostly semantic: because unknown positive values use `strerror`, a Vice-specific positive error not listed here may be misreported as an unrelated errno string. The return type allows callers to assume mutability even though literals must not be modified. Thread-safety follows the behavior of `strerror` and `RPC2_ErrorMsg` on the target platform. Test signals include all explicit mappings, a negative RPC2 code, an ordinary errno such as `EPIPE`, and an unmapped positive Vice-like value to confirm fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/ViceErrorMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/clientproc.cc -->
# sources/distributed-fs/coda/coda-src/vice/clientproc.cc

`clientproc.cc` maintains Vice file-server client state. It builds and deletes `ClientEntry` objects for RPC2 connections, tracks workstations in a fixed `hostTable`, manages callback connections back to Venus clients, cleans up dead hosts, prints active clients, maps security levels to names, resolves authenticated user ids and CPS groups, and reports workstation activity counts.

`CLIENT_Build` authenticates or coerces the user name, allocates a `ClientEntry`, stores it in the RPC2 private pointer, initializes list and timestamp/security fields, links it to a `HostTable` through `client_GetVenusId`, resolves user identity/CPS with `client_SetUserName`, and increments `CurrentConnections`. `CLIENT_Delete` unlinks a client, clears the RPC2 private pointer, optionally delays unbind if an operation is active (`LastOp`), unbinds, frees CPS, and releases memory. `CLIENT_InitHostTable` initializes locks and client lists for all host slots.

`client_GetVenusId` maps an RPC handle to host/port using `RPC2_GetPeerInfo`, finds an existing host entry or evicts the oldest entry with `CLIENT_CleanUpHost`, initializes host identity, and links the client under the host lock. `CLIENT_MakeCallBackConn` creates an RPC2 binding to the client's callback subsystem, stores it in the host entry, sends a gratuitous callback, and cleans up on binding failure. `CLIENT_CallBackCheck` periodically probes idle callback connections and deletes stale clients that never established callbacks. `CLIENT_CleanUpHost` removes clients, deletes callback state, unbinds, and clears host address/port.

State is in-memory server state: host locks, callback handles, per-client RPC handles, CPS, security level, timestamps, and global connection counts. Dependencies include RPC2, callback RPC stubs, AL/PRS authentication and group lookup, Vice private server globals, lock/list utilities, and `ViceErrorMsg`. Risks include fixed host-table eviction, lock ordering with `CLIENT_Delete`, delayed unbind lifetime, callback failures tearing down all clients for a host, and reliance on RPC2 private pointer discipline. Test signals include authenticated and unauthenticated binds, stale private pointer cleanup, host-table reuse/eviction, callback bind failure, periodic callback cleanup, delayed delete during active calls, CPS fallback to `AnyUser`, and work-stat counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vice/clientproc.cc -->
