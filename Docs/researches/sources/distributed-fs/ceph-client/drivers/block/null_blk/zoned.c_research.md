# sources/distributed-fs/ceph-client/drivers/block/null_blk/zoned.c

## Purpose
Implements zoned block device behavior for the `null_blk` synthetic block driver. It lets null_blk emulate conventional and sequential write required zones, write pointers, zone append, zone management commands, max active/open zone limits, optional memory-backed contents, badblocks interaction, and configfs-driven read-only/offline zone condition injection.

## Important APIs, Types, And Functions
The file works against `struct nullb_device`, `struct nullb`, `struct nullb_cmd`, and `struct nullb_zone` from `null_blk.h`, and Linux block layer zone types and request operations. Public entry points used by the rest of null_blk are `null_init_zoned_dev()`, `null_register_zoned_dev()`, `null_free_zoned_dev()`, `null_report_zones()`, `null_zone_valid_read_len()`, `null_process_zoned_cmd()`, and `zone_cond_store()`.

`null_init_zoned_dev()` validates power-of-two zone size, capacity constraints, smaller-last-zone rules, max active/open limits, and initializes each zone's type, start, length, capacity, condition, write pointer, and per-zone lock. It also programs `queue_limits` with `BLK_FEAT_ZONED`, chunk size, zone append maximum, and resource limits.

`null_zone_write()` is the core write path. Conventional zones pass through to `null_process_cmd()`. Sequential zones enforce write-at-WP semantics, implement zone append by rewriting the request sector, optionally enforce active/open resources, process badblocks and memory backing, advance `zone->wp`, and transition to `FULL` at capacity.

Zone management is implemented by `null_open_zone()`, `null_close_zone()`, `null_finish_zone()`, `null_reset_zone()`, and `null_zone_mgmt()`. Resource accounting is centralized in `null_check_active()`, `null_check_open()`, `null_check_zone_resources()`, and `null_close_imp_open_zone()`.

## Control Flow
Device setup calls `null_init_zoned_dev()`, then registration calls `blk_revalidate_disk_zones()` through `null_register_zoned_dev()`. Reads and writes later enter `null_process_zoned_cmd()`. Writes and zone appends go to `null_zone_write()`, management commands go to `null_zone_mgmt()`, and all other operations are passed through under the target zone lock after rejecting offline zones.

Zone reporting computes the first zone from the requested sector, copies zone state under the zone lock, and calls `disk_report_zone()` with a local `struct blk_zone` to avoid allowing stacked devices to mutate the internal zone array. Configfs writes through `zone_cond_store()` parse a sector, find the zone, reject non-zoned/unpowered/conventional-zone cases, and toggle read-only or offline state through `null_set_zone_cond()`.

## State And Persistence Behavior
All zone state is in memory in `dev->zones`: type, condition, start, length, capacity, write pointer, and lock. Resource state is kept in device counters: `nr_zones_exp_open`, `nr_zones_imp_open`, `nr_zones_closed`, `zone_max_active`, `zone_max_open`, `need_zone_res_mgmt`, and `imp_close_zone_no`. There is no persistent metadata; module/device teardown frees the zone array. If `memory_backed` is enabled, writes, resets, and condition toggles affect the in-memory data store through null_blk memory helpers.

Locking switches by backing mode: non-memory-backed zones use spinlocks, while memory-backed zones use mutexes because `null_handle_memory_backed()` and discard paths can sleep. Resource counters are guarded by `zone_res_lock`.

## Dependencies And Integration Points
This code integrates with null_blk main command processing, null_blk configfs attributes, block zoned APIs (`blk_revalidate_disk_zones`, `disk_report_zone`), request operations (`REQ_OP_ZONE_*`, `REQ_OP_ZONE_APPEND`), tracepoints in `trace.h`, badblocks handling, and optional memory-backed data handling. It is built when null_blk and zoned block support are enabled.

## Risks
The highest-risk behavior is correct synchronization between per-zone locks and `zone_res_lock`, because resource counters must match zone condition transitions. Boundary handling is also critical: smaller last zones, `zone_capacity < zone_size`, write pointer overflow, and zone append maximum alignment all affect block-layer correctness. Memory-backed paths use mutexes to avoid sleeping under spinlock; future changes must preserve that distinction. `null_finish_zone()` sets `wp` to `start + len` rather than `start + capacity`, which is intentional in current code but is a detail to recheck when changing capacity semantics. Configfs condition toggling invalidates write pointers with `NULL_ZONE_INVALID_WP`, so write and report paths must continue to handle invalid WPs safely.

## Test Signals
Good signals include `blktests` zoned block tests, fio zoned workloads with regular write and zone append, zone reset/open/close/finish command tests, configfs toggling of read-only/offline zones, memory-backed read-after-write and reset/discard checks, badblocks injection, and limit tests for max active/open resources. Tracepoints `trace_nullb_report_zones()` and `trace_nullb_zone_op()` are useful for confirming state transitions.
