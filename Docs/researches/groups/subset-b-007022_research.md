# subset-b-007022 Research

Grouped source research for Coda volume utility server/client handlers, salvage and restore internals, version-vector list support, and the vtools Automake manifest. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-makevldb.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-makevldb.cc

## Purpose

`vol-makevldb.cc` implements the server-side `S_VolMakeVLDB` RPC used by `volutil makevldb` to rebuild Coda's binary Volume Location Database from a textual VolumeList. The complete 552-line file was read. It converts read-write, read-only, backup, and non-replicated volume records into hash-indexed `struct vldb` entries, writes `VLDB_TEMP`, atomically renames it to `VLDB_PATH`, and asks the fileserver to reload volume-location state.

## Important APIs, Types, and Functions

The public entry point is `S_VolMakeVLDB(RPC2_Handle, RPC2_String)`. Core helpers are `Pass()`, `VolumeEntry()`, `AddReadWriteEntry()`, `AddReadOnlyEntry()`, `AddBackupEntry()`, `Lookup()`, `Add()`, `Replace()`, `AddServer()`, `AddAssociate()`, `CheckRWindex()`, and `GetArgs()`. File-level state includes `vldb_array`, `Dates`, `RWindex`, `vldbSize`, `vldbHashSize`, `haveEntry`, and `AddedEntries`. `InitAddEntry()` maps Coda volume types to per-type add handlers.

## Control Flow

`S_VolMakeVLDB` opens the input file, runs `Pass('P')` to count lines, allocates an oversized in-memory VLDB/hash array, and then replays the file in type order: read-write, read-only, backup, then non-replicated. Each data pass parses single-letter fields such as `I`, `H`, `W`, `D`, `B`, and `C`, creates both numeric-key and name-key entries, and lets type-specific handlers decide whether to add, replace, or merge with existing entries. After header initialization, the whole array is written to `VLDB_TEMP`, renamed, and `VCheckVLDB()` is called.

## State and Persistence Behavior

Persistence is file-based rather than RVM-based. The rebuilt database is staged in a temporary file and installed with `rename()`. VLDB entries store network-order volume ids and a hash-chain stride in `hashNext`; copy, backup, or creation dates are kept only in the transient `Dates` array to select newest entries. Read-only servers are merged into a single entry when creation dates match, and associated read-only/backup ids are copied into matching read-write entries through `RWindex`.

## Dependencies and Integration Points

The file depends on `vldb.h`, `voltypes.h`, `voldefs.h`, `volume.h`, `vutil.h`, `srv.h`, `vice_file.h`, RPC2 error codes, and `HashString()`. It is invoked by the generated volutil RPC stub and by the client command in `volclient.cc`. It integrates with the fileserver through `VCheckVLDB()`.

## Risks and Test Signals

Risks include fixed-size line/argument buffers, no bounds check while probing for the next free hash slot, limited error propagation from `Pass()`, possible `nServers` overflow in `AddServer()`, and full-array binary writes that rely on exact on-disk struct layout. Useful tests include VolumeList fixtures for all four volume classes, duplicate/newer backup handling, read-only server merging, malformed field rejection, hash collision stress, temp-file rename failure, and reload notification verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-makevldb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-makevrdb.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-makevrdb.cc

## Purpose

`vol-makevrdb.cc` implements `S_VolMakeVRDB`, the volume utility RPC that translates a textual VRList into Coda's binary Volume Replication Database. The complete 131-line file was read. Its input format is a replicated group name, group volume id, VSG size, up to eight replica volume ids, and an ignored VSG address.

## Important APIs, Types, and Functions

The single service entry point is `S_VolMakeVRDB(RPC2_Handle, RPC2_String)`. It allocates `vrent` records from `vrdb.h`, fills `key`, `volnum`, `nServers`, and `ServerVolnum[]`, calls `vrent::hton()`, and writes fixed-size records to `VRDB_TEMP`.

## Control Flow

The handler creates `VRDB_TEMP`, opens the input file, scans each line with `sscanf`, validates field count and volume-name length, writes one converted `vrent` per valid line, and aborts on parse or write failure. At EOF it renames the temp file to `VRDB_PATH`, logs the number of entries, and calls `CheckVRDB()` so the fileserver refreshes replication metadata.

## State and Persistence Behavior

Persistence is a flat binary database installed by temp-file rename. The handler does not update RVM directly. It deletes each heap-allocated `vrent` after writing; on early error it closes handles but leaves cleanup of any partial temp file to later operations.

## Dependencies and Integration Points

Dependencies include `vrdb.h`, `volume.h`, `vice.h`, `volutil.h`, and RPC2 error conventions. It is the server counterpart for `volclient.cc`'s `makevrdb()` command and feeds the VRDB used by replicated-volume translation such as `XlateVid()`.

## Risks and Test Signals

Risks include accepting `servercount` without validating it against the number of parsed replica ids, fixed `line[500]`, possible stale temp file after failures, and no validation that replica ids are nonzero or unique. Tests should cover valid maximum-width VRList rows, short rows, overlong names, bad writes, rename failure, network-order round trips, and post-build `CheckVRDB()` reload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-makevrdb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-maxid.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-maxid.cc

## Purpose

`vol-maxid.cc` exposes administrative RPCs to read and safely advance the server's maximum allocated volume id. The complete 88-line file was read. It protects the server-id byte embedded in volume ids and prevents lowering the allocator watermark.

## Important APIs, Types, and Functions

`S_VolGetMaxVolId()` returns `VGetMaxVolumeId()`. `S_VolSetMaxVolId()` validates the requested id against `SRV_RVM(MaxVolId)`, then calls `VSetMaxVolumeId()` inside an RVM transaction.

## Control Flow

The get path is direct and side-effect free. The set path rejects any id with a different high server-id byte and rejects ids less than the current maximum. Only then does it begin a `restore` transaction, update `MaxVolId`, and flush the transaction.

## State and Persistence Behavior

The only persistent mutation is `SRV_RVM(MaxVolId)`, through the volume-layer setter. Transaction boundaries make the update recoverable in RVM. There is no explicit `VInitVolUtil()` call here; it relies on the volutil worker context already being initialized.

## Dependencies and Integration Points

Dependencies include `recov.h`, `camprivate.h`, `coda_globals.h`, `volume.h`, `rvmlib`, and `volutil.h`. The client commands are `volutil getmaxvol` and `volutil setmaxvol` in `volclient.cc`.

## Risks and Test Signals

Risks are mostly administrative: setting an unexpectedly high id can create large gaps, while validation only checks high-byte server identity and monotonicity. Tests should cover get, successful monotonic set, server-id mismatch rejection, lower-id rejection, transaction failure propagation, and persistence across restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-maxid.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-printstats.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-printstats.cc

## Purpose

`vol-printstats.cc` implements `S_PrintStats`, an administrative RPC that captures server counters and callback state and transfers them back to the volutil client over SMARTFTP. The complete 81-line file was read.

## Important APIs, Types, and Functions

The only exported service handler is `S_PrintStats(RPC2_Handle, SE_Descriptor *)`. It uses `tmpfile()`, `PrintCounters()`, `PrintCallBackState()`, `RPC2_InitSideEffect()`, and `RPC2_CheckSideEffect()`.

## Control Flow

The handler writes stats to an unnamed temporary file, seeks back to offset zero, constructs a `SERVERTOCLIENT` SMARTFTP descriptor using `FILEBYFD`, initializes the side effect, waits for local status, closes the file, and returns the RPC/side-effect status.

## State and Persistence Behavior

It has no persistent state. It reads current in-memory counters and callback state, and the temporary file is closed after transfer.

## Dependencies and Integration Points

The file depends on RPC2 side effects, `srv.h` stats/callback printers, and `volutil.h`. It is called by `volclient.cc`'s `printstats()` command.

## Risks and Test Signals

Risks include transferring large callback dumps through a temporary file, losing the original client-supplied side-effect descriptor, and returning side-effect error codes directly. Tests should mock SMARTFTP failure paths, verify file rewind before transfer, and confirm both counter and callback sections are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-printstats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-purge.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-purge.cc

## Purpose

`vol-purge.cc` implements `S_VolPurge`, the destructive administrative RPC that removes a named volume from recoverable and in-memory volume state. The complete 171-line file was read.

## Important APIs, Types, and Functions

The service entry point is `S_VolPurge(RPC2_Handle, RPC2_Unsigned, RPC2_String)`. It uses `VInitVolUtil()`, `VGetVolume()`, `VAttachVolume()`, `VOffline()`, `DeleteVolume()`, `VDisconnectFS()`, and the LWP `FSTAG` `ProgramType` rock to temporarily act as a fileserver for offline transition.

## Control Flow

The handler initializes volume utility mode, gets or attaches the target volume, verifies the caller-supplied name matches the internal volume name, forces the volume offline if it was online, asserts it is no longer in use, deletes the volume, marks the VM object as shutting down, prints the hash table, disconnects from the fileserver, and returns either the purge status or earlier error.

## State and Persistence Behavior

`DeleteVolume()` removes volume state from RVM and VM structures and should handle inode/header cleanup through the volume layer. The handler does not start its own RVM transaction; it relies on lower-level delete semantics. It mutates the per-LWP program type while forcing `VOffline()`.

## Dependencies and Integration Points

Dependencies include `rvmlib`, `volume.h`, `viceinode.h`, `partition.h`, `vutil.h`, `recov.h`, and `volutil.h`. It is called by the `volutil purge VolumeId VolumeName` client path and interacts with normal volume attachment/offline machinery.

## Risks and Test Signals

Risks include destructive action guarded only by id plus exact name, reliance on asserts for offline/in-use invariants, no callback to put an unexpectedly attached volume back online on late failure, and ambiguous handling of offline `VGetVolume()` results. Tests should cover online purge, already-offline purge, name mismatch, nonexistent volume, attach failure, and post-purge hash/RVM absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-purge.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-restore.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-restore.cc

## Purpose

`vol-restore.cc` implements server-side volume restore from a dump streamed by the volutil client over the `VOLDUMP_SUBSYSTEMID` side channel. The complete 792-line file was read. It creates a new restored volume, reconstructs large and small vnode lists in RVM, rebuilds file and directory data, and brings the restored volume online.

## Important APIs, Types, and Functions

The exported entry point is `S_VolRestore()`. Major helpers are `RestoreVolume()`, `FreeVnodeIndex()`, `ReadLargeVnodeIndex()`, `ReadSmallVnodeIndex()`, and `ReadVnodeDiskObject()`. It uses dump parsing helpers from `voldump.h`/`dump.h`, inode operations such as `icreate()` and `iopen()`, directory inode helpers `DI_Copy()`/`DI_VMFree()`, RVM list storage `rec_smolist`, and volume APIs `VCreateVolume()`, `VUpdateVolume()`, `VDetachVolume()`, and `HashDelete()`.

## Control Flow

`S_VolRestore` initializes volutil state, validates the partition and requested id, binds back to the client dump subsystem, allocates a dump buffer, and calls `RestoreVolume()`. `RestoreVolume()` reads and validates a full dump header, rejects incremental and illegal read-write/replicated volume types, creates or allocates a target id in a transaction, creates a provisional volume, reads large and small vnode indexes, validates end-of-dump, copies dumped disk data into the volume header, marks the volume blessed/in service, updates and detaches it. Vnode reads are batched by `VnodePollPeriod` so long restores periodically end transactions and yield.

## State and Persistence Behavior

Restore mutates RVM volume metadata, RVM vnode-list arrays, recoverable vnode objects, directory inodes, and underlying vice inodes for file data. Provisional vnode lists from `VCreateVolume()` are freed before restored lists are installed. On failure after volume creation, `S_VolRestore` calls `HashDelete(*volid)` but many partial disk/RVM side effects depend on transaction aborts and later salvage. Dump content is streamed from the client rather than read from a server-side path.

## Dependencies and Integration Points

Dependencies include `rvmlib`, `recov`, `camprivate`, `partition`, `viceinode`, `volhash`, `voldump`, `al`, `fssync`, `codadir`, RPC2 SMARTFTP, and dump-buffer code. The client side is `volclient.cc`'s `restorefromback()` plus `S_ReadDump()`.

## Risks and Test Signals

Risks include partial restore cleanup, multiple places that return without freeing newly allocated directory pages or closing handles on error, reliance on dump tag correctness, host-endian dump assumptions, and `CODA_ASSERT` for RVM allocation/list invariants. Tests should cover full restore, id allocation and `MaxVolId` update, duplicate id rejection, bad partition, incremental dump rejection, malformed vnode tags, directory ACL externalization, file-data transfer failure, and salvage of interrupted restores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-restore.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-rvmsize.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-rvmsize.cc

## Purpose

`vol-rvmsize.cc` implements `S_VolRVMSize`, an administrative estimator for the RVM space consumed by a volume's header, vnode list arrays, vnode records, directory inodes, and directory pages. The complete 130-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_VolRVMSize(RPC2_Handle, VolumeId, RVMSize_data *)`. It uses `XlateVid()`, `VGetVolume()`, `SRV_RVM(VolumeList[])`, `vindex`, `vindex_iterator`, `DI_Pages()`, and `VPutVolume()`.

## Control Flow

The handler initializes volutil mode, translates replicated ids to local replica ids, attaches the volume, accumulates fixed header/list sizes, fills vnode count and byte fields in `RVMSize_data`, iterates large vnodes to add directory-page bytes, then releases the volume and disconnects.

## State and Persistence Behavior

The handler is read-only with respect to persistent volume state. It computes from in-memory/RVM metadata and returns the result through the RPC output structure.

## Dependencies and Integration Points

Dependencies include `camprivate.h`, `vrdb.h`, `index.h`, `coda_globals.h`, `codadir.h`, and `volutil.h`. The client formatter is `volclient.cc`'s `rvmsize()` command.

## Risks and Test Signals

Risks include approximate accounting, assuming all large vnodes have valid `dirNode` pointers, ignoring volume logs and allocator overhead, and returning zero `status` even if accounting undercounts. Tests should compare known synthetic volumes, missing-volume errors, replicated id translation, directory page accounting, and empty-volume handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-rvmsize.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-rvmtrunc.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-rvmtrunc.cc

## Purpose

`vol-rvmtrunc.cc` implements asynchronous RVM log truncation for volutil. The complete 71-line file was read. It starts a separate LWP with a larger stack so the RPC can return while `rvm_truncate()` continues.

## Important APIs, Types, and Functions

`S_TruncateRVMLog(RPC2_Handle)` creates the LWP. `TruncProcess(void *)` calls `rvm_truncate()`, logs start/end, and destroys its own process. `rvm_truncate_stack` defaults to 1024 KB.

## Control Flow

The RPC logs the request, calls `LWP_CreateProcess()` with `TruncProcess`, and immediately returns that creation status. The worker performs synchronous truncation and exits.

## State and Persistence Behavior

The operation mutates the RVM log outside the caller's request path. There is no additional persistent state in this file and no result channel for truncation success after the worker starts.

## Dependencies and Integration Points

Dependencies include `rvm/rvm.h`, LWP, RPC2, `srv.h`, and `volutil.h`. The client command is `volutil truncatervmlog`.

## Risks and Test Signals

Risks include concurrent truncation requests, no completion/error reporting to the client, and global stack-size tuning. Tests should verify LWP creation failure handling, one successful truncate invocation, server logging, and behavior when a second truncate is requested while one is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-rvmtrunc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-salvage.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-salvage.cc

## Purpose

`vol-salvage.cc` implements Coda's partition and volume salvager. The complete 1715-line file was read. It can run as startup/full salvager or as a volume utility request, scans partition inodes, summarizes RVM volume headers, repairs vnode/inode correspondence, clears salvage flags, optionally verifies directory completeness and resolution logs, and cleans orphaned inodes or destroyed volumes.

## Important APIs, Types, and Functions

The public RPC/direct entry point is `S_VolSalvage()`. Major helpers include `SalvageFileSys()`, `SalvageVolumeGroup()`, `QuickCheck()`, `SalvageVolHead()`, `VnodeInodeCheck()`, `DirCompletenessCheck()`, `DistilVnodeEssence()`, `JudgeEntry()`, `MarkLogEntries()`, `CleanInodes()`, `ClearROInUseBit()`, `AskOffline()`, `AskOnline()`, `GetSkipVolumeNumbers()`, `SanityCheckFreeLists()`, `DestroyBadVolumes()`, `FixInodeLinkcount()`, `GetInodeSummary()`, `GetVolumeSummary()`, `CompareInodes()`, and `CompareVolumes()`.

## Control Flow

`S_VolSalvage` initializes global flags, chooses `volumeUtility` or `salvager` mode, reads skip lists and free-list state for full salvage, then salvages either all partitions or a selected partition/volume. `SalvageFileSys` locks the partition, handles `FORCESALVAGE`, offlines a selected volume, builds a sorted inode summary file, builds a sorted volume summary from RVM, and salvages each matching volume group in one RVM transaction. `SalvageVolumeGroup` skips configured volumes, fast-paths clean headers through `QuickCheck`, loads the group's inodes, checks volume headers, validates/repairs small vnode inode references, optionally runs directory completeness checks, and fixes remaining inode link counts.

## State and Persistence Behavior

The salvager mutates RVM volume headers (`inUse`, `needsSalvaged`, `dontSalvage`, `needsCallback`, file/block counts), vnode disk objects, free lists, resolution logs, volume hash entries, and underlying vice inode link counts. It uses temporary files `/tmp/salvage.inodes` and `/tmp/salvage.temp` for inode listings and summaries. Many mutations are inside RVM transactions, but raw inode operations are not rolled back by transaction aborts. Global state is reset by `zero_globals()`.

## Dependencies and Integration Points

Dependencies span `partition` inode listing, `inodeops`, `rvmlib`, `codadir`, `volume`, `fssync`, `vutil`, `index`, `recov`, `camprivate`, `volhash`, `bitmap`, `recle`, and `vice_file`. It coordinates with the running fileserver through FSYNC offline/online requests and lock files, and with resolution logging through `recov_vol_log`.

## Risks and Test Signals

Risks include raw inode side effects that survive RVM aborts, heavy use of `CODA_ASSERT` on corrupt input, fixed `/tmp` file names, a likely typo `unlink("forcepath")`, commented-out directory repair despite checking, and ambiguity for read-only versus read-write volume identity. Tests should cover full and single-volume salvage, skip list handling, clean `DONT_SALVAGE` quick path, missing inode repair, barren/debarrenize flows, orphan inode cleanup, destroyed-volume removal, directory completeness fatal cases, resolution-log salvage, and interrupted salvage followed by restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-salvage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-salvage.private.h -->
# sources/distributed-fs/coda/coda-src/volutil/vol-salvage.private.h

## Purpose

`vol-salvage.private.h` defines the private data structures and internal prototypes shared within the salvage implementation. The complete 117-line header was read. It documents the salvager's core summaries for partition inodes, volumes, vnode essence, vnode-class state, and directory traversal.

## Important APIs, Types, and Functions

Important declarations include `readOnly(vsp)`, `InodeSummary`, `VolumeSummary`, `VnodeEssence`, `VnodeInfo`, and `DirSummary`. It prototypes all internal salvage phases: summary construction, volume-group salvage, quick checks, vnode/inode checks, directory completeness, free-list sanity, inode cleanup, callback/offline helpers, skip-list logic, and global reset.

## Control Flow

The header has no executable flow, but it encodes the staged salvager pipeline: build inode and volume summaries, run checks, apply corrections, coordinate with fileserver state, and release locks/reset globals.

## State and Persistence Behavior

The structs carry transient mirrors of persistent state. `InodeSummary` records offsets into the temporary inode file. `VolumeSummary` connects RVM volume headers to inode summaries and optional resolution logs/bitmaps. `VnodeEssence` and `VnodeInfo` are in-memory distilled views used to validate directory references and volume accounting.

## Dependencies and Integration Points

It depends on `rec_dlist.h`, `bitmap.h`, and `recov_vollog.h`, and assumes types from volume/vnode/directory headers are already visible. It is included by `vol-salvage.cc`.

## Risks and Test Signals

Risks include macro-based read-only classification, static prototypes in a private header, signed link-count assumptions in `VnodeEssence::count`, and tight coupling to salvage globals. Test coverage comes indirectly from salvage tests that exercise summaries, log bitmaps, directory traversal, and skip-list helper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-salvage.private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-setlogparms.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-setlogparms.cc

## Purpose

`vol-setlogparms.cc` implements `S_VolSetLogParms`, the administrative RPC for enabling/disabling RVM resolution logging on a volume and increasing the log admin limit. The complete 145-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_VolSetLogParms(RPC2_Handle, VolumeId, RPC2_Integer, RPC2_Integer)`. It uses `VInitVolUtil()`, `XlateVid()`, `VGetVolume()`, `V_RVMResOn()`, `V_VolLog()`, `recov_vol_log::Increase_Admin_Limit()`, `VUpdateVolume()`, RVM transactions, and `VPutVolume()`.

## Control Flow

After initializing and translating the id, the handler attaches the volume and validates `OnFlag`. It updates `ResOn` for `RVMRES` or `0`, begins a transaction, optionally validates that the requested log size is a multiple of 32, increases the admin limit if resolution/log storage are active, updates the volume header, flushes or aborts the transaction, releases the volume, and disconnects.

## State and Persistence Behavior

It persistently mutates the volume header's `ResOn` flag and possibly the recoverable volume log admin limit. Header update and log limit change are wrapped in one RVM transaction.

## Dependencies and Integration Points

Dependencies include `rvmlib`, `vrdb.h`, `srv.h`, `vutil.h`, `volume.h`, and `recov_vollog.h`. The client command is `volutil setlogparms <volid> reson <flag> logsize <nentries>`.

## Risks and Test Signals

Risks include changing `ResOn` before `rvmlib_begin_transaction()`, allowing unsupported flags only by runtime validation, and only supporting log-size increases in practice. Tests should cover enable, disable, invalid flag, invalid size multiple, replicated id translation, inactive resolution with log-size request, and persistence across detach/reattach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-setlogparms.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-setvv.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-setvv.cc

## Purpose

`vol-setvv.cc` implements `S_VolSetVV`, an emergency administrative RPC that replaces an object's version vector or debarrenizes a barren vnode. The complete 175-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_VolSetVV(RPC2_Handle, RPC2_Unsigned, RPC2_Unsigned, RPC2_Unsigned, ViceVersionVector *)`. It uses `XlateVid()`, `VInitVolUtil()`, `VGetVolume()`, `VGetVnode()`, `VPutVnode()`, `VRDB.find()`, `AddVVs()`, `CodaBreakCallBack()`, `icreate()`, barren/inconsistent version-vector helpers, and RVM transactions.

## Control Flow

The handler translates group ids to local ids, begins a transaction, gets the volume and target vnode with a write lock, and either copies the supplied version vector or, on `EIO`, reopens a barren vnode, clears barren state, marks it inconsistent, creates a fresh inode, and ignores the supplied vector. It then increments the volume version vector at this host's VRDB index, breaks callbacks for the original fid, puts vnode/volume, flushes the transaction, and disconnects.

## State and Persistence Behavior

Persistent mutations include vnode version vector or barren repair fields, vnode inode number/data version, volume version vector, and callback invalidation. The operation is explicitly lock-light and intended for bad situations.

## Dependencies and Integration Points

Dependencies include `vrdb.h`, `partition.h`, `viceinode.h`, `srv.h`, `volume.h`, and `rvmlib`. The client path is `volclient.cc`'s `setvv()` parser, which requires eight site versions, store id host/uniquifier, and flags.

## Risks and Test Signals

Risks include direct manual consistency changes, fatal `Die()` if VRDB lacks the volume group or local host, creating empty inodes during debarrenize, and sparse error cleanup around `VGetVnode()`. Tests should cover normal vector set, barren debarrenize path, missing volume/vnode errors, callback break verification, VRDB host-index failure, and transaction abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-setvv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-showcallbacks.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-showcallbacks.cc

## Purpose

`vol-showcallbacks.cc` implements `S_ShowCallbacks`, a diagnostics RPC that prints callbacks for a specific fid plus global callback state and transfers the report to the client. The complete 82-line file was read.

## Important APIs, Types, and Functions

The exported handler is `S_ShowCallbacks(RPC2_Handle, ViceFid *, SE_Descriptor *)`. It uses `tmpfile()`, `PrintCallBacks()`, `PrintCallBackState()`, and SMARTFTP `FILEBYFD` side effects.

## Control Flow

The handler writes callback information into an unnamed temporary file, rewinds it, initializes a `SERVERTOCLIENT` side-effect transfer by file descriptor, waits for local status, closes the temporary file, and returns the transfer status.

## State and Persistence Behavior

It has no persistent mutations. It reads in-memory callback structures for diagnostics.

## Dependencies and Integration Points

Dependencies include RPC2, `srv.h`, callback printers, and `volutil.h`. The client path is `volclient.cc`'s `showcallbacks()` command.

## Risks and Test Signals

Risks include large callback dumps, failure to preserve caller-provided descriptor fields, and direct return of side-effect errors. Tests should verify fid formatting, empty/no-callback cases, side-effect failures, and inclusion of global callback state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-showcallbacks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-showvnode.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-showvnode.cc

## Purpose

`vol-showvnode.cc` implements `S_VolShowVnode`, a diagnostics RPC that dumps one vnode's metadata, optional directory contents, and optional resolution log to a SMARTFTP result file. The complete 199-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_VolShowVnode(RPC2_Handle, RPC2_Unsigned, RPC2_Unsigned, RPC2_Unsigned, SE_Descriptor *)`. It uses `XlateVid()`, `VGetVolume()`, `VGetVnode()`, `FPrintVV()`, directory cache helpers `DC_Get()`/`DH_Print()`/`DC_Put()`, `PrintLog()`, and SMARTFTP `FILEBYNAME`.

## Control Flow

The handler translates replicated ids, starts a transaction, attaches the volume, reads the vnode with barren access allowed, writes metadata to `/tmp/vshowvnode.tmp`, prints directory and resolution-log details when applicable, releases the volume, ends the transaction, closes the file, and transfers it back to the client.

## State and Persistence Behavior

The operation is intended as read-only diagnostics. It still opens a transaction and uses a fixed temporary path. It puts the vnode at exit after the transfer setup.

## Dependencies and Integration Points

Dependencies include `srv.h`, `volume.h`, `partition.h`, `viceinode.h`, `vutil.h`, `vrdb.h`, `codadir.h`, and resolution-log headers. The client path is `volclient.cc`'s `showvnode()`.

## Risks and Test Signals

Risks include fixed `/tmp` filename races, returning after `VPutVolume()` but before `VPutVnode()`, side-effect path exposure, and assert-prone directory/log printing on corrupt vnodes. Tests should cover files, directories, symlinks, barren vnodes, missing vnode/volume, replicated id translation, output file transfer, and concurrent requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-showvnode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-timing.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-timing.cc

## Purpose

`vol-timing.cc` implements `S_VolTiming`, which toggles server timing/probing and transfers processed timing traces when disabled. The complete 115-line file was read.

## Important APIs, Types, and Functions

The service entry point is `S_VolTiming(RPC2_Handle, RPC2_Integer, SE_Descriptor *)`. It uses global `probingon`, `tpinfo`, `FileresTPinfo`, `timing_path::postprocess()`, and SMARTFTP `FILEBYNAME` transfer from `/tmp/timing.tmp`.

## Control Flow

When `OnFlag` is true, the handler initializes volutil mode and sets `probingon`. When `OnFlag` is false and probing is active, it disables probing, writes processed timing-path reports to the temp file, deletes timing buffers, transfers the file to the client, and disconnects.

## State and Persistence Behavior

It mutates in-memory timing globals only. The temporary report path is fixed and not persistent configuration.

## Dependencies and Integration Points

Dependencies include LWP timers, RPC2 side effects, `timing.h`, `volume.h`, `vice.h`, and `util.h`. The client path is `volclient.cc`'s `timing on|off [file]` command.

## Risks and Test Signals

Risks include fixed temp-file races, no transfer when `off` is requested while probing is already off, deletion of global timing buffers, and side-effect error returns as `-1`. Tests should cover on/off transitions, double-off behavior, postprocess output for both timing buffers, side-effect failures, and cleanup of globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-timing.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-tracerpc.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vol-tracerpc.cc

## Purpose

`vol-tracerpc.cc` implements `S_TraceRpc`, a diagnostics RPC that toggles RPC2 tracing and returns trace-buffer/state output to the client. The complete 103-line file was read.

## Important APIs, Types, and Functions

The entry point is `S_TraceRpc(RPC2_Handle, SE_Descriptor *)`. It uses global `RPCTraceBufInited`, `RPC2_Trace`, `RPC2_InitTraceBuffer()`, `RPC2_DumpTrace()`, `RPC2_DumpState()`, and SMARTFTP transfer by file descriptor.

## Control Flow

On first call it initializes a 500-entry trace buffer and enables tracing. If initialized but disabled, it enables tracing. If already enabled, it dumps trace buffers and RPC2 state to a temporary file and disables tracing. Every call transfers a short status or dump file to the client.

## State and Persistence Behavior

The handler mutates in-memory RPC2 tracing globals only. No persistent files are kept after the temporary file closes.

## Dependencies and Integration Points

Dependencies include RPC2 tracing APIs, SMARTFTP side effects, and `volutil.h`. The client command is `volutil tracerpc [outfile]`.

## Risks and Test Signals

Risks include process-global trace toggling from an admin command, fixed buffer size, and potential large dumps. Tests should cover first-call initialization, enable-after-disable, dump-and-disable path, side-effect failures, and trace state after each call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-tracerpc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/volclient.cc -->
# sources/distributed-fs/coda/coda-src/volutil/volclient.cc

## Purpose

`volclient.cc` is the command-line client for Coda volume utility administration. The complete 2083-line file was read. It parses global options, binds to the fileserver's volutil RPC subsystem with either the shared volutil key or Coda tokens, dispatches many administrative subcommands, and implements the client-side dump/restore side-channel service.

## Important APIs, Types, and Functions

Important functions include `main()`, `ReadConfigFile()`, `V_InitRPC()`, `V_BindToServer()`, `VolDumpLWP()`, `S_WriteDump()`, `S_ReadDump()`, and command handlers such as `create()`, `create_rep()`, `clone()`, `backup()`, `dump()`, `restorefromback()`, `makevldb()`, `makevrdb()`, `dumpvrdb()`, `info()`, `showvnode()`, `setvv()`, `purge()`, `lock()`, `unlock()`, `updatedb()`, `timing()`, `tracerpc()`, `printstats()`, `showcallbacks()`, `rvmsize()`, `setlogparms()`, `getmaxvol()`, and `setmaxvol()`. `rockInfo` tracks dump file descriptors, target volume id, and byte offsets.

## Control Flow

`main()` loads `server.conf`, resolves `-h`, `-r`, `-t`, and `-d`, initializes LWP/RPC2/SFTP, binds to the server, stores `argv` in globals, and dispatches by subcommand name. Most command handlers parse positional arguments, build optional SMARTFTP descriptors for output files, call the matching generated RPC stub, print result text, and exit. Dump and restore create a local `VolDumpLWP` that exports `VOLDUMP_SUBSYSTEMID`; the server calls back into `S_WriteDump()` for dumping or `S_ReadDump()` for restore file streaming.

## State and Persistence Behavior

The client owns no Coda server persistence directly. It can request destructive server mutations such as purge, restore, setvv, setlogparms, shutdown, database rebuilds, and max-volume-id changes. Local state includes RPC binding handles, selected host/realm, the process-wide argument globals, temporary output file descriptors, and dump byte counters.

## Dependencies and Integration Points

Dependencies include LWP, RPC2, SFTP, auth token helpers, `codaconf`, `vice_file`, generated volutil/voldump stubs, partition/volume headers, and service lookup via `coda_getservbyname("codasrv", "udp")`. It integrates with server handlers in this directory and with external admin scripts such as `createvol_rep`, `bldvldb`, and clone/backup workflows.

## Risks and Test Signals

Risks include global argument and RPC state, many `exit()` paths, sparse file-open error checks, dump/restore side-channel loops that run forever, host-endian dump assumptions, typo-prone manual parsing, and highly privileged operations protected by local key/token availability. Tests should cover command usage errors, auth selection, binding failures, each RPC argument marshalling path, SMARTFTP output descriptors, dump/restore offset accounting, large dump transfer, and failure messages for server-side errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/volclient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/volutil.cc -->
# sources/distributed-fs/coda/coda-src/volutil/volutil.cc

## Purpose

`volutil.cc` is the fileserver-side RPC service harness for volume utility requests. The complete 357-line file was read. It exports the utility subsystem, starts worker LWPs, authenticates admin callers, dispatches generated volutil RPC requests, and provides several simple administrative service handlers.

## Important APIs, Types, and Functions

Key functions are `InitVolUtil()`, `VolUtilLWP()`, `InitServer()`, `IsAdminUser()`, `VolGetKey()`, `GetVolId()`, `S_VolUpdateDB()`, `S_VolShutdown()`, `S_VolSwaplog()`, `S_VolSwapmalloc()`, `S_VolSetDebug()`, `S_VolMerge()`, and stubbed debug-memory handlers `S_VolDumpMem()`, `S_VolPeekInt()`, `S_VolPokeInt()`, `S_VolPeekMem()`, and `S_VolPokeMem()`.

## Control Flow

`InitVolUtil()` exports `UTIL_SUBSYSID` and starts two `VolUtilLWP` workers. Each worker initializes per-thread RVM state when needed, tags itself with `FSTAG=volumeUtility`, blocks in `RPC2_GetRequest()` with `VolGetKey()` authentication, dispatches through `volUtil_ExecuteRequest()`, logs errors, and unbinds failed connections. `VolGetKey()` authenticates Coda tokens and checks `System:Administrators`, or falls back to the volutil shared key for legacy clients.

## State and Persistence Behavior

The harness mutates process state: exported RPC subsystem, worker LWPs, per-thread RVM structures, logging/debug levels, malloc tracing, shutdown flag via `ViceTerminate()`, and database reload via `ViceUpdateDB()`. Memory peek/poke RPCs are intentionally disabled and return "use gdb" behavior.

## Dependencies and Integration Points

Dependencies include RPC2, RVM, auth2, getsecret, access-list group checks, `srv.h`, `vldb.h`, and generated `volUtil_ExecuteRequest()`. It is the server counterpart to `volclient.cc`.

## Risks and Test Signals

Risks include only two utility workers, backward-compatible shared-key auth, process-wide debug changes, reliance on LWP rocks for program type, and broad administrative authority once authenticated. Tests should cover token admin acceptance/rejection, shared-key auth, worker dispatch, unbind-on-error behavior, `GetVolId()` numeric/name lookup, debug level propagation, shutdown/update requests, and disabled memory-debug RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/volutil.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/volutil.private.h -->
# sources/distributed-fs/coda/coda-src/volutil/volutil.private.h

## Purpose

`volutil.private.h` declares shared private definitions for Coda volume utility implementation files. The complete 60-line header was read.

## Important APIs, Types, and Functions

It defines `VOLUTIL_TIMEOUT`, `VOLUTIL_RESTART`, and `VOLUTIL_ABORT`, and declares `CloneVnode()` and `PrintVersionVector()`. `CloneVnode()` is annotated as requiring a transaction.

## Control Flow

The header has no executable flow. It centralizes prototypes and constants used by implementation files in the volutil subsystem.

## State and Persistence Behavior

There is no state in this header. `CloneVnode()`'s contract implies persistent RVM/vnode mutation in its implementation, while the header only exposes the transaction expectation.

## Dependencies and Integration Points

It depends on `coda_tsa.h` for transaction annotations and assumes volume/vnode types are visible to consumers. It is included by salvage and clone-related volutil code.

## Risks and Test Signals

Risks are interface drift and weak type isolation: this private header exposes low-level helpers but not their owning modules. Tests are indirect through clone and volume utility code that uses `CloneVnode()` and version-vector printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/volutil.private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vvlist.cc -->
# sources/distributed-fs/coda/coda-src/volutil/vvlist.cc

## Purpose

`vvlist.cc` implements backup dump version-vector list support. The complete 276-line file was read. It writes per-vnode version-vector records for dumps and reads earlier lists to decide whether each vnode changed for incremental backups.

## Important APIs, Types, and Functions

Functions include `getlistfilename()`, `ValidListVVHeader()`, `DumpListVVHeader()`, `ListVV()`, `vvtable::vvtable()`, `vvtable::~vvtable()`, `vvtable::IsModified()`, `vvent_iterator::vvent_iterator()`, and `vvent_iterator::operator()()`. It works with `vvent`, `ViceStoreId`, `ViceVersionVector`, `Volume`, and `VnodeDiskObject`.

## Control Flow

Dump helpers build backup-list filenames and write human-readable headers and vnode lines. The `vvtable` constructor parses a previous list file, hashes entries by vnode bit number, and stops at `ENDLARGEINDEX` for large-vnode lists or EOF for small-vnode lists. `IsModified()` checks whether the current vnode's unique and store id match an old entry and applies dump-level rules so a lower-level incremental includes changes from higher-level incrementals when needed.

## State and Persistence Behavior

The persisted state is a text file in the backup directory named from group id, replica id, and suffix. In memory, `vvtable` owns an array of linked `vvent` lists and marks entries `isThere` when encountered. It frees all entries in the destructor.

## Dependencies and Integration Points

Dependencies include `vcrcommon.h`, `voltypes.h`, `srv.h`, `vrdb.h`, `vutil.h`, `vice_file.h`, and `vvlist.h`. The code integrates with volume dump/backup paths that need incremental backup decisions.

## Risks and Test Signals

Risks include fixed line sizes, loose parsing compatibility (`n == 12` defaulting dump level to zero), asserts on bad vnode indexes, and linked-list memory ownership. Tests should cover header validation, filename generation with and without group ids, round-trip line parsing, new/unchanged/changed vnode decisions, multilevel incremental behavior, bad index handling, and iterator traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vvlist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vvlist.h -->
# sources/distributed-fs/coda/coda-src/volutil/vvlist.h

## Purpose

`vvlist.h` declares the text-format version-vector list API used by Coda backup and incremental dump code. The complete 64-line header was read.

## Important APIs, Types, and Functions

It defines `vvent`, `ENDLARGEINDEX`, `LISTLINESIZE`, class `vvtable`, class `vvent_iterator`, and functions `ValidListVVHeader()`, `DumpListVVHeader()`, `ListVV()`, and `getlistfilename()`.

## Control Flow

The header exposes construction of a parsed table from an ancient list file, lookup of modification state through `IsModified()`, and one-bucket iteration through `vvent_iterator`.

## State and Persistence Behavior

`vvent` stores parsed previous-dump state: unique id, store id, seen flag, linked-list next pointer, and dump level. The header describes in-memory ownership but the text files are produced/consumed by `vvlist.cc`.

## Dependencies and Integration Points

Dependencies include `vcrcommon.h` and `cvnode.h`; callers also need volume and vnode disk types. It is part of the volutil backup/dump implementation boundary.

## Risks and Test Signals

Risks include manual linked-list ownership, fixed list line length, and friend-based iterator access. Tests should compile users against the public declarations and exercise table construction, `IsModified()`, and iterator behavior through `vvlist.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vvlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/Makefile.am -->
# sources/distributed-fs/coda/coda-src/vtools/Makefile.am

## Purpose

`vtools/Makefile.am` is the Automake manifest for Coda venus/client-side command tools. The complete 50-line file was read. It selects installed programs, scripts, man pages, source files, distribution extras, and clean files for the `vtools` directory.

## Important APIs, Types, and Functions

This is build metadata, not C/C++ code. Important Automake variables are `bin_PROGRAMS`, `dist_man_MANS`, `bin_SCRIPTS`, `sbin_PROGRAMS`, per-target `_SOURCES`, `EXTRA_DIST`, and `CLEANFILES`. Conditional blocks use `BUILD_CLIENT` and `HAVE_PYTHON`.

## Control Flow

Automake conditionals install client tools only when `BUILD_CLIENT` is true. If Python is available, `gcodacon` is installed as a script. `codaconfedit` is always listed as an sbin program. Source variables map each program target to its implementation files.

## State and Persistence Behavior

There is no runtime state. Build-time outputs include generated `Makefile.in`, compiled tool binaries, installed man pages, optional scripts, distributed helper scripts, and cleaned generated script files.

## Dependencies and Integration Points

The manifest integrates with the repository's Autotools build system and source files such as `codacon.cc`, `cfs.cc`, `cmon.cc`, `coda_replay.cc`, `hoard.cc`, and `spy.cc`. It also ensures logging helper scripts are included in distribution tarballs through `EXTRA_DIST`.

## Risks and Test Signals

Risks include missing sources causing build failures, conditional installation mismatches, generated script cleanup issues, and tools/man pages drifting out of sync. Test signals are `autoreconf`/`automake` generation, `make distcheck`, builds with `BUILD_CLIENT` on/off, builds with `HAVE_PYTHON` on/off, and install-manifest checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/Makefile.am -->
