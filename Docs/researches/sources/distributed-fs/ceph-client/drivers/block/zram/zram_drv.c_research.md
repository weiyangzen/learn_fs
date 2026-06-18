# Research: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.c

## Purpose

`zram_drv.c` implements the Linux compressed RAM block device. It exposes `/dev/zramN` disks whose logical pages are stored as compressed objects in a `zsmalloc` pool, with optional writeback to a configured backing block device and optional multi-compressor recompression. The file owns the block-device operations, sysfs control plane, per-slot locking, compressor lifecycle, metadata allocation, I/O path, writeback/recompression post-processing, debugfs memory tracking, and module hot-add/hot-remove lifecycle.

## Important APIs, Types, And Functions

The primary runtime object is `struct zram` from `zram_drv.h`; this file manipulates its table, `zs_pool`, compressor array, disk, `dev_lock`, stats, and optional writeback/debugfs fields. Slot state is stored in `struct zram_table_entry` through `handle` and packed flags, with helpers such as `get_slot_handle`, `set_slot_size`, `test_slot_flag`, `set_slot_comp_priority`, and `slot_allocated`.

The I/O entry point is `zram_submit_bio`, installed in `zram_devops`. It dispatches reads to `zram_bio_read`, writes to `zram_bio_write`, and discard/write-zeroes to `zram_bio_discard`. Page-level operations are handled by `zram_read_page`, `zram_write_page`, `read_from_zspool`, `write_same_filled_page`, `write_incompressible_page`, and partial-I/O helpers. `slot_free` is the central cleanup routine for in-memory, same-filled, huge, writeback, and post-processing slots.

The sysfs surface includes `disksize`, `initstate`, `reset`, `compact`, `mem_limit`, `mem_used_max`, `idle`, `comp_algorithm`, `algorithm_params`, stats files, and, when configured, `backing_dev`, `writeback`, `writeback_limit`, `writeback_batch_size`, `compressed_writeback`, `recomp_algorithm`, and `recompress`. Device management uses `zram_add`, `zram_remove`, `hot_add_show`, and `hot_remove_store`.

## Control Flow

Module initialization registers a CPU hotplug state for zcomp streams, registers the `zram-control` class, registers a dynamic block major, creates debugfs root state if enabled, and pre-creates `num_devices` devices with `zram_add`. `zram_add` allocates a `struct zram`, reserves an IDR id under `zram_index_mutex`, builds a `gendisk` with PAGE-sized physical limits, installs sysfs groups, sets the default compressor, and publishes the disk at zero capacity. A device becomes usable when userspace writes `disksize`: `disksize_store` allocates the slot table and zsmalloc pool, creates configured compressors, records `zram->disksize`, and updates block capacity.

Writes call `zram_bvec_write` for each bio segment. Full-page writes compress directly through the primary compressor unless the page is same-filled or too large for the huge class. Same-filled pages store the fill element in the slot handle and set `ZRAM_SAME`; incompressible pages are stored uncompressed in zsmalloc and set `ZRAM_HUGE`; normal pages store compressed bytes and a size. The old slot is freed while holding the slot lock before the new handle and flags are installed. Reads lock the slot, read same-filled/huge/compressed objects from zsmalloc, or unlock and read from the backing device if `ZRAM_WB` is set.

Writeback is driven by `writeback_store`. It parses mode/range arguments, scans eligible slots into post-processing buckets using `ZRAM_PP_SLOT`, allocates a bounded request pool from `wb_batch_size`, reserves backing-device bitmap blocks, reads slot contents into request pages, submits write BIOs, and completes them through `zram_writeback_endio` and `zram_writeback_complete`. Recompression follows a similar scan/select pattern, using secondary compressor priorities and replacing an object only if the new zsmalloc class is smaller and below the optional threshold.

## State And Persistence

Runtime state is memory resident except for optional writeback contents stored on the configured backing block device. The zram metadata table records per-logical-page handles, compressed size, and flags such as `ZRAM_SAME`, `ZRAM_WB`, `ZRAM_HUGE`, `ZRAM_IDLE`, `ZRAM_PP_SLOT`, `ZRAM_INCOMPRESSIBLE`, and compressor priority bits. Stats are atomic and reset by `zram_reset_device`. The backing device is opened exclusively before initialization, tracked by `zram->backing_dev`, `zram->bdev`, a bitmap of reserved PAGE-sized blocks, and writeback counters. Reset closes and forgets backing state; it does not preserve zram contents across reset, device removal, or module unload.

`dev_lock` gates device initialization, reset, sysfs configuration, writeback, and recompression. Per-slot bit locks serialize individual slot mutation and are lockdep-instrumented. The `claim` flag, protected by `disk->open_mutex`, blocks opens during reset/removal. Debugfs `block_state` can expose per-slot state and access time when memory tracking is enabled.

## Dependencies And Integration Points

This file integrates the block layer (`gendisk`, `bio`, queue limits, block stats, swap slot free notifications), zsmalloc, zcomp compressor backends, sysfs, debugfs, CPU hotplug, the firmware/file reading API for dictionaries, and optional backing block-device BIO submission. It relies on `zcomp_cpu_up_prepare` and `zcomp_cpu_dead` from the zcomp implementation and on Kconfig features such as `CONFIG_ZRAM_WRITEBACK`, `CONFIG_ZRAM_MULTI_COMP`, `CONFIG_ZRAM_MEMORY_TRACKING`, and `CONFIG_ZRAM_TRACK_ENTRY_ACTIME`.

## Risks

The highest-risk areas are concurrency and state transitions: writeback intentionally releases slot locks while I/O is in flight and relies on `ZRAM_PP_SLOT` to detect slot replacement or free, so any future changes to `slot_free` or scan logic must preserve that protocol. Partial I/O requires read-modify-write of whole pages and, for backing-device reads, sync workers to avoid block-layer deadlocks. Limit accounting is subtle for non-4K PAGE_SIZE, as shown by the writeback limit rounding. `slot_free` updates several counters depending on flag combinations; incorrect flag ordering can underflow stats or leak backing-device bitmap blocks. Firmware/dictionary loading through `algorithm_params` and backing-device path parsing are privileged sysfs surfaces and should remain initialization-only where intended.

## Test Signals

Useful validation signals include sysfs initialization/reset behavior, `mm_stat`, `io_stat`, `bd_stat`, `debug_stat`, and debugfs `block_state`. Functional tests should cover same-filled writes, incompressible writes, read-after-write, discard/write-zeroes, partial I/O on PAGE_SIZE != logical block size, `mem_limit` failures, compressor parameter rejection after initialization, reset refusal while open, hot-add/hot-remove, writeback modes and ranges, compressed writeback readback, backing-device full conditions, and recompression with secondary algorithms and thresholds.
