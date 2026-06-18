# sources/distributed-fs/ceph-client/fs/nilfs2/bmap.c

## Purpose

`bmap.c` is the generic NILFS2 block-map front-end. It hides whether an inode uses a compact direct map or a btree, translates virtual block numbers through the DAT when needed, serializes map operations, handles conversion between direct and btree forms, and provides helper state for allocation target selection, dirty propagation, GC, and save/restore.

## Important APIs, Types, and Functions

Lookup APIs are `nilfs_bmap_lookup_at_level()`, `nilfs_bmap_lookup_contig()`, and the inline `nilfs_bmap_lookup()` from the header. Mutation APIs include `nilfs_bmap_insert()`, `nilfs_bmap_delete()`, `nilfs_bmap_truncate()`, and `nilfs_bmap_clear()`. Segment-construction and GC integration uses `nilfs_bmap_propagate()`, `nilfs_bmap_lookup_dirty_buffers()`, `nilfs_bmap_assign()`, and `nilfs_bmap_mark()`.

Initialization and persistence helpers are `nilfs_bmap_read()`, `nilfs_bmap_write()`, `nilfs_bmap_init_gc()`, `nilfs_bmap_save()`, and `nilfs_bmap_restore()`. Allocation target helpers include `nilfs_bmap_data_get_key()`, `nilfs_bmap_find_target_seq()`, and `nilfs_bmap_find_target_in_group()`. `nilfs_bmap_convert_error()` turns internal `-EINVAL` bmap corruption signals into filesystem errors and `-EIO`.

## Control Flow

Every public map operation takes the bmap rwsem in read or write mode, dispatches to the current `b_ops` table, releases the lock, and converts errors. Lookup first obtains a pointer from the direct/btree implementation; for virtual-block maps it translates that pointer through the DAT into a physical block number and treats a missing DAT entry as metadata corruption.

Insert can trigger direct-to-btree conversion: if the current direct ops report that a key exceeds direct capacity, existing direct records are gathered and passed to `nilfs_btree_convert_and_insert()`, then the large-map flag is set. Delete can trigger btree-to-direct conversion when btree occupancy falls below the direct threshold. Truncate repeatedly deletes the last key until the requested cutoff is reached.

## State and Persistence Behavior

The in-memory `struct nilfs_bmap` contains raw on-disk bmap words, an rwsem, owning inode, ops table, last allocation key/pointer hints, pointer type, dirty state, and btree node fanout. `nilfs_bmap_read()` copies raw inode bmap data and selects pointer type by inode number: DAT uses physical pointers, cpfile/sufile use single-version virtual pointers, ifile and ordinary files use multi-version virtual pointers. `nilfs_bmap_write()` copies the raw map back to the on-disk inode and resets DAT allocation hints.

## Dependencies and Integration Points

This file depends on `direct.h`, `btree.h`, `btnode.h`, `mdt.h`, `dat.h`, and `alloc.h`. It is used by inode/page/segment code for logical-to-physical mapping and by metadata files for their own block maps. DAT translation ties ordinary block pointers to NILFS's log-structured relocation model.

## Risks and Edge Cases

The direct/btree conversion thresholds must remain consistent with on-disk root capacity constants. Missing DAT entries after bmap lookup indicate corruption and are deliberately escalated. Lock class setup for DAT and metadata files prevents false lockdep recursion reports; wrong classes can hide or invent deadlocks. Truncate loops can be expensive for very large maps. Save/restore only snapshots selected in-memory fields and assumes callers handle associated btree buffers safely.

## Test Signals

Test direct insertion up to conversion, btree deletion back to direct, lookups with DAT translation, missing DAT entry corruption handling, truncate from sparse and dense files, dirty propagation during segment writes, block assignment info generation, GC mark paths, bmap read/write across remount/recovery, and lockdep under DAT/metadata nesting.
