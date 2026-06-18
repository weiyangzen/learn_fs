# Chunk Research: sources/virtualization/spdk/lib/bdev/bdev.c lines 1-9156

## Scope

This chunk covers the first 9,156 lines of SPDK's generic block-device core. It includes global bdev manager setup, bdev option/config handling, module initialization/finalization, examine orchestration, per-thread/channel resources, public I/O submission APIs, split I/O, QoS, reset/abort paths, completion/status translation, registration/unregistration, and descriptor open setup. The chunk ends inside the async-open implementation; descriptor close, media events, claims v1/v2, LBA lock/unlock continuation, module registration, memory-domain queries, and trace registration continue in chunk 2.

## Core State

- `g_bdev_mgr` is the process-global registry: bdev I/O mempool, zero buffer, module list, bdev list, RB tree of names/aliases, subsystem init flags, spinlock, and pending async opens.
- `g_bdev_opts` controls bdev I/O pool/cache sizing, auto examine, and per-channel iobuf cache sizes. `spdk_bdev_get_opts()`/`spdk_bdev_set_opts()` use versioned struct-size field copying and validate mempool size against thread count.
- `spdk_bdev_channel` is the per-thread/per-bdev state: backend channel, accel channel, shared resource, outstanding counters, submitted/locked/accel/memory-domain queues, QoS queue, histogram, trace id, and replicated locked ranges.
- `spdk_bdev_shared_resource` centralizes NOMEM retry queues, shared outstanding counters, a retry poller, and refcounting across bdev channels sharing a backend channel.
- `spdk_bdev_desc` is an open handle with write permission, open options, owner thread, event callback, refcount, timeout poller, media-event pool, and claim pointer.
- `lba_range` is used for compare-and-write emulation, quiesce, and range locking; main lock/unlock implementation continues in chunk 2.

## Control Flow

- `spdk_bdev_initialize()` registers notify types, the bdev iobuf module, the global I/O mempool, zero buffer, manager io_device, and each bdev module.
- `bdev_examine()` runs module `examine_config()` and `examine_disk()` based on claim state: unclaimed, v1 exclusive-write claim, or v2 claim list.
- `spdk_bdev_finish()` cancels async opens, waits for examine completion, finalizes modules, unregisters bdevs, and frees global resources.
- Public I/O APIs allocate/init `spdk_bdev_io`, validate access/ranges/features/metadata, then call `_bdev_io_submit_ext()` or `bdev_io_submit()`.
- `bdev_io_submit()` checks locked ranges, records trace/timestamp, handles split I/O, QoS, reset-in-progress, and backend `submit_request()`.
- Completion flows through `spdk_bdev_io_complete()`, which balances outstanding counters, handles reset completion, NOMEM retry, accel/bounce completion, stats, histogram, trace, and user callbacks.

## Key APIs Covered

- Config/discovery: `spdk_bdev_get_opts()`, `spdk_bdev_set_opts()`, `spdk_bdev_get_by_name()`, bdev iteration, `spdk_bdev_subsystem_config_json()`, `spdk_bdev_examine()`.
- I/O: read/readv/readv_ext, write/writev/writev_ext, compare, compare-and-write, zcopy, write zeroes, write uncorrectable, unmap, flush, reset, abort, seek data/hole, NVMe passthrough.
- Stats/status: device/channel stats, stat reset, QD sampling/current QD, resize notification, SCSI/AIO/NVMe/base status mapping.
- Lifecycle: `bdev_register()`, `spdk_bdev_unregister()`, `spdk_bdev_open_ext_v2()`, `spdk_bdev_open_ext()`, partial `spdk_bdev_open_async()`.

## Dependencies

- SPDK core threading, io_device/channels, pollers/messages, spinlocks, mempools, iobuf, notify, trace, JSON, UUID, logging, and env allocation.
- SPDK accel, DMA/memory-domain APIs, DIF helpers, NVMe and SCSI specs/status translation.
- Backend bdev module `fn_table`: `submit_request`, `get_io_channel`, feature support, optional accel/memory-domain support, config/info JSON, destruct, and optional metrics.

## Risks And Invariants

- Submitted I/Os must be on `io_submitted`; unsubmitted error paths must use `bdev_io_complete_unsubmitted()`.
- Outstanding counters must balance across backend submit, accel execution, memory-domain transfer, reset, and queued abort paths.
- Memory-domain and accel operations cannot be forcibly aborted; reset may fail if these are still active after drain timeout.
- QoS teardown swaps structures because new opens/channels can race with poller destruction.
- Name registration intentionally happens only after the io_device and bdev internals are ready.
- Compare-and-write emulation depends on range locking implemented later in the file.

## Cross-Chunk References

- Lines after 9156 complete `spdk_bdev_open_async()`, then implement descriptor close, media events, claims, QoS setters, histogram APIs, memory-domain query wrappers, LBA lock/unlock/quiesce internals, `spdk_bdev_for_each_io()`, and log/trace registration.
- Forward declarations resolved later include `bdev_enable_qos_msg()`, `bdev_enable_qos_done()`, `bdev_lock_lba_range()`, `bdev_unlock_lba_range()`, `claim_type_is_v2()`, `bdev_desc_release_claims()`, `claim_reset()`, and `bdev_write_zero_buffer()`.