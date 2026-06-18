# sources/distributed-fs/openafs/src/vol/partition.h

## Purpose
Defines the vice partition data model, constants, lock structures, disk-stat structure, and public partition API used across the volume package.

## Important APIs, Types, And Functions
Key constants are `VICE_PARTITION_PREFIX`, `VICE_PREFIX_SIZE`, NAMEI-only `VICE_ALWAYSATTACH_FILE`, `VICE_NEVERATTACH_FILE`, `PART_DONTUPDATE`, and `PART_DUPLICATE`. `struct DiskPartition64` stores list linkage, canonical name, device name, device id, partition index, lock fd, free-space accounting, flags, file count, and demand-attach volume-list/header-lock state. `struct DiskPartitionStats64`, `struct VLockFile`, and demand-attach `struct VDiskLock` describe exported state and lock internals.

## Control Flow
Consumers initialize the package, attach partitions, look up a partition by name or id, lock/unlock it for low-level operations, and periodically refresh or adjust disk accounting. Demand-attach consumers can lock partition header state independently of full partition locks.

## State And Persistence
The header declares `DiskPartitionList` and describes the in-memory state preserved for each partition while the volume package is running. Persistent lock-file names and attach-marker names are encoded as constants and must remain stable for administrators and cross-process coordination.

## Dependencies And Integration Points
It depends on OpenAFS parameter headers, `nfs.h`, `afs_lock.h`, pthreads in demand-attach builds, and NT vptab definitions when applicable. Nearly all volume-layer modules include it for partition metadata.

## Risks And Test Signals
Risks are ABI/struct-layout drift across modules, inconsistent locking expectations between `_r` and non-`_r` functions, and persistent marker-name changes. Compile coverage for demand-attach and non-demand-attach builds plus runtime partition attach/lock tests are primary signals.
