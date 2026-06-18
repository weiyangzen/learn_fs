# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.c

## Purpose

Implements NILFS-specific buffer-head and folio/page-cache state management, including buffer grabbing, copying, dirty clearing, shadow copy support, and delayed extent discovery.

## Main Responsibilities

- Grabs or creates buffer heads for a given block offset in a mapping.
- Clears NILFS and generic buffer state when discarding buffers or dirty pages.
- Copies buffer contents and selected buffer/page state between folios.
- Copies dirty folios into shadow mappings and copies shadow folios back to original mappings.
- Clears dirty folios in a mapping without ordinary writeback.
- Counts clean buffers in a write range so NILFS can update dirty block accounting.
- Finds delayed/uncommitted extents by scanning buffer heads marked `BH_Delay`.

## Important Functions

- `nilfs_grab_buffer()` grabs a locked folio and returns the requested buffer head, creating empty buffers if needed.
- `nilfs_forget_buffer()` clears uptodate/dirty/mapped/async/NILFS/delay bits, resets block number, clears folio state when all buffers are clean, and drops the buffer.
- `nilfs_copy_buffer()` copies one buffer’s data and inherent NILFS state to another buffer and updates destination folio uptodate/mapped state.
- `nilfs_folio_buffers_clean()` checks whether any buffer on a folio remains dirty.
- `nilfs_folio_bug()` prints diagnostic folio/buffer state before `NILFS_FOLIO_BUG()` triggers `BUG()`.
- `nilfs_copy_dirty_pages()` copies all dirty folios from source mapping to destination mapping, preserving dirty buffer state.
- `nilfs_copy_back_pages()` copies or moves folios from shadow mapping back to destination mapping.
- `nilfs_clear_dirty_pages()` iterates dirty-tagged folios and calls `nilfs_clear_folio_dirty()`.
- `nilfs_clear_folio_dirty()` clears buffer and folio working states if buffers are not busy.
- `__nilfs_clear_folio_dirty()` clears the xarray dirty tag and folio dirty state.
- `nilfs_find_uncommitted_extent()` scans contiguous folios for delayed buffers and returns the first delayed extent length.

## Dependencies and Interactions

- Used by `inode.c` for write accounting, FIEMAP delayed extents, and read-only dirty-page discard.
- Used by `mdt.c` for metadata block cache manipulation and shadow-map save/restore.
- Uses NILFS buffer state bits declared in `page.h`.

## Notable Behaviors and Edge Cases

- `nilfs_grab_buffer()` returns with the folio locked; callers must unlock and release it.
- Dirty clearing refuses to clear buffer state if buffers remain referenced or locked after one LRU invalidation attempt.
- `nilfs_copy_back_pages()` directly manipulates mapping xarrays when moving shadow folios back, updating `nrpages` and dirty tags.
- `nilfs_find_uncommitted_extent()` stops when a delayed run ends or non-buffered folio is encountered after a run begins.
