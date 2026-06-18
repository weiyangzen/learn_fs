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
