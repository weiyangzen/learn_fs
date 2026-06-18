# subset-b-007011 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/monitor.h -->
# sources/distributed-fs/coda/coda-src/vcodacon/monitor.h

## Purpose
This header declares the `monitor` class used by the FLTK-based `vcodacon` visual console to watch the Coda console/mariner stream on the codacon port. It is a small UI-facing connection wrapper around an `Inet` endpoint with counters and display sizing state.

## Important APIs, Types, and Functions
`CODACONPORT` is fixed at `2430` and `LINESIZE` at `1024`. `monitor::Start()` establishes or starts monitoring the stream, `NextLine()` advances the display by one line, `ForceClose()` closes the active connection, and `AgeActColor()` decays activity highlighting. `SetBrowserSize(int)` only accepts sizes above ten. The global `NextLine(void)` exposes line advancement outside the class.

## Control Flow
The constructor initializes activity color, browser size, and counters for stores, reintegrations, and disconnected filesystem events. Runtime behavior is implemented elsewhere: callers create a monitor, start it, and drive line consumption through `NextLine`.

## State and Persistence Behavior
All state is transient UI state. The class keeps an `Inet conn`, active color, browser row count, and three event counters. It does not persist anything or mutate Coda state.

## Dependencies and Integration Points
It depends on `config.h` and `Inet.h` and integrates with the vcodacon GUI and the codacon network stream.

## Risks and Test Signals
Risks are connection lifecycle mismatches, stale UI counters, and hidden assumptions around the hard-coded port and line size. Test signals are successful connect/close cycles, line rendering under long messages, and activity color aging after store/reintegration/disconnected events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/util.cc -->
# sources/distributed-fs/coda/coda-src/vcodacon/util.cc

## Purpose
This file implements utility callbacks for the `vcodacon` GUI: initialization, realm discovery, Coda login/logout commands, token display, and realm path validation.

## Important APIs, Types, and Functions
`XferLabel[3]` mirrors transfer labels for GUI progress slots. Realm state is held in `realmlist`, `nlist`, and `nrealm`. `lookup_realm()` searches the list, `add_realm()` grows it, and `update_realmlist()` scans `/coda` for non-hidden realm names while rejecting `NOT_REALLY_CODA`. `do_clog()` runs `clog -pipe`, writes the password to stdin, and hides the login window. `do_cunlog()` runs `cunlog @realm`. `menu_clog()`, `menu_cunlog()`, and `menu_ctokens()` populate and show FLTK dialogs. `do_findRealm()` stats `/coda/<realm>`. `MainInit()` hides progress widgets and seeds the realm list from `venus.conf`.

## Control Flow
Menu callbacks refresh realm choices from `/coda`, populate FLTK widgets, and show dialogs. Login/logout callbacks validate GUI selections, construct command lines, invoke subprocesses through `popen`, report failures via `fl_alert`, and clear sensitive UI state on success.

## State and Persistence Behavior
The file only stores process-local GUI state and a heap-allocated realm list. Persistent Coda authentication tokens are changed indirectly by external `clog` and `cunlog` commands.

## Dependencies and Integration Points
It depends on generated GUI globals from `vcodacon.h`, FLTK alerts/widgets, `/coda`, `venus.conf` via `codaconf`, and command-line tools `clog`, `cunlog`, and `ctokens`.

## Risks and Test Signals
Risks include command injection through usernames or realm names, leaked realm strings, early return from `update_realmlist()` without `closedir`, fixed-size command buffers, and password handling through a pipe. Tests should cover empty user/realm selections, missing `/coda`, seeded `venus.conf` realms, malformed realm names, failed subprocesses, and token list refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/util.h -->
# sources/distributed-fs/coda/coda-src/vcodacon/util.h

## Purpose
This header exposes the `vcodacon` utility callbacks implemented in `util.cc` to the GUI code.

## Important APIs, Types, and Functions
It declares the shared `XferLabel[3]` array plus `MainInit`, `do_clog`, `do_cunlog`, `menu_clog`, `menu_ctokens`, `menu_cunlog`, and `do_findRealm`.

## Control Flow
There is no executable flow in the header. It defines the callback and helper surface the GUI can bind to menu actions and startup initialization.

## State and Persistence Behavior
Only the external transfer-label pointer array is declared here. Authentication and token changes happen indirectly through the implementation.

## Dependencies and Integration Points
The header is included by the FLTK GUI source and any code that needs realm probing or Coda authentication menu callbacks.

## Risks and Test Signals
The main risks are untyped global callback coupling and no include guard. Compile tests should verify this header can be included in the generated GUI translation unit, and GUI smoke tests should invoke each declared callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vcodacon/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/9pfs.cc -->
# sources/distributed-fs/coda/coda-src/venus/9pfs.cc

## Purpose
This file implements the Venus 9P server. It parses 9P2000, 9P2000.u, and 9P2000.L messages from a `mariner` connection, maps fids to Venus cnodes and attachments, invokes Venus VFS-style operations, and serializes protocol responses.

## Important APIs, Types, and Functions
Static pack/unpack helpers encode little-endian integers, strings, qids, legacy stats, dotl stats, statfs data, and directory entries with strict buffer accounting. `attachment` stores a mount root, user/aname strings, uid, and refcount. `fidmap` maps a client fid to a cnode, open flags, and root attachment. `plan9server` implements request dispatch plus handlers for version, attach, walk, open/create/read/write/clunk/remove/stat/wstat and dotl operations including getattr, setattr, lopen, lcreate, symlink, mkdir, readdir, readlink, statfs, fsync, unlinkat, link, rename, and renameat. Unsupported mknod/xattr/locking handlers consume request fields and return `ENOTSUP`.

## Control Flow
`main_loop()` processes an optional initial magic buffer, then repeatedly reads a 9P header and calls `handle_request()`. `handle_request()` validates message size, reads the remainder, initializes the mariner user context, and dispatches by opcode. Most handlers unpack request fields, look up fids, set `conn->u.u_uid` from the attachment, call a Venus operation, translate `conn->u.u_error` into protocol errors, and pack a response into the fixed server buffer.

## State and Persistence Behavior
Persistent filesystem changes are delegated to Venus operations: create, remove, rename, link, mkdir, rmdir, symlink, setattr, write, and local cache file IO. The file's own state is transient protocol state: negotiated `max_msize`, protocol variant, fid list, open flags, and attachment refcounts. `del_fid()` closes open cnodes and frees attachment user strings when the last fid disappears. `fidmap_replace_cfid()` updates active fids when temporary local Venus Fids are replaced by server Fids.

## Dependencies and Integration Points
It depends on `mariner`, `fsobj`/`FSDB`, Venus cnodes, `vproc`-style file operations, directory enumeration, `VenusRetStr`, `SpookyHash` for qid paths, and worker downcalls that repair fid mappings. `mariner.cc` enables this server after detecting a 9P version request, and `worker.cc` calls `fidmap_replace_cfid`.

## Risks and Test Signals
Risks include memory leaks on error paths, incorrect dotl response opcodes, use-after-yield when operations drop fids, missing write-back semantics after raw `pwrite`, hard-coded `P9_BUFSIZE`, incomplete fsync, unsupported flags, and directory offset handling. Tests should mount through 9P in all three protocol variants, exercise fid reuse, clunk/remove semantics, symlink/hardlink/rename paths, large messages, partial readdir offsets, disconnected writes, temporary Fid replacement, and unsupported dotl operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/9pfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/9pfs.h -->
# sources/distributed-fs/coda/coda-src/venus/9pfs.h

## Purpose
This header defines the Venus 9P protocol constants, wire structs, and `plan9server` class interface used by `9pfs.cc`.

## Important APIs, Types, and Functions
It lists legacy and dotl message opcodes, protocol flags, special tag/fid values, permission bits, qid types, open flags, dotl open/unlink flags, getattr/setattr masks, and `V9FS_MAGIC`. `plan9_qid`, `plan9_stat`, `plan9_stat_dotl`, and `plan9_statfs` model wire payloads. `plan9server` owns the mariner connection, fid list, packet buffer, negotiated message size, protocol variant, all receive handlers, fid helpers, stat/read helpers, public `main_loop`, `pack_dirent`, and `fidmap_replace_cfid`.

## Control Flow
The header has no executable flow but documents the full dispatcher surface. The handler declarations show which requests can yield outside transactions and which unsupported operations are explicit.

## State and Persistence Behavior
Class state is per-client transient protocol state. Persistent effects occur only through handler implementations. Constants such as qid and stat masks define how Venus state is exposed to clients.

## Dependencies and Integration Points
It includes C system types, `dlist`, and `mariner`; after C declarations it exposes C++ Venus integration. It is included by `9pfs.cc`, mariner code that creates a server, and worker code that updates fids.

## Risks and Test Signals
Risks are protocol drift against Linux 9p clients, macro arrays defined in a header causing duplicate definitions if included by multiple translation units, and inconsistent constants between header and handlers. Build tests should include all users; runtime tests should negotiate 9P2000, 9P2000.u, and 9P2000.L and verify stat/open flag encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/9pfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/Makefile.am -->
# sources/distributed-fs/coda/coda-src/venus/Makefile.am

## Purpose
This Automake input defines the Venus client build targets, installed man pages/config files, Venus source list, compiler include paths, and link dependencies.

## Important APIs, Types, and Functions
`sbin_PROGRAMS` conditionally includes `vutil` under `BUILD_CLIENT` and `venus` under `BUILD_VENUS`. `venus_SOURCES` enumerates the Venus implementation, including `archive.c`, `9pfs.cc`, and `SpookyV2.cc`. `AM_CPPFLAGS` defines `VENUS`, timing/debug macros, and include paths across base, kernel dependency, util, dir, auth, vv, lka, vol, and repair libraries. `venus_LDADD` links repair, lka, vv, codadir, venusdep, util, rwcdb, base, and RPC2/RVM dependencies.

## Control Flow
Build-time conditionals select installed programs and man/config data. Automake expands the source and library lists into generated Makefile rules.

## State and Persistence Behavior
No runtime state is managed. Build configuration determines whether Venus, vutil, `venus.conf.ex`, and `realms` are installed.

## Dependencies and Integration Points
The file integrates with top-level configure options `BUILD_CLIENT` and `BUILD_VENUS`, generated build directories, and libraries used by the Venus daemon.

## Risks and Test Signals
Risks are missing source additions, stale include paths, and link-order regressions. Test signals are successful `make` with client-only, Venus-enabled, and both-disabled configurations, plus distribution checks ensuring installed config/man files are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/SpookyV2.cc -->
# sources/distributed-fs/coda/coda-src/venus/SpookyV2.cc

## Purpose
This file implements Bob Jenkins' SpookyHash V2 non-cryptographic hash for one-shot and incremental 128-bit hashing. Venus uses it in this subset to derive stable 9P qid path values from Venus Fids.

## Important APIs, Types, and Functions
`SpookyHash::Short()` handles messages shorter than the long-buffer threshold using 32-byte chunks and tail mixing. `Hash128()` chooses the short path for small inputs, otherwise mixes 96-byte blocks and finalizes a padded partial block. `Init()`, `Update()`, and `Final()` implement streaming hashing using `m_state`, `m_data`, `m_length`, and `m_remainder`.

## Control Flow
Short inputs go through `ShortMix` and `ShortEnd`; long inputs initialize twelve 64-bit lanes, repeatedly call `Mix`, pad the final block with the remainder length, and call `End`. Streaming updates stash short fragments until enough data exists, then mix full blocks and retain the tail for `Final`.

## State and Persistence Behavior
The hash object keeps only transient hash state. It does not persist data. Its output affects externally visible 9P qid identity; changing the implementation would change client inode identity expectations.

## Dependencies and Integration Points
It depends on `SpookyV2.h` and `memory.h`. In this tree, `9pfs.cc` uses `Hash64` for qid paths.

## Risks and Test Signals
Risks include endian differences, unaligned-read assumptions, tail handling regressions, and accidental use for security-sensitive hashing. Tests should compare one-shot and streaming results across fragment boundaries, zero-length input, lengths around 15/16/32/96/192 bytes, and known SpookyHash V2 vectors on the supported architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/SpookyV2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/SpookyV2.h -->
# sources/distributed-fs/coda/coda-src/venus/SpookyV2.h

## Purpose
This header declares and mostly defines the SpookyHash V2 class, including public one-shot hash APIs and inline mixing primitives.

## Important APIs, Types, and Functions
`Hash128`, `Hash64`, and `Hash32` are public one-shot hash functions. `Init`, `Update`, and `Final` provide incremental hashing. Inline helpers include `Rot64`, `Mix`, `EndPartial`, `End`, `ShortMix`, and `ShortEnd`. Private constants define twelve 64-bit state lanes, 96-byte blocks, a 192-byte short-buffer threshold, and the `0xdeadbeefdeadbeef` seed constant.

## Control Flow
Most mixing logic is inline in the header for performance. Public static wrappers seed and call `Hash128`, while streaming callers initialize state, feed fragments, and finalize without mutating the state further.

## State and Persistence Behavior
Instances store transient buffered input, hash state, total length, and remainder length. No persistent state is declared, but hash stability matters wherever output is stored or used as a wire identity.

## Dependencies and Integration Points
It provides portable integer typedefs for MSVC and standard `<stdint.h>` builds. `9pfs.cc` depends on `Hash64`.

## Risks and Test Signals
Risks are duplicate type definitions, architecture-dependent output on big endian systems, and the absence of include guards. Tests should compile on target compilers and validate deterministic vectors for 32-, 64-, and 128-bit outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/SpookyV2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/archive.c -->
# sources/distributed-fs/coda/coda-src/venus/archive.c

## Purpose
This file writes Coda repair/archive output in old tar, POSIX ustar, old portable cpio, and SVR4 newc cpio formats.

## Important APIs, Types, and Functions
The global `archive_type` defaults to `CPIO_NEWC`. `write_padding()` pads a stream to the selected alignment. `archive_write_entry()` emits one metadata record for regular files, directories, symlinks, and hardlinks, translating path names, mode bits, uid, nlink, mtime, file size, and link targets into the selected archive format. `archive_write_data()` copies a container file to the archive and pads it. `archive_write_trailer()` emits tar zero blocks or a cpio `TRAILER!!!` record and flushes the stream.

## Control Flow
Entry writing first strips a leading slash and calculates name length, then switches on `archive_type`. Tar paths build a 512-byte header and checksum. CPIO ODC writes octal text fields with overflow handling. CPIO newc writes fixed-width hexadecimal fields and 4-byte padding. File data is read in chunks and periodically yields to LWP scheduling.

## State and Persistence Behavior
The output archive is persistent. Source data is read from cache container files. The only module state is the selected archive format.

## Dependencies and Integration Points
It depends on libc IO, Coda assertions, LWP/IOMGR yielding, and `archive.h`. `vol_cml.cc` uses these functions to dump local modification logs or repair archives.

## Risks and Test Signals
Risks include path length limits, tar prefix boundary errors, uid/inode/time truncation, returning without closing the input fd on read/write errors, and assuming only regular/dir/symlink types. Tests should extract all supported formats with standard tools, cover long names, links, large files near format limits, and simulated ENOSPC/EIO failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/archive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/archive.h -->
# sources/distributed-fs/coda/coda-src/venus/archive.h

## Purpose
This header declares the Venus archive writer format constants, selected archive type, and public writer functions.

## Important APIs, Types, and Functions
Constants `TAR_TAR`, `TAR_USTAR`, `CPIO_ODC`, and `CPIO_NEWC` select the output format. `archive_type` is an extern global. `archive_write_entry`, `archive_write_data`, and `archive_write_trailer` form the archive-writing API.

## Control Flow
There is no runtime flow in the header. Callers set `archive_type`, emit entries and data in archive order, and finish with a trailer.

## State and Persistence Behavior
The header exposes mutable process-global archive format state. The implementation writes persistent archive files through `FILE *` streams.

## Dependencies and Integration Points
It depends on `<sys/types.h>` and `<stdio.h>` and is included by Venus CML/repair archive code.

## Risks and Test Signals
Risks are global format races and callers forgetting the trailer. Compile tests should include both C and C++ consumers, and integration tests should validate every format option configured by Venus startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/archive.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/binding.cc -->
# sources/distributed-fs/coda/coda-src/venus/binding.cc

## Purpose
This file implements the small `binding` object used as a generic association between a binder and bindee, with dlist handles for both sides and explicit reference counting.

## Important APIs, Types, and Functions
The constructor initializes `binder`, `bindee`, and `referenceCount` to zero and increments debug allocation counters. The destructor increments debug deallocation counters, logs a warning if the reference count is nonzero, and treats non-null endpoints as fatal. `print(int)` writes endpoint pointers and refcount to a file descriptor.

## Control Flow
Bindings are allocated empty, then other subsystems attach them to lists and set endpoints. Before deletion, owners must detach both handles, clear endpoints, and decrement references to zero.

## State and Persistence Behavior
State is in-memory only. Bindings connect runtime structures such as hoard database entries, modification log entries, and fsobjs.

## Dependencies and Integration Points
It includes `binding.h` and `venus.private.h` for logging and fatal error handling. `fso.h` uses `binding` in hoard and MLE linkage.

## Risks and Test Signals
Risks are dangling list links, double deletes, reference leaks, and fatal destructor checks during shutdown. Tests should attach/detach bindings through representative fsobj/hdb/mle paths and assert debug alloc/dealloc balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/binding.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/binding.h -->
# sources/distributed-fs/coda/coda-src/venus/binding.h

## Purpose
This header defines the generic `binding` class used to represent a two-sided association with list handles and explicit refcount management.

## Important APIs, Types, and Functions
`binding` contains `binder_handle`, `binder`, `bindee_handle`, `bindee`, and `referenceCount`. `IncrRefCount()` and `DecrRefCount()` manage references, with an assertion preventing underflow. Copy construction and assignment abort. `print` overloads write debug state.

## Control Flow
The class is a passive container. External owners manipulate handles and endpoint pointers, then call refcount methods as ownership changes.

## State and Persistence Behavior
Binding state is transient and not recoverable on its own. Persistent or recoverable semantics belong to the structures connected by the binding.

## Dependencies and Integration Points
It depends on `dlist.h` and Coda assertions. `fsobj` declares methods to attach/detach `binding` instances for hoard database and modification log relationships.

## Risks and Test Signals
Risks include unscoped public fields and manual lifecycle requirements. Tests should cover underflow assertions, copy prevention, print output, and subsystem-level cleanup before destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/binding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/comm.cc -->
# sources/distributed-fs/coda/coda-src/venus/comm.cc

## Purpose
This file implements Venus communication setup, server objects, RPC connection caching, server probing helpers, error translation, and test hooks for simulated disconnect/reconnect.

## Important APIs, Types, and Functions
`CommInit()` initializes unset RPC2/SFTP parameters, validates COP modes, initializes connection/server tables, activates SFTP, calls `RPC2_Init`, and starts the probe daemon. `srvent::GetConn()` reuses an idle `connent` or binds through `Connect()`. `PutConn()` releases references and deletes dying idle connections. `connent::CheckResult()` maps Vice/RPC errors to Unix-style errors and marks bad connections. Server functions include `FindServer`, `GetServer`, `PutServer`, `Reset`, `ServerError`, `ServerUp`, `GetLiveness`, and `GetBandwidth`. Probe helpers include `ProbeServers`, `DoProbes`, `MultiBind`, `MultiProbe`, and `HandleProbe`.

## Control Flow
Startup establishes global communication state. File/volume code asks a server for a connection; if an idle matching connection exists it is reused, otherwise `srvent::Connect()` serializes binding with `Xbinding`, asks the realm/user layer to authenticate, and installs a new `connent`. Probing collects eligible servers, binds in parallel with `probeslave` workers, then uses `MRPC_MakeMulti` for `ViceGetTime`.

## State and Persistence Behavior
State is process-local: server table, connection table, callback connection handles, liveness flags, bandwidth estimates, and queue counts. Persistent filesystem state is affected indirectly by RPCs made over these connections.

## Dependencies and Integration Points
It depends on RPC2/SFTP, Vice stubs, realm/user authentication, `VDB` volume events, mariner logging, vproc scheduling, and timing/stat macros from `comm.h`. It is initialized from Venus startup and used throughout fsobj and volume code.

## Risks and Test Signals
Risks include refcount leaks in iterators, stale down/up transitions, binding serialization races, missed reset after RPC errors, and fail hook global side effects. Tests should simulate server up/down/NAK/timeouts, forced binds, parallel probes, bandwidth changes, and connection reuse under concurrent vprocs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/comm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/comm.h -->
# sources/distributed-fs/coda/coda-src/venus/comm.h

## Purpose
This header declares the Venus communications subsystem: connection entries, server entries, probe workers, global tunables, exported communication functions, synchronization macros, and RPC statistics macros.

## Important APIs, Types, and Functions
`connent` represents one authenticated RPC2 connection for a server and uid, with `connid`, `CheckResult`, refcounting, and death marking. `srvent` represents a file server, callback connection, binding state, probe flags, bandwidth estimate, and connection factory. `probeslave` is a `vproc` worker for up probes, down probes, or forced binds. Constants define defaults for RPC retries/timeouts and SFTP windows. Functions cover initialization, server lookup, connection release, probing, multi-bind/probe, down-server reporting, bandwidth checks, and fail disconnect/reconnect.

## Control Flow
Macros `START_COMMSYNC` and `END_COMMSYNC` make lower-priority vprocs yield to higher-priority communication traffic. Timing/stat macros wrap uni- and multi-RPC calls, log packet statistics when enabled, and update operation counters.

## State and Persistence Behavior
The header exposes process-global communication tunables and `CommQueue`. No state is persisted, but these declarations govern all Venus RPC access to persistent Coda data.

## Dependencies and Integration Points
It depends on RPC2, SFTP, Vice interfaces, callback types, collection utilities, `fso`, `venusrecov`, `vproc`, and volume classes. It is included by most Venus components that perform file server RPCs.

## Risks and Test Signals
Risks are macro side effects, priority starvation, hidden friend coupling, and inconsistent timing builds. Tests should compile with and without `TIMING`, exercise priority synchronization, and verify public error mappings through representative Vice operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/comm_daemon.cc -->
# sources/distributed-fs/coda/coda-src/venus/comm_daemon.cc

## Purpose
This file implements the Venus probe daemon that periodically checks server liveness and communication quality.

## Important APIs, Types, and Functions
`PROD_Init()` adjusts the down-server probe interval relative to `T1Interval` and starts a `ProbeDaemon` vproc. `ProbeDaemon()` registers a periodic daemon signal and, on wakeup, calls `ServerProbe()` when up/down probe intervals expire and `CheckServerBW()` every communication check interval. `ServerProbe()` marks servers requiring probes, starts separate up/down `probeslave` workers, waits for completion, and updates last-probe times.

## Control Flow
The daemon sleeps on `probe_sync`, wakes through the generic daemon scheduler, checks elapsed logical time, and dispatches work. Server selection suppresses probes when RPC2 liveness data shows recent communication or when interval guards have not expired.

## State and Persistence Behavior
State is transient timing state: last up probe, last down probe, last communication check, and per-server `probeme` flags. It updates server liveness and bandwidth state, which then influences Venus connection behavior.

## Dependencies and Integration Points
It depends on `comm.h`, `venus.private.h`, `venusrecov.h`, `vproc`, the daemon scheduler, server iterators, RPC2 liveness, and `probeslave` workers.

## Risks and Test Signals
Risks include probe suppression errors, stale `probeme` flags, daemon wakeup failures, and poor behavior when intervals are zero or very low. Tests should force probes via pioctl, simulate recent liveness, verify separate up/down worker paths, and confirm bandwidth refreshes continue even when probes are suppressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/comm_daemon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/daemon.cc -->
# sources/distributed-fs/coda/coda-src/venus/daemon.cc

## Purpose
This file implements the generic Venus daemon scheduler and a helper class for simple periodic daemon vprocs.

## Important APIs, Types, and Functions
`DaemonInit()` initializes the timer list and schedules once-a-day logging. `RegisterDaemon()` inserts a timer element with interval and optional sync byte. `InitOneADay()` schedules the first daily task around midnight. `DispatchDaemons()` rescans expired timers, reinserts them, signals registered daemons, or performs daily log/rusage/malloc reporting. The private `Daemon` class wraps a `PROCBODY` function in a vproc. `FireAndForget()` creates a daemon and waits until it has registered.

## Control Flow
The scheduler stores each daemon as a timer element. When dispatch runs, every expired element is requeued for its next interval and its sync byte is signaled. `Daemon::main()` yields once, signals startup readiness, registers itself, then waits for sync events and runs the target function.

## State and Persistence Behavior
State is in-memory timer list metadata. Daily tasks write diagnostics to the Venus log but do not persist scheduler state.

## Dependencies and Integration Points
It depends on LWP timers, `vproc`, Venus logging, `RusagePrint`, and `MallocPrint`. `comm_daemon.cc` and realm code register daemon work through this scheduler.

## Risks and Test Signals
Risks include leaked timer metadata, drift from reinserting fixed intervals after delayed dispatch, missing synchronization for daemon startup, and daily scheduling edge cases around local time changes. Tests should register short-interval daemons, verify repeated signaling, run once-a-day logic across midnight/DST, and ensure `FireAndForget` does not return before registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/daemon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fidtest.cc -->
# sources/distributed-fs/coda/coda-src/venus/fidtest.cc

## Purpose
This small diagnostic program calls the Venus pioctl interface to print the Coda Fid, realm, and version vector for a path.

## Important APIs, Types, and Functions
`GetFid` mirrors the expected `VIOC_GETFID` output: `ViceFid`, `ViceVersionVector`, and realm string. `main()` prepares a `ViceIoctl`, calls `pioctl(argv[1], VIOC_GETFID, ...)`, prints `FID_(&out.fid)` and the realm, then prints version vector sites, store id, and flags.

## Control Flow
The program zeroes output storage, invokes pioctl on the first command-line argument, exits with failure on error, and prints fields on success.

## State and Persistence Behavior
It reads kernel/Venus state only and does not persist or mutate filesystem data.

## Dependencies and Integration Points
It depends on `venusioctl.h`, `vice.h`, `pioctl`, `FID_`, and the Venus kernel/user pioctl contract.

## Risks and Test Signals
Risks include no argc validation before `argv[1]`, legacy `void main`, and fixed output struct compatibility with the pioctl implementation. Tests should call it with a valid Coda path, a non-Coda path, no argument, and paths from multiple realms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fidtest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso.h -->
# sources/distributed-fs/coda/coda-src/venus/fso.h

## Purpose
This header specifies Venus' cached file-system object layer. It defines the recoverable FSDB cache database, individual `fsobj` records, cache state flags, status summaries, local/disconnected mutation APIs, object locking, and integration hooks for communication, volumes, hoarding, repair, and 9P.

## Important APIs, Types, and Functions
`fsdb` owns cache sizing, block/file accounting, hash table, freelist, priority queue, delete queue, open-for-write queue, cache statistics, and object allocation/reclamation. Public methods include `Find`, `Get`, `Put`, `Flush`, `TranslateFid`, callback break handling, user reset, priority reset, and stats/printing. `fsobj` stores Fids, component names, volume pointers, persistent Venus status, access rights, dirty/local/fetch flags, mount state, parent/child links, priority state, hoard/MLE bindings, data pointers, cache files, locks, and repair metadata. Its APIs span fetch/getattr/store/setattr, create/remove/link/rename/mkdir/rmdir/symlink, open/read/close/access/lookup/readdir/readlink/read-intent, directory package operations, disconnected/local mutation logging, repair operations, conflict handling, and cache reporting.

## Control Flow
Callers obtain objects through `FSDB->Get`/`Find`, operate through `fsobj` public CFS methods, and release with `Put`. Object methods coordinate cache validity, server reachability, dirty state, partial data, local mutation logs, and locks. Macros describe replacement, fetchability, garbage collection, and activity decisions used by implementations.

## State and Persistence Behavior
Many fields are recoverable through RVM-backed structures, while `/*T*/` marks transient runtime fields. FSDB persists cached object metadata, local/disconnected mutation state, cache allocation state, and dirty objects. File data lives in cache files or directory handles. The layer is central to Venus recovery and reintegration.

## Dependencies and Integration Points
It depends on Vice/RPC2 types, Coda directory utilities, LKA, hoard database, communication, realm DB, cache files, Venus recovery, vproc, volume classes, and `binding`. `9pfs.cc` is a friend so it can inspect cnodes through fsobjs.

## Risks and Test Signals
Risks include recoverable/transient field confusion, lock/refcount imbalance, dirty object loss, partial fetch holes, callback invalidation races, local/global conflict errors, and cache replacement of active objects. Tests should cover crash recovery, callback breaks, disconnected mutation/reintegration, mount points, partial file reads, cache pressure reclamation, repair operations, and 9P reads/writes through fsobjs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/venus/fso.h -->
