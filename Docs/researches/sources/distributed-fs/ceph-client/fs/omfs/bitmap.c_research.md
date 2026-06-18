# sources/distributed-fs/ceph-client/fs/omfs/bitmap.c

Purpose: implements OMFS free-space accounting and allocation over an in-memory bitmap mirrored from the on-disk free-space bitmap when present.

Important APIs and functions: `omfs_count_free` counts zero bits across all bitmap pages. `omfs_allocate_block` tries to reserve one exact block. `omfs_allocate_range` finds and marks a contiguous run satisfying `min_request` and up to `max_request`. `omfs_clear_range` clears an allocated run. Internal helpers `count_run` and `set_run` scan and modify runs that may cross bitmap buffer boundaries.

Control flow: allocation locks `s_bitmap_lock`, searches `s_imap` for zero bits, uses `count_run` to measure a free run across bitmap pages, and calls `set_run` to update both memory and the on-disk bitmap buffers. Exact block allocation computes the bitmap page and bit using division by bits per filesystem block. Clearing computes the starting page/bit and delegates to `set_run`.

State and persistence behavior: `s_imap` is the authoritative in-memory allocation map during the mount. If `s_bitmap_ino > 0`, changes are also written to bitmap blocks at `clus_to_blk(sbi, s_bitmap_ino) + map` and marked dirty. The bitmap lock serializes concurrent allocation and freeing. No journaling is used; dirty buffer writeback persists updates.

Dependencies and integration points: depends on `omfs_sb_info`, `clus_to_blk`, `sb_bread`, Linux bitmap helpers, and buffer-head dirtying. It is called from inode allocation in `inode.c`, file extent growth and truncation in `file.c`, and inode eviction.

Risks: if the on-disk bitmap read fails inside `set_run`, bits may already have been changed in earlier pages before returning an error. `omfs_allocate_block` sets the in-memory bit before reading the on-disk bitmap and does not roll back on `sb_bread` failure. Filesystems without a loaded bitmap have `s_imap_size == 0`, making allocation impossible unless a future tree-walk path is added. Bounds checking in `omfs_clear_range` only checks the starting map.

Test signals: mount with a valid bitmap, free-space counts before and after create/write/unlink, allocation crossing bitmap-block boundaries, ENOSPC behavior, exact contiguous extension via `omfs_allocate_block`, simulated bitmap I/O failures, and concurrent file creation/truncation under the bitmap mutex.
