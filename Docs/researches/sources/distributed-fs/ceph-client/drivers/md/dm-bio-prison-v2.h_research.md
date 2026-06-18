<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.h

## Purpose
`dm-bio-prison-v2.h` declares the v2 shared/exclusive bio-prison API for DM targets.

## Important APIs, Types, And Functions
`struct dm_cell_key_v2` describes a virtual/physical range. `struct dm_bio_prison_cell_v2` exposes exclusive state, exclusive level, shared count, quiesce continuation, rbtree node, key, and detained bios. The header declares init/exit, prison create/destroy, cell alloc/free, shared get/put, exclusive lock/quiesce/promote/unlock functions.

## Control Flow
Targets create a prison with a workqueue, preallocate cells, use shared locks for bios, and exclusive locks for conflicting operations. Return values signal grant/denial, quiescing requirements, and cell ownership transfer.

## State And Persistence
Only runtime synchronization state is defined. No disk metadata is persisted.

## Dependencies, Integration Points, Risks, And Test Signals
It includes DM persistent-data/thin metadata, bio, rbtree, and workqueue headers. Risks include exposed layout, subtle lock-level rules, shared locks remaining after unlock, and ownership/free misuse. Test compile coverage, lock-level matrices, continuation delivery, ownership paths, and concurrent overlapping ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.h -->
