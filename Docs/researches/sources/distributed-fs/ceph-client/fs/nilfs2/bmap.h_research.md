# sources/distributed-fs/ceph-client/fs/nilfs2/bmap.h

## Purpose

`bmap.h` declares NILFS2's block-map abstraction. It defines the polymorphic operation table shared by direct and btree maps, the in-memory `struct nilfs_bmap`, pointer allocation helper wrappers around DAT operations, dirty-state helpers, and public map APIs.

## Important APIs, Types, and Functions

`union nilfs_bmap_ptr_req` carries either a raw pointer or a persistent allocator request. `struct nilfs_bmap_stats` reports block count changes. `struct nilfs_bmap_operations` is the direct/btree vtable for lookup, contiguous lookup, insert, delete, clear, dirty propagation, dirty-buffer lookup, assignment, mark, seek, last-key, conversion checks, and data gathering.

`struct nilfs_bmap` stores raw inode bmap data, rwsem, owner inode, ops pointer, allocation hints, pointer type, dirty state, and non-root btree capacity. Pointer types distinguish physical, single-version virtual, multi-version virtual, and no-pointer-ops GC maps. `struct nilfs_bmap_store` snapshots raw data and allocation/dirty fields.

Inline helpers implement bmap lookup, DAT-backed pointer allocation/end prepare/commit/abort, target pointer tracking, dirty flag checks/updates, and constants for direct/btree size thresholds.

## Control Flow

Callers invoke public functions declared here; `bmap.c` locks and dispatches to the active ops table. Direct and btree implementations call the pointer helper wrappers to allocate or end DAT entries when `NILFS_BMAP_USE_VBN()` is true. For physical maps, allocation helpers just advance or rewind `b_last_allocated_ptr`.

## State and Persistence Behavior

The raw `b_u.u_data` array is copied to/from the on-disk inode bmap field. The `NILFS_BMAP_LARGE` flag selects btree representation. Dirty state tracks whether bmap metadata must be propagated. Allocation hints are in-memory optimization state, while DAT commits persist virtual-to-physical mapping lifecycle.

## Dependencies and Integration Points

The header depends on Linux buffer heads, NILFS on-disk definitions, `alloc.h`, and `dat.h`. It is a shared contract for `bmap.c`, `direct.c`, `btree.c`, DAT, metadata files, segment writing, and garbage collection.

## Risks and Edge Cases

Pointer helper calls must be balanced: prepare allocation/end needs commit or abort. Physical-pointer fallback mutates `b_last_allocated_ptr` and must rewind on abort. The large/small threshold constants must match direct and btree capacities. Dirty helper comments assume the bmap semaphore is already locked.

## Test Signals

Build direct and btree users after any vtable change. Runtime tests should cover pointer allocation commit/abort for DAT-backed and physical maps, dirty flag transitions, save/restore, direct/btree conversion thresholds, GC map initialization, and bmap lookup/assign integration during segment construction.
