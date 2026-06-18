# sources/distributed-fs/ceph-client/fs/nilfs2/page.c

## Purpose

`page.c` contains NILFS2-specific folio and buffer-head management. It supports metadata shadow copies, buffer state copying, dirty-page cleanup, delayed/uncommitted extent discovery, and debugging of inconsistent folio state. These helpers are used by metadata files, btree/node caches, DAT shadow maps, and segment construction.

## Important APIs, Types, and Functions

`nilfs_grab_buffer()` obtains and locks/grabs a folio-backed buffer for a logical block offset. `nilfs_forget_buffer()` clears mapping, dirty, async, volatile, checked, redirected, and delay state from a buffer. `nilfs_copy_buffer()` copies one buffer's data and inherent state.

`nilfs_copy_dirty_pages()` copies dirty folios from one mapping to a shadow mapping, preserving dirty buffer state. `nilfs_copy_back_pages()` copies or moves pages back from shadow mapping to the original mapping. `nilfs_clear_folio_dirty()`, `nilfs_clear_dirty_pages()`, and `__nilfs_clear_folio_dirty()` clear dirty state while coordinating xarray dirty tags and buffer states.

`nilfs_page_count_clean_buffers()` counts clean buffers in a byte range. `nilfs_find_uncommitted_extent()` scans for contiguous `BH_Delay` buffers. Debug support is provided by `nilfs_folio_bug()`.

## Control Flow

`nilfs_grab_buffer()` calculates the folio index from a block offset, grabs a folio from the given mapping, creates empty buffers if needed, waits on the target buffer, and assigns the superblock device.

Shadow copy flow starts with dirty folio iteration on the source mapping. For each dirty source folio, `nilfs_copy_dirty_pages()` locks the source, grabs the destination folio, copies data and buffer states with `nilfs_copy_folio()`, marks the destination dirty, and releases both folios. Copy-back either overwrites an existing destination folio or moves the folio's xarray entry between mappings, preserving dirty tags.

Dirty cleanup first invalidates buffer LRU references if buffers are busy, then clears buffer state and folio uptodate/mapped/checked/dirty state. `__nilfs_clear_folio_dirty()` clears the mapping's dirty xarray mark under lock before calling `folio_clear_dirty_for_io()`.

Uncommitted extent discovery scans contiguous folios and their buffers from a starting block, begins an extent at the first delayed buffer, and stops when a non-delayed buffer or bufferless folio follows an active extent.

## State and Persistence Behavior

The file operates entirely on in-memory page-cache and buffer-head state. It controls which dirty or delayed buffers are later collected into NILFS logs. Clearing or copying these flags affects persistence indirectly by changing what the segment constructor sees as pending work.

The inherent buffer bit mask intentionally copies only stable state such as uptodate, mapped, NILFS node, volatile, and checked; redirected/dirty/delay state is selectively copied depending on the call path.

## Dependencies and Integration Points

Dependencies include Linux folio, page cache, buffer-head, writeback, highmem mapping, xarray, and swap/LRU helpers. Integration points include `mdt.c` shadow maps, btree node cache handling, DAT copy-back during GC, and `segment.c` writeback cleanup through `nilfs_folio_buffers_clean()` and `__nilfs_clear_folio_dirty()`.

## Risks and Edge Cases

This code manipulates low-level xarray entries in `nilfs_copy_back_pages()`, so mapping/nrpages/tag accounting must remain exact. Busy buffer cleanup can leave state intact after one invalidation pass, which callers must tolerate. `nilfs_copy_buffer()` and `nilfs_copy_folio()` assume buffer sizes/layouts are compatible. Debug paths call `BUG()` through `NILFS_FOLIO_BUG`, so inconsistent dirty state can become a hard failure.

## Test Signals

Good tests include metadata shadow save/restore, copy-back with existing and absent destination folios, dirty xarray tag preservation, busy buffer invalidation, delayed extent discovery across folio boundaries, block sizes smaller than page size, and injected allocation failures in destination folio creation.
