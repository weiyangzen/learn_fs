# sources/distributed-fs/ceph-client/drivers/block/brd.c

## Purpose

`brd.c` implements the RAM-backed block device driver. Each ramdisk stores written pages in a sparse xarray keyed by page-sized sector ranges, reads unwritten pages as zeroes, supports page-granular discard, exposes optional debugfs page counts, and registers the historical ramdisk major with optional on-demand device allocation.

## Important APIs, Types, and Data

- `struct brd_device` holds the ramdisk number, `gendisk`, global list node, xarray of backing pages, and `brd_nr_pages` debug/accounting counter.
- `brd_lookup_page()` performs an RCU xarray lookup and safely grabs a page reference with retry handling.
- `brd_insert_page()` allocates a zeroed highmem page and atomically inserts it into the xarray with `__xa_cmpxchg()`.
- `brd_rw_bvec()` processes one bio segment fragment capped to a brd page boundary.
- `brd_do_discard()` erases fully page-aligned page ranges from the xarray.
- `brd_submit_bio()` is the block I/O entry point.
- Module parameters: `rd_nr`, `rd_size`, and `max_part`.
- `brd_alloc()`, `brd_probe()`, `brd_cleanup()`, `brd_init()`, and `brd_exit()` manage device lifecycle.

## Control Flow

`brd_init()` normalizes `max_part`, creates the `ramdisk_pages` debugfs directory, registers `RAMDISK_MAJOR` with `brd_probe()` as an on-demand probe callback, and allocates `rd_nr` initial devices.

`brd_alloc()` creates one `struct brd_device`, initializes its xarray, creates a debugfs `u64` page counter if debugfs setup succeeded, allocates a disk with queue limits, assigns `brd_fops`, sets capacity to `rd_size * 2` sectors, and calls `add_disk()`.

Normal I/O reaches `brd_submit_bio()`. Discard bios are handled by `brd_do_discard()` and completed immediately. Read/write bios loop over `brd_rw_bvec()` until `bio->bi_iter.bi_size` is exhausted, then call `bio_endio()`.

`brd_rw_bvec()` calculates the target brd page and offset from `bi_sector`, limits the operation to the rest of that page, looks up the existing page, allocates on write if missing, maps the bio vector locally, copies bytes into or out of the page, zero-fills reads from missing pages, advances the bio iterator, and drops the page reference. Allocation failure reports `bio_wouldblock_error()` for `REQ_NOWAIT` allocation misses or `bio_io_error()` otherwise.

`brd_do_discard()` rounds the requested sector range inward to full brd pages, erases pages under xarray lock, drops page references, and decrements `brd_nr_pages`.

Cleanup removes debugfs, deletes/puts disks, frees all xarray pages, destroys xarrays, and frees device structs.

## State and Persistence Behavior

The device contents are volatile memory only. Written pages persist until discarded, the module exits, the device is destroyed, or memory is reclaimed by explicit driver teardown. Unwritten sectors are implicit zeroes and consume no memory.

The xarray is the authoritative content store. `brd_nr_pages` tracks currently allocated backing pages for debugfs visibility. No backing storage, metadata, or recovery path exists.

## Dependencies and Integration Points

- Linux block layer: `gendisk`, `block_device_operations.submit_bio`, queue limits, capacity, dynamic block-major probing.
- Memory APIs: highmem pages, local bvec mapping, xarray with RCU and explicit xarray lock.
- Debugfs: optional `ramdisk_pages/ramN` counters.
- Kernel boot/module compatibility: `ramdisk_size=` setup when built in, `MODULE_ALIAS_BLOCKDEV_MAJOR(RAMDISK_MAJOR)`, and alias `rd`.

## Risks and Edge Cases

- `brd_lookup_page()` must handle concurrent erasure and page ref acquisition correctly; its retry loop is central to avoiding use-after-free.
- `brd_insert_page()` allocates before xarray insertion. Concurrent writers may race; the cmpxchg path drops the unused page and returns the existing page with a reference.
- Discard erases only full page-aligned ranges, so partial-page discard does not zero partial sectors.
- Memory growth is proportional to written pages and bounded only by allocation failure. Large writes can exhaust memory.
- Queue limits advertise `BLK_FEAT_NOWAIT`, so `REQ_NOWAIT` paths must fail with would-block semantics when allocation cannot proceed.
- `brd_alloc()` creates debugfs entries before disk allocation; cleanup relies on recursive debugfs removal during module cleanup rather than per-device removal on early allocation failure.

## Test Signals

- Build with ramdisk support as built-in and module.
- Create initial and on-demand `/dev/ramN` devices and verify capacity/minor spacing with several `max_part` values.
- Read unwritten sectors and verify zero-fill.
- Write, read back, discard aligned ranges, and verify discarded pages read zero and page counters decrease.
- Exercise unaligned discard to confirm only full pages are removed.
- Use `REQ_NOWAIT` write paths under memory pressure to verify would-block completion.
- Concurrent read/write/discard stress to shake xarray reference and erase races.
