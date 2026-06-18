# subset-b-007810 Research

Grouped research for the requested OpenAFS Venus command utilities, Venus test helpers, and vfsck build file. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/afsio.c -->
# sources/distributed-fs/openafs/src/venus/afsio.c

## Purpose
`afsio.c` implements the `afsio` command, a clientless or client-assisted AFS file I/O tool built around `libafscp`. It supports locking, unlocking, reading, directory reading, writing, and appending by pathname or by explicit `volume.vnode.unique` FID, with optional cell/realm selection, clear or encrypted RX behavior, MD5 reporting, synthetic write data, overwrite control, and transfer-rate diagnostics.

## Important APIs, Types, And Functions
The command surface is registered in `main` with `cmd_CreateSyntax` for `lock`, `fidlock`, `unlock`, `fidunlock`, `read`, `fidread`, `readdir`, `fidreaddir`, `write`, `fidwrite`, `append`, and `fidappend`. Shared parsing is handled by `CmdProlog`, `common_parms`, `ScanFid`, `BreakUpPath`, `GetVenusFidByFid`, and `GetVenusFidByPath`. The main operations are `lockFile`, `readFile`, and `writeFile`. Transfer helpers include `time_elapsed`, `printDatarate`, `summarizeDatarate`, and `summarizeMD5`. `struct wbuf` forms a linked list of 64 KiB write buffers, up to a nominal 64 MiB staging window.

## Control Flow
Startup derives the program name, initializes error tables and pthread local state when needed, initializes `libafscp`, registers commands, dispatches through the OpenAFS command parser, and finalizes `libafscp`. `CmdProlog` inspects command name and parameters to set global flags such as FID mode, append mode, directory-read mode, verbosity, clear/encrypted behavior, force, read-lock, MD5, cell, realm, and alternate local auth user.

`lockFile` authenticates anonymously by default, optionally makes RX insecure, resolves a path or FID to an `afscp_venusfid`, polls status while a conflicting lock exists, waits for callbacks if requested, then invokes `afscp_Lock`. `readFile` resolves and type-checks the object, fetches status for length, loops with `afscp_PRead` into a 64 KiB buffer, writes to stdout, updates MD5 and rate counters, and reports final metrics. `writeFile` resolves or creates the target, rejects accidental overwrites unless `-force` or append semantics allow them, buffers stdin or synthesized offset patterns, writes each buffer through `afscp_PWrite`, and frees all staged buffers and FID references.

## State And Persistence
Most state is process-global command state: selected cell, auth mode, append/FID/read-directory flags, rate counters, MD5 context, and timing snapshots. Persistent effects occur on AFS files: locks are modified on fileserver state, reads stream file or directory data to stdout, writes create or overwrite AFS files, append extends existing files, and `-as-user` changes the local authorization context used by `libafscp`. No local configuration files are written.

## Dependencies And Integration Points
The file depends on `libafscp`, RX/auth/VLDB types, OpenAFS command parsing, `hcrypto` MD5, portable roken APIs, and Windows pioctl/path support under `AFS_NT40_ENV`. It integrates directly with fileservers through `libafscp` rather than relying solely on cache-manager pioctls, which is why the FID modes can work on hosts without an AFS client.

## Risks And Test Signals
Risk areas include global mutable command flags reused across subcommands, duplicated statements in argument and synth-length handling, fixed 64 MiB write staging before transfer, partial-read/write error mapping to ad hoc negative codes, FID volume rewriting when forcing RW volume lookup, stdout/stdin binary mode handling on Windows, and unbounded wait/retry behavior when locks contend. Useful test signals are successful path and FID read/write/append, directory read rejection for files and file read rejection for directories, `-force` overwrite behavior, `-synthesize` large writes, MD5 parity with external checksums, lock/unlock against an active fileserver, clear/encrypted RX toggles, and operation without a local cache manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/afsio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/cacheout.c -->
# sources/distributed-fs/openafs/src/venus/cacheout.c

## Purpose
`cacheout.c` implements a cell-wide utility for invalidating fileserver ACL/CPS cache entries for selected AFS user IDs and/or client IP addresses. It discovers fileservers through the VLDB, establishes RX connections to each fileserver, and calls `RXAFS_FlushCPS`. It also exposes a `listservers` command for the same VLDB-derived server list.

## Important APIs, Types, And Functions
`ListServers` queries `ubik_VL_GetAddrs` and, for multihomed entries, `ubik_VL_GetAddrsU`, filling the fixed `server_id[256]` array in network byte order. `InvalidateCache` parses `-id` and `-ip` lists into `ViceIds` and `IPAddrs`, then loops over discovered servers and calls `RXAFS_FlushCPS`. `GetServerList` prints resolved server names. `MyBeforeProc` initializes RX, opens client or server configuration, selects null/token/localauth security, initializes VLDB ubik connections, and stores the global `client`, `sc`, and `scindex` used by command handlers.

## Control Flow
`main` installs `MyBeforeProc` as the command prelude, registers the default invalidation syntax plus alias `ic`, registers `listservers` plus alias `ls`, dispatches, finalizes RX, and exits with the command result. The prelude chooses `/usr/vice/etc` or server configuration depending on `-localauth`, changes security level for `-encrypt`, reads VLDB server endpoints for the selected cell, optionally obtains RXKAD credentials, and creates a ubik client.

The invalidation command first refreshes the server list, rejects calls with neither user IDs nor IP addresses, converts up to 255 IDs and IPs, and sends the flush RPC to each fileserver. Individual server connection or RPC failures are reported as informational and summarized by a nonzero return, because the VLDB may contain down or non-fileserver hosts.

## State And Persistence
State is entirely runtime: discovered fileserver count and addresses, one ubik client, and one RX security object/index. Persistent effects occur remotely on fileservers by clearing authorization-related cache entries for the specified users or clients. The tool does not mutate VLDB, local configuration, or disk files.

## Dependencies And Integration Points
The file integrates OpenAFS auth, cell configuration, ubik/VLDB RPCs, RX/RXKAD, token cache lookup through `ktc_GetToken`, and the fileserver `RXAFS_FlushCPS` interface. It relies on client/server CellServDB configuration to find VLDB servers and on fileserver support for the flush RPC.

## Risks And Test Signals
Notable risks are fixed 256-entry arrays for servers, IDs, and IPs, minimal bounds feedback when more than 255 list items are provided, a duplicated `if (code)` line in the RX initialization error path, possible invalid address use in the multihomed error print when `bulkaddrs_len` is zero, and weak validation of `inet_addr` results. Test signals include `listservers` against single-homed and multihomed VLDB data, noauth/token/localauth/encrypt startup paths, invalid ID and IP inputs, partial server failures, and verifying that ACL/CPS changes become visible after a targeted flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/cacheout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/cmdebug.c -->
# sources/distributed-fs/openafs/src/venus/cmdebug.c

## Purpose
`cmdebug.c` implements `cmdebug`, an RX diagnostic client for querying an AFS cache manager callback service. It prints cache configuration, host interfaces, callback capabilities, kernel/cache-manager locks, cache entries, refcount/callback-filtered entries, and the cache manager's CellServDB view.

## Important APIs, Types, And Functions
`PrintCacheConfig` calls `RXAFSCB_GetCacheConfig` and decodes `cm_initparams_v1`. `PrintInterfaces` calls `RXAFSCB_TellMeAboutYourself` with fallback to `RXAFSCB_WhoAreYou`. Lock rendering is handled by `IsLocked`, `PrintLock`, and `PrintLocks`. Cache-entry rendering uses `PrintCacheEntries`, which tries `RXAFSCB_GetCE64` first and falls back to `PrintCacheEntries32`; both print FID, cell, locks, size, callback expiry, opens/writers, mvstat, and state bits. `GetCellName` caches `RXAFSCB_GetCellByNum` results. `PrintCellServDBEntry` and `PrintCellServDB` call `RXAFSCB_GetCellServDB`. `CommandProc` builds the RX connection and dispatches the selected mode.

## Control Flow
`main` initializes platform networking if needed, starts RX, registers one syntax with `-servers`, optional `-port`, detail/filter flags, and mode flags `-addrs`, `-cache`, and `-cellservdb`, then dispatches. `CommandProc` resolves the host, creates a null-security RX connection to callback service port 7001 by default, handles the exclusive simple modes first, sets `print_ctime` if requested, selects a cache-entry filter, prints locks for normal or long modes, and then prints cache entries.

## State And Persistence
The file has minimal local state: `print_ctime`, a static `no_getcellbynum` flag, and a linked cache of cell number to cell name mappings. It is read-only with respect to the remote cache manager. It allocates and frees callback-returned bulk arrays in the interface and CellServDB paths, while cell names cached by `GetCellName` persist for process lifetime.

## Dependencies And Integration Points
`cmdebug` depends on RX, `afscbint` callback RPC definitions, AFS lock descriptions, OpenAFS command parsing, host utility resolution, error translation, and platform UUID formatting. It integrates with the cache manager's callback/debug RPC service, so struct layout and opcode availability must match the cache manager version.

## Risks And Test Signals
Risks include iterating up to large hard-coded limits when a callback service misbehaves, legacy 32-bit and 64-bit cache-entry structure compatibility, static memory retained for cached cell names, duplicated assignment in `GetCellName`, and success paths that often print an error but return zero for optional diagnostics. Test signals are connections to old and new cache managers, `-long`, `-refcounts`, `-callbacks`, and `-ctime` output, `-addrs` with and without capabilities support, `-cache` structure size validation, CellServDB enumeration, and fallback when `RXAFSCB_GetCE64` or `TellMeAboutYourself` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/cmdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/fs.c -->
# sources/distributed-fs/openafs/src/venus/fs.c

## Purpose
`fs.c` is the main Unix `fs` command implementation for controlling and inspecting an OpenAFS cache manager and AFS namespace state. It is a large pioctl front-end for ACLs, volume status/quota, mount points, cache flushing and sizing, cell configuration, server preferences, workstation sysname, RX statistics, encryption, disconnected mode, callback address, UUID regeneration, NFS translator behavior, and FID lookup.

## Important APIs, Types, And Functions
The file's core data types are `struct Acl`, `struct AclEntry`, `struct vcxstat2`, local `struct VenusFid`, `struct ViceIoctl`, and several pioctl payload structures from OpenAFS headers. ACL helpers include `Convert`, `PRights`, `ParseAcl`, `EmptyAcl`, `AclToString`, `ChangeList`, `PruneList`, `CleanAcl`, `BadName`, and `getidf`. Path helpers include `SetDotDefault`, `InAFS`, `Parent`, `GetLastComponent`, `GetCell`, and `GetCellName`.

Major command handlers include `SetACLCmd`, `ListACLCmd`, `CopyACLCmd`, `CleanACLCmd`, `GetCallerAccess`, `FlushCmd`, `FlushMountCmd`, `FlushVolumeCmd`, `FlushAllVolumesCmd`, `SetVolCmd`, `ExamineCmd`, `ListQuotaCmd`, `DiskFreeCmd`, `QuotaCmd`, `WhereIsCmd`, `ListMountCmd`, `MakeMountCmd`, `RemoveMountCmd`, `CheckServersCmd`, `MessagesCmd`, `CheckVolumesCmd`, `SetCacheSizeCmd`, `GetCacheParmsCmd`, `ListCellsCmd`, `ListAliasesCmd`, `NewCellCmd`, `NewAliasCmd`, `WhichCellCmd`, `WSCellCmd`, `MonitorCmd`, `SysNameCmd`, `ExportAfsCmd`, `SetPrefCmd`, `GetPrefCmd`, `StoreBehindCmd`, `SetCryptCmd`, `GetCryptCmd`, `DisconCmd`, `GetClientAddrsCmd`, `SetClientAddrsCmd`, `RxStatProcCmd`, `RxStatPeerCmd`, `CallBackRxConnCmd`, `NukeNFSCredsCmd`, `UuidCmd`, `PreCacheCmd`, and `GetFidCmd`.

## Control Flow
`main` registers every subcommand and alias, captures parameter indexes for ACL `-id` and `-if` flags, conditionally registers cache-bypass/server-debug features, dispatches with `cmd_Dispatch`, and finalizes RX only if initialized by helper paths. Most handlers build a `ViceIoctl` around the static `space` buffer, call a `VIOC*` pioctl, decode output, print human-facing status, and continue across list arguments while accumulating an error bit.

ACL commands fetch ACL strings with `VIOCGETAL`, parse AFS or DFS ACL format, apply requested changes, optionally prune bad numeric-looking principals by querying the protection database, serialize with `AclToString`, and store with `VIOCSETAL`. Mount-point commands split parent and final component, use mount pioctls for inspection/deletion/flushing, and create mount points as symlinks with `#`, `%`, optional cell prefix, volume name, and trailing dot. Server preference commands pack `setspref`/`spref` structures and fall back from newer `VIOC_SETSPREFS` to older `VIOC_SETSPREFS33` when needed.

## State And Persistence
Local process state includes reusable static buffers, a global ubik client used for VLDB mount checks, ACL command parameter indexes, and a global `ViceIoctl` used by server-preference helpers. Persistent effects are broad and mostly remote/cache-manager mediated: ACL and quota changes, mount point symlinks, cell and alias configuration in the cache manager, server and client address preferences, cache size/precache/storebehind/encryption/disconnected-mode settings, RX stats state, NFS translator settings, callback address, UUID regeneration, and cache flushes.

## Dependencies And Integration Points
`fs.c` depends on OpenAFS pioctl constants and payload structs, cache-manager pioctl semantics, command parsing, CellServDB configuration, ubik/VLDB RPCs for optional volume existence checks, protection server APIs for ACL cleanup, RX utilities for local interface discovery, host utilities, and platform filesystem syscalls. It is one of the highest-level integration points between administrators/users and the Unix cache manager.

## Risks And Test Signals
Risk areas include heavy reuse of fixed-size global buffers, legacy ACL string parsing, DFS ACL corner cases, command handlers that mutate argument strings, root-only checks for some but not all privileged pioctls, compatibility fallbacks for old cache managers, unclear disconnected-mode packing using individual bytes in an `afs_int32` buffer, possible leaks from repeated `afsconf_Open`, and many commands returning partial success across lists. Test signals should cover ACL set/list/copy/clean including DFS flags, mount list/create/remove/flush including symlink and literal behavior, quota/status output, cache-size/cache-params paths, cell/alias add and list, server preference set/get with large lists and old cache managers, sysname get/set lists, encryption and RX stats toggles, disconnected mode transitions, `getfid -literal`, and correct error text for non-AFS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/fstrace.c -->
# sources/distributed-fs/openafs/src/venus/fstrace.c

## Purpose
`fstrace.c` implements the `fstrace` command for inspecting and controlling OpenAFS kernel ICL trace logs and event sets. It can dump logs, follow a log like tail, list logs and sets, clear logs or sets, activate/deactivate/free event sets, and resize kernel log buffers.

## Important APIs, Types, And Functions
Trace decoding centers on `icl_GetSize`, `CheckTypes`, `DisplayRecord`, and `dce1_error_inq_text`. Kernel interaction wrappers include `icl_DumpKernel`, `icl_TailKernel`, `icl_ClearLog`, `icl_ClearSet`, `icl_ClearAll`, `icl_ListSets`, `icl_ListLogs`, `icl_ListLogsBySet`, `icl_ChangeSetState`, `icl_ChangeAllSetState`, `icl_ChangeLogSize`, `icl_GetLogsize`, and `icl_GetSetState`. The platform syscall adapter is `afs_syscall`, with Linux, Darwin, SGI, AIX, and generic syscall paths. Command handlers are `DoDump`, `DoShowLog`, `DoShowSet`, `DoClear`, `DoSet`, and `DoResize`, registered by the `SetUp*` helpers.

## Control Flow
`main` sets locale, detects SGI kernel pointer size when relevant, registers six subcommands (`dump`, `lslog`, `lsset`, `clear`, `setset`, `setlog`), and dispatches. Every command requires effective UID zero. Dump mode writes a header, then either dumps all logs, dumps logs attached to selected event sets, or follows one log with periodic sleep. Listing modes enumerate logs/sets through ICL syscalls. Clear and set modes send kernel operations for selected names or all names. Resize converts kilobytes to words/bytes according to `BUFFER_MULTIPLIER`, defaulting to the ICL default log size when zero.

## State And Persistence
Runtime state includes `allInfo`, a linked list of log names to dump, `dumpDebugFlag`, and kernel word-size flags. Persistent effects are in kernel memory: clearing logs, allocating/freeing dormant set state, toggling event set activity, and resizing log buffers. Dump output may be written to stdout or to a user-specified file. Message decoding reads installed NLS catalog files under the OpenAFS client data directory.

## Dependencies And Integration Points
The file depends on OpenAFS ICL constants, AFS syscall/proc syscall support, RX headers, OpenAFS command parsing, platform syscall ABI details, and NLS message catalogs for opcode text. It is tightly coupled to kernel ICL record layout and the installed message catalog naming scheme derived from facility/component/status fields.

## Risks And Test Signals
Risks include raw `fprintf` with decoded catalog strings after type checking, architecture-sensitive long/pointer decoding, global `allInfo` not freed, root-only commands exiting from handlers, platform syscall fallbacks that may silently become `-1` without `AFS_SYSCALL`, and a likely bug in `DoClear` where the `-log` branch iterates `as->parms[0].items` instead of the `-log` list. Test signals include dumping with known trace records, `-debug` raw output, following a log across buffer resizes, listing logs by set with missing slots, clearing by set/log/all, set active/inactive/dormant transitions, resizing `cmfx` and named logs, and running on 32-bit and 64-bit kernel/user ABI combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/fstrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/gcpags.c -->
# sources/distributed-fs/openafs/src/venus/gcpags.c

## Purpose
`gcpags.c` is a minimal administrative helper that asks the cache manager to run garbage collection for PAGs through the `VIOC_GCPAGS` pioctl. Its visible message says "disable gcpags failed", but the operation is the cache-manager pioctl named for PAG garbage collection.

## Important APIs, Types, And Functions
The only function is `main`. It constructs an empty `struct ViceIoctl` and calls `pioctl(0, VIOC_GCPAGS, &blob, 1)`. It includes `AFS_component_version_number.c` for OpenAFS build/version metadata.

## Control Flow
Startup initializes no command parser and accepts no arguments. It zeroes all input/output pointers and sizes in the ioctl blob, invokes the pioctl, prints a `perror` message on nonzero return, and returns the pioctl result directly.

## State And Persistence
There is no local state beyond the stack `ViceIoctl`. The only effect is inside the running cache manager, which may reclaim or alter PAG-related credential bookkeeping. No files or configuration are read or written by this utility.

## Dependencies And Integration Points
The file depends on OpenAFS pioctl declarations from `sys_prototypes.h` and `vioc.h`. It integrates with the cache manager's `VIOC_GCPAGS` implementation and therefore requires a local AFS client with the expected pioctl support.

## Risks And Test Signals
Risks are mostly operational: no argument validation, no privilege precheck, terse error reporting, and direct propagation of a possibly negative syscall return as process exit status. Test signals are successful execution on a running cache manager, expected failure on hosts without AFS, and verification from cache-manager diagnostics that PAG cleanup behavior occurred.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/livesys.c -->
# sources/distributed-fs/openafs/src/venus/livesys.c

## Purpose
`livesys.c` implements `livesys`, a small utility that prints the first current AFS sysname value, the value normally substituted for `@sys`. It is a simplified read-only counterpart to `fs sysname`.

## Important APIs, Types, And Functions
The only function is `main`. It uses a static `space[AFS_PIOCTL_MAXSIZE]`, writes an input count of zero, and calls `pioctl(0, VIOC_AFS_SYSNAME, &blob, 1)`. It decodes the returned leading `afs_int32` count and prints the first string following that count.

## Control Flow
On startup it applies the AIX full-core signal action when applicable, prepares an in/out `ViceIoctl` using `space`, sets `setp` to zero to request the current sysname list, and invokes `VIOC_AFS_SYSNAME`. If the pioctl fails or returns zero entries, it prints an error and exits 1. Otherwise it prints the first returned sysname and exits 0.

## State And Persistence
The utility is read-only and has no state beyond the static buffer and stack variables. It does not modify the sysname list; persistence remains entirely inside the cache manager's current configuration/runtime state.

## Dependencies And Integration Points
It depends on OpenAFS pioctl headers and cache-manager support for `VIOC_AFS_SYSNAME`. It integrates with the same sysname state surfaced by `fs sysname`, but intentionally ignores additional entries in a sysname list.

## Risks And Test Signals
Risks include printing only the first sysname even when the cache manager returns a list, using `afs_error_message(code)` even though pioctl failures usually communicate via `errno`, and no bounds validation beyond trusting the pioctl buffer. Test signals include matching first output with `fs sysname`, failure on an absent cache manager, and behavior when the sysname list is empty or contains multiple values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/livesys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/Makefile.in -->
# sources/distributed-fs/openafs/src/venus/test/Makefile.in

## Purpose
This makefile builds the small Venus test utilities in `src/venus/test`: `fulltest`, `owntest`, `idtest`, and `getinitparams`. It wires them into the OpenAFS build system with the required command, pioctl/syscall, auth, ubik, VLDB, RX, utility, roken, and crypto libraries.

## Important APIs, Types, And Functions
The important targets are `all`, `test`, `fulltest`, `owntest`, `idtest`, `getinitparams`, and `clean`. `LT_deps` lists OpenAFS libtool archive dependencies, including `liboafs_sys`, `liboafs_ubik`, `liboafs_vldb`, `liboafs_auth`, `liboafs_rxkad`, `liboafs_comerr`, `liboafs_cmd`, `liboafs_rx`, `liboafs_util`, and `liboafs_opr`. `LT_libs` appends roken, hcrypto, and platform libraries.

## Control Flow
The default `all` and `test` targets build all four programs. Each executable links the corresponding object with `$(LT_LDRULE_static)`, the dependency archives, and external libraries. `install` and `dest` are intentionally empty, so these diagnostics are build/test artifacts rather than installed user commands. `clean` invokes `$(LT_CLEAN)` and removes objects and binaries.

## State And Persistence
The makefile creates object files and four local test executables in the build directory, and removes them during clean. It does not install persistent artifacts or modify source files.

## Dependencies And Integration Points
It includes `Makefile.config` and `Makefile.pthread`, so it inherits compiler, libtool, threading, and platform settings from the top-level OpenAFS build. It integrates test binaries with the same libraries used by Venus command tools, especially pioctl/syscall and command parsing support for `getinitparams`.

## Risks And Test Signals
Risks include dependency drift if test programs stop needing or newly need libraries, static link portability, and the empty install targets meaning packaging will not naturally exercise these tests. Test signals are successful `make test` or `make all` in this directory, clean rebuilds, and running the resulting binaries against an AFS mount/cache manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/fulltest.c -->
# sources/distributed-fs/openafs/src/venus/test/fulltest.c

## Purpose
`fulltest.c` is a destructive filesystem smoke test for Venus/cache-manager semantics in a supplied test directory. It exercises ordinary POSIX operations that an AFS client must implement correctly: create, chmod/fchmod, stat/fstat, byte-range locks, fsync, write, truncate, read, hardlink, symlink, mkdir/rmdir, directory reads, ownership edge behavior, rename, utimes, and cleanup.

## Important APIs, Types, And Functions
The only function is `main`. It uses standard POSIX calls: `mkdir`, `chdir`, `getcwd`, `open`, `close`, `access`, `chmod`, `stat`, `fchmod`, `fstat`, `fcntl` with `F_SETLK`, `fsync`, `write`, `ftruncate`, `read`, `link`, `unlink`, `symlink`, `readlink`, `rmdir`, `fchown`, `rename`, `truncate` when available, `utimes`, and `perror`.

## Control Flow
The program requires one directory argument, creates and enters it, then runs a fixed sequence of assertions. Each failure prints a diagnostic and returns `-1` or exits with status 1. The test starts with file creation and mode checks, validates shared and write lock set/unlock, writes and truncates content, checks hardlink and symlink behavior, validates non-empty directory removal failure, attempts directory reading, verifies writes to a read-only-mode file opened read/write, renames a file and checks source/target visibility, truncates to one byte where supported, updates timestamps, removes the final file, returns to the parent, removes the test directory, and prints success.

## State And Persistence
All state is filesystem state under the caller-provided directory. A successful run cleans up its generated files and directory. Failed runs can leave partial test artifacts such as `hi`, `bye`, `tdir`, `rotest`, or the top-level test directory.

## Dependencies And Integration Points
The test depends on POSIX filesystem behavior as mediated by the AFS cache manager when the target directory is in AFS. It is built by the local Venus test makefile and does not use pioctls directly.

## Risks And Test Signals
Risks include destructive behavior in the supplied directory, assumptions about directory read behavior, unset `struct timeval tvp[2]` before `utimes`, platform exclusions for `truncate`, and returning `-1` from `main` producing platform-specific exit codes. Its primary signal is broad AFS client POSIX compatibility; failures identify which basic operation or cache consistency path is broken.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/fulltest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/getinitparams.c -->
# sources/distributed-fs/openafs/src/venus/test/getinitparams.c

## Purpose
`getinitparams.c` is a diagnostic utility for retrieving and printing cache-manager initialization parameters. It can test either direct `ioctl` against an opened AFS file or `lpioctl` without a file, using `VIOC_GETINITPARAMS`.

## Important APIs, Types, And Functions
`GetInitParamsCmd` is the command handler. It fills a `struct cm_initparams`, wraps it in `struct ViceIoctl`, and uses either `ioctl(fd, VIOC_GETINITPARAMS, &blob)` or `lpioctl(NULL, VIOC_GETINITPARAMS, &blob, 0)`. `main` registers the optional `-file` parameter with the OpenAFS command parser.

## Control Flow
If `-file` is supplied, the handler prints `ioctl test`, opens the file read-only, issues the ioctl, and closes it. Otherwise it prints `lpioctl test` and issues `lpioctl`. On any open or ioctl failure it prints with `perror` and exits 1. On success it prints version, chunk file count, stat/data/volume cache counts, first and other chunk sizes, initial cache size, set-time flag, and disk-vs-memory cache flag, then exits 0.

## State And Persistence
The program is read-only. It observes cache-manager initialization state and optionally opens a file descriptor temporarily. It does not change cache configuration or filesystem data.

## Dependencies And Integration Points
It depends on OpenAFS Venus, vice, syscall, and command headers and on cache-manager support for `VIOC_GETINITPARAMS`. It tests both the path/file-descriptor ioctl path and the local pioctl path, which can expose platform-specific pioctl plumbing issues.

## Risks And Test Signals
Risks include process exit from inside the handler, minimal version-aware decoding of `struct cm_initparams`, and requiring a valid AFS file for the direct ioctl mode. Test signals are successful output through both `-file` and no-file modes, plausible cache counts matching `afsd` startup options, and expected failure on non-AFS or cache-manager-absent hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/getinitparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/idtest.c -->
# sources/distributed-fs/openafs/src/venus/test/idtest.c

## Purpose
`idtest.c` is a tiny identity diagnostic that prints the process effective UID and real UID. In the Venus test directory it helps check setuid, credential, or execution-context behavior on an AFS-mounted path.

## Important APIs, Types, And Functions
The only function is `main`. It calls `geteuid`, `getuid`, prints both integer values, and exits 0.

## Control Flow
The program ignores arguments. It reads and prints the effective UID first, then the real UID, then terminates with `exit(0)`.

## State And Persistence
The program is purely observational. It creates no files, changes no credentials, and writes only stdout.

## Dependencies And Integration Points
It depends only on standard Unix identity APIs plus OpenAFS build configuration headers. Within OpenAFS testing, it can be installed or executed with specific mode bits to observe whether AFS client and host policy honor effective-ID transitions.

## Risks And Test Signals
Risks are minimal; output formatting is fixed and no errors are possible from the two calls in normal POSIX environments. Useful signals are matching or intentionally different real/effective UID values under normal, setuid, and AFS `setcell` suid-policy scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/idtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/owntest.c -->
# sources/distributed-fs/openafs/src/venus/test/owntest.c

## Purpose
`owntest.c` tests whether a caller can modify mode bits and timestamps on a writable file that may be owned by someone else. It is aimed at AFS ownership/permission semantics where write access through ACLs may not align with local Unix ownership.

## Important APIs, Types, And Functions
The only function is `main`. It uses `chmod`, `gettimeofday`, `utimes`, `stat`, `perror`, and `exit`. It expects a single pathname argument.

## Control Flow
The program validates its argument count, prints a start message, changes the target file to read-only mode `0444`, changes it back to `0666`, sets access and modification times to two times in the past, stats the file, verifies the modification time stuck, prints `Done.`, and exits 0. Any syscall failure exits with `errno`; a mismatched modification time exits 1.

## State And Persistence
The test intentionally persists changes to the target file's mode and timestamps. It does not restore the original mode or times, so it should be run only on disposable fixtures.

## Dependencies And Integration Points
It depends on POSIX metadata syscalls as implemented by the local filesystem or AFS cache manager. In AFS, it provides a focused signal for ACL-mediated metadata updates separate from Unix owner identity.

## Risks And Test Signals
Risks include destructive metadata changes, typoed usage text, assuming second-resolution mtime equality, and platform differences in permission checks for non-owner metadata operations. A passing run signals that chmod and utimes changes are accepted and visible via stat for the selected target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/test/owntest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/twiddle.c -->
# sources/distributed-fs/openafs/src/venus/twiddle.c

## Purpose
`twiddle.c` implements a hidden/diagnostic-style `fs`-named utility for adjusting RX transport parameters in the cache manager through `VIOC_TWIDDLE`. It packages command-line numeric values into `struct rxparams` and sends them to the local client.

## Important APIs, Types, And Functions
`Twiddle` parses optional numeric command parameters into `rx_initReceiveWindow`, `rx_maxReceiveWindow`, `rx_initSendWindow`, `rx_maxSendWindow`, `rxi_nSendFrags`, `rxi_nRecvFrags`, `rxi_OrphanFragSize`, `rx_maxReceiveSize`, and `rx_MyMaxSendSize`. `main` registers one command syntax with those nine parameters. `Die` formats common pioctl/errno failures.

## Control Flow
Startup applies the AIX full-core signal action when relevant, registers the single syntax, dispatches, conditionally finalizes RX, and exits. The command handler treats omitted parameters as zero, uses `atoi` without range checking, sends the filled structure as both input and output through `pioctl(0, VIOC_TWIDDLE, &blob, 1)`, and reports errors through `Die`.

## State And Persistence
Local state is temporary, but the pioctl can change cache-manager RX runtime behavior such as window sizes, fragment counts, and max send/receive sizes. Those changes are runtime cache-manager state, not local file edits.

## Dependencies And Integration Points
The file depends on OpenAFS Venus pioctl definitions, RX parameter structures, command parsing, and cache-manager support for `VIOC_TWIDDLE`. It is coupled to the cache manager's interpretation of zero values and the exact `struct rxparams` layout.

## Risks And Test Signals
Risks include no numeric validation, parameter names containing trailing spaces in `cmd_AddParm`, confusing program name `pn` set to `fs`, error reporting that ignores the handler's `code` argument and uses global `errno`, and easy destabilization of RX behavior with bad values. Test signals include pioctl success with safe values, expected rejection for invalid/unsupported clients, and observable RX behavior or diagnostics changing after parameter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/twiddle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/up.c -->
# sources/distributed-fs/openafs/src/venus/up.c

## Purpose
`up.c` implements `up`, a recursive update/copy utility that mirrors a source file tree to a target while preserving ownership, group, mode bits, timestamps by default, AFS ACLs by default, and optionally AFS mount points. It is similar to a specialized recursive copy tuned for AFS update workflows.

## Important APIs, Types, And Functions
Global flags are set by `ScanArgs`: `-v` verbose, `-1` one level only, `-r` rename existing targets to `.old`, `-f` force overwrite write-protected targets, `-x` do not preserve dates, and `-m` preserve AFS mount points. `MakeParent` recursively creates missing parent directories and sets owner. `Copy` handles regular files, symlinks, mount points, and directories. `isMountPoint` tests a path with `VIOC_AFS_STAT_MT_PT`. `struct OldAcl` supports conversion from older ACL ioctl output.

## Control Flow
`main` parses flags and two paths, then calls `Copy(source, target, !oneLevel, 0)`. `Copy` uses `lstat` to classify the source, creates missing target parents, and branches by object type. Regular files are copied through a temporary `target.UPD`, optionally preserving times, optionally renaming the previous target, then setting owner, group, and mode. Symlinks are recreated from `readlink` output. When `-m` is active, AFS mount points are detected and recreated as symlinks to the mount target plus trailing dot. Directories are recursively traversed, created as needed, ownership/group/mode/times are applied, and ACLs are copied using new-style `_VICEIOCTL(2)` get and `_VICEIOCTL(1)` set, or old-style `_VICEIOCTL(4)` conversion when enabled.

## State And Persistence
The program modifies the target tree: it creates directories, files, symlinks, mount-point symlinks, temporary `.UPD` files, optional `.old` backups, ownership, group, mode, timestamps, and AFS ACLs. Global `setacl` can be turned off after an EINVAL and then suppresses ACL copying for later directories.

## Dependencies And Integration Points
It depends on POSIX directory/file syscalls, AFS pioctl/ioctl constants, `VIOC_AFS_STAT_MT_PT`, and the cache manager's ACL pioctls. It integrates ordinary filesystem metadata copying with AFS-specific ACL and mount-point representation.

## Risks And Test Signals
Risks include destructive target updates, fixed `MAXPATHLEN` buffers, duplicated `strlcpy` and `chown` statements, no cleanup of stale `.UPD` on failures, possible uninitialized symlink text in a verbose message before `readlink`, process-global ACL disabling after one unsupported path, old ACL conversion assumptions, and limited protection against path truncation. Test signals include regular file copy with metadata preservation, force and rename-target behavior, recursive directory copy, one-level mode, symlink recreation, mount-point preservation with `-m`, ACL copy success/fallback, timestamp opt-out with `-x`, and behavior when target files are write-protected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/whatfid.c -->
# sources/distributed-fs/openafs/src/venus/whatfid.c

## Purpose
`whatfid.c` implements a small command that prints the cell and AFS FID for one or more pathnames using `VIOCGETFID`. It predates or overlaps with `fs getfid` and provides a simple diagnostic view of cache-manager path-to-FID resolution.

## Important APIs, Types, And Functions
The local `struct VenusFid` contains `Cell` and `struct AFSFid`. `WhatFidCmd` iterates `-path` arguments, calls `pioctl(path, VIOCGETFID, &blob, follow)`, and prints `cell:volume.vnode.unique`. `PioctlError` formats common pioctl error cases. `main` registers the `initcmd` syntax with `-path` and `-link`.

## Control Flow
The command defaults to following symlinks/mount evaluation via pioctl follow flag `1`. If `-link` is present, it sets follow to `0`, despite the parameter description saying "do not follow symlinks". Each path is processed independently; failures print an error and continue. The program returns the command parser's dispatch result, not a per-path error count.

## State And Persistence
The utility is read-only. It stores only the program name pointer and command parameter indexes as process globals. It does not mutate cache-manager state or files.

## Dependencies And Integration Points
It depends on OpenAFS pioctl support, `vioc.h`, AFS FID structures, command parsing, and error translation. It integrates with the local cache manager's path resolution and FID reporting.

## Risks And Test Signals
Risks include no nonzero aggregate error status for failed paths, ambiguous `-link` naming versus follow behavior, local duplication of `struct VenusFid`, and reliance on `errno` in the error printer while passing the unused pioctl return code. Test signals include FID output for files, directories, symlinks with and without `-link`, mount points, non-AFS paths, missing files, and permission-denied paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/venus/whatfid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/Makefile.in -->
# sources/distributed-fs/openafs/src/vfsck/Makefile.in

## Purpose
This makefile builds and installs the OpenAFS `vfsck` utility, a server-side filesystem checker derived from Berkeley fsck sources and adapted for OpenAFS-supported platforms. It collects the vfsck source modules, applies platform CFLAGS, links the binary, and installs it into server libexec or destination root.server locations.

## Important APIs, Types, And Functions
Important variables are `MODULE_CFLAGS=${VFSCK_CFLAGS}`, `SRCS`, and `OBJS`. The main targets are `all`, `vfsck`, `main.o`, `install`, `dest`, and `clean`. `SRCS` includes pass files (`pass1.c` through `pass5.c` plus `pass1b.c`), setup/utilities, inode/dir helpers, UFS tables/subroutines, and `vprintf.c`. `main.o` depends on generated `AFS_component_version_number.c`.

## Control Flow
The default target builds `vfsck`. The link rule uses `$(AFS_LDRULE)` over all object files plus `$(XLIBS)`. `install` creates `$(DESTDIR)$(afssrvlibexecdir)` and installs `vfsck` there. `dest` installs copies under `${DEST}/root.server/etc/vfsck` and `${DEST}/root.server/usr/afs/bin/vfsck`, and conditionally copies HP-UX boot/check scripts plus mount/umount helpers with executable permissions. `clean` removes objects, the binary, core files, and generated component version source. The file includes `../config/Makefile.version` at the end to generate version metadata.

## State And Persistence
Build state consists of object files, `vfsck`, and `AFS_component_version_number.c`. Install/dest targets persist binaries and HP-UX helper scripts under server installation trees. Clean removes local build artifacts only.

## Dependencies And Integration Points
It includes OpenAFS `Makefile.config` and `Makefile.lwp`, takes platform-specific `VFSCK_CFLAGS`, and links with platform libraries. It integrates with OpenAFS server packaging layout and HP-UX root.server boot/check support.

## Risks And Test Signals
Risks include the age and platform specificity of UFS/fsck code, conditional HP-UX script handling, reliance on `SYS_NAME` patterns, and link portability if `XLIBS` or LWP/config flags drift. Test signals are successful clean builds, generated component version dependency behavior, install and dest layout checks, HP-UX conditional file copies when applicable, and running `vfsck` in controlled filesystem images rather than production partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/Makefile.in -->
