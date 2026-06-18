# Chunk Research: sources/virtualization/spdk/lib/bdev/bdev.c lines 9157-11549

## Scope

This chunk covers the tail of asynchronous bdev open, descriptor close and registration completion, bdev claim APIs including v1 exclusive claims and v2 multi-claim modes, bdev iteration helpers, bdev I/O metadata accessors, module registration, zero-fill fallback writes, QoS rate-limit enable/update/disable orchestration, histogram control and collection, media-management event queues, LBA-range locking and module quiesce/unquiesce, memory-domain queries, channel/I/O iteration wrappers, copy-blocks emulation, and bdev tracepoint registration.

The first line continues `_bdev_open_async()` from the previous chunk: open attempts, timeout checks, async-open shutdown cancellation, and `struct spdk_bdev_open_async_ctx` are defined just before this range. Many low-level helpers used here, including I/O submission, block-range validation, LBA overlap checks, QoS poller setup/destruction, and `set_qos_limit_ctx`, are also defined earlier in `bdev.c`.

## APIs And Entry Points

- Async open: `spdk_bdev_open_async()`, `bdev_open_async()`, option default/copy helpers.
- Close/register: `spdk_bdev_close()`, internal `bdev_close()`, `spdk_bdev_register()`, and `bdev_register_finished()`.
- Claims: legacy `spdk_bdev_module_claim_bdev()` plus v2 `spdk_bdev_module_claim_bdev_desc()` modes.
- Enumeration: `spdk_for_each_bdev()`, `spdk_for_each_bdev_leaf()`, `spdk_for_each_bdev_by_name()`.
- QoS/histograms/media events: rate-limit changes, per-channel histogram allocation/merge/free, descriptor media-event queues.
- LBA locks/quiesce: global and per-channel range locking plus module-scoped quiesce/unquiesce.
- Copy/tracing: `spdk_bdev_copy_blocks()` native-or-emulated copy and `bdev_trace()` tracepoint registration.

## Control Flow

Async open allocates a context, registers a 100 ms poller, queues it under `g_bdev_mgr.spinlock`, and immediately attempts open. Completion unregisters the poller, removes the async-open queue entry, and sends the callback to the originating thread.

Close removes a descriptor from `open_descs`, marks it closed, releases claims, frees it when refs reach zero, destroys QoS on last close, and may finish deferred unregister for a removing bdev.

Claim verification is mode-specific: read-write-once rejects existing claims and other writers; read-only-many requires non-writable descriptors; read-write-shared requires a nonzero matching shared key. Successful v2 claims allocate `spdk_bdev_module_claim`, link it into `claim.v2.claims`, and may promote the descriptor to writable.

QoS changes are serialized by `qos_mod_in_progress`. Limits are normalized in place, enabling walks channels to set QoS, updating posts to the QoS thread, and disabling clears per-channel QoS flags, resubmits queued I/O, then frees QoS state on the owning thread.

Histogram enable/disable is serialized by `histogram_in_progress`; enable allocates per-channel histograms and rolls back partial allocations on failure, while get merges all channel histograms into the caller aggregate.

LBA locking inserts a global lock range or pending range, installs per-channel copies, polls until overlapping submitted I/O drains, then lets matching owner-channel/caller-context I/O proceed. Unlock removes the global range first, removes channel copies, resubmits locked I/O, promotes pending ranges, and may resume unregister.

Copy-blocks validates writable descriptor and source/destination ranges. It submits native/split copy when available; otherwise it allocates a buffer and performs read-then-write emulation, queuing retry callbacks on `-ENOMEM`.

## State And Dependencies

Global state: `g_bdev_mgr.spinlock`, `async_bdev_opens`, `bdev_modules`, `zero_buffer`.

Per-bdev state: `open_descs`, `status`, `qos`, `qos_mod_in_progress`, claim fields, `examine_in_progress`, histogram fields, `locked_ranges`, `pending_locked_ranges`.

Per-descriptor/channel state: descriptor refs/write/claim/media queues; channel `locked_ranges`, `io_locked`, `io_submitted`, `qos_queued_io`, flags, histogram.

Dependencies include SPDK threads/pollers, spinlocks, TAILQ, bdev open/register/unregister/examine helpers, channel iteration, histogram APIs, bdev function-table callbacks, QoS helpers, event notification, I/O submission/range validation, and trace registration.

## Risks And Cross-Chunk References

- The chunk starts mid async-open completion; shutdown cancellation and timeout logic are in the prior chunk.
- V2 claim release during examination leaves dead claim nodes for later cleanup outside this chunk.
- `spdk_bdev_set_qos_rate_limits()` mutates the caller-provided `limits` array.
- QoS teardown is lifetime-sensitive because channel iteration and final free can occur on different threads.
- Histogram state fields are written after dropping the spinlock once `histogram_in_progress` is set.
- Media-event push targets the first writable descriptor with a buffer and can short-count/drop events.
- LBA lock correctness depends on earlier `bdev_io_range_is_locked()` and `bdev_lba_range_overlapped()`.
- Unlock resubmits all `io_locked` entries and depends on `bdev_io_submit()` rechecking remaining locks.
- Copy emulation can allocate `num_blocks * block_size`; large copies rely on native copy or split logic.
- Trace relations reference NVMe/blob/RAID tracepoints defined elsewhere.

## Summary

This chunk is the public-control and coordination tail of SPDK bdev: close/register, descriptor claims, iteration, QoS, histograms, media events, LBA quiesce/locking, memory-domain access, copy emulation, and tracing. The highest-risk areas are descriptor/bdev lifetime, claim cleanup during examination, cross-thread QoS/histogram changes, and range-lock interaction with submitted and locked I/O queues.