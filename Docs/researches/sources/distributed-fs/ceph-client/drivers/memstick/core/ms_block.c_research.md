# sources/distributed-fs/ceph-client/drivers/memstick/core/ms_block.c Research

## Purpose
`ms_block.c` implements the legacy Sony MemoryStick block-device driver. It binds legacy/Duo storage cards through the memstick core, builds an in-memory flash translation layer from boot/OOB metadata, exposes the medium as a blk-mq disk named `msblkN`, and serializes all media I/O through memstick TPC state machines.

## Important APIs, Types, And Functions
The public integration surface is `struct memstick_driver msb_driver`, `msb_probe`, `msb_remove`, optional `msb_suspend`/`msb_resume`, `msb_check_card`, `msb_stop`, and `msb_start`. Block-layer integration is via `msb_init_disk`, `msb_queue_rq`, `msb_io_work`, `msb_bdops`, and `msb_mq_ops`. The core media logic is split into state-machine callbacks (`h_msb_read_page`, `h_msb_write_block`, `h_msb_send_command`, `h_msb_reset`, `h_msb_parallel_switch`) and synchronous wrappers (`msb_read_page`, `msb_write_block`, `msb_erase_block`, `msb_update_block`). FTL setup is handled by `msb_read_boot_blocks`, `msb_read_bad_block_table`, `msb_ftl_initialize`, and `msb_ftl_scan`. Cache behavior lives in `msb_cache_init`, `msb_cache_read`, `msb_cache_write`, `msb_cache_flush`, and `msb_cache_flush_timer`.

## Control Flow
Probe allocates `struct msb_data`, resets and initializes the card, optionally switches to parallel mode, reads boot blocks, allocates FTL/cache buffers, reads factory bad-block tables, scans every physical block OOB, and then registers a blk-mq disk. A blk-mq request is accepted only if no request is already active; an ordered workqueue maps the request scatterlist, converts sector offsets to logical-block/page coordinates, and executes read or write loops one page at a time. Reads consult the write cache before issuing `MS_CMD_BLOCK_READ`. Whole-block writes bypass cache and allocate a replacement physical block; partial writes are coalesced in a block-size cache and later flushed by timer or before conflicting writes.

## State And Persistence
Persistent on-card state is the boot block, OOB logical-address fields, overwrite/management flags, factory bad-block tables, erased/free block state, and card data pages. Runtime-only state includes `lba_to_pba_table`, used and erased bitmaps, per-zone free counts, cached block data, request pointer, memstick register-window cache, and state-machine counters. The driver never persists a separate mapping table; it reconstructs the FTL from OOB metadata at probe/resume. Bad blocks/pages are persisted by clearing overwrite flag bits. Serious internal consistency failures switch the device read-only.

## Dependencies And Integration Points
This file depends on the Linux memstick core request protocol, blk-mq, gendisk lifetime, scatterlist helpers, timers, workqueues, IDR allocation, endian helpers, and the register/format constants from `<linux/memstick.h>` and `ms_block.h`. Host adapters must implement `memstick_host::set_param`, request submission, INT retrieval, and optional parallel/auto-INT capabilities. The block layer sees a single logical disk with logical block size equal to the MemoryStick page size.

## Risks
The FTL assumes single-threaded I/O and relies on one active blk-mq request; any future concurrency change would need stronger locking around bitmaps, cache, and register windows. Partial-write cache loss on sudden removal/power loss can leave updates pending. Error handling erases or marks blocks bad aggressively after resets, so host-controller false errors can cause avoidable wear or data loss. `msb_sg_copy` uses small temporary SG arrays in several paths; unexpected SG fragmentation beyond local limits would be a correctness risk. Resume validation is only active under `CONFIG_MEMSTICK_UNSAFE_RESUME`; otherwise the card is marked dead.

## Test Signals
Useful tests include module load/unload with legacy MemoryStick media, read-only class detection, serial-to-parallel fallback, full-card scan with factory bad blocks, random read/write/fsck cycles, partial-page writes that force cache fill and flush, bad-page/bad-block injection, suspend/resume with same and swapped cards, removal during active I/O, `verify_writes=1`, `debug=2`, and blk status checks for media errors.
