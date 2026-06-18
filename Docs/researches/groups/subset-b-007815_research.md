# Research: subset-b-007815

Grouped research for the exact source files assigned to `subset-b-007815`. Each section preserves the source path in its title and is wrapped for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vldb_check.c -->
## sources/distributed-fs/openafs/src/vlserver/vldb_check.c

Purpose: offline consistency checker and optional repair utility for a VLDB Ubik database file. It opens the raw database, skips the Ubik header for VLDB payload I/O, decodes VLDB headers, volume entries, free-list entries, and multihomed server extension blocks, then reports structural errors and can rebuild hash/free chains with `-fix`.

Important APIs/types/functions: global `record[]` tracks each file address and classification bits (`VL`, `FR`, `MH`, hash/free/multihome chain membership, duplicate and bad-chain flags). `readUbikHeader()` validates Ubik magic and header size. `vldbio()` is the raw seek/read/write helper behind `vldbread` and `vldbwrite`. `readheader()`/`writeheader()`, `readentry()`/`writeentry()`, and `readMH()`/`writeMH()` do host/network byte-order conversion for on-disk VLDB structures. `ReadAllEntries()`, `FollowNameHash()`, `FollowIdHash()`, `FollowFreeChain()`, and `CheckIpAddrs()` perform the main scan phases. `WorkerBee()` is the `cmd` callback implementing option parsing, scanning, validation, and optional repair. `main()` registers `-database`, display flags, `-quiet`, and `-fix`.

Control flow: `WorkerBee()` opens the database read-only or read-write, reads the Ubik and VLDB headers, allocates a record table sized from `eofPtr`, resets server address tracking, and performs independent passes over physical entries, multihomed blocks, volume-name hash chains, volume-id hash chains, and the free chain. It then revisits every recorded entry to cross-check membership, names, volume ids, lock consistency, server references, and chain anomalies. With `-fix`, it zeroes and rebuilds the hash heads and free pointer from discovered entries, renames invalid entries to `.bogus.<addr>`, assigns missing RW ids from `MaxVolumeId`, consolidates cross-linked multihome server numbers, removes unreferenced multihome entries, writes changed entries/blocks, updates the header, and reports hash head changes.

State and persistence: state is process-global while scanning: output flags, `fd`, severity `error_level`, `serveraddrs`, `serverxref`, `serverref`, and `mhinfo`. Persistent mutation occurs only with `-fix`, via direct writes to the raw database file. The checker assumes VLDB structures are in network byte order on disk and restores that order before writing. It exits with warning/error/fatal severity through `error_level`.

Dependencies: OpenAFS `cmd`, `ubik`, VLDB internal layouts from `vlserver.h`/`vldbint.h`, roken/POSIX file I/O (`open`, `lseek`, `read`, `write`, `close`), byte-order helpers, `afsUUID`, and standard formatting/string APIs.

Integration points: complements live `vlserver` operation and is referenced by server-side corruption logs as the repair/checking tool. It shares hash algorithms and layout constants with `vlutils.c` and `vlserver.p.h`, so changes to VLDB layout, hash semantics, multihome extent sizing, or server limits must be reflected here.

Risks: `-fix` is intentionally invasive and rebuilds chains from what the scanner can classify; running it on a live or misidentified file can corrupt state. Several checks are legacy-tolerant rather than exhaustive, such as not validating entry alignment and not deduplicating multihomed IP lists. The checker has duplicated conversion lines and a suspicious totalEntries conversion pattern that repeatedly uses index `1`, so header counter reporting/rewriting deserves targeted tests. `record` indexes are derived from `addr / sizeof(vlentry)` even for extension blocks, so range checks are critical. Fatal errors call `exit()` from `log_error()`.

Test signals: useful tests include synthetic VLDB files with valid headers, bad Ubik magic/size, out-of-range hash links, duplicate name/id hash membership, invalid volume names, missing RW ids, free entries off the free chain, orphaned/cross-linked multihome entries, lock timestamp/operation mismatches, and `-fix` round trips that rebuild chains without changing valid databases. Exit status should reflect warning/error/fatal severities, and `-quiet` must suppress stdout while preserving stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vldb_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlprocs.c -->
## sources/distributed-fs/openafs/src/vlserver/vlprocs.c

Purpose: implementation of the exported VLDB RPC procedures served by `vlserver`. It validates callers and request data, opens Ubik transactions, converts between external RPC entries and compact on-disk `nvlentry` records, updates hash/free/server-address state, emits audit records, and maintains dynamic per-op statistics.

Important APIs/types/functions: public entry points are the `SVL_*` RPC handlers such as create/delete/replace/update/get/list/lock/stats/address registration calls and `SVL_ProbeServer()`. `Init_VLdbase()` is the common transaction/cache initializer. Internal helpers include `CreateEntry[N]`, `DeleteEntry`, `GetEntryByID`, `GetEntryByName`, `ReplaceEntry[N]`, `UpdateEntry`, `ListAttributes[N/N2]`, `LinkedList[N]`, `SVL_RegisterAddrs`, `SVL_GetAddrs[U]`, `RemoveEntry`, `ReleaseEntry`, `check_*vldbentry`, `*vldbentry_to_vlentry`, `vlentry_to_*vldbentry`, `get_vldbupdateentry`, `IpAddrToRelAddr`, and `ChangeIPAddr`.

Control flow: each RPC increments request stats, enforces superuser or restricted-query policy, validates volume type/name/operation/release masks, calls `Init_VLdbase()` with read or write locking, performs lookups through `FindByID`, `FindByName`, or `NextEntry`, and either ends the Ubik transaction or jumps to an abort path that increments abort stats and calls `ubik_AbortTrans()`. Mutating calls allocate or free VLDB blocks with `AllocBlock()`/`FreeBlock()`, keep name/id hash chains coherent through `ThreadVLentry()` and `Unhash*`/`Hash*`, and write modified entries through `vlentrywrite()`.

State and persistence: durable state is the Ubik VLDB: `vlheader` vital data, max volume id, hash heads, free list, server address table, multihome extent blocks, and volume entries. Process state includes `dynamic_statistics`, `maxnservers`, `smallMem`, `restrictedQueryLevel`, global Ubik database/config pointers, and read/write caches in `vlutils.c`. Address registration persists UUID-based multihome entries and uniquifiers. Lock RPCs persist advisory lock timestamps and operation bits in entries.

Dependencies: `ubik` transactions, Rx/RxKAD caller information, `afsconf` authorization and restricted query checks, audit (`osi_auditU` events), VLDB wire types from `vldbint.h`, internal storage helpers from `vlserver_internal.h`, optional POSIX regex for wildcarded `ListAttributesN2`, and OpenAFS logging/time utilities.

Integration points: called by generated Rx dispatch (`VL_ExecuteRequest`) from `vlserver.c`. It relies on `vlutils.c` for disk layout, cache synchronization, hash/free-list manipulation, id allocation, and multihome extent allocation. Volume-management clients (`vos`, fileservers registering addresses, volserver workflows) observe its compatibility surfaces: old `vldbentry`, new `nvldbentry`, UUID-bearing `uvldbentry`, linked-list and bulk-list forms.

Risks: this file is a high-blast-radius persistence path: partial hash updates before a later abort rely on Ubik rollback semantics. Large list calls can be expensive full scans; `smallMem` changes allocation behavior and can return `VL_SIZEEXCEEDED`. Address registration has complex conflict detection for UUID and multihomed entries, and mistakes can orphan or merge server identities. Some loops still use legacy `OMAXNSERVERS` in update paths while newer entries support `NMAXNSERVERS`. The source contains visible duplicated statements/braces in several regions, so compile coverage and careful review are important when editing. Name wildcard search requires superuser when a nontrivial regex is supplied.

Test signals: exercise RPCs under authenticated, unauthenticated, restricted-query-anyuser, and restricted-query-admin modes; create/duplicate-name/duplicate-id/delete/replace/update flows; lock/release edge cases; volume id bumping over occupied ids; list filtering by id/server/partition/flag/name with pagination; multihomed registration conflicts, replacement, duplicate-address removal, and `GetAddrsU` by UUID/index/IP; Ubik abort paths after injected I/O/allocation errors; and audit/stat counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlserver.c -->
## sources/distributed-fs/openafs/src/vlserver/vlserver.c

Purpose: executable entry point for the OpenAFS Volume Location server. It parses server/Rx/security/logging options, opens cell configuration, initializes Rx and Ubik, registers VLDB and RX statistics services, and starts the Rx server loop.

Important APIs/types/functions: global server state includes `vldb_confdir`, `VL_dbase`, `dynamic_statistics`, `rd_HostAddress`, `wr_HostAddress`, `lwps`, `smallMem`, `restrictedQueryLevel`, Rx tuning flags, and bind address state. `initialize_dstats()` resets dynamic opcode counters. `vldb_rxstat_userok()` gates RX stats administration to superusers. `vldb_IsLocalRealmMatch()` supplies audit user realm checks. `CheckSignal()` dumps name and id hash tables after initializing a read transaction; `CheckSignal_Signal()` bridges signal handling into pthread or LWP soft-signal paths. `main()` owns startup.

Control flow: startup initializes AFS paths, builds a `cmd` syntax, parses options, configures audit/logging, opens the server config dir, resolves the local host and VLDB server list, applies Rx bind/jumbo/MTU options, initializes Rx on `AFSCONF_VLDBPORT`, configures Ubik client/server security, sets `ubik_SyncWriterCacheProc = vlsynccache`, starts the Ubik database, initializes VLDB read/write address caches and stats, builds security classes, creates the VLDB service and RX stats service, applies dotted-principal policy, logs version/command line, sets the RX stats authorization callback, and calls `rx_StartServer(1)`.

State and persistence: this file does not directly mutate VLDB records, but it determines the persistent database path (`AFSDIR_SERVER_VLDB_FILEPATH` or `-database`) passed to Ubik and installs `vlsynccache()` so committed write-cache state is copied to read-cache state. It also opens audit and log destinations, and can bind to a restricted local interface based on NetInfo/NetRestrict.

Dependencies: OpenAFS command parser, directory path/config/auth/keys/audit/log utilities, Rx/RxKAD/Rx stats, Ubik, pthread soft signals or LWP soft signals, platform event/logging hooks, and generated `AFS_component_version_number.c`.

Integration points: `vlserver.c` wires generated Rx dispatchers (`VL_ExecuteRequest`, `RXSTATS_ExecuteRequest`) to the implementations in `vlprocs.c`. Ubik security callbacks use `afsconf_ClientAuth` or rxgk crypt based on `-s2scrypt`. Runtime options such as `-smallmem`, `-restricted_query`, `-allow-dotted-principals`, and `-rxbind` directly influence behavior in other VLDB modules.

Risks: startup failure paths often `exit()` after logging, so service managers see hard failures. Misconfigured `-rxbind`, NetInfo/NetRestrict, or host resolution can bind to an unintended address. `-noauth` changes the security posture for the whole service. Thread count is clamped only above `MAXLWP` and raised to at least four for the VLDB service. Signal-triggered hash dumping opens a transaction and can be noisy/expensive on large databases.

Test signals: cover option parsing conflicts (`-syslog` with `-logfile`/`-transarc-logs`), invalid `-restricted_query`, invalid `-s2scrypt`, Rx MTU rejection, `-p` clamping/minimum behavior, noauth and dotted-principal security configuration, bind host selection with mocked NetInfo/NetRestrict, Ubik init failure logging, and service registration using expected min/max procs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlserver.p.h -->
## sources/distributed-fs/openafs/src/vlserver/vlserver.p.h

Purpose: private VLDB server layout header. It defines constants and persistent in-memory/on-disk structures used by `vlserver`, `vlutils`, `vlprocs`, and `vldb_check`.

Important APIs/types/functions: defines hash and allocation constants (`HASHSIZE`, `VLDBALLOCCOUNT`, `MAXSERVERID`, `BADSERVERID`, `MAXPARTITIONID`, `MAXBUMPCOUNT`, `MAXLOCKTIME`), volume-id array indexes (`RWVOL`, `ROVOL`, `BACKVOL`), entry flags (`VLFREE`, `VLDELETED`, `VLLOCKED`, `VLCONTBLOCK`), release-lock masks, and per-repsite flags. `struct vlheader` contains `vital_vlheader`, server address map, name hash table, id hash tables, and multihome extension pointer `SIT`. `struct vlentry` is the older compact entry with `OMAXNSERVERS`; `struct nvlentry` is the newer entry with `NMAXNSERVERS`. `struct extentaddr` overlays extension-block headers with multihomed address entries and exposes field aliases such as `ex_count`, `ex_hostuuid`, `ex_addrs`, and `ex_uniquifier`.

Control flow: no runtime flow; it fixes storage layout and semantic constants. The `DOFFSET` macro computes byte offsets for in-place field writes into the Ubik database.

State and persistence: most definitions here are persistent VLDB format. `vlheader`, `vlentry`, `nvlentry`, and `extentaddr` are serialized in network byte order by helper code. `VLCONTBLOCK` lets sequential scanners skip 8192-byte multihome extension blocks inside the same database file. `IpMappedAddr` entries either hold a single IP or an encoded multihome reference beginning with `0xff`.

Dependencies: includes VLDB wire definitions from `vldbint.h` and utility declarations from `afs/afsutil.h`; uses `afs_uint32`, `afs_int32`, `afsUUID`, and VLDB constants such as `MAXTYPES`, `VL_MAXNAMELEN`, `OMAXNSERVERS`, and `NMAXNSERVERS`.

Integration points: this is the shared contract between live server logic, offline checker, and generated/public RPC structures. Any layout change must coordinate byte-order conversion in `vlutils.c`, validation/repair in `vldb_check.c`, and client compatibility in conversion routines in `vlprocs.c`.

Risks: changing sizes or constants can make existing VLDB files unreadable or misinterpreted. The header mixes old and new entry formats, so `maxnservers`/version handling must remain exact. The `extentaddr` union depends on flags being in the same position as `vlentry.flags`. `MAXSERVERID` and encoded multihome sentinel values constrain future expansion.

Test signals: compile-time size/layout checks, database migration/open tests across `OVLDBVERSION`, `VLDBVERSION`, and `VLDBVERSION_4`, byte-order conversion round trips, multihome encoded address decoding, and offline `vldb_check` compatibility against live server-written databases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlserver.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlserver_internal.h -->
## sources/distributed-fs/openafs/src/vlserver/vlserver_internal.h

Purpose: internal VLDB server interface between RPC procedure code and low-level Ubik/storage utilities.

Important APIs/types/functions: defines `struct vl_ctx`, the per-operation transaction context containing the active `ubik_trans`, selected host address cache, selected multihome extent cache, and selected VLDB header cache. Declares `Init_VLdbase()` from `vlprocs.c` and storage/hash/cache helpers from `vlutils.c`: `vlwrite`, `vlentrywrite`, `write_vital_vlheader`, `readExtents`, `CheckInit`, `AllocBlock`, `FindExtentBlock`, `FindByID`, `FindByName`, `EntryIDExists`, `NextUnusedID`, hash dump/thread/unthread/hash/unhash functions, `NextEntry`, `FreeBlock`, `vlsetcache`, and `vlsynccache`.

Control flow: no executable control flow, but it codifies the layering: RPC handlers call `Init_VLdbase()` to populate `vl_ctx`; helpers then operate through that context and return VLDB/Ubik error codes.

State and persistence: `vl_ctx` selects either read caches or write caches depending on lock type. Persistent mutation happens through the declared helper functions, which write Ubik database offsets and update cached headers/extent blocks.

Dependencies: requires `struct ubik_trans`, `afs_uint32`, `afs_int32`, `afsUUID`, `struct extentaddr`, `struct vlheader`, and `struct nvlentry` from included VLDB/Ubik headers.

Integration points: included by `vlserver.c`, `vlprocs.c`, and `vlutils.c`. It is the narrow private boundary that keeps generated/public RPC types out of the lower storage manipulation APIs.

Risks: because the prototypes expose raw offsets and mutable cache pointers, callers must hold the correct Ubik transaction and lock mode. Omitting a new storage helper here can push modules toward duplicate declarations. The header does not own synchronization; correctness depends on Ubik transaction discipline and `vlsetcache`/`vlsynccache` usage.

Test signals: compile/link coverage across VLDB modules, transaction tests proving read contexts never mutate write caches, write transaction commit invoking `vlsynccache`, and error-path tests for each declared helper through RPC-level operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlserver_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlutils.c -->
## sources/distributed-fs/openafs/src/vlserver/vlutils.c

Purpose: low-level VLDB storage, cache, hash, free-list, id allocation, and multihome extension-block utilities used by the VLDB RPC procedures and server diagnostics.

Important APIs/types/functions: exports `IDHash`, `NameHash`, `vlwrite`, `vlread`, `vlentrywrite`, `vlentryread`, `write_vital_vlheader`, `readExtents`, `CheckInit`, `GetExtentBlock`, `FindExtentBlock`, `AllocBlock`, `FreeBlock`, `FindByID`, `FindByName`, `EntryIDExists`, `NextUnusedID`, `HashNDump`, `HashIdDump`, `ThreadVLentry`, `UnthreadVLentry`, `HashVolid`, `UnhashVolid`, `HashVolname`, `UnhashVolname`, `NextEntry`, `vlsetcache`, and `vlsynccache`. Global caches are `rd_cheader`/`wr_cheader`, `rd_HostAddress`/`wr_HostAddress`, and `rd_ex_addr`/`wr_ex_addr`.

Control flow: `CheckInit()` uses `ubik_CheckCache()` with `UpdateCache()` to read or build the VLDB header, validate version, load server address maps, and read multihome extents. Write operations select write caches via `vlsetcache()`, mutate the cache and database through offset writes, then Ubik commit triggers `vlsynccache()` to copy write caches into read caches. Entry allocation takes from the header free pointer or grows `eofPtr`; freeing writes a `VLFREE` entry and links it into the free list. Hash insertion/removal updates header buckets and entry next pointers. Sequential iteration skips `VLCONTBLOCK` extension blocks.

State and persistence: persistent state is written through Ubik offsets in network byte order. `vlentrywrite()`/`vlentryread()` bridge old and new on-disk entry layouts based on `maxnservers` and database version. `readExtents()` keeps in-memory copies of multihome extension blocks and can mark/fix bad continuation pointers with `extent_mod`. `grow_eofPtr()` enforces the legacy 2 GiB VLDB limit.

Dependencies: Ubik transaction APIs, VLDB layout constants/types, byte-order helpers, UUID helpers, global `maxnservers`, and OpenAFS logging. It relies on `ubik_SyncWriterCacheProc` being set by `vlserver.c`.

Integration points: `vlprocs.c` is the main consumer for all RPC-visible mutations and lookups. `vlserver.c` uses hash dump helpers in signal diagnostics and installs `vlsynccache()`. `vldb_check.c` independently mirrors many layout assumptions for offline validation.

Risks: cache coherence is central; forgetting to write the header or sync write caches can expose stale state to readers. Hash updates are linked-list manipulations by raw offsets, so corrupted chains can return `VL_DBBAD`/`VL_NOENT` and require `vldb_check`. `FindExtentBlock()` encodes multihome references into server slots and upgrades the database version to `VLDBVERSION_4`; failures mid-operation depend on Ubik rollback. Several duplicate lines are present in the source, suggesting old merge or formatting artifacts. `NameHash()` assumes nonempty names and `IDHash()` uses `abs()` on signed input.

Test signals: version/header initialization for empty and existing databases; old/new entry conversion with `maxnservers` 8 and 13; hash insert/remove/find for RW/RO/BK/name chains; free-list allocate/free/reuse; `NextEntry()` skipping extension blocks; multihome extent creation, continuation validation, version upgrade, and cache sync; `NextUnusedID()` over occupied ranges; and injected Ubik read/write/seek failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/Makefile.in -->
## sources/distributed-fs/openafs/src/vol/Makefile.in

Purpose: Automake-style template for building and installing the OpenAFS volume package library and related utilities: `vlib.a`, salvager, `volinfo`, `volscan`, `vol-bless`, `fssync-debug`, optional `xfs_size_check`, headers, and support objects.

Important APIs/targets: variables include `LIBS`, `MODULE_CFLAGS` with `FSSYNC_BUILD_SERVER`/`FSSYNC_BUILD_CLIENT`, `PUBLICHEADERS`, `VLIBOBJS`, and `OBJECTS`. Major targets are `all`, top-level library/header install copies, `install`, `dest`, object dependencies, `vlib.a`, `salvager`, `volinfo`, `volscan`, `fssync-debug`, `vol-bless`, `xfs_size_check`, `clean`, `check-splint`, and helper `gi`/`namei_map`.

Control flow: `all` builds generated version info, libraries, binaries, optional platform tools, and exported headers. `vlib.a` archives core volume objects including `clone.o`, `common.o`, and `daemon_com.o`. Install/dest targets create server/library/include directories and copy programs and public headers into packaged locations. Program targets link specific main/object combinations with `LIBS`, roken, and platform libraries. `check-splint` runs static analysis over the volume source set.

State and persistence: build artifacts are object files, archives, generated `AFS_component_version_number.c`, server binaries, and installed headers/programs. No runtime state is handled here, but build flags determine whether daemon sync code compiles server/client features.

Dependencies: top-level config make fragments, LWP config, OpenAFS static libraries (`libcmd`, `util`, `libdir`, `librx`, crypto, `liblwp`, `libsys`, `libacl`, `libopr`), roken, platform C compiler/linker macros, and source headers.

Integration points: this template is consumed by the OpenAFS configure/build system. It exports headers under `afs/` for other components and packages volume tools used by fileserver, volserver, salvager, and diagnostics workflows. The `VLIBOBJS` list ties `clone.c`, `common.c`, and `daemon_com.c` into the shared volume library.

Risks: object/header dependency drift can cause stale or missing rebuilds. Platform-specific `listinodes.o` and `gi` cases are easy to break in cross-platform changes. Adding a new public header or vlib object requires updating multiple target lists and install/dest sections. `clean` must track generated binaries and version files. Link order matters because this is static-library-heavy legacy C.

Test signals: configure/build on Linux and at least one non-Linux path, `make all`, staged `install`/`dest`, exported header presence, archive contents containing expected `VLIBOBJS`, optional `xfs_size_check` behavior when enabled, `clean` removing generated artifacts, and `check-splint` command construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/clone.c -->
## sources/distributed-fs/openafs/src/vol/clone.c

Purpose: volume clone implementation for copying vnode index metadata from an original read/write volume into a clone or reclone target while managing inode reference counts and directory clone flags.

Important APIs/types/functions: exported `CloneVolume()` clones both large and small vnode indexes and copies the volume header. `DoCloneIndex()` performs the per-vnode-class clone/reclone work. `struct clone_head` and `struct clone_items` batch old clone inodes that should be decremented after the new index is safely written and synced. `ci_InitHead()`, `ci_AddItem()`, `ci_Apply()`, and `ci_Destroy()` manage that batch list. `IDecProc()` applies `IH_DEC()` to queued inodes. `vol_PollProc`/`DOPOLL` integration allows long clone operations to yield/progress.

Control flow: `CloneVolume()` decides whether this is a reclone (`new == old`), clones `vLarge` then `vSmall`, logs filecount/diskused changes, and copies the disk volume header. `DoCloneIndex()` opens original and clone vnode index streams, optionally opens the existing clone for reading, walks original vnode records, increments referenced inodes when needed, marks original directory vnodes as cloned, writes the clone vnode record with `cloned = 0`, queues obsolete clone inodes for later decrement, truncates the clone index during reclone, syncs the target index, then decrements queued old inodes.

State and persistence: mutates vnode index files, inode link counts, original directory `cloned` flags, clone index length, and original volume counters (`V_filecount`, `V_diskused`) when `ReadWriteOriginal` is true. It uses inode handles from volume structures and fsync/truncate operations to make the clone index durable before old references are dropped.

Dependencies: volume/vnode/partition/inode handle APIs (`IH_OPEN`, `IH_INC`, `IH_DEC`, `FDH_*`, `STREAM_*`, `VNDISK_*`), `VnodeClassInfo`, `CopyVolumeHeader`, logging/panic helpers from `common.c`, and OpenAFS poll macros.

Integration points: called by volume server/salvage workflows that create or refresh clone/backup/readonly volumes. It is built into `vlib.a` and linked into volume tools via `Makefile.in`.

Risks: inode reference count ordering is safety-critical: failures after `IH_INC()` must decrement immediately or queue later decrements only after durable replacement. Recloning reads and writes the same clone index through separate streams and assumes it never reads data being simultaneously written. Directory `cloned` rollback is best-effort if a later write fails. `ReadWriteOriginal` is hard-coded true with a comment about readonly fileserver behavior. Memory allocation failure in `ci_AddItem()` panics the process.

Test signals: clone and reclone volumes with large/small vnode classes; directory and file vnodes; unchanged clinode matching rwinode; stale clone inodes that must be decremented; write/seek/IH_INC/IH_DEC/truncate/sync failure injection; filecount/diskused recomputation; old clone tail truncation; and verification that original directory clone bits are set or rolled back correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/clone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/common.c -->
## sources/distributed-fs/openafs/src/vol/common.c

Purpose: small shared logging and fatal-exit helpers for volume package tools and library code.

Important APIs/types/functions: defines global `int Statistics`. `Log()` chooses ViceLog level `-1` when statistics mode is enabled and `0` otherwise, then delegates to `vViceLog`. `Abort()` logs a program-aborted prefix and formatted message, then calls `abort()`. `Quit()` logs a formatted message and exits with status `1`.

Control flow: all three functions are variadic wrappers around OpenAFS logging. `Abort()` and `Quit()` do not return.

State and persistence: only mutable state is the process-global `Statistics` flag. Persistence is limited to whatever `ViceLog` backend writes. `Abort()` may produce a core dump depending on platform/runtime settings.

Dependencies: OpenAFS config/param, roken, `afs/afsutil.h` for `ViceLog`/`vViceLog`, standard varargs, `abort`, and `exit`.

Integration points: included by volume sources such as `clone.c` and `daemon_com.c` for consistent diagnostics and fatal handling. Declarations live in `common.h`; object is included in `VLIBOBJS`.

Risks: fatal helpers terminate the process, so library callers must know these are not recoverable paths. The logging call style uses the OpenAFS double-parentheses convention and should be preserved. The global `Statistics` flag changes log level process-wide.

Test signals: unit or harness tests can stub `vViceLog`/`ViceLog` to verify level selection, format propagation, `Abort()` non-return behavior, and `Quit()` exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/common.h -->
## sources/distributed-fs/openafs/src/vol/common.h

Purpose: public declarations for the volume package logging and fatal-exit helpers implemented in `common.c`.

Important APIs/types/functions: declares `Log(const char *format, ...)`, `Abort(const char *format, ...)`, and `Quit(const char *format, ...)`. Format attributes request compile-time printf checking; `Abort` and `Quit` are marked `AFS_NORETURN`.

Control flow: no runtime flow; annotations communicate non-returning behavior and format contracts to compilers and static analysis.

State and persistence: no state declared here. `Statistics` is defined in `common.c` but not exposed by this header.

Dependencies: expects OpenAFS attribute macros such as `AFS_ATTRIBUTE_FORMAT` and `AFS_NORETURN` to be available from included configuration headers in consumers.

Integration points: included by volume code needing shared logging or fatal helpers. It is part of the volume source tree rather than an installed public AFS header in this Makefile.

Risks: consumers that include it without prior OpenAFS attribute definitions may fail to compile. Since `Abort`/`Quit` are non-returning, incorrect annotations would affect optimizer/static-analysis assumptions.

Test signals: compile checks with GCC/Clang format warnings, splint/static-analysis coverage, and link checks against `common.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/daemon_com.c -->
## sources/distributed-fs/openafs/src/vol/daemon_com.c

Purpose: localhost synchronous command/response transport used by volume-related daemons and clients, currently over Unix-domain sockets when available or loopback TCP otherwise.

Important APIs/types/functions: client helpers include `SYNC_getAddr()`, `SYNC_getSock()`, `SYNC_connect()`, `SYNC_disconnect()`, `SYNC_closeChannel()`, `SYNC_reconnect()`, `SYNC_ask()`, and internal `SYNC_ask_internal()`. Server helpers include `SYNC_getCom()`, `SYNC_putRes()`, `SYNC_verifyProtocolString()`, `SYNC_cleanupSock()`, and `SYNC_bindSock()`. Globals include callback hook `V_BreakVolumeCallbacks`; constants include `MAXHANDLERS`, `MAX_BIND_TRIES`, and `AFS_SOCKADDR_LEN`.

Control flow: clients lazily connect, retry connection with a fixed backoff sequence, stamp outgoing command headers with protocol version, sequence numbers, pid/tid, and DAFS flags, write the command, optionally short-circuit channel close, then read and validate a response header/payload. `SYNC_ask()` wraps the low-level exchange with retry/reconnect behavior until retry count or hard timeout is exceeded. Servers read command headers and optional payloads with `readv`/`recv`, validate lengths, fill response headers with protocol version and sequence numbers, serialize response header/payload, and write it back. Binding configures `SO_REUSEADDR`, retries bind, and listens.

State and persistence: client state persists socket descriptor, endpoint, protocol version, sequence counters, retry/hard-timeout policy, and protocol name. Server state persists listening socket, endpoint address, protocol version, sequence counters, bind retry limit, and listen depth. Filesystem persistence is limited to Unix socket path creation/removal under the server local directory.

Dependencies: socket APIs (`socket`, `connect`, `bind`, `listen`, `send`/`recv` or `write`/`readv`), Unix socket path utilities, OpenAFS endpoint/protocol structures from `daemon_com.h`, LWP/pthread thread id helpers, `FT_ApproxTime`, logging from `common.c`, and platform abstractions such as `rk_closesocket` and `osi_socket`.

Integration points: shared by fileserver, volserver, salvageserver, salvager, FSSYNC, and SALVSYNC style local coordination. Protocol mismatch logs explicitly tell operators to keep fileserver, volserver, salvageserver, and salvager on the same version.

Risks: assumes full writes/reads for command and response sizes; partial socket I/O is treated as failure rather than looped. Connection setup can sleep for a long backoff sequence. Some error handling has duplicate unreachable statements. `SYNC_getSock()` uses `opr_Verify` and aborts on socket creation failure. Unix socket paths are formatted into fixed `sun_path`. Protocol length fields must be correct, or peers return `SYNC_COM_ERROR`.

Test signals: client/server loopback exchanges with and without payloads, channel close behavior, protocol mismatch `SYNC_BAD_COMMAND`, response too short/too long/bad length, retry/reconnect on dropped sockets, Unix and TCP endpoint address construction, bind retry and cleanup behavior, unterminated protocol string detection, sequence number increments, and partial I/O/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/daemon_com.c -->
