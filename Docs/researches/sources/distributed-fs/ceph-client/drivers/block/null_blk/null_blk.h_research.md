# sources/distributed-fs/ceph-client/drivers/block/null_blk/null_blk.h

## Purpose
This header defines the shared data structures and function contracts for null_blk core, zoned support, tracing, and memory-backed helpers.

## Important APIs, Types, And Functions
`struct nullb_cmd` is the blk-mq request PDU and carries status, fake-timeout state, queue pointer, and optional timer. `struct nullb_queue` is per-hctx queue state with poll list and lock. `struct nullb_zone` represents a zoned block zone with lock, type, condition, start, write pointer, length, and capacity. `struct nullb_device` stores configfs/module configuration, radix-tree storage/cache, badblocks, zoned accounting, and all tunables. `struct nullb` is the live disk instance with queue, gendisk, tag set, throttling timer/counter, cache flush position, lock, queue array, and disk name.

The header declares core helpers `null_handle_discard()`, `null_process_cmd()`, `null_handle_badblocks()`, and `null_handle_memory_backed()`. When `CONFIG_BLK_DEV_ZONED` is enabled it declares zoned helpers implemented elsewhere; otherwise it provides stubs returning unsupported/no-op behavior and maps `null_report_zones` to `NULL`.

## Control Flow
The header controls compile-time flow for zoned support. `main.c` can call zoned operations unconditionally because the header supplies either real declarations or stubs. It also defines the layout that blk-mq callbacks, memory-backed data paths, configfs code, and tracepoints share.

## State And Persistence Behavior
All state is volatile per module/device lifetime. `struct nullb_device` contains the pseudo-persistent contents when memory backing is enabled, represented by `data` and `cache` radix trees. Zone arrays and counters represent simulated zoned-media state. No on-disk persistence is defined.

## Dependencies And Integration Points
The header depends on blkdev, blk-mq, hrtimer, configfs, badblocks, fault injection, spinlocks, and mutexes. It is included by `main.c`, `trace.h`, `trace.c`, and zoned support.

## Risks
Changing structure fields affects blk-mq PDU sizing, configfs behavior, and zoned helper assumptions. Zoned stubs must remain behaviorally compatible with callers when zoned support is disabled. `struct nullb_device` mixes immutable-after-config fields with live-updatable queue fields, so users of the header must respect locking and configured/up flags.

## Test Signals
Successful builds with and without `CONFIG_BLK_DEV_ZONED` are the primary header test. Runtime signals include correct PDU operation, configfs attribute state reflecting `struct nullb_device`, zoned calls returning `-EOPNOTSUPP` or working depending on config, and memory-backed helpers operating on the declared radix trees.
