# sources/distributed-fs/ceph-client/fs/ntfs/mft.c

## Purpose
`mft.c` implements the NTFS Master File Table record lifecycle: validating and mapping MFT records, allocating and freeing records, extending `$MFT` and `$MFT/$BITMAP`, applying MST fixups around writes, synchronizing `$MFTMirr`, and providing `$MFT` writeback. It is the persistence core behind inode creation, deletion, extent records, and many metadata mutations.

## Important APIs and Functions
The public entry points are `ntfs_mft_record_check()`, `map_mft_record()`, `unmap_mft_record()`, `map_extent_mft_record()`, `__mark_mft_record_dirty()`, `ntfs_sync_mft_mirror()`, `write_mft_record_nolock()`, `ntfs_mft_record_alloc()`, `ntfs_mft_record_free()`, `ntfs_mft_writepages()`, and `ntfs_mft_mark_dirty()`. Internal helpers include `map_mft_record_folio()`, `ntfs_may_write_mft_record()`, bitmap/data extension helpers, `ntfs_mft_record_layout()`, `ntfs_mft_record_format()`, `lcn_from_index()`, and `ntfs_write_mft_block()`.

## Control Flow and State
Mapping computes the folio index and offset from the record number, reads the `$MFT` mapping, copies the on-disk record into `ni->mrec`, applies `post_read_mst_fixup()`, validates general record fields, then stores the pinned folio and offset in the `ntfs_inode`. Dirty state is per-`ntfs_inode` through `NInoDirty`; `mark_mft_record_dirty()` marks the base VFS inode `I_DIRTY_DATASYNC`.

Allocation first sets the target bit in `$MFT/$BITMAP`, extending bitmap allocation/initialized size if needed, then extends `$MFT/$DATA` allocation and initialized size until the target record exists. It formats records on the way, marks the chosen record in use, prepares base or extent inode state, and updates `vol->mft_data_pos` and free-record counters. Freeing clears `MFT_RECORD_IN_USE`, increments the sequence number, writes the record, then clears the bitmap bit with rollback attempts.

Writeout copies `ni->mrec` back to the folio, applies `pre_write_mst_fixup()`, submits bios per `ni->mft_lcn[]`, optionally updates `$MFTMirr`, and keeps folio references until I/O completion. `$MFT` writeback scans each record in the folio and uses `ntfs_may_write_mft_record()` to avoid racing dirty in-cache inodes, creating/deleting inodes, and extent locks.

## Dependencies and Integration
This file depends heavily on `bitmap`, `lcnalloc`, `attrib`, `inode`, `mst`, `runlist`, folio/page-cache APIs, bios, and VFS writeback. `namei.c` uses allocation/freeing for namespace operations; attribute code uses mapping and dirty marking; runlist mapping feeds physical LCN lookup for writeback.

## Risks
Risk is high. Partial rollback after bitmap, runlist, or mapping-pair updates can leave metadata inconsistent and sets `NVolErrors()`. Lock order is delicate around `$MFT`, extent records, runlist locks, and folio locks. `unmap_mft_record()` decrements references but does not free the copied `mrec` or put the folio in the visible path, so lifetime expectations must be checked elsewhere. `ntfs_sync_mft_mirror()` submits async bio despite documenting synchronous I/O. Any arithmetic mistake in record-to-folio or record-to-LCN conversion risks metadata corruption.

## Test Signals
Exercise create/delete cycles until `$MFT/$BITMAP` and `$MFT/$DATA` extend, record reuse after deletion, extent-record allocation for attribute lists, `$MFTMirr` updates for low records, ENOSPC rollback, writeback during concurrent create/unlink, and corrupted MST/record headers. Kernel tests should watch `NVolErrors`, bitmap/free counters, sequence-number changes, and chkdsk/fsck-style consistency after forced failures.
