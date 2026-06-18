# Research Report: subset-b-007821

This grouped report covers the OpenAFS volume and volserver files assigned to `subset-b-007821`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volume.h -->
# sources/distributed-fs/openafs/src/vol/volume.h

## Purpose
Defines the core OpenAFS volume package ABI: on-disk volume header formats, in-memory `Volume` state, attachment modes, package options, statistics structures, lock macros, and externally visible volume-management functions. It is consumed by fileserver, volserver, salvager, utilities, and dump/restore paths.

## Important APIs, Types, And Constants
Key types include `ProgramType`, `VolumePackageOptions`, `VolumeHeader_t`, `VolumeDiskHeader_t`, `VolumeDiskData`, `VolPkgStats`, `VolumeHashTable_t`, and `Volume`. Under `AFS_DEMAND_ATTACH_FS`, it also defines `VolState`, `VolFlags`, VLRU queue identifiers, per-volume `VolumeStats`, `VolumeOnlineSalvage`, and `VolumeVLRUState`. Field-access macros such as `V_id`, `V_name`, `V_diskused`, `V_vnodeIndex`, and `V_destroyMe` are the dominant API for callers. Exported functions cover attach/get/put, create/detach/offline, disk-header read/write/create/destroy, bitmap allocation, package init, volume header walking, FSSYNC/SALVSYNC connection, salvage scheduling, VLRU stats, and volume operation registration.

## Control Flow And State
The header models two layers of state: persistent disk state in `.vol` files and special inode files, and runtime state in `Volume`. Demand-attach builds add an explicit state machine from unattached through attaching, attached, updating, offlining, salvaging, deleted, and freed. `VOL_LOCK`, `VTRANS_LOCK`, and SALVSYNC locks are global package synchronization hooks, while `VLockFile`/`VDiskLock` declarations support per-volume disk locks.

## Persistence And Integration
`VolumeDiskHeader_t` stores split high/low inode numbers for portable disk layout, while `VolumeDiskData` persists quota, volume ids, flags such as `inUse`, `destroyMe`, `dontSalvage`, usage counters, timestamps, and offline messages. Integration points include partition metadata, inode handles, vnode indexes, FSSYNC/SALVSYNC, RX call interruption, salvager behavior, and dump/restore serialization via field macros.

## Risks And Test Signals
This is a high-blast-radius ABI header. Risks include struct layout drift, incorrect field macro use before `header` is attached, inconsistent DAFS state transitions, lock misuse across pthread/non-pthread builds, and stale disk-header version/magic handling. Test signals should include compile coverage across DAFS/non-DAFS and pthread/non-pthread builds, salvage/attach integration tests, dump/restore round trips, volume header walk tests with corrupt headers, and lock contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volume_inline.h -->
# sources/distributed-fs/openafs/src/vol/volume_inline.h

## Purpose
Provides small inline policy and state-machine helpers for the volume package. These helpers decide when volumes require checkout or disk/partition locking, classify program types and states, and implement demand-attach wait/state-change primitives.

## Important APIs And Functions
`VOL_CV_TIMEDWAIT` wraps condition-variable waiting with optional absolute timeout while preserving VOL lock debug bookkeeping. `VIsSalvager`, `VRequiresPartLock`, `VMustCheckoutVolume`, `VShouldCheckInUse`, `VCanUnlockAttached`, and `VVolLockType` encode attach policy across fileserver, volserver, utilities, and salvagers. DAFS helpers include `VLockVolumeByIdNB`, `VUnlockVolumeById`, `VIsSalvaging`, `VIsExclusiveState`, `VIsErrorState`, `VIsOfflineState`, `VIsValidState`, `VCreateReservation_r`, `VWaitStateChange_r`, `VTimedWaitStateChange_r`, `VWaitExclusiveState_r`, and `VChangeState_r`. `VPTypeToString` provides diagnostics.

## Control Flow And State
The file centralizes decision branches around `programType`, attach mode, and volume type. Non-DAFS utility processes take partition locks; DAFS uses per-volume header locks. Volume state waits assume `VOL_LOCK` is held and at least one user/waiter reference exists. `VChangeState_r` updates global state counters and broadcasts `attach_cv`.

## Persistence And Integration
The helpers do not persist directly, but they protect persistent volume headers and special inode state by selecting read/write/no-lock modes and deciding whether the `inUse` bit should be trusted during attach. They depend on `volume.h`, `partition.h`, pthread/opr primitives, DAFS locks, and configured package options such as FSSYNC and unsafe attach.

## Risks And Test Signals
Policy bugs here can cause false salvage, unsafe concurrent attach, or deadlock. `VShouldCheckInUse` is particularly sensitive because readonly checkouts intentionally tolerate `inUse`. Test signals include attach-mode matrix tests, DAFS lock mode tests for writable vs readonly volumes, timed wait timeout behavior, state counter accounting, and asserts for invalid states or unknown checkout modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/volume_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vutil.c -->
# sources/distributed-fs/openafs/src/vol/vutil.c

## Purpose
Implements low-level volume utility operations: volume creation, volume disk-data copying/stat maintenance, `.vol` disk-header read/write/create/destroy, partition volume-header walking, and DAFS-compatible file/disk locking primitives.

## Important APIs And Functions
With `FSSYNC_BUILD_CLIENT`, `VCreateVolume_r` creates the special inode set, initializes the volume info/index/link files, writes the `.vol` disk header, and secretly attaches the new volume. `AssignVolumeName_r`, `CopyVolumeHeader_r`, `ClearVolumeStats_r`, and `CopyVolumeStats_r` manipulate `VolumeDiskData`. `VReadVolumeDiskHeader`, `VWriteVolumeDiskHeader`, `VCreateVolumeDiskHeader`, and `VDestroyVolumeDiskHeader` manage volume header files and DAFS VGC notifications. `VWalkVolumeHeaders` scans partition directories for `.vol` files and retries questionable headers under DAFS partition header locks. `VLockFile*` and `VDiskLock*` implement portable byte-range lock files and intra-process reader/writer coordination.

## Control Flow And State
`VCreateVolume_r` validates partition placement, takes a DAFS volume lock or non-DAFS partition lock, creates each special inode, writes stamps, writes `VolumeDiskData`, creates the disk header, and on failure decrements created inodes and destroys partial headers. Header walking reads without a lock first, retries under lock on DAFS if the read or callback reports a positive error, then calls an error callback for bad headers.

## Persistence And Integration
The file writes persistent volume metadata and special inode files through `IH_CREATE`, `IH_OPEN`, `FDH_PWRITE`, and `.vol` files named by `VFORMAT`. DAFS integrates with `FSYNC_VGCAdd` and `FSYNC_VGCDel` to keep the fileserver volume group cache aligned. Locking abstracts Unix `fcntl`/Windows `LockFileEx` semantics behind volume-package structs.

## Risks And Test Signals
Risks include partial volume creation cleanup gaps, stale VGC entries after disk-header changes, races during header scanning/writing, and lock lifecycle mistakes. Notable behavior: `VLockFileUnlock` closes the lock fd when the refcount drops to zero, relying on close to release the last file lock. Test signals include forced failures after each inode creation step, concurrent create of same id, corrupt `.vol` scan behavior, VGC add/delete error handling, and DAFS multi-thread lock contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vutils.h -->
# sources/distributed-fs/openafs/src/vol/vutils.h

## Purpose
Defines small common constants for volume utility programs.

## Important APIs And Constants
`VUTIL_TIMEOUT` sets a 15-second remote host timeout. `VUTIL_RESTART` and `VUTIL_ABORT` provide utility exit-code conventions aligned with `tcp/exits.h` comments.

## Control Flow, State, And Persistence
This header has no control flow and no persistent state. Its values are compile-time integration points for utilities that need common timeout and restart/abort signaling.

## Dependencies And Integration
It has only an include guard and no direct includes. Consumers are expected to include it where remote volume utility command behavior needs standardized timing and process-exit semantics.

## Risks And Test Signals
Risk is low, but changing exit codes can break scripts or supervising jobs. Test signals are mostly build coverage and utility-level tests that verify restartable vs non-restartable failures use the expected exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/vutils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/xfs_size_check.c -->
# sources/distributed-fs/openafs/src/vol/xfs_size_check.c

## Purpose
Implements a platform-specific utility that checks whether mounted `/vicep*` XFS partitions have inode sizes large enough for OpenAFS XFS attributes.

## Important APIs And Functions
On `AFS_SGI_XFS_IOPS_ENV`, `VerifyXFSInodeSize` tries to set the OpenAFS XFS attribute, inspects `F_FSGETXATTRA`, returns `VERIFY_OK`, `VERIFY_FIX`, or `VERIFY_ERROR`, and removes the temporary attribute. `CheckPartitions` scans mounted read-write filesystems via `setmntent`/`getmntent`, filters AFS partition prefixes and XFS filesystems, and accumulates partitions needing remake. `main` enforces root execution, prints `mkfs` guidance for bad partitions, and exits nonzero when fixes are needed. On other platforms, `main` prints that the utility only runs on XFS platforms.

## Control Flow And State
State is a dynamically grown global `partList` with `nParts` and `nAvail`. The utility treats inability to set attributes or inspect fsxattr as a verification error, but only `VERIFY_FIX` adds a partition to the remediation list.

## Persistence And Integration
It temporarily writes and removes `AFS_XFS_ATTR` on partition roots. It depends on mount-table APIs, XFS attribute syscalls, AFS partition naming, and `xfsattrs.h`.

## Risks And Test Signals
Risks include root-only behavior, reliance on SGI/XFS-specific fields such as `st_fstype` and `fsx_nextents`, old-style implicit `int main`, and possible stale `errno` reporting after cleanup. Test signals include running as non-root, mocked mount entries for non-AFS and read-only partitions, XFS partitions with/without inline attribute capacity, allocation growth tests, and non-XFS build behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/xfs_size_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/Makefile.in -->
# sources/distributed-fs/openafs/src/volser/Makefile.in

## Purpose
Builds and installs the OpenAFS volume server tools, generated RX interfaces, and volser libraries.

## Important Targets And Variables
Major outputs are `volserver`, `vos`, `restorevol`, `voldump`, `libvolser.a`, `liboafs_volser.la`, `libvolser_pic.la`, installed headers `volser.h`, `volint.h`, `volser_prototypes.h`, and `vsutils_prototypes.h`. `SOBJS` define volserver server-side objects, `LT_objs` define client/library objects, `LIBS` collects volserver dependencies, and `VOLDUMP_LIBS` supplies the standalone dump utility.

## Control Flow And Build Integration
Generated files come from `volerr.et` via `COMPILE_ET_*` and `volint.xg` via `RXGEN`. Build rules link LWP and libtool variants, then install binaries and headers into server/client locations. Platform conditionals skip or alter volserver installation on Linux, AIX, SGI, Solaris, and Darwin families.

## State And Persistence
The makefile itself does not persist runtime state, but it controls generated source files and installed artifacts. Clean removes generated C/header files, objects, libraries, and binaries.

## Risks And Test Signals
Risks include stale dependency lists after source/header changes, duplicated or order-sensitive libraries, generated-interface mismatch, platform install typos, and divergence between `install` and `dest`. Test signals include full `make all`, `make generated`, clean rebuild, libtool library symbol checks, `check-splint`, and install/dest dry-runs on supported platform families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/common.c -->
# sources/distributed-fs/openafs/src/volser/common.c

## Purpose
Provides shared logging, abort, and error-table initialization helpers for volserver and non-pthread volume utilities.

## Important APIs And Functions
`Log` and `Abort` are compiled only outside `AFS_PTHREAD_ENV`; they wrap `vViceLog`, with `Abort` also calling `abort()`. `LogError` logs a com_err table name and message for an AFS error code. `InitErrTabs` initializes KA, RXK, KTC, ACFG, CMD, VL, and VOLS error tables for non-pthread builds.

## Control Flow And State
The file is intentionally small. Non-pthread utilities get local logging/error-table support; pthread builds presumably get these symbols elsewhere. `InitErrTabs` is idempotent in practice through the underlying com_err table initializers.

## Persistence And Integration
There is no persistent state. Integration points are `ViceLog`, `vViceLog`, AFS com_err tables, rxkad/auth/cellconfig/vlserver includes, and `volser.h`.

## Risks And Test Signals
Risks include missing logging symbols under unexpected build flags and incomplete error-table initialization causing numeric error output. Test signals include pthread and non-pthread link tests, invoking `LogError` for VOLS and VL errors, and utility startup tests that parse/display volume service errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/dump.h -->
# sources/distributed-fs/openafs/src/volser/dump.h

## Purpose
Defines the on-wire/on-file volume dump format constants and `DumpHeader` structure used by volserver dump/restore tools.

## Important APIs, Types, And Constants
`DUMPVERSION`, `DUMPBEGINMAGIC`, and `DUMPENDMAGIC` identify dump streams. Section tags are `D_DUMPHEADER`, `D_VOLUMEHEADER`, `D_VNODE`, and `D_DUMPEND`. `DumpHeader` stores the dumped volume id/name and up to `MAXDUMPTIMES` from/to timestamp pairs. `SHAKE1` through `SHAKE5` and `SHAKE_ABORT` are volume move handshaking constants.

## Format And Control Flow
The comments document the tag grammar: legacy short tags, TLV-style standard tags with variable-length length fields, indefinite length value `0x80`, and critical-tag marker `0x7e`. Separate known tag tables are documented for dump header, volume header, and vnode sections.

## Persistence And Integration
This header is the shared contract for `dumpstuff.c`, `restorevol.c`, `vol-dump.c`, and volserver RPC paths. It maps serialized dump fields back to `VolumeDiskData` and `VnodeDiskObject` fields.

## Risks And Test Signals
Risks include format drift between writer and reader, unbounded or unsupported dump-time counts, incorrect handling of unknown critical tags, and compatibility with historical nonstandard tags. Test signals include dump/restore round trips, incremental dump tests, unknown noncritical tag skipping, unknown critical tag rejection, big-file `h` records, and `MAXDUMPTIMES` boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/dumpstuff.c -->
# sources/distributed-fs/openafs/src/volser/dumpstuff.c

## Purpose
Implements the volserver dump, multidump, restore, and dump-size calculation engine over RX calls and OpenAFS inode/vnode handles.

## Important APIs And Functions
Public entry points are `DumpVolume`, `DumpVolMulti`, `RestoreVolume`, `SizeDumpVolume`, and `ProcessIndex`. The internal `iod` layer abstracts RX input/output and supports multi-call writes with per-call error codes. Serialization helpers read/write tags, integers, strings, ACL byte strings, vnode files, and standard TLV lengths. Restore helpers include `ReadDumpHeader`, `ReadVolumeHeader`, `ReadVnodes`, and `volser_WriteFile`.

## Control Flow
Dump flow writes a dump header, volume header, large vnode index, small vnode index, and dump end marker. Vnode dumping emits metadata for every non-null vnode and file data only when `serverModifyTime >= fromtime` or forced for directories. Restore flow reads the dump header and volume header, snapshots existing large/small vnode index entries, streams new vnodes into newly created inodes, removes old vnode inodes not present in the dump, copies or clears stats, rewrites `V_disk(vp)`, clears `destroyMe`, and calls `VUpdateVolume`.

## State And Persistence
The file reads/writes vnode index files, special inode data, ACLs, and volume disk data. It decrements old inode references when overwriting or cleaning restore state. It preserves existing volume stats only when `DoPreserveVolumeStats` is set, otherwise clears day/week stats. It sets `V_needsSalvaged` when inode creation/write failures may leave inconsistent disk state.

## Dependencies And Integration
Dependencies include RX, inode handles, vnode classes, ACL conversion, FSSYNC/daemon headers, volserver error codes, and volume macros. `dump.h` defines the stream grammar.

## Risks And Test Signals
High-risk areas are untrusted dump parsing, duplicate file data tags, large-file length handling, partial restore cleanup, ACL byte-order conversion, and size calculation staying in sync with actual dump emission. Test signals include malformed dumps, duplicate `f`/`h` tags, invalid ACLs, interrupted RX streams, partial restore failure injection, incremental restore deletion behavior, multidump with one failed receiver, and comparing `SizeDumpVolume` with actual byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/dumpstuff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/dumpstuff.h -->
# sources/distributed-fs/openafs/src/volser/dumpstuff.h

## Purpose
Declares the dump/restore entry points and the `iod` compatibility structure used by the volserver dump implementation.

## Important APIs And Types
`struct iod` carries either one RX call or an array of RX calls, dump device/parent/partition context, per-call return codes, and one-character pushback state. Declared functions are `DumpVolume`, `DumpVolMulti`, `RestoreVolume`, and `SizeDumpVolume`.

## Control Flow And State
The header documents the old `qi_in`/stdio-like pushback model. `haveOldChar` and `oldChar` permit a parser to read one byte too far and push it back, but the comments warn that direct `rx_Read` must not bypass this state when a pushed-back byte exists.

## Persistence And Integration
This header does not persist data itself. It ties RX streaming calls to volume objects, restore cookies, and size RPC structures, and is included by dump/restore server code.

## Risks And Test Signals
The main risk is parser inconsistency when code uses raw RX reads while `oldChar` is pending. Multi-dump callers also depend on `codes` alignment with `calls`. Test signals include parser boundary tests around section transitions, multidump partial-failure behavior, and compile/link checks wherever dumpstuff APIs are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/dumpstuff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/lockdata.h -->
# sources/distributed-fs/openafs/src/volser/lockdata.h

## Purpose
Defines small queue data structures used by volser lock/list processing to group related RW/RO/backup volume ids.

## Important APIs And Types
`struct aqueue` stores a volume name, three ids, three copy dates, validity flags, and a next pointer. `struct qHead` stores a queue count and head pointer. Constants include `ZERO`, a placeholder value intended to be replaced by zero, and `N_SECURITY_OBJECTS`.

## Control Flow, State, And Persistence
This header has no executable control flow. Queue state is in-memory only and is managed by `lockprocs.c` functions such as `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, and `Lp_QEnumerate`.

## Dependencies And Integration
It relies on `VOLSER_MAXVOLNAME` and volume-type indexes such as `RWVOL`, `ROVOL`, and `BACKVOL` from volser headers. It is part of VLDB/volser utility support, not persistent volume metadata.

## Risks And Test Signals
Risks include fixed-size name truncation, ambiguous `ZERO`, and ownership expectations for queued `aqueue` allocations. Test signals include queue add/enumerate memory behavior, scan by RW id, and boundary tests for maximum volume names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/lockdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/lockprocs.c -->
# sources/distributed-fs/openafs/src/volser/lockprocs.c

## Purpose
Implements helper routines for manipulating VLDB server/partition entries and in-memory queues of related volume ids.

## Important APIs And Functions
`FindIndex` searches an `nvldbentry` for a matching server, partition, and volume type, using `VLDB_IsSameAddrs` for address equivalence. `Lp_SetRWValue` and `Lp_SetROValue` update or remove RW/RO site entries. `Lp_Match`, `Lp_ROMatch`, `Lp_AnyMatch`, and `Lp_GetRwIndex` query entry placement. Queue helpers `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, `Lp_QEnumerate`, and `Lp_QTraverse` manage `qHead`/`aqueue`.

## Control Flow And State
`SetAValue` finds the matching site, rewrites server/partition, and compacts arrays when both new server and partition are zero. `FindIndex` stops early for RW searches because only one RW site is expected. Queue operations maintain a singly linked head insertion list; enumeration pops and frees the first node while copying its fields.

## Persistence And Integration
The file mutates in-memory VLDB entries before callers commit them through VLDB APIs. It depends on volser generated headers, VLDB flags, network-order server ids, and `vsutils` address matching.

## Risks And Test Signals
Risks include array compaction without visibly decrementing `nServers` in this helper, address-lookup failures while using index `e` in diagnostics, fixed-size string copying, and queue traversal assuming non-empty state. Test signals include RW/RO match/update/remove cases, multi-address server equivalence, no-match behavior, VLDB error injection, and queue memory ownership tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/lockprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/lockprocs_prototypes.h -->
# sources/distributed-fs/openafs/src/volser/lockprocs_prototypes.h

## Purpose
Declares the lock/list helper APIs implemented in `lockprocs.c`.

## Important APIs
Prototypes cover VLDB entry mutation (`Lp_SetRWValue`, `Lp_SetROValue`), matching/query helpers (`Lp_Match`, `Lp_ROMatch`, `Lp_AnyMatch`, `Lp_GetRwIndex`), and queue operations (`Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, `Lp_QEnumerate`, `Lp_QTraverse`).

## Control Flow, State, And Persistence
The header has no control flow. It exposes functions that mutate `nvldbentry` and `qHead`/`aqueue` objects owned by callers. No persistent state is created directly.

## Dependencies And Integration
Callers must include definitions for `struct nvldbentry`, `struct qHead`, and `struct aqueue`. This header provides compile-time linkage between volser utility modules and `lockprocs.c`.

## Risks And Test Signals
Risks are primarily declaration drift from implementation and missing includes that rely on include order. Test signals are strict-prototype builds, warning-free compilation, and caller coverage for each declared helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/lockprocs_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/physio.c -->
# sources/distributed-fs/openafs/src/volser/physio.c

## Purpose
Provides physical directory I/O and `DirHandle` utility routines used by volser/salvage-style directory manipulation.

## Important APIs And Functions
`ReallyRead` reads one AFS directory page from an inode handle and distinguishes physical errors from logical short reads through `physerr`. `ReallyWrite` writes one directory page and sets external `VolumeChanged`. `SetSalvageDirHandle`, `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, and `FidCpy` manage `DirHandle` identity and handle references. `Die` prints and panics.

## Control Flow And State
Each read/write opens the inode handle, performs page-sized positioned I/O, then closes or really closes on errors. `SetSalvageDirHandle` increments a static cache-check value so new handles force directory cache refresh semantics.

## Persistence And Integration
This file directly persists directory pages through `FDH_PREAD` and `FDH_PWRITE`. It integrates with `afs_dir` code via expected physical I/O hooks, inode handles, and `DirHandle` from `vol.h`.

## Risks And Test Signals
Risks include short read/write handling, leaked handles on error paths, global `VolumeChanged` coupling, and `private int SalvageCacheCheck` portability. Test signals include page read/write success, short I/O simulation, handle copy/release reference behavior, directory mutation paths in `vol_split.c`, and error propagation through `physerr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/physio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/physio.h -->
# sources/distributed-fs/openafs/src/volser/physio.h

## Purpose
Declares the `DirHandle` setup and teardown helpers exported by `physio.c`.

## Important APIs
`SetSalvageDirHandle` initializes a `DirHandle` for a volume/device/inode and takes an inode-handle reference. `FidZap` releases the handle and clears the structure.

## Control Flow, State, And Persistence
No control flow exists in the header. The declared functions affect in-memory handle state; callers use those handles for persistent directory page I/O through `physio.c` and directory-library callbacks.

## Dependencies And Integration
It depends on `DirHandle`, `VolumeId`, and `Inode` declarations supplied by surrounding includes such as `vol.h` and AFS syscall headers. It is used by code that performs salvage or split-volume directory edits.

## Risks And Test Signals
Risks include missing prototypes for other `physio.c` functions used indirectly and include-order dependency for `DirHandle`. Test signals are warning-free builds and directory operation tests that confirm every `SetSalvageDirHandle` is paired with `FidZap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/physio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/restorevol.c -->
# sources/distributed-fs/openafs/src/volser/restorevol.c

## Purpose
Implements the standalone `restorevol` utility, which reads a `vos dump` stream and recreates a filesystem tree outside AFS using normal directories, files, and symlinks.

## Important APIs And Functions
`readvalue`, `readchar`, and `readdata` parse raw dump bytes from `dumpfile`. `ReadDumpHeader` and `ReadVolumeHeader` parse dump metadata. `ReadVNode` handles directory, file, and symlink vnode records, reconstructing names through directory pages. `WorkerBee` implements command-line behavior for `-file`, `-dir`, `-extension`, `-mountpoint`, and `-umask`; `main` registers the command syntax.

## Control Flow And State
The utility reads a dump header to choose the restore root, then loops through volume-header and vnode sections until dump end. Directory vnodes are parsed to create real directories plus temporary root-level `AFSDir-<vnode>` symlinks. File entries first create temporary `AFSFile-<vnode>` symlinks in parent dirs; file vnode records resolve those symlinks and write data. Missing parents or files become `__ORPHANEDIR__.<vnode>` or `__ORPHANFILE__.<vnode>`. Incremental dumps trigger cleanup of leftover `AFSFile-` symlinks; all runs remove `AFSDir-` links at the end.

## Persistence And Integration
It writes to the local filesystem using `mkdir`, `symlink`, `rename`, `open`, `write`, and `unlink`. It depends on `dump.h`, vnode constants, AFS directory-page layout assumptions, and command parsing.

## Risks And Test Signals
Risks include old parser assumptions, limited unknown-tag handling, fixed-size buffers for names/MOTD/ACL, directory-page trust from input dumps, path/symlink collisions, partial output after errors, and no ACL restoration. Test signals include full and incremental dump extraction, orphan reconstruction, mountpoint symlink rewriting, long names/path overflow, truncated file data, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/restorevol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vol-dump.c -->
# sources/distributed-fs/openafs/src/volser/vol-dump.c

## Purpose
Implements `voldump`, a standalone utility that attaches a local volume directly from partition files and emits a `vos dump`-format stream without using volserver.

## Important APIs And Functions
`main` initializes the volume package as `volumeUtility` and registers command options. `handleit` parses partition, volume id, output file, verbosity, dump time, and `-pad-errors`. `HandleVolume` reads the `.vol` header, validates magic/version, converts it to `VolumeHeader`, and calls `AttachVolume`. `AttachVolume` builds a minimal in-memory `Volume` with inode handles and reads volume/index/link headers. Dump helpers mirror `dumpstuff.c`: `DumpDumpHeader`, `DumpVolumeHeader`, `DumpVnodeIndex`, `DumpVnode`, `DumpFile`, and `DumpEnd`.

## Control Flow And State
The utility attaches partitions, locates the requested volume header, constructs a `Volume`, opens the output fd or stdout, writes dump header/volume header/vnodes/end marker, then closes the fd. Incremental filtering uses `serverModifyTime >= fromtime`; directories can be force-dumped through the `dumpAllDirs` argument, currently false in this utility.

## Persistence And Integration
It reads persistent volume headers, vnode indexes, link table, ACLs, and vnode file inodes. It writes only the dump output, except for no runtime volume metadata changes. `-pad-errors` can convert file read errors or premature EOF into NUL-filled output while preserving declared size.

## Risks And Test Signals
Risks include code duplication with `dumpstuff.c`, minimal attach cleanup, ACL byte-order mutation while dumping directory vnode buffers, stdout close behavior, dump stream corruption on partial writes, and padded dumps hiding media errors. Test signals include direct dump/volserver dump comparison, corrupted header/version rejection, date parser coverage, large-file dumps, invalid ACL handling, `-pad-errors` behavior, and round-trip restore tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vol-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vol.h -->
# sources/distributed-fs/openafs/src/volser/vol.h

## Purpose
Defines the `DirHandle` structure used by volser physical directory I/O helpers.

## Important APIs And Types
`DirHandle` stores a volume id, device, inode, cache-check value, and referenced `IHandle_t *`. It includes `<afs/afssyscalls.h>` to pick up `Inode`.

## Control Flow, State, And Persistence
There is no executable control flow. The structure is in-memory state that identifies a directory object; `physio.c` uses it to open inode handles and read/write AFS directory pages.

## Dependencies And Integration
Integrated with `physio.c`, `afs_dir` routines, `vol_split.c`, and salvage-style directory manipulation. Consumers must manage `dirh_handle` references using `IH_INIT`, `IH_RELEASE`, or helpers such as `SetSalvageDirHandle` and `FidZap`.

## Risks And Test Signals
Risks include stale cache-check identity, leaked inode handles, and structure layout expectations in directory helper code. Test signals include handle lifecycle tests, `FidEq`/`FidVolEq` behavior, and split-volume mountpoint directory updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vol_split.c -->
# sources/distributed-fs/openafs/src/volser/vol_split.c

## Purpose
Implements namei-only volume splitting: moving a subtree from an existing volume into a newly created volume, replacing the original subtree with a mountpoint.

## Important APIs And Functions
When `AFS_NAMEI_ENV` and not Windows, public `split_volume` orchestrates the operation. Helpers include `ExtractVnodes` to collect vnode/parent metadata and locate the split root, `FindVnodes` to mark subtree files/directories, `copyDir` to copy directory inode contents, `copyVnodes` to hardlink/copy selected vnode data into the new volume and rewrite parents, `findName` to inverse-lookup the split directory name, `createMountpoint` to create a symlink vnode and update the parent directory, and `deleteVnodes` to remove transferred data from the old volume.

## Control Flow
The split flow extracts large vnodes, finds the split directory and parent name, marks all descendant directories, extracts small vnodes, marks descendant files, marks the new volume as `DESTROY_ME`/out of service, copies file and directory vnodes into the new volume, copies the split directory into the new root vnode, writes new volume metadata, creates a mountpoint in the old parent directory, deletes moved vnodes from the old volume, adjusts disk/file counts, updates both volume headers, and sends progress over RX.

## State And Persistence
This code mutates vnode index files, creates namei hard links or OSD objects, copies directory data, rewrites parent vnode ids for new-root children, creates a symlink mountpoint inode, updates AFS directory entries, decrements old inode references, and persists `V_diskused`, `V_filecount`, quota, uniquifier, service, and destroy flags via `VUpdateVolume`.

## Dependencies And Integration
Depends on namei inode layout masks, vnode classes, inode handles, `afs_dir` operations, `physio.c` directory handles, volserver RPC status output, and optional RXOSD split/remove hooks.

## Risks And Test Signals
This is high-risk destructive code. Failure after copying but before mountpoint/deletion can leave duplicate or inconsistent trees; failure during deletion can leave old data; quota/count updates are manual; many error paths return without freeing lists or fully rolling back. Test signals include split at root child, missing parent/name failures, file-only and deep directory subtrees, hardlink creation failure injection, mountpoint creation verification, post-split salvage/fsck, quota/filecount checks, and RXOSD-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/volser/vol_split.c -->
