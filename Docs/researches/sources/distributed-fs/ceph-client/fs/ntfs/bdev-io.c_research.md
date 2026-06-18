# sources/distributed-fs/ceph-client/fs/ntfs/bdev-io.c

## Purpose

`bdev-io.c` provides NTFS-specific helpers for direct block-device reads and page-cache-mediated block-device writes. It is used where metadata code needs to access raw device bytes outside ordinary file data paths.

## Important APIs, Types, And Functions

- `ntfs_bdev_read(struct block_device *bdev, char *data, loff_t start, size_t size)` synchronously reads bytes from a sector-aligned device offset. Non-vmalloc buffers use `bdev_rw_virt()`; vmalloc buffers are filled through one or more BIOs with `REQ_META | REQ_SYNC`.
- `ntfs_bdev_write(struct super_block *sb, void *buf, loff_t start, size_t size)` updates `sb->s_bdev->bd_mapping` folios covering the target range, copies bytes into the page cache, marks folios uptodate and dirty, and returns immediately after dirtying.

## Control Flow And Algorithms

The read path validates 512-byte sector alignment, chooses a simple virtual-buffer helper for linear memory, or builds a BIO chain for vmalloc-backed memory. It repeatedly adds vmalloc chunks to the current BIO; if the BIO fills, it chains a new BIO, submits the previous one, and continues. The last BIO is submitted with `submit_bio_wait()`.

The write path computes page indices from byte offsets, reads each block-device mapping folio, copies the corresponding slice from `buf`, and dirties the folio. It handles partial first/last pages through `from`, `to`, and `buf_off` offsets.

## State And Persistence Behavior

Reads do not modify persistent state. Writes modify the block device address-space page cache and rely on normal dirty-page writeback for persistence. `ntfs_bdev_read()` invalidates vmalloc mappings only if `op == REQ_OP_READ`, but `op` includes flags, so this condition is false as written for `REQ_OP_READ | REQ_META | REQ_SYNC`.

## Dependencies And Integration Points

The file depends on Linux block-layer APIs (`bio_alloc`, `bio_add_vmalloc_chunk`, `bio_chain`, `submit_bio`, `submit_bio_wait`, `bdev_rw_virt`) and folio/page-cache APIs for block-device mapping writes. It includes `ntfs.h` for `ntfs_error()` logging and NTFS constants.

## Risks And Edge Cases

- `bio_alloc()` return values are not checked for NULL; allocation failure can lead to dereference faults.
- The vmalloc read path chains and submits prior BIOs but only waits on the last BIO, relying on `bio_chain()` completion semantics; this should be validated for the target kernel version.
- The invalidation check compares `op` to `REQ_OP_READ` after OR-ing flags, so the vmalloc destination range may not be invalidated as intended.
- `ntfs_bdev_write()` calls `memcpy_to_folio(folio, from, buf + buf_off, to)` with `to` as a length-like value, but `to` is calculated as an end offset within the page. For nonzero `from`, this can copy too much unless the API expects an end offset, which should be verified.
- Writes are not synchronous and do not report later writeback errors.

## Test Signals

Tests should cover sector misalignment rejection, non-vmalloc read, vmalloc read spanning more BIO segments than one BIO can hold, partial first/last page writes, block-device read folio failure, and writeback/invalidation behavior under metadata consumers.
