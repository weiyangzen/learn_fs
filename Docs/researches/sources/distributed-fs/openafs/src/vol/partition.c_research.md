# sources/distributed-fs/openafs/src/vol/partition.c

## Purpose
Discovers, initializes, tracks, locks, and accounts for vice partitions. It supports many platform-specific mount-table mechanisms, NAMEI always/never attach marker files, NT registry vptab entries, disk usage refresh, quota/free-space adjustment, partition locks, and demand-attach partition-header locking.

## Important APIs, Types, And Functions
Public functions include `VInitPartitionPackage`, `VAttachPartitions`, `VPartitionPath`, `VGetPartition_r`, `VGetPartition`, `VSetPartitionDiskUsage_r`, `VSetPartitionDiskUsage`, `VResetDiskUsage_r`, `VResetDiskUsage`, `VAdjustDiskUsage_r`, `VAdjustDiskUsage`, `VDiskUsage_r`, `VDiskUsage`, `VPrintDiskStats_r`, `VPrintDiskStats`, `VLockPartition_r`, `VUnlockPartition_r`, `VLockPartition`, `VUnlockPartition`, and demand-attach-only `VPartHeaderLock`, `VPartHeaderUnlock`, `VGetPartitionById_r`, and `VGetPartitionById`. Private helpers handle partition validation, marker files, attach scanning, and partition-table lookup.

## Control Flow
Startup calls `VInitPartitionPackage` and then `VAttachPartitions`. Each platform variant scans the OS mount source or NT vptab, skips non-writable/invalid/never-attach entries, defers always-attach NAMEI directories, validates `/vicep*` names, checks backend compatibility, rejects dangerous `FORCESALVAGE` conditions for fileserver startup, then calls `VInitPartition`. Initialization appends a `DiskPartition64` to `DiskPartitionList`, derives canonical and device names, creates NAMEI lock files/README where needed, refreshes disk stats, and initializes demand-attach volume/header lock structures.

## State And Persistence
Runtime state is `DiskPartitionList`, and under demand attach also `DiskPartitionTable` indexed by partition id plus per-partition volume-list and disk-lock objects. Persistent state observed or created includes `/vicep*` directories, `AlwaysAttach`, `NeverAttach`, NAMEI `Lock` files, `.volheaders.lock`, `.volume.lock`, NT hidden `LOCKFILE`, and disk/filesystem free-space data. Accounting fields are estimates refreshed from `statfs`/`statvfs` or `GetDiskFreeSpaceEx`.

## Dependencies And Integration Points
This file integrates with platform mount APIs, OpenAFS volume package locks, `volutil_GetPartitionID`, `namei_ops`, `ntops`, vptab on NT, `VLockFile`/`VDiskLock` helpers in demand attach builds, and volume quota/free-space logic. Salvager, fileserver, volserver, nuke, purge, and salvsync scheduling all depend on partition lookup and ids.

## Risks And Test Signals
Risks include platform-specific mount parsing differences, partition-name validation, stale free-space estimates, integer conversion in block-size scaling, duplicate NT drive handling, lock-file portability, and attaching a directory that is not a separate partition unless `AlwaysAttach` is intentional. Tests should cover attach discovery on each platform, marker-file behavior, disk-full/quota paths, partition locks across processes, demand-attach header locks, and duplicate/missing partition handling.
