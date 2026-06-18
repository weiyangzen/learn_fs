# subset-b-007817 Research

Grouped research for the listed OpenAFS volume-layer namei, partition, purge/nuke, physical I/O, standalone salvager, online salvageserver, and SALVSYNC files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/namei_ops.c -->
# sources/distributed-fs/openafs/src/vol/namei_ops.c

## Purpose
Implements the OpenAFS NAMEI backend, where vice "inodes" are represented as regular filesystem paths under the partition's `AFSIDat` tree instead of raw filesystem inodes. It maps `IHandle_t` values to platform-specific paths, creates and removes data files/directories, stores/reconstructs inode metadata, maintains synthetic link counts in a link-table special file, lists files for salvage, supports copy-on-write/hardlink replacement on Unix, and converts read-only volume storage into read-write volume storage for recovery workflows.

## Important APIs, Types, And Functions
Public entry points include `namei_iread`, `namei_iwrite`, `namei_HandleToName`, `namei_ViceREADME`, `namei_MakeSpecIno`, `namei_icreate`, `namei_icreate_init`, `namei_iopen`, `namei_dec`, `namei_inc`, `namei_replace_file_by_hardlink`, `namei_GetLinkCount`, `namei_SetLinkCount`, `ListViceInodes`, `namei_ListAFSFiles`, `namei_ConvertROtoRWvolume`, `PrintInode`, `namei_SetWorkQueue`, and `namei_RemoveDirectories`. Important internal helpers are `namei_HandleToInodeDir`, `namei_HandleToVolDir`, `namei_CreateDataDirectories`, `namei_RemoveDataDirectories`, `GetFreeTag`, `DecodeVolumeName`, `DecodeInode`, `_namei_examine_special`, `_namei_examine_reg`, and `namei_ListAFSSubDirs`. The `namei_t` path buffer comes from `namei_ops.h`, and the encoded inode layout is controlled by platform-specific bit masks such as `NAMEI_VNODEMASK`, `NAMEI_TAGSHIFT`, `NAMEI_INODESPECIAL`, and `NAMEI_TAGMASK`.

## Control Flow
Normal file access starts with an `IHandle_t`; `namei_HandleToName` derives the full path from partition id, RW volume id, vnode number, uniquifier, special-file type, and link-table tag. `namei_icreate` allocates a tag, creates missing directories on `ENOENT`/`ENOTDIR`, opens the data file `O_CREAT|O_EXCL`, writes the hidden metadata into Unix owner/group/mode bits or NT file creation time, and initializes link-count state. `namei_dec` decrements a synthetic link count and only unlinks data when it reaches zero; special inodes are validated through OGM/creation-time metadata and then unlinked directly, with the link-table special inode removed only after its own count reaches zero. `namei_inc` increments counts and rejects counts above the 3-bit maximum.

Salvage enumeration calls `ListViceInodes`, which validates directory protections, then delegates to `namei_ListAFSFiles`. That routine either walks a single volume directory or all volume directories, processing special files first so the link-table handle is available before regular vnode files are decoded. In `AFS_SALSRV_ENV`, `namei_SetWorkQueue` allows `namei_ListAFSSubDirs` to enqueue per-file examination work for parallel salvageserver scans; otherwise scans are synchronous. `DecodeInode` rejects malformed or misplaced files by recomputing the canonical path and comparing stat data.

## State And Persistence
Persistent state is the `AFSIDat`/volume-directory hierarchy, encoded data-file names, special inode files, hidden metadata in file attributes, the link-table special file, and optional README files warning administrators not to modify NAMEI storage. Link counts are stored as 3-bit columns in 2-byte rows, offset by vnode number after an 8-byte stamp area. Directory cleanup deliberately avoids removing higher shared volume hash directories on Unix to avoid races with concurrent creators. Runtime state includes optional salvage work-queue TLS, the global link-count mutex for threaded builds, zero-link-count cleanup lists on NT, and global diagnostic variables such as `Testing` and `big_vno`.

## Dependencies And Integration Points
This file is active only under `AFS_NAMEI_ENV` and integrates with `ihandle`, vnode/volume metadata, partition id helpers, `viceinode.h`, `voldefs.h`, FSSYNC notifications during RO-to-RW conversion, and salvage code through `ListViceInodes`. It uses `ntops` on Windows, OpenAFS directory/work-queue utilities for online salvage, and `partition.c` state for disk partition lookup. `nuke.c`, `purge.c`, salvager code, volume creation, cloning, and vnode I/O all depend on its inode-compatible API.

## Risks And Test Signals
High-risk areas are path encoding compatibility, concurrent link-table updates, 3-bit link-count overflow, hidden metadata corruption, zero-link-count cleanup, crash windows between file creation and link-table updates, and directory removal races. `namei_ConvertROtoRWvolume` is recovery-sensitive because it rewrites volume info, relinks special files, rewrites headers, and sends FSSYNC state transitions. Useful tests include NAMEI volume create/delete, clone/release/purge, salvager list and repair passes, link-count overflow/error injection, misplaced-file salvage detection, RO-to-RW conversion on a test partition, NT and Unix path generation, and concurrent salvageserver scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/namei_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/namei_ops.h -->
# sources/distributed-fs/openafs/src/vol/namei_ops.h

## Purpose
Declares the public NAMEI backend interface used by the OpenAFS volume package when `AFS_NAMEI_ENV` is enabled. It exposes file-style wrappers, inode creation/open/read/write/link-count operations, salvage listing hooks, path-construction helpers, RO-to-RW conversion, hardlink replacement, work-queue integration for the online salvager, and directory cleanup.

## Important APIs, Types, And Functions
The main API surface includes `namei_fdopen`, `namei_unlink`, `namei_MakeSpecIno`, `namei_icreate`, `namei_icreate_init`, `namei_iopen`, `namei_irelease`, `namei_iread`, `namei_iwrite`, `namei_dec`, `namei_inc`, `namei_GetLinkCount`, `namei_SetLinkCount`, `namei_ViceREADME`, `namei_FixSpecialOGM`, `namei_ListAFSFiles`, `ListViceInodes`, `namei_HandleToName`, `namei_ConvertROtoRWvolume`, `namei_replace_file_by_hardlink`, `namei_SetWorkQueue`, and `namei_RemoveDirectories`. It defines `namei_t`, whose fields differ between NT and Unix layouts: NT tracks drive, volume directory, hash directory, inode component, and full path; Unix tracks base `AFSIDat`, two volume hash components, two vnode hash components, inode component, and full path.

## Control Flow
Callers generally use `IH_*` and `FDH_*` macros that resolve to these functions in NAMEI builds. Creation flows allocate an inode with `namei_icreate` or `namei_icreate_init`, open it with `namei_iopen`, read/write through `namei_iread` and `namei_iwrite`, and release storage with `namei_dec`. Salvage flows call `ListViceInodes` or `namei_ListAFSFiles` to enumerate encoded files and produce `ViceInodeInfo` records.

## State And Persistence
The header defines no storage itself, but it defines the shape and maximum lengths of path buffers that must be large enough for persistent NAMEI paths. `NAMEI_PATH_LEN` and component constants are part of the ABI between path construction, listing, purge/nuke, and salvage repair code.

## Dependencies And Integration Points
The declarations depend on `nfs.h`, `viceinode.h`, volume/inode handle types, and `afs/work_queue.h` when `AFS_SALSRV_ENV` is present. This header is included by partition discovery, volume operations, purge/nuke, salvager, and any module needing NAMEI-specific path or link-table operations.

## Risks And Test Signals
Risks are declaration drift against `namei_ops.c`, path buffer truncation if the layout changes, and accidental use outside `AFS_NAMEI_ENV`. Compile coverage for NAMEI Unix, NAMEI NT, and online-salvager builds is the primary signal, with runtime checks around generated path length and salvage enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/namei_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/nfs.h -->
# sources/distributed-fs/openafs/src/vol/nfs.h

## Purpose
Provides legacy volume-layer type aliases and simple constants originally shared with NFS-oriented code. It normalizes boolean-like constants, the `private` alias, fixed-width byte/word typedefs, the `Device` type, and the `Error` macro used by older volume and salvage modules.

## Important APIs, Types, And Functions
The header defines `private` as `static`, `TRUE`, `FALSE`, `bit32`, `bit16`, `byte`, `Device`, and conditionally `Error`. `Device` is a `bit32` and represents a Unix device number or the NAMEI partition id/NT drive index abstraction, depending on backend.

## Control Flow
There is no executable flow. Its role is to make older source files compile with consistent names before the richer OpenAFS headers define their own structures and macros.

## State And Persistence
No runtime or persistent state is defined. The `Device` typedef influences persisted metadata indirectly because many volume/inode handle records and salvage structures store device identifiers using this type.

## Dependencies And Integration Points
It includes `errno.h` and assumes `afs_uint32` has been defined by earlier OpenAFS parameter headers. It is included throughout `src/vol`, including partition, NAMEI, purge/nuke, physical I/O, and salvager code.

## Risks And Test Signals
The main risk is macro pollution from legacy names such as `private`, `TRUE`, `FALSE`, and `Error`. Build coverage across C files that include newer system or OpenAFS headers after `nfs.h` is the useful signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ntops.c -->
# sources/distributed-fs/openafs/src/vol/ntops.c

## Purpose
Implements Windows NT file-operation wrappers for the OpenAFS volume layer. It translates POSIX-like open, read, write, pread, pwrite, seek, truncate, sync, close, unlink, and drive/device operations into Win32 `HANDLE` and `CreateFile`/`ReadFile`/`WriteFile` semantics.

## Important APIs, Types, And Functions
Exported functions are `nt_unlink`, `nt_open`, `nt_close`, `nt_write`, `nt_pwrite`, `nt_read`, `nt_pread`, `nt_size`, `nt_getFileCreationTime`, `nt_setFileCreationTime`, `nt_sync`, `nt_ftruncate`, `nt_fsync`, `nt_seek`, `nt_DevToDrive`, and `nt_DriveToDev`. The file uses `BASEFILEATTRIBUTE`, `FILE_FLAG_POSIX_SEMANTICS`, `FILE_FLAG_DELETE_ON_CLOSE`, overlapped I/O offsets, `BY_HANDLE_FILE_INFORMATION`, `SetFilePointerEx`, `SetEndOfFile`, and OpenAFS `nterr_nt2unix` error mapping.

## Control Flow
`nt_open` maps POSIX flags to access, share, and create modes before calling `CreateFile`. Sequential reads/writes use `ReadFile`/`WriteFile`; positioned reads/writes populate an `OVERLAPPED` offset without modifying the shared file pointer. EOF during read is treated as a short read, not an error. `nt_sync` opens the raw drive path `\\.\X:` and flushes it. `nt_ftruncate` seeks to the target length and calls `SetEndOfFile`. Device conversion maps drive letters starting at C/D through integer indices used by the volume package.

## State And Persistence
The wrappers persist changes to NTFS files and volume metadata through Win32 handles. They do not own long-lived global state. `nt_unlink` emulates Unix delete-on-last-close by opening with delete access and `FILE_FLAG_DELETE_ON_CLOSE`, which affects later name reuse semantics until all handles close.

## Dependencies And Integration Points
The implementation is compiled only for `AFS_NT40_ENV` and integrates with `ihandle`, vnode/volume code, NAMEI-on-NT path handling, `partition.c`, and error translation from `afs/errmap_nt.h`. `namei_ops.c` uses NT creation times as hidden metadata through these wrappers.

## Risks And Test Signals
Risks include mismatch between POSIX and mandatory-locking/delete semantics, truncation of `afs_sfsize_t` counts to `DWORD`, partial I/O behavior, error mapping drift, and drive-letter assumptions. Tests should cover create/truncate/open flag combinations, positioned I/O beyond 4 GiB offsets, delete while open, drive flush, creation-time metadata round trips, and invalid drive conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ntops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ntops.h -->
# sources/distributed-fs/openafs/src/vol/ntops.h

## Purpose
Declares the Windows NT volume-layer file-operation API and NT-specific inode formatting helpers used by NAMEI and partition code.

## Important APIs, Types, And Functions
The header defines `VALID_INO` for Windows builds, `AFS_INO_STR_LENGTH`, and `afs_ino_str_t`. It declares `PrintInode`, all `nt_*` file wrappers, and `nt_DevToDrive`/`nt_DriveToDev`. `nt_fdopen` is declared here as part of the file abstraction, although its implementation may be supplied by the handle layer rather than this file.

## Control Flow
There is no direct control flow. Callers use these declarations behind OpenAFS `OS_*`, `FDH_*`, and `IH_*` abstractions to keep volume code mostly platform-neutral.

## State And Persistence
The header owns no state. Its type and prototype definitions determine how persistent NTFS handles and encoded NAMEI files are manipulated.

## Dependencies And Integration Points
It requires Windows `FILETIME`, OpenAFS `FD_t`, `Inode`, `IHandle_t`, and AFS size/offset types to be available from surrounding includes. It is paired with `ntops.c` and used by NAMEI, partition, and volume modules under `AFS_NT40_ENV`.

## Risks And Test Signals
Risks are prototype drift, missing `AFS_NT40_ENV` guards in consumers, and ABI assumptions around `HANDLE`-typed `FD_t`. Windows build coverage and targeted file-operation tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ntops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/nuke.c -->
# sources/distributed-fs/openafs/src/vol/nuke.c

## Purpose
Implements `nuke`, a low-level volume removal routine that deletes all storage associated with a volume id from a partition. It is used when a volume must be forcibly removed outside normal vnode-by-vnode purge paths.

## Important APIs, Types, And Functions
The main exported function is `nuke(char *aname, VolumeId avolid)`. `NukeProc` is the inode-listing callback passed to `ListViceInodes`; it filters `ViceInodeInfo` records for the requested volume or volume group and records inode numbers plus link counts in chunked `struct ilist` lists. The file uses `VGetPartition`, `ListViceInodes`, `IH_INIT`, `IH_DEC`, `namei_HandleToName`, `namei_RemoveDirectories`, `VDestroyVolumeDiskHeader`, and a file-local `localLock`.

## Control Flow
`nuke` validates the partition and volume id, derives the device/partition identity required by `ListViceInodes`, obtains `localLock`, and lists matching inodes through `NukeProc`. For NAMEI, it translates every collected inode to a path and unlinks it directly; for non-NAMEI, it decrements each inode as many times as the recorded link count requires. After data removal, NAMEI tries to prune empty storage directories, and all builds explicitly destroy the volume disk header.

## State And Persistence
Persistent effects are destructive: data files/inodes and the volume header are removed. Runtime state is the temporary linked list of inode batches and the global local lock that prevents concurrent nuke operations in this process. Special inode filtering treats an RW id as matching special files for children in the volume group via parent id, so nuking an RW can remove clone storage.

## Dependencies And Integration Points
`nuke.c` integrates salvage listing (`ListViceInodes`), partition lookup, `ihandle`, volume headers, and NAMEI path conversion. It is a lower-level complement to `purge.c`, which deletes a loaded volume through vnode indexes.

## Risks And Test Signals
Risks are obvious data loss if the wrong volume id or partition is provided, stale or incomplete inode listing, direct NAMEI unlink bypassing link-count adjustment, and partial cleanup if the process exits after data removal but before header destruction. Test signals include nuking test RW and RO volumes, verifying headers disappear, checking NAMEI directory cleanup, and confirming unrelated volumes in the same partition survive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/nuke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/partition.c -->
# sources/distributed-fs/openafs/src/vol/partition.c

## Purpose
Discovers, initializes, tracks, locks, and accounts for vice partitions. It supports many platform-specific mount-table mechanisms, NAMEI always/never attach marker files, NT registry vptab entries, disk usage refresh, quota/free-space adjustment, partition locks, and demand-attach partition-header locking.

## Important APIs, Types, And Functions
Public functions include `VInitPartitionPackage`, `VAttachPartitions`, `VPartitionPath`, `VGetPartition_r`, `VGetPartition`, `VSetPartitionDiskUsage_r`, `VSetPartitionDiskUsage`, `VResetDiskUsage_r`, `VResetDiskUsage`, `VAdjustDiskUsage_r`, `VAdjustDiskUsage`, `VDiskUsage_r`, `VDiskUsage`, `VPrintDiskStats_r`, `VPrintDiskStats`, `VLockPartition_r`, `VUnlockPartition_r`, `VLockPartition`, `VUnlockPartition`, and demand-attach-only `VPartHeaderLock`, `VPartHeaderUnlock`, `VGetPartitionById_r`, and `VGetPartitionById`. Important private helpers are `VInitPartition_r`, platform-specific `VCheckPartition`, `VIsAlwaysAttach`, `VIsNeverAttach`, `VAttachPartitions2`, `VLookupPartition_r`, and `AddPartitionToTable_r`.

## Control Flow
Startup calls `VInitPartitionPackage` and then `VAttachPartitions`. Each platform variant scans the OS mount source or NT vptab, skips non-writable/invalid/never-attach entries, defers always-attach NAMEI directories, validates `/vicep*` names, checks backend compatibility, rejects dangerous `FORCESALVAGE` conditions for fileserver startup, then calls `VInitPartition`. Initialization appends a `DiskPartition64` to `DiskPartitionList`, derives canonical and device names, creates NAMEI lock files/README where needed, refreshes disk stats, and initializes demand-attach volume/header lock structures. Disk accounting later adjusts partition free blocks and volume disk-used fields under `VOL_LOCK`.

## State And Persistence
Runtime state is `DiskPartitionList`, and under demand attach also `DiskPartitionTable` indexed by partition id plus per-partition volume-list and disk-lock objects. Persistent state observed or created includes `/vicep*` directories, `AlwaysAttach`, `NeverAttach`, NAMEI `Lock` files, `.volheaders.lock`, `.volume.lock`, NT hidden `LOCKFILE`, and disk/filesystem free-space data. Accounting fields `free`, `totalUsable`, `minFree`, and `f_files` are estimates refreshed from `statfs`/`statvfs` or `GetDiskFreeSpaceEx`.

## Dependencies And Integration Points
This file integrates with platform mount APIs, OpenAFS volume package locks, `volutil_GetPartitionID`, `namei_ops`, `ntops`, vptab on NT, `VLockFile`/`VDiskLock` helpers in demand attach builds, and volume quota/free-space logic. Salvager, fileserver, volserver, nuke, purge, and salvsync scheduling all depend on partition lookup and ids.

## Risks And Test Signals
Risks include platform-specific mount parsing differences, partition-name validation, stale free-space estimates, integer conversion in block-size scaling, duplicate NT drive handling, lock-file portability, and attaching a directory that is not a separate partition unless `AlwaysAttach` is intentional. Tests should cover attach discovery on each platform, marker-file behavior, `/vicepaa` style ids, disk-full/quota paths, partition locks across processes, demand-attach header locks, and duplicate/missing partition handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/partition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/partition.h -->
# sources/distributed-fs/openafs/src/vol/partition.h

## Purpose
Defines the vice partition data model, constants, lock structures, disk-stat structure, and public partition API used across the volume package.

## Important APIs, Types, And Functions
Key constants are `VICE_PARTITION_PREFIX`, `VICE_PREFIX_SIZE`, NAMEI-only `VICE_ALWAYSATTACH_FILE`, `VICE_NEVERATTACH_FILE`, `PART_DONTUPDATE`, and `PART_DUPLICATE`. `struct DiskPartition64` stores list linkage, canonical name, device name, device id, partition index, lock fd, free-space accounting, flags, file count, and demand-attach volume-list/header-lock state. `struct DiskPartitionStats64`, `struct VLockFile`, and demand-attach `struct VDiskLock` describe exported state and lock internals. Prototypes cover partition attach, lookup, locking, disk usage, quota/free-space adjustment, and demand-attach header/id lookup.

## Control Flow
Consumers initialize the package, attach partitions, look up a partition by name or id, lock/unlock it for low-level operations, and periodically refresh or adjust disk accounting. Demand-attach consumers can lock partition header state independently of full partition locks.

## State And Persistence
The header declares `DiskPartitionList` and describes the in-memory state preserved for each partition while the volume package is running. Persistent lock-file names and attach-marker names are encoded as constants and must remain stable for administrators and cross-process coordination.

## Dependencies And Integration Points
It depends on OpenAFS parameter headers, `nfs.h`, `afs_lock.h`, pthreads in demand-attach builds, and NT vptab definitions when applicable. Nearly all volume-layer modules include it for partition metadata.

## Risks And Test Signals
Risks are ABI/struct-layout drift across modules, inconsistent locking expectations between `_r` and non-`_r` functions, and persistent marker-name changes. Compile coverage for demand-attach and non-demand-attach builds plus runtime partition attach/lock tests are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/partition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/physio.c -->
# sources/distributed-fs/openafs/src/vol/physio.c

## Purpose
Provides salvager physical I/O callbacks for OpenAFS directory objects. It reads and writes fixed `AFS_PAGESIZE` directory pages through inode handles and supplies small `DirHandle` identity/manipulation helpers.

## Important APIs, Types, And Functions
Functions include `ReallyRead`, `ReallyWrite`, `SetSalvageDirHandle`, `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, `FidCpy`, and `Die`. `ReallyRead` and `ReallyWrite` open `DirHandle.dirh_handle` with `IH_OPEN` and use `FDH_PREAD`/`FDH_PWRITE`; `SetSalvageDirHandle` initializes a salvage-only `DirHandle` and bumps a static cache-check counter.

## Control Flow
The directory package calls `ReallyRead` or `ReallyWrite` for a page number. Reads return `0` on a full page and `EIO` on physical or logical short-read failure, optionally reporting physical `errno` separately. Writes return `errno`/`EIO` and set `*volumeChanged` after a successful full-page write. Handle helpers release, zero, compare, copy, or panic.

## State And Persistence
Persistent effects are directory page writes to backing vnode files. Runtime state is the `DirHandle`, its referenced `IHandle_t`, the caller-owned `volumeChanged` flag, and the static `SalvageCacheCheck` counter used to force cache distinction across handles.

## Dependencies And Integration Points
This file integrates the salvager with `afs/dir.h`, `ihandle`, `salvage.h`, and volume internals. It is deliberately distinct from fileserver directory I/O because the salvager uses its own `DirHandle` definition.

## Risks And Test Signals
Risks include short reads being interpreted as logical corruption, stale handle references if `FidZap` is missed, and write failures after partial disk writes. Test signals include salvaging directories with good pages, short/truncated directory files, injected read/write errors, and verification that successful writes mark the volume changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/physio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/purge.c -->
# sources/distributed-fs/openafs/src/vol/purge.c

## Purpose
Implements `VPurgeVolume`, the normal loaded-volume deletion path. It makes volume deletion idempotent by zeroing vnode index records before decrementing referenced data inodes, then removes special/header files and breaks callbacks.

## Important APIs, Types, And Functions
The main function is `VPurgeVolume(Error *ec, Volume *vp)`. Private helpers are `ObliterateRegion`, `PurgeIndex_r`, and `PurgeHeader_r`. It uses vnode class metadata from `VnodeClassInfo`, stream wrappers (`STREAM_ASEEK`, `STREAM_READ`, `STREAM_WRITE`, `STREAM_FLUSH`, `STREAM_CLOSE`), `IH_OPEN`, `IH_DEC`, `VDestroyVolumeDiskHeader`, and `FSYNC_VolOp`.

## Control Flow
`VPurgeVolume` clears `V_inUse`, purges large and small vnode indexes, purges special header/link-table storage, destroys the disk header on the original partition, and sends `FSYNC_VOL_BREAKCBKS`. `ObliterateRegion` scans up to `MAXOBLITATONCE` vnode records from a vnode index, remembers nonzero backing inodes, rewinds and overwrites the scanned records with zeroes, flushes and syncs the index, then decrements the remembered inodes. This ordering lets a crash retry avoid double-decrementing data already erased from the index.

## State And Persistence
Persistent state changed includes vnode index files, data inode/link counts, volume info/small-index/large-index special files, NAMEI link table, and the volume disk header. Runtime state is the scanned inode array and stream/fd handles.

## Dependencies And Integration Points
Purge sits between volume transaction code, vnode index layout, `ihandle`, NAMEI/non-NAMEI link semantics, partition headers, and FSSYNC callback invalidation. It is a safer, volume-object-aware counterpart to `nuke`.

## Risks And Test Signals
Risks include corrupt vnode magic causing early failure, partial index write/sync failures, data leaks if inodes are not decremented after zeroing, and incorrect parent id in `IH_DEC`. Tests should delete populated volumes, inject crashes between zeroing and decrementing, purge NAMEI and non-NAMEI volumes, verify callback-break notification, and run salvager after interrupted purge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/purge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvage.h -->
# sources/distributed-fs/openafs/src/vol/salvage.h

## Purpose
Defines the salvager-specific `DirHandle` used by directory repair code. This is intentionally separate from fileserver directory handles.

## Important APIs, Types, And Functions
`DirHandle` stores `dirh_volume`, `dirh_device`, `dirh_inode`, `dirh_handle`, `dirh_cacheCheck`, and a pointer to `volumeChanged`. The file includes `afs/afssyscalls.h` so `Inode` and related system-call abstractions are available.

## Control Flow
No functions are implemented here. `physio.c` initializes, copies, compares, reads, writes, and releases this structure during salvage directory processing.

## State And Persistence
The structure holds runtime identity for a directory object and a pointer to mutable caller state indicating whether the volume was repaired. It represents persistent directory storage through its inode handle but stores no data on its own.

## Dependencies And Integration Points
It is used by `physio.c`, the salvager directory routines, and code including `afs/dir.h` in salvage mode. It must match the expectations of `SetSalvageDirHandle`, `ReallyRead`, and `ReallyWrite`.

## Risks And Test Signals
Risks are layout/signature drift against directory package callbacks and missed `IH_RELEASE` when handles are copied or zapped incorrectly. Salvager build coverage and directory salvage tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvaged.c -->
# sources/distributed-fs/openafs/src/vol/salvaged.c

## Purpose
Implements the demand-attach online salvage server executable (`salvageserver`) and its client mode. In server mode it accepts SALVSYNC work, forks bounded child salvagers, reaps them, updates scheduler state, and merges per-child logs. In client mode it submits a volume salvage request to an already-running salvageserver and polls until completion.

## Important APIs, Types, And Functions
Important functions are `handleit`, `main`, `SalvageClient`, `SalvageServer`, `DoSalvageVolume`, `SalvageChildReaperThread`, `Reap_Child`, `SalvageLogCleanupThread`, `SalvageLogCleanup`, `SalvageLogScanningThread`, and `ScanLogs`. Runtime structures include `log_cleanup_node`, `log_cleanup_queue`, `pending_q`, `current_workers`, `worker_lock`, `worker_cv`, and `child_slot`. Command options include salvage behavior flags, `-parallel`, `-tmpdir`, `-orphans`, syslog/logfile options, `-client`, and Transarc-style logging.

## Control Flow
`main` validates server paths/root privileges, registers command syntax, and dispatches to `handleit`. Client mode initializes enough volume package state to use SALVSYNC, sends `SALVSYNC_SALVAGE`, then polls with `SALVSYNC_QUERY` every two seconds until done/error/unknown. Server mode opens logging, obtains a shared salvage lock, initializes the volume package and directory package, starts reaper/log cleanup/log scanning threads, and loops on `SALVSYNC_getWork`. For each node it finds a free slot, forks, runs `DoSalvageVolume` in the child, records pid in the parent, and throttles by `Parallel`.

## State And Persistence
Persistent effects are salvage repairs performed by child processes and log files under the server log directory. Runtime scheduling state is split between this file's child slots/condition variables and `salvsync-server.c`'s queues. Child logs are named `SalvageLog.<pid>`, later appended into the main log and unlinked. Server restart handling scans for existing `SalvageLog.<pid>` files and waits for those pids to disappear before cleanup.

## Dependencies And Integration Points
This file requires `AFS_DEMAND_ATTACH_FS` and rejects NT. It integrates with `salvsync.h`, `vol-salvage.h`, `partition.c`, `fssync.h`, volume package initialization, process management, OpenAFS command parsing, logging, and directory salvage I/O. It is the executable counterpart to the SALVSYNC server thread.

## Risks And Test Signals
Risks include fork/reaper races, in-memory worker-slot loss after crashes, child log truncation/cleanup issues, waiting forever for stale pid logs, partition id lookup failures, and no online salvager support outside DAFS. Test signals include client request/poll success, parallel worker throttling, child failure propagation, log merge after normal and restarted salvageserver runs, invalid partition/volume handling, and signal/core reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvaged.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvager.c -->
# sources/distributed-fs/openafs/src/vol/salvager.c

## Purpose
Implements the standalone OpenAFS salvager executable. It parses salvage options, initializes logging and the volume package, coordinates with DAFS/non-DAFS fileservers, obtains salvage locks, and invokes the core salvage routines for all partitions, one partition, or one volume.

## Important APIs, Types, And Functions
Key functions are `TimeStampLogFile`, `handleit`, and `main`. It sets global salvage behavior flags such as `debug`, `Testing`, `ListInodeOption`, `ForceSalvage`, `OKToZap`, `ShowRootFiles`, `RebuildDirs`, `forceR`, `Parallel`, `PartsPerDisk`, `tmpdir`, `ShowLog`, `ShowSuid`, `ShowMounts`, and `orphans`. It invokes `VInitVolumePackage2`, `ObtainSalvageLock`, `ObtainSharedSalvageLock`, `DInit`, `SalvageFileSysParallel`, and `SalvageFileSys`.

## Control Flow
`main` initializes server paths, enforces root on Unix, marks that a salvage lock is needed, registers legacy command options, and dispatches. `handleit` validates `-partition`/`-volumeid`, configures logging to syslog, a timestamped file, or the standard salvage log, initializes the volume package as either full `salvager` or `volumeSalvager`, obtains the appropriate exclusive/shared salvage lock, checks DAFS compatibility and `-forceDAFS`, initializes the directory package, then runs parallel partition salvage or targeted volume salvage.

## State And Persistence
Persistent effects are repairs to volume headers, vnode indexes, directories, and NAMEI/inode metadata through `vol-salvage.c`, plus salvage logs. Runtime state is mostly global option flags consumed by the core salvage engine. `-nowrite`, `-showsuid`, and `-showmounts` force readonly/testing-style behavior.

## Dependencies And Integration Points
The program ties command parsing, logging, partition discovery, volume package setup, FSSYNC/SALVSYNC coordination, and the core salvage engine together. It includes platform-specific inode/mount headers and has NT child-salvager setup paths.

## Risks And Test Signals
Risks include unsafe standalone use against a DAFS fileserver without explicit override, option-offset fragility in legacy `cmd_AddParm` ordering, invalid volume id parsing, lock acquisition mistakes, and divergent behavior between full-partition and single-volume salvage. Tests should cover option parsing, readonly/list-inodes modes, DAFS refusal/force behavior, all-partition parallel salvage, single-volume salvage while fileserver is running, and timestamp/syslog logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvsync-client.c -->
# sources/distributed-fs/openafs/src/vol/salvsync-client.c

## Purpose
Implements the client-side SALVSYNC protocol helpers used by the fileserver, volserver utilities, and `salvageserver -client` to communicate with the demand-attach salvage server.

## Important APIs, Types, And Functions
Public functions are `SALVSYNC_clientInit`, `SALVSYNC_clientFinis`, `SALVSYNC_clientReconnect`, `SALVSYNC_askSalv`, `SALVSYNC_SalvageVolume`, and `SALVSYNC_LinkVolume`. The static `salvsync_client_state` defines the endpoint (`SALVSYNC_ENDPOINT_DECL`), protocol version, retry limit, timeout, and protocol name. Requests use `SYNC_command`, `SYNC_response`, `SALVSYNC_command_hdr`, and `SALVSYNC_response_hdr`.

## Control Flow
Clients connect with `SYNC_connect`, build a `SALVSYNC_command_hdr`, set command/reason/length metadata, and call `SALVSYNC_askSalv`. `SALVSYNC_askSalv` stamps the current protocol version, serializes access with `VSALVSYNC_LOCK`, invokes `SYNC_ask`, logs unusual responses, and returns the protocol status. `SALVSYNC_SalvageVolume` schedules, queries, cancels, or reprioritizes a volume by using the same helper with different command/reason values. `SALVSYNC_LinkVolume` sends the clone/parent relationship command.

## State And Persistence
Runtime state is the connected SALVSYNC socket/channel in `salvsync_client_state`, protected by the volume salvsync mutex. No state persists locally; all scheduling state lives in the salvageserver process.

## Dependencies And Integration Points
The file is compiled only for `AFS_DEMAND_ATTACH_FS`. It depends on generic daemon sync transport (`daemon_com.h` via `salvsync.h`), volume locks, partition/volume headers for types, and OpenAFS logging. It is used by salvage clients and volume code that needs to request online salvage or link clone scheduling to a parent.

## Risks And Test Signals
Risks include protocol version mismatch, stale or disconnected channel state, part-name truncation to the wire field size, and in-memory-only server state after reconnect. Tests should cover connect/reconnect/close, malformed or denied responses, schedule/query/cancel flows, link-volume requests, and concurrent callers contending on `VSALVSYNC_LOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvsync-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvsync-server.c -->
# sources/distributed-fs/openafs/src/vol/salvsync-server.c

## Purpose
Implements the server-side SALVSYNC scheduler and socket protocol for the demand-attach salvage server. It accepts client commands, maintains queued and pending salvage work, groups clone requests under parent volume groups, chooses work by partition/priority, tracks child completion, and notifies the fileserver on salvage failure.

## Important APIs, Types, And Functions
Public server entry points are `SALVSYNC_salvInit`, `SALVSYNC_getWork`, and `SALVSYNC_doneWorkByPid`. Important internal pieces include `SALVSYNC_syncThread`, `SALVSYNC_newconnection`, `SALVSYNC_com`, handler-array helpers, `AllocNode`, `AddToSalvageQueue`, `DeleteFromSalvageQueue`, `AddToPendingQueue`, `DeleteFromPendingQueue`, `LookupNode`, `LookupNodeByCommand`, `LinkNode`, `HandlePrio`, `UpdateCommandPrio`, `SALVSYNC_com_Salvage`, `SALVSYNC_com_Cancel`, `SALVSYNC_com_CancelAll`, `SALVSYNC_com_Link`, and `SALVSYNC_com_Query`. Persistent in-memory structures are `salvageQueue`, `pendingQueue`, `SalvageHashTable`, `partition_salvaging`, and the fixed `HandlerFD`/`HandlerProc` arrays.

## Control Flow
`SALVSYNC_salvInit` initializes queues, hash buckets, locks, condition variables, and starts the detached sync thread. The sync thread binds the SALVSYNC endpoint, registers an atfork cleanup handler, accepts up to `MAXHANDLERS` sockets, and dispatches readable fds. `SALVSYNC_com` reads and validates one command, rejects malformed length or protocol version, dispatches under `VOL_LOCK`, fills queue lengths in the response, and drops channels flagged for shutdown. Salvage/reprioritize commands allocate or find a node, adjust priority, and enqueue it if not already active. Query and cancel inspect existing nodes. Link commands attach a clone node to a parent so future clone requests schedule the parent volume group.

Workers call `SALVSYNC_getWork`, which waits for queued work, prefers partitions without active salvage, otherwise selects queued work round-robin-ish across partition list, removes the node from the salvage queue, and appends it to pending. Reaper code calls `SALVSYNC_doneWorkByPid`, which moves the node out of pending, updates success/error state, mirrors parent state to clone children, decrements partition activity, and calls `FSYNC_VOL_FORCE_ERROR` for affected volumes if the child failed.

## State And Persistence
All scheduler state is in process memory: queued nodes, pending nodes, volume-group links, priorities, pid associations, and done/error state. It is not durable across salvageserver restart. The only external persistent effect is indirect: failed child status can force fileserver volume error state through FSSYNC. The SALVSYNC endpoint is a TCP or Unix-domain daemon-com endpoint on port/path declared in `salvsync.h`.

## Dependencies And Integration Points
This file requires `AFS_DEMAND_ATTACH_FS` and integrates with `daemon_com` transport, `partition.c` id lookup, `DiskPartitionList`, volume global locking, `rx_queue`, `salvaged.c` worker dispatch, and `fssync.h` for failure notification. It depends on command payload layout from `salvsync.h`.

## Risks And Test Signals
Risks include fixed `MAXHANDLERS` limiting concurrent clients, non-durable queue state, careful `VOL_LOCK` requirements around all queue/hash operations, priority ordering bugs, partition id validation, child pid reuse, and clone-parent state propagation. The current file also contains duplicated harmless-looking statements in the checkout (`memset(&com,...)` and nested `for` in the raw grep output were checked; line-number view shows only one each at the inspected lines, so review should rely on actual line-numbered source). Test signals include malformed packet rejection, protocol mismatch, queue length responses, cancel/cancel-all, priority reordering, clone link scheduling, partition concurrency limits, child success/error completion, and fileserver force-error notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvsync-server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvsync.h -->
# sources/distributed-fs/openafs/src/vol/salvsync.h

## Purpose
Defines the SALVSYNC protocol, wire payloads, scheduler node type, endpoint, and public client/server APIs for demand-attach online salvage coordination.

## Important APIs, Types, And Functions
The header declares protocol versions `SALVSYNC_PROTO_VERSION_V1` through `V3`, command codes (`SALVSYNC_OP_NOP`, `SALVSYNC_OP_SALVAGE`, `SALVSYNC_OP_CANCEL`, `SALVSYNC_OP_RAISEPRIO`, `SALVSYNC_OP_QUERY`, `SALVSYNC_OP_CANCELALL`, `SALVSYNC_OP_LINK`), reason codes, `SALVSYNC_FLAG_VOL_STATS_VALID`, command states, `SALVSYNC_command_hdr`, `SALVSYNC_response_hdr`, wrapper structs `SALVSYNC_command` and `SALVSYNC_response`, `SALVSYNC_command_info`, `SalvageQueueNodeType_t`, and `struct SalvageQueueNode`. It declares client functions and server functions `SALVSYNC_salvInit`, `SALVSYNC_getWork`, and `SALVSYNC_doneWorkByPid`.

## Control Flow
Clients fill `SALVSYNC_command_hdr` and send it inside generic `SYNC_command` frames. The server validates the version and payload size, changes scheduler state, and returns `SALVSYNC_response_hdr` containing state, priority, and queue lengths. Salvage worker code consumes `SalvageQueueNode` objects and reports completion by pid.

## State And Persistence
The header defines in-memory command and scheduler state, not durable state. The wire-visible partition name is a 16-byte fixed field, so partition naming and truncation behavior are part of the protocol contract. `SALVSYNC_IN_PORT` and `SALVSYNC_UN_PATH` define the persistent endpoint identity used by clients and server.

## Dependencies And Integration Points
It is only active under `AFS_DEMAND_ATTACH_FS` and depends on `daemon_com.h` and `voldefs.h`. It is shared by `salvsync-client.c`, `salvsync-server.c`, `salvaged.c`, fileserver/volserver code that schedules salvages, and any caller that needs volume-group link scheduling.

## Risks And Test Signals
Risks include protocol version drift across binaries, fixed-size `partName`, enum compatibility, and scheduler-node layout assumptions shared only in-process. Tests should build mixed client/server modules together and exercise every command code, malformed strings, queue state responses, clone links, and version mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/salvsync.h -->
