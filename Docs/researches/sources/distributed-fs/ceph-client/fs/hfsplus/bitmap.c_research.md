# sources/distributed-fs/ceph-client/fs/hfsplus/bitmap.c

Purpose: manages the HFS+ allocation bitmap stored in the allocation file, allocating and freeing allocation blocks.

Important APIs and control flow: `hfsplus_block_allocate()` locks `alloc_mutex`, reads bitmap pages from `sbi->alloc_file`, scans from an offset for the first zero bit, sets contiguous zero bits up to `*max`, handles page boundaries, dirties modified pages, subtracts allocated count from `free_blocks`, marks the MDB dirty, and returns the starting block or `size` when full/error. `hfsplus_block_free()` validates range, locks the bitmap, clears the requested bit range across pages, dirties pages, adds the count back to `free_blocks`, and marks the MDB dirty.

State and persistence: mutates allocation file pages, `HFSPLUS_SB(sb)->free_blocks`, and MDB dirty state. The bitmap is page-cache backed rather than an in-memory fixed array, so normal file writeback persists allocation changes.

Dependencies and integration: called by `extents.c` for file/fork growth and truncation/freeing. Depends on `read_mapping_page()`, page mapping/dirtying, allocation-file inode setup from mount code, and `hfsplus_mark_mdb_dirty()`.

Risks and test signals: allocation returns `size` on some read errors, which callers interpret like no space. Freeing does not verify bits were set before clearing, so double-free detection is weak at this layer. Tests should exercise partial-word start/end ranges, page-boundary allocations/frees, wraparound allocation fallback, ENOSPC, and corrupted/short allocation files.
