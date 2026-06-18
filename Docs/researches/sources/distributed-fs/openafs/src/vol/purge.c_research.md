# sources/distributed-fs/openafs/src/vol/purge.c

## Purpose
Implements `VPurgeVolume`, the normal loaded-volume deletion path. It makes volume deletion idempotent by zeroing vnode index records before decrementing referenced data inodes, then removes special/header files and breaks callbacks.

## Important APIs, Types, And Functions
The main function is `VPurgeVolume(Error *ec, Volume *vp)`. Private helpers are `ObliterateRegion`, `PurgeIndex_r`, and `PurgeHeader_r`. It uses vnode class metadata from `VnodeClassInfo`, stream wrappers, `IH_OPEN`, `IH_DEC`, `VDestroyVolumeDiskHeader`, and `FSYNC_VolOp`.

## Control Flow
`VPurgeVolume` clears `V_inUse`, purges large and small vnode indexes, purges special header/link-table storage, destroys the disk header on the original partition, and sends `FSYNC_VOL_BREAKCBKS`. `ObliterateRegion` scans up to `MAXOBLITATONCE` vnode records, remembers nonzero backing inodes, rewinds and overwrites scanned records with zeroes, flushes and syncs the index, then decrements remembered inodes. This ordering lets a crash retry avoid double-decrementing data already erased from the index.

## State And Persistence
Persistent state changed includes vnode index files, data inode/link counts, volume info/small-index/large-index special files, NAMEI link table, and the volume disk header. Runtime state is the scanned inode array and stream/fd handles.

## Dependencies And Integration Points
Purge sits between volume transaction code, vnode index layout, `ihandle`, NAMEI/non-NAMEI link semantics, partition headers, and FSSYNC callback invalidation. It is a safer, volume-object-aware counterpart to `nuke`.

## Risks And Test Signals
Risks include corrupt vnode magic causing early failure, partial index write/sync failures, data leaks if inodes are not decremented after zeroing, and incorrect parent id in `IH_DEC`. Tests should delete populated volumes, inject crashes between zeroing and decrementing, purge NAMEI and non-NAMEI volumes, verify callback-break notification, and run salvager after interrupted purge.
