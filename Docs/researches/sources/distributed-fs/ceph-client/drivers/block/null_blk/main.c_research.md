# sources/distributed-fs/ceph-client/drivers/block/null_blk/main.c

## Purpose
This file implements the null_blk test block driver. It creates synthetic block devices through module parameters and configfs, exercises blk-mq queueing/completion paths, optionally stores data in memory, supports discard/cache/FUA/badblocks/zoned hooks, throttles bandwidth, supports polling and timer/softirq/inline completions, and optionally injects request faults.

## Important APIs, Types, And Functions
Core runtime types are `struct nullb_device` and `struct nullb` from `null_blk.h`, plus local `struct nullb_page` for memory-backed radix-tree pages. Module parameters populate global defaults such as `gb`, `bs`, `submit_queues`, `poll_queues`, `irqmode`, `completion_nsec`, `memory_backed`, `discard`, `cache_size`, `mbps`, zoned settings, shared tags, and fault strings.

Configfs is implemented with generated `NULLB_DEVICE_ATTR()` attributes, `nullb_device_power_store()`, badblocks stores, zone condition stores, `nullb_group_make_group()`, `nullb_group_drop_item()`, and subsystem `nullb_subsys`. Device lifecycle is `null_alloc_dev()`, `null_add_dev()`, `null_del_dev()`, `null_destroy_dev()`, and `null_free_dev()`. blk-mq integration is `null_mq_ops` with `null_queue_rq()`, `null_queue_rqs()`, `null_complete_rq()`, `null_timeout_rq()`, `null_poll()`, `null_map_queues()`, and `null_init_hctx()`.

Memory-backed behavior uses `null_alloc_page()`, `null_insert_page()`, `copy_to_nullb()`, `copy_from_nullb()`, `null_handle_discard()`, `null_handle_flush()`, `null_handle_data_transfer()`, and `null_process_cmd()`. Throttling uses `null_handle_throttled()` and `nullb_bwtimer_fn()`. Init/exit are `null_init()` and `null_exit()`.

## Control Flow
Module init validates global parameters, initializes optional fault attributes, registers the configfs subsystem, registers a dynamic block major, and creates `nr_devices` default devices. Configfs users can create named device groups and set attributes before powering them on; once powered, most attributes reject changes with `-EBUSY`, while submit/poll queue counts can be applied live through `blk_mq_update_nr_hw_queues()`.

`null_add_dev()` validates config, allocates `struct nullb`, queue state, tag set, queue limits, optional zoned state, cache/writeback features, disk, IDA index, capacity, and gendisk. It adds the disk and tracks it in `nullb_list`. `null_del_dev()` reverses this, cancels throttling, deletes the disk, releases tag sets/queues, flushes cache storage, and detaches the device.

For each request, `null_queue_rq()` prepares the command PDU, handles injected timeout/requeue, enforces bandwidth throttling, starts the request, and either queues it to a poll list, leaves fake timeouts incomplete, or calls `null_handle_cmd()`. `null_handle_cmd()` handles flush specially, dispatches zoned or generic processing, preserves earlier timeout errors, and completes inline, through softirq, or through an hrtimer. Generic processing checks configured badblocks, performs memory-backed reads/writes/discards when enabled, and otherwise completes successfully without storing data. Poll queues defer processing until `null_poll()` drains the poll list and batches completions.

## State And Persistence Behavior
The driver is synthetic. Without `memory_backed`, data is not persisted and reads normally complete without filling buffers except under KMSAN zero-fill behavior. With `memory_backed`, written sectors are stored in radix trees of pages (`data`) and optional writeback cache pages (`cache`). Cache pages use bitmap bits for valid sectors plus lock/free sentinel bits. `REQ_FUA` writes bypass/flush cache sector state. Flush drains the cache into the backing radix tree. All state is volatile and lost when the device or module is removed. Badblocks, configfs attributes, throttling counters, queue mappings, and zoned state are runtime-only.

## Dependencies And Integration Points
The file integrates with blk-mq, gendisk, configfs, module parameters, IDA, radix trees, badblocks, hrtimers, fault injection configfs, optional zoned support from `zoned.c`, queue limits, request polling, KMSAN, and block features for discard, write cache, FUA, rotational, and zoned reporting.

## Risks
Memory-backed mode uses spinlock-protected radix trees but temporarily drops the lock for allocation/preload, so lookup/insert races are handled by radix insert fallback and page-private checks. Cache flushing uses lock/free sentinel bits to avoid freeing a page while another thread flushes it. Poll timeout must remove requests from the poll list safely. Shared global tag sets mean multiple devices share blk-mq resources when `shared_tags` is set. Configfs power transitions must avoid double add/delete. Throttling stops hardware queues and relies on timer refill to restart them.

## Test Signals
Signals include module load/unload, default `nullb*` device creation, configfs create/attribute/power flows, blk-mq reads/writes with every irq mode, poll I/O, bandwidth throttling, memory-backed data readback, discard clearing stored data, cache flush/FUA behavior, badblocks full and partial errors, fault-injected timeout/requeue/init_hctx failure, live queue-count updates, zoned mode when configured, and teardown while I/O is active.
