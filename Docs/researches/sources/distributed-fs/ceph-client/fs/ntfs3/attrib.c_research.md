# sources/distributed-fs/ceph-client/fs/ntfs3/attrib.c

## Purpose
Implements NTFS3 attribute storage mutation: resident/nonresident conversion, runlist loading, cluster allocation/deallocation, size changes, delayed allocation, sparse/compressed frame handling, block mapping, hole punching, range collapse/insert, and WOF compression frame metadata reads.

## Important APIs, Types, And Functions
`attr_load_runs()` and `attr_load_runs_vcn()` unpack nonresident runlists into `runs_tree`. `run_deallocate_ex()` frees cluster ranges and updates delayed-allocation accounting. `attr_allocate_clusters()` finds free space, marks it used, zeroes when requested, and records new run fragments. `attr_make_nonresident()` converts resident attributes to nonresident form. `attr_set_size_ex()` is the main grow/shrink path for resident, normal, sparse, compressed, MFT, and delayed-allocated attributes. `attr_data_get_block()` and `_locked()` map VCNs to LCNs, optionally allocating holes. `attr_is_frame_compressed()` and `attr_allocate_frame()` manage NTFS compression-unit state. `attr_collapse_range()`, `attr_punch_hole()`, and `attr_insert_range()` implement fallocate-style mutations. `attr_force_nonresident()` forces default data out of the MFT record.

## Control Flow
Most mutations locate the base attribute via `ni_find_attr()`, load relevant runlist segments, modify runs in memory, repack runs into one or more MFT records with `mi_pack_runs()`, update attribute-list entries when segments split or merge, then update inode size/bytes and mark the inode dirty. When an attribute record lacks room, the code creates or expands the attribute list and inserts new nonresident segments. On allocation failure, simple steps are rolled back; for deep multi-segment failures the inode is marked bad because a complete undo is too complex.

## State And Persistence
Persistent state includes resident attribute payloads, nonresident runlists, allocation/data/valid/total sizes, attribute-list entries, bitmap allocation, sparse/compressed markers, and MFT record dirty state. Runtime state includes `ni->file.run`, `ni->file.run_da`, `run_lock`, delayed allocation counters, `ni->i_valid`, inode byte counts, and `NI_FLAG_UPDATE_PARENT`.

## Dependencies And Integration Points
Depends on NTFS3 runlist, bitmap allocator, MFT record, inode, attribute-list, compression, block I/O, and VFS folio/page-cache code. It is called from file write, mmap/page fault, truncate, fallocate, compression, and inode writeback paths.

## Risks And Edge Cases
This file has high corruption risk because it edits on-disk runlists and allocation bitmaps. Edge cases include resident-to-nonresident transitions, compressed frame alignment, sparse holes, delayed allocation crossing real allocations, attribute-list expansion requiring extra clusters/MFT records, MFT self-extension recursion, rollback after partial allocation, and stale `attr_b` pointers after layout changes. A notable risk in `attr_allocate_frame()` is that the final valid-size update writes the existing `valid_size` value instead of `new_valid`, which is worth targeted review.

## Test Signals
Use xfstests-style coverage for truncate grow/shrink, write into sparse holes, delayed allocation flush, ENOSPC during each allocation stage, resident/nonresident boundary crossings, compressed file writes, WOF reads, hole punch alignment, collapse/insert range, MFT growth, attribute-list splits, and metadata consistency checks with chkdsk/ntfsinfo after fault injection.
