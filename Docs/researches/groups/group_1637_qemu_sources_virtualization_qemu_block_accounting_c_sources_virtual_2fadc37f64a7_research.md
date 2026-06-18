# Group Research: group_1637_qemu_sources_virtualization_qemu_block_accounting_c_sources_virtual_2fadc37f64a7

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/virtualization/qemu`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/accounting.c -->
# File Research: sources/virtualization/qemu/block/accounting.c

This file implements QEMU block-layer I/O accounting: operation counts, byte counts, failed/invalid/merged request counters, latency totals, timed moving averages, idle-time calculation, and optional latency histograms.

Key entry points:
- `block_acct_init()` initializes the mutex, selects virtual clock under qtest, and defaults `account_invalid`/`account_failed` to true.
- `block_acct_setup()` applies `OnOffAuto` policy for invalid/failed accounting and installs timed-stat intervals via `block_acct_add_interval()`.
- `block_acct_start()` records bytes, start timestamp, and I/O type in a `BlockAcctCookie`.
- `block_acct_done()` and `block_acct_failed()` both route to `block_account_one_io()`, which updates counters, histograms, total latency, last-access time, and interval averages under `stats->lock`.
- `block_acct_invalid()` counts invalid submissions without adding latency because no actual I/O happened.
- `block_latency_histogram_set()` validates strictly increasing bucket boundaries and replaces the histogram arrays for a specific `BlockAcctType`.
- `block_acct_queue_depth()` derives queue depth as timed latency sum divided by elapsed interval time.

Concurrency model:
- Mutable `BlockAcctStats` fields are protected by `stats->lock`.
- Histogram updates occur inside the same accounting lock when called from request completion.
- Interval list mutation is locked during insertion, but iteration helper `block_acct_interval_next()` itself does not lock, so callers must already be in a safe context.

Notable behavior:
- qtest forces deterministic latency (`qtest_latency_ns`) for stable tests.
- Failed I/O increments `failed_ops` and only contributes latency if `account_failed` is enabled.
- Successful I/O increments bytes and operation count.
- Invalid I/O may update `last_access_time_ns` depending on `account_invalid`.
- `cookie->type` is reset to `BLOCK_ACCT_NONE` after completion to avoid double-accounting.

Filesystem/block relevance:
- This is observability infrastructure for QEMU block devices rather than a storage format or driver.
- It feeds monitor-visible block statistics and timing metrics used to reason about guest-visible disk behavior, throttling, and error handling.

Potential pitfalls:
- `block_acct_idle_time_ns()` reads `last_access_time_ns` without taking the stats lock, so consumers should treat it as an approximate statistic.
- `block_acct_queue_depth()` divides by `elapsed`; correctness relies on `timed_average_sum()` providing nonzero elapsed time.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/accounting.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/aio_task.c -->
# File Research: sources/virtualization/qemu/block/aio_task.c

This file provides a small coroutine task-pool helper for running bounded numbers of asynchronous block-related tasks.

Key structures and functions:
- `AioTaskPool` tracks the main coroutine, first negative status, maximum concurrent tasks, current busy count, and whether the main coroutine is waiting.
- `aio_task_pool_new()` creates a pool bound to the current coroutine and asserts `max_busy_tasks > 0`.
- `aio_task_pool_start_task()` waits for capacity, assigns the pool to the task, and enters a newly created coroutine running `aio_task_co()`.
- `aio_task_co()` increments `busy_tasks`, runs `task->func(task)`, records the first negative return as pool status, frees the task, and wakes the main coroutine if needed.
- `aio_task_pool_wait_one()`, `aio_task_pool_wait_slot()`, and `aio_task_pool_wait_all()` implement capacity and completion waiting.
- `aio_task_pool_status()` returns zero for a null pool, allowing lazy pool allocation.

Concurrency model:
- This is coroutine-local coordination, not thread-level locking.
- The main coroutine is expected to be the only waiter and is asserted in `aio_task_pool_wait_one()`.
- Tasks are heap-owned by the pool once started; `aio_task_co()` frees them after completion.

Filesystem/block relevance:
- Used by block-copy style code to bound parallel copy workers while preserving coroutine scheduling semantics.
- Provides a simple failure propagation model: first failing task sets pool status, and later submitters can observe that failure.

Potential pitfalls:
- Only one waiter is modeled via `pool->waiting`.
- The pool must not be freed before all tasks finish; callers should use `aio_task_pool_wait_all()` before `aio_task_pool_free()`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/aio_task.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/amend.c -->
# File Research: sources/virtualization/qemu/block/amend.c

This file implements the QMP `x-blockdev-amend` job path for changing image-format options through a block job.

Key structures and functions:
- `BlockdevAmendJob` embeds `Job`, stores cloned `BlockdevAmendOptions`, the target `BlockDriverState`, and the `force` flag.
- `blockdev_amend_run()` runs under graph read lock, sets job progress to one unit, invokes the format driver's `bdrv_co_amend()`, updates progress, and frees the cloned options.
- `blockdev_amend_pre_run()` calls optional driver-specific `bdrv_amend_pre_run()`.
- `blockdev_amend_free()` calls optional `bdrv_amend_clean()` under graph read lock and unreferences the target BDS.
- `qmp_x_blockdev_amend()` validates node lookup, driver lookup, whitelist rules, driver immutability, and amend support, then creates and starts a manual-dismiss amend job.

Concurrency and graph model:
- QMP setup uses `GRAPH_RDLOCK_GUARD_MAINLOOP()`.
- The actual job run uses `GRAPH_RDLOCK_GUARD()`.
- Cleanup takes the graph read lock in the main loop before invoking driver cleanup.

Filesystem/block relevance:
- This is a format-maintenance control path, not data-plane I/O.
- It exposes driver-specific image option mutation while using QEMU's job framework for async execution, progress, lifecycle, and failure reporting.

Potential pitfalls:
- The command rejects changing the block driver; the option driver must match `bs->drv`.
- Driver support is mandatory through `.bdrv_co_amend`.
- `options` are cloned into the job; caller-owned QAPI options are not consumed directly by the job.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/amend.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/backup.c -->
# File Research: sources/virtualization/qemu/block/backup.c

This file implements QEMU block backup jobs using copy-before-write filtering and the shared `block-copy` engine.

Key structures:
- `BackupBlockJob` embeds `BlockJob` and stores the copy-before-write node, source and target BDS pointers, optional sync bitmap, sync/bitmap modes, source/target error policies, image length, cluster size, performance settings, `BlockCopyState`, and state for a background block-copy call.

Major flows:
- `backup_job_create()` validates source/target presence and size, rejects source equal to target, checks compression support, operation blockers, worker/chunk constraints, and optional dirty-bitmap writability.
- It creates a successor dirty bitmap when incremental bitmap synchronization is requested.
- It appends a copy-before-write filter with `bdrv_cbw_append()`, obtains a `BlockCopyState`, creates the block job on the CBW node, configures block-copy options/progress/speed, and adds the target as a job BDS.
- `backup_run()` initializes the copy bitmap, handles `sync=top` by scanning/resetting unallocated regions, then either waits for cancellation in `sync=none` mode or runs `backup_loop()`.
- `backup_loop()` repeatedly launches `block_copy_async()` over the full aligned job length, waits/yields for completion or cancellation, and handles read/write errors according to backup error policies.
- `backup_pause()` cancels an active block-copy call and waits for it to finish.
- `backup_cancel()` cancels target in-flight requests.
- `backup_commit()` and `backup_abort()` reconcile the sync bitmap differently depending on success/failure and `BitmapSyncMode`.

Bitmap semantics:
- `backup_cleanup_sync_bitmap()` either abdicates the successor into the parent bitmap or reclaims it.
- With `BITMAP_SYNC_MODE_ALWAYS`, failure still syncs and then merges bits that were not copied back from the block-copy dirty bitmap.
- `backup_do_checkpoint()` only supports `sync=none` and marks the entire block-copy bitmap dirty for future CBW-triggered copying.

Concurrency and job model:
- Backup work is coroutine-driven through the job framework.
- Background copy is represented by `BlockCopyCallState`; callbacks wake the job coroutine or re-enter the job.
- Cancellation and pause rely on `block_copy_call_cancel()` plus explicit coroutine yield/wake coordination.

Filesystem/block relevance:
- This is a central virtual block snapshot/backup mechanism.
- It combines dirty bitmaps, copy-before-write filters, block graph permissions, and target writes to preserve point-in-time source content.

Potential pitfalls:
- Source and target lengths must match exactly.
- `max_chunk` must be zero or at least the copy cluster size.
- `sync=none` jobs do not proactively copy; they rely on CBW write interception until cancellation/completion semantics decide lifecycle.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/backup.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/blkdebug.c -->
# File Research: sources/virtualization/qemu/block/blkdebug.c

This file implements the `blkdebug` block filter/protocol for deterministic error injection, state transitions, breakpoints, request suspension, and block-limit override testing.

Key state:
- `BDRVBlkdebugState` stores fixed limit overrides, config filename, child permission modifiers, current state, per-event rules, active injected-error rules, suspended requests, and a mutex.
- `BlkdebugRule` describes one event/action: inject error, set state, or suspend.
- `BlkdebugSuspendedReq` tracks a yielded coroutine and tag for later resume.

Configuration:
- `inject-error` options support event, state, I/O type mask, errno, sector offset, once/immediately behavior, and delay.
- `set-state` options support event, state, and new state.
- Runtime options include `config`, internal `x-image`, alignment and max-transfer overrides, write-zero/discard alignments and maximums.
- `read_config()` parses both config file and QDict-provided rules, then resets global `QemuOptsList` state.

Open and limits:
- `blkdebug_parse_filename()` accepts `blkdebug:config:image` and maps it to `config` and `x-image`.
- `blkdebug_open()` initializes lock, reads rules, parses child permission modifiers, opens the image child, mirrors supported write/zero flags, validates override limits, and triggers `BLKDBG_NONE`.
- `blkdebug_refresh_limits()` applies configured overrides to `bs->bl`.
- `blkdebug_child_perm()` applies default permissions plus explicit take/unshare permission modifiers.

I/O behavior:
- `rule_check()` scans active injected-error rules for matching offset and I/O type, optionally removes one-shot rules, sleeps for configured delay, optionally yields once, and returns `-errno`.
- Read, write, flush, write-zeroes, discard, and block-status handlers check rules before delegating to the child.
- Handlers assert that block-layer alignment and maximum request guarantees are being honored.

Debug events and suspension:
- `blkdebug_co_debug_event()` processes all rules for an event under lock, updates state, activates injected errors, or suspends requests.
- `suspend_request()` records the current coroutine and removes the suspend rule.
- `blkdebug_debug_breakpoint()`, `blkdebug_debug_resume()`, `blkdebug_debug_remove_breakpoint()`, and `blkdebug_debug_is_suspended()` implement breakpoint management by tag.
- `resume_req_by_tag()` temporarily drops the mutex while entering the suspended coroutine.

Filesystem/block relevance:
- `blkdebug` is a test-oriented block filter that exercises error paths and block-limit handling in upper layers and image drivers.
- It is especially useful for filesystem/block-stack reliability testing because it can inject failures at precise block events and request types.

Potential pitfalls:
- Rule storage is protected by a mutex, but callbacks can enter coroutines while lock is temporarily dropped.
- `remove_rule()` assumes the rule is linked in its event list.
- `blkdebug` is intentionally invasive and should be viewed as a test harness, not a production storage backend.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/blkdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/blkio.c -->
# File Research: sources/virtualization/qemu/block/blkio.c

This file implements QEMU block drivers backed by `libblkio`: `io_uring`, `nvme-io_uring`, `virtio-blk-vfio-pci`, `virtio-blk-vhost-user`, and `virtio-blk-vhost-vdpa`.

Key state:
- `BDRVBlkioState` stores the libblkio instance, queue, completion fd, a poll-side cached completion, locks, bounce-buffer pool/list/queue, memory-region properties, and whether memory regions may pin guest RAM.
- `blkio_lock` protects libblkio objects because libblkio is not thread-safe.
- `bounce_lock` protects bounce-buffer allocation state and must be acquired before `blkio_lock`.

I/O path:
- Completion fd handlers integrate libblkio queue completions into QEMU's AioContext.
- `blkio_completion_fd_poll()` can prefetch one completion into `poll_completion`; `blkio_completion_fd_read()` wakes the owning coroutine for cached and newly fetched completions.
- `blkio_co_preadv()`, `blkio_co_pwritev()`, `blkio_co_flush()`, `blkio_co_pdiscard()`, and `blkio_co_pwrite_zeroes()` submit libblkio requests, defer actual queue kicking through `defer_call()`, yield, and return completion status.
- If libblkio requires registered memory regions and the caller did not provide `BDRV_REQ_REGISTERED_BUF`, reads/writes use a bounce buffer.

Bounce-buffer management:
- The bounce pool is a libblkio memory region and is resized when no buffers are in flight and the current pool is too small.
- Allocations are tracked in address order and use a linear hole search.
- Waiting coroutines use `CoQueue` fairness: first wait joins the back, subsequent waits join the front to avoid losing place.

Memory registration:
- `blkio_mem_region_from_host()` validates alignment and optionally resolves RAMBlock fd/fd offset for drivers requiring fd-backed regions.
- `blkio_register_buf()` maps eligible memory regions unless unnecessary; `blkio_unregister_buf()` unmaps them.
- If a driver may pin memory, `blkio_open()` disables RAM discard via `ram_block_discard_disable(true)` until close.

Open/connect behavior:
- `blkio_io_uring_connect()` maps `filename` to libblkio `path` and sets `direct` when `BDRV_O_NOCACHE` is requested.
- `blkio_nvme_io_uring_connect()` requires `path` and requires direct cache mode.
- `blkio_virtio_blk_connect()` requires `path`, requires direct cache mode, tries fd passing when supported, falls back to path-based open for older/unsupported libblkio behavior, and handles fd cleanup on connect failure.
- `blkio_open()` creates the libblkio driver, sets read-only when needed, connects, queries memory-region properties, starts libblkio, initializes locks/queues, records supported flags, and installs the completion fd handler.

Limits and capabilities:
- `blkio_refresh_limits()` queries request alignment, optimal I/O size, max transfer, buffer alignment, optimal buffer alignment, and max segments from libblkio and validates them.
- Truncate does not grow or resize devices; it only accepts compatible no-op truncation.
- Block status and cache invalidation are noted as missing libblkio APIs.

Filesystem/block relevance:
- This is a high-performance virtual block transport integration layer.
- It bridges QEMU's coroutine/block API to external kernel/userspace backends and virtio transport mechanisms, including registered memory and zoned/zero/discard style constraints via block limits.

Potential pitfalls:
- Correctness depends on strict lock ordering: `bounce_lock` before `blkio_lock`.
- Registered buffers must be aligned to `mem_region_alignment`.
- Memory pinning has system-wide implications for RAM discard/virtio-mem.
- `blkio_close()` destroys `blkio_lock` before detaching AioContext handlers, which is the order implemented here and assumes no concurrent handler execution during close.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/blkio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/blklogwrites.c -->
# File Research: sources/virtualization/qemu/block/blklogwrites.c

This file implements the `blklogwrites` filter, which logs write, write-zeroes, discard, and flush operations to a separate log file using the Linux `dm-log-writes` disk format.

On-disk format:
- Superblock fields: magic, version, number of entries, sector size.
- Entry fields: sector, number of sectors, flags, data length.
- Flags include flush, FUA, discard, and mark, though the driver emits flush/discard and regular/zero write records.

State:
- `BDRVBlkLogWritesState` tracks the log child, sector size/bits, superblock update interval, current log sector, number of entries, a mutex, active superblock update sequence, and a coroutine queue for serializing superblock updates.

Open behavior:
- Opens the main `file` child and a metadata `log` child.
- Supports `log-append`; if appending, it reads and validates an existing superblock or synthesizes one for an empty log.
- `blk_log_writes_find_cur_log_sector()` scans existing entries to find the append position and validates flags.
- Validates log sector size as power-of-two, large enough for superblock and entry, and below `1 << 24`.
- Initializes mutex and superblock update queue.

I/O behavior:
- Reads pass through unchanged.
- Writes, zero writes, flushes, and discards call `blk_log_writes_co_log()`.
- The driver executes the underlying file operation and log write, then returns a log error preferentially if logging failed, otherwise the underlying file result.
- Log records include an entry header padded to log sector size, followed by data for normal writes or zeroed log space for write-zeroes.
- Discards log only the entry because discard data is not present.

Superblock update:
- The superblock is updated on flush records or every configured interval.
- Only one superblock update runs at a time using `super_update_seq` plus `super_update_queue`.
- Older waiting updates can bail out if a newer sequence already superseded them.
- Superblock update writes a full sector then flushes the log file.

Filesystem/block relevance:
- This is a replay/audit-oriented block filter useful for filesystem consistency testing.
- It captures the write stream needed to reproduce storage mutation order, including discard and flush boundaries.

Potential pitfalls:
- Logging is not atomic with the underlying write; failures are reported but the underlying file may already have changed.
- The mutable log position is reserved under mutex before I/O, so failed log writes can leave gaps or unusable log tails depending on failure mode.
- `log-super-update-interval` cannot be zero.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/blklogwrites.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/blkreplay.c -->
# File Research: sources/virtualization/qemu/block/blkreplay.c

This file implements the `blkreplay` filter for deterministic record/replay synchronization of block I/O completions.

Key behavior:
- `blkreplay_open()` opens an `image` child and propagates `BDRV_REQ_WRITE_UNCHANGED` support for write and zero flags.
- Each I/O wrapper obtains a replay request id with `blkreplay_next_id()`, performs the child I/O synchronously in coroutine context, creates a replay block event, yields, and resumes only when the replay-scheduled bottom half fires.
- Supported operations include read, write, write-zeroes, discard, flush, and snapshot goto.
- `block_request_create()` creates a bottom half in the coroutine's AioContext and registers it with `replay_block_event()`.
- `blkreplay_bh_cb()` wakes the coroutine, deletes the bottom half, and frees request state.

Snapshot behavior:
- `blkreplay_snapshot_goto()` obtains the file child under graph read lock, then delegates to `bdrv_snapshot_goto()`.

Filesystem/block relevance:
- This filter is not a storage format; it is determinism infrastructure.
- It makes block I/O completion ordering reproducible across record/replay, which matters for debugging guest filesystems and storage race conditions.

Potential pitfalls:
- The child I/O is performed before the coroutine yields for deterministic completion scheduling.
- The filter has no private instance state.
- Replay correctness relies on integration with the global replay subsystem.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/blkreplay.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/blkverify.c -->
# File Research: sources/virtualization/qemu/block/blkverify.c

This file implements the `blkverify` block protocol/filter for comparing a test image against a raw reference image.

State and open:
- `BDRVBlkverifyState` stores a `test_file` child; the raw/reference child is the standard `bs->file`.
- `blkverify_parse_filename()` accepts `blkverify:raw:image` and maps paths into internal `x-raw` and `x-image`.
- `blkverify_open()` opens the raw file child and the test child, then advertises `BDRV_REQ_WRITE_UNCHANGED` for write and zero flags.

Verification flow:
- `blkverify_co_prwv()` creates two coroutines: one I/O to the test child and one to the raw child.
- It waits until both complete, compares return codes, and aborts the entire QEMU process on mismatch via `blkverify_err()`.
- `blkverify_co_preadv()` allocates an aligned buffer for the raw read, clones the caller I/O vector, performs both reads, then compares returned data using `qemu_iovec_compare()`.
- `blkverify_co_pwritev()` writes the same buffer to both images.
- Flush only flushes the test file because the raw file is considered nonessential for flush verification.

Graph behavior:
- `blkverify_recurse_can_replace()` allows replacement recursion through either child because mismatch-free operation implies equivalence.
- `blkverify_refresh_filename()` synthesizes `blkverify:raw:test` only when both children have exact filenames.
- `blkverify_dirname()` always fails because two children may have different base directories.

Filesystem/block relevance:
- This is a correctness-testing filter for image drivers.
- It is useful when validating that a format driver returns the same data and error behavior as a raw reference.

Potential pitfalls:
- Any mismatch calls `exit(1)`, so this is a test/debug tool rather than production infrastructure.
- Read comparison clears `BDRV_REQ_REGISTERED_BUF` for the raw side because the cloned buffer is not necessarily registered.
- It does not implement discard/write-zeroes verification wrappers in this file, only read/write/flush.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/blkverify.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/block-backend.c -->
# File Research: sources/virtualization/qemu/block/block-backend.c

This file implements QEMU's `BlockBackend`, the object that connects device models, monitor-owned block devices, jobs, throttling, permissions, AioContexts, media events, and the block graph's root `BlockDriverState`.

Core state:
- `BlockBackend` stores name/refcount/root child/AioContext, legacy drive info, public throttle member, attached device and callbacks, cached root state, write-cache setting, accounting stats, error policies, permissions, request queuing/drain state, VM-state handler, and in-flight AIO count.
- All BlockBackends are tracked in `block_backends`; monitor-visible ones are tracked separately in `monitor_block_backends`.
- The root BDS is attached through `child_root`, a `BdrvChildClass` with callbacks for media changes, resize, drain, activate/inactivate, attach/detach, AioContext migration, and parent naming.

Lifecycle:
- `blk_new()` creates a backend, initializes accounting, locks, queues, notifier lists, defaults error policy, and adds it to the global list.
- `blk_new_with_bs()` and `blk_new_open()` create backends around existing or newly opened BDS trees.
- `blk_ref()`/`blk_unref()` manage lifetime; final unref drains before deletion.
- `blk_delete()` removes the backend from global state, disables throttling, removes root BDS, removes VM state handler, checks notifier queues, cleans accounting, and frees memory.
- `monitor_add_blk()` and `monitor_remove_blk()` manage monitor-visible names and enforce id validity/name conflicts.

Root BDS management:
- `blk_insert_bs()` attaches a BDS as the root child with current or inactive permissions, notifies insert listeners, and moves throttle group AioContext.
- `blk_remove_bs()` notifies remove listeners, drains, saves root state, detaches throttling to main loop, clears `blk->root`, and unreferences the child under graph write lock.
- `blk_replace_bs()` delegates to `bdrv_replace_child_bs()`.
- `blk_update_root_state()` caches open flags and detect-zeroes for later reinsertion.

Permissions and migration:
- `blk_set_perm_locked()` applies permissions to the root child unless disabled.
- Incoming migration can temporarily disable permissions so storage migration/block jobs can still write.
- `blk_root_activate()` re-enables permissions after migration, temporarily shares all permissions, and defers final tightening if still in `RUN_STATE_INMIGRATE`.
- `blk_root_inactivate()` drops permissions for eligible guest devices/job backends.

Device model integration:
- `blk_attach_dev()` and `blk_detach_dev()` bind/unbind a `DeviceState`.
- `blk_set_dev_ops()` installs callbacks for media change, tray status, medium lock, resize, and drain.
- Media helpers emit `DEVICE_TRAY_MOVED` and call device callbacks.
- I/O status helpers track `OK`, `NOSPACE`, or `FAILED` when stop-on-error policy enables iostatus.

I/O data path:
- Coroutine APIs include read, write, write-zeroes, compressed write, discard, flush, ioctl, block status, allocation query, truncate, copy-range, zoned operations, and getlength/geometry.
- Each request generally increments `blk->in_flight`, waits while drained unless `BDRV_REQ_NO_QUEUE`, validates medium/offset/length through `blk_check_byte_request()`, applies throttling, delegates to the root child/BDS, then decrements in-flight.
- Write operations add `BDRV_REQ_FUA` when write cache is disabled.
- Asynchronous APIs wrap coroutine operations in `BlkAioEmAIOCB`, handle immediate coroutine completion with replay bottom halves, and keep in-flight accounting correct.
- `blk_abort_aio_request()` creates an async completion for immediate errors such as no medium.

Drain and quiescing:
- `blk_root_drained_begin()` increments the quiesce counter, calls device `drained_begin`, and disables/restarts throttling.
- `blk_wait_while_drained()` queues coroutines while drained, carefully dropping in-flight only after taking `queued_requests_lock`.
- `blk_root_drained_poll()` reports busy if device callbacks or in-flight requests remain.
- `blk_root_drained_end()` re-enables queued requests, restoring in-flight for each resumed coroutine.
- `blk_drain()` and `blk_drain_all()` wait for BDS drain and backend-only in-flight completions.

AioContext handling:
- `blk_get_aio_context()` returns the atomic backend context.
- `blk_set_aio_context()` handles empty backends directly or asks the BDS graph to move context with temporary permission to change.
- `blk_root_change_aio_ctx()` rejects active/attached backends unless explicitly allowed, and commits context changes through a transaction.
- AioContext notifier add/remove functions mirror notifications onto the current root BDS.

Error policy:
- `blk_get_error_action()` maps read/write `BlockdevOnError` policy and errno into report/stop/ignore.
- `blk_error_action()` sets iostatus, orders `BLOCK_IO_ERROR` before VM stop, and requests `RUN_STATE_IO_ERROR` when policy is stop.

Limits and memory:
- Helpers expose request alignment, write-zero alignment, max hardware transfer, max transfer, max iov, and block-aligned allocation.
- `blk_register_buf()`/`blk_unregister_buf()` forward registered-buffer lifecycle to the root BDS when present.
- `blk_root()` exposes the root child.

Filesystem/block relevance:
- This is one of QEMU's central block abstractions: guest devices and management code use `BlockBackend`, while image/protocol drivers live below it as BDS nodes.
- It is responsible for translating guest-facing block operations into graph operations with permissions, drains, throttling, accounting, and media semantics.

Potential pitfalls:
- Many APIs require the right execution domain (`GLOBAL_STATE_CODE`, `IO_CODE`, graph read/write locks).
- Drain accounting is subtle because some in-flight completions can exist without a root BDS.
- AioContext changes are constrained for active backends; callers must opt in carefully.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/block-backend.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/block-copy.c -->
# File Research: sources/virtualization/qemu/block/block-copy.c

This file implements the reusable `block-copy` engine used by backup/copy-before-write workflows to copy dirty clusters from a source child to a target child with concurrency, rate limiting, bitmap tracking, copy-range optimization, zero detection, and cancellation.

Core state:
- `BlockCopyState` stores source/target children, cluster size, max transfer, total length, write flags, mutex, in-flight bytes, current copy method, discard-source flag, active request list, active async calls, skip-unallocated flag, dirty bitmap, progress meter, shared memory limit, and rate limiter.
- `BlockCopyCallState` represents one sync or async copy call over an offset/range, with worker limits, callback, coroutine, cancellation/finished flags, sleep state, and final error information.
- `BlockCopyTask` represents a dirty chunk being copied, including the chosen method and conflict-tracked `BlockReq`.

Initialization:
- `block_copy_state_new()` validates minimum cluster size, determines effective cluster size from the target image, creates and disables an internal dirty bitmap, merges an input bitmap or marks the whole image dirty, detects image-fleecing topology, initializes shared memory/rate-limit/locks/lists, and chooses initial copy options.
- `block_copy_calculate_cluster_size()` uses target `BlockDriverInfo` and backing-chain presence to avoid unsafe cluster-size assumptions.
- `block_copy_set_copy_opts()` chooses between buffered read/write, cluster-sized buffered copy, or copy-range modes depending on compression, max transfer, and `use_copy_range`.

Task creation and tracking:
- `block_copy_task_create()` finds the next dirty area, aligns it to cluster size, clears the dirty bits, adds bytes to in-flight accounting, and registers a request-list entry.
- `block_copy_task_shrink()` returns the tail of an oversized task to the dirty bitmap and shrinks the request.
- `block_copy_task_end()` subtracts in-flight bytes, restores dirty bits on failure, updates progress remaining, and removes the request entry.
- Request-list conflict handling lets parallel copy callers cooperate and wait for intersecting tasks.

Copy methods:
- `COPY_WRITE_ZEROES` writes zeroes directly to the target.
- `COPY_RANGE_SMALL`/`COPY_RANGE_FULL` try `bdrv_co_copy_range()` and promote chunk size after success.
- Copy-range failure falls back to buffered read/write and changes later tasks to buffered copying.
- Buffered mode allocates a block-aligned bounce buffer, reads source, writes target, and records whether errors were read-side or write-side.
- Successful tasks optionally discard the copied source range when `discard_source` is enabled.

Dirty-cluster loop:
- `block_copy_dirty_clusters()` finds dirty tasks, consults block status, skips unallocated regions when requested, converts zero ranges to write-zeroes, applies rate limiting, reserves shared memory, and runs tasks directly or through an `AioTaskPool`.
- The task pool is created only when there is more work, and uses `max_workers`.
- A failed task pool returns the first negative status.

Call lifecycle:
- `block_copy_common()` inserts the call into `s->calls`, repeatedly copies dirty clusters, waits for intersecting requests if no immediate dirty bits remain, and retries when progress or wait results imply new dirty bits may exist.
- It marks the call finished atomically, invokes the callback, and removes it from the active calls list.
- `block_copy()` provides a synchronous coroutine API with timeout support.
- `block_copy_async()` starts a copy coroutine and returns a `BlockCopyCallState`.
- Call helpers expose finished/succeeded/failed/cancelled/status state and cancellation.

Control APIs:
- `block_copy_reset()` clears dirty bits and updates remaining progress.
- `block_copy_reset_unallocated()` queries source allocation and clears dirty bits for unallocated clusters.
- `block_copy_set_skip_unallocated()` toggles sync=top unallocated skipping.
- `block_copy_set_speed()` updates the rate limiter; callers must kick active call state separately.
- `block_copy_dirty_bitmap()` and `block_copy_cluster_size()` expose internal state to users such as backup jobs.

Filesystem/block relevance:
- This is the core data-copy mechanism behind incremental/full backups and copy-before-write preservation.
- It manages bitmap consistency, sparse/unallocated optimization, zero handling, and safe parallel copying across QEMU block graph children.

Potential pitfalls:
- Source and target are expected to remain in the same AioContext.
- Cancellation and finish are explicitly racy; callers may cancel an already finished call.
- `block_copy_set_speed()` does not itself wake every active call because doing so safely requires coroutine context.
- Failure restores dirty bits for the failed task so future retries can recopy the region.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/block-copy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/block-gen.h -->
# File Research: sources/virtualization/qemu/block/block-gen.h

This small header defines the shared polling wrapper used by autogenerated block coroutine wrappers in `block/block-gen.c`.

Key contents:
- `BdrvPollCo` packages an `AioContext`, an `in_progress` flag, and the target coroutine pointer.
- `bdrv_poll_co()` asserts the caller is not already in a coroutine, enters the coroutine in the stored AioContext, and waits with `AIO_WAIT_WHILE()` until `in_progress` becomes false.

Filesystem/block relevance:
- This supports QEMU's sync-to-coroutine wrapper generation for block APIs.
- It is glue between non-coroutine callers and coroutine-native block implementations.

Potential pitfalls:
- Must not be called from coroutine context.
- Correctness depends on the launched coroutine clearing `in_progress`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/block-gen.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/block-ram-registrar.c -->
# File Research: sources/virtualization/qemu/block/block-ram-registrar.c

This file implements `BlockRAMRegistrar`, a helper that registers guest RAM blocks as block backend buffers when RAM blocks are added and unregisters them when removed.

Key behavior:
- `blk_ram_registrar_init()` stores the target `BlockBackend`, initializes a `RAMBlockNotifier`, sets `ok = true`, and registers the notifier.
- `ram_block_added()` calls `blk_register_buf()` for the new RAM block using `max_size`. On failure, it reports the error, removes the notifier, and marks the registrar failed so it will not retry.
- `ram_block_removed()` calls `blk_unregister_buf()` with the same host and max size.
- `blk_ram_registrar_destroy()` removes the notifier only if still active/ok.

Design note:
- Resize notifications are not needed because registration uses `max_size`, which does not change across resize.

Filesystem/block relevance:
- This supports block drivers that benefit from or require pre-registered guest memory, such as libblkio/virtio paths with registered buffers.
- It bridges QEMU RAM lifecycle events to block-backend buffer registration.

Potential pitfalls:
- A single registration failure permanently disables the registrar.
- Removal uses `max_size`, so register/unregister region derivation must remain consistent in lower block drivers.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/block-ram-registrar.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/bochs.c -->
# File Research: sources/virtualization/qemu/block/bochs.c

This file implements read-only support for Bochs "growing" Redolog virtual disk images.

On-disk structures:
- `bochs_header` contains magic, type, subtype, version, header/catalog/bitmap/extent sizes, and disk-size fields for v1 and v2 layouts.
- Supported images must have magic `"Bochs Virtual HD Image"`, type `"Redolog"`, subtype `"Growing"`, and version `0x00010000` or `0x00020000`.

Open/probe:
- `bochs_probe()` returns strong confidence for matching headers.
- `bochs_open()` forces auto read-only because writes are unsupported, opens the file child, reads and validates the header, sets `total_sectors`, validates catalog size, allocates and loads the catalog bitmap, computes data offsets and extent/bitmap block counts, validates extent size, checks catalog coverage, and initializes a coroutine mutex.

Read mapping:
- `seek_to_sector()` maps a virtual sector to a file offset:
  - Calculates extent index and sector offset within the extent.
  - Treats catalog entry `0xffffffff` as unallocated.
  - Reads the extent bitmap byte and checks whether the sector is allocated.
  - Returns zero for unallocated sectors or the physical data offset for allocated sectors.
- `bochs_co_preadv()` enforces sector alignment, serializes reads with `s->lock`, iterates one sector at a time, reads allocated sectors from the file, and zero-fills unallocated sectors.

Limits and driver registration:
- `bochs_refresh_limits()` sets request alignment to 512 bytes.
- The driver is registered as a block format named `bochs`.

Filesystem/block relevance:
- This is a legacy image-format reader that exposes sparse Bochs growing disks as QEMU block devices.
- Its allocation bitmap handling is analogous to filesystem block mapping: unallocated virtual sectors read as zero.

Potential pitfalls:
- It is read-only.
- Reads are sector-by-sector, which is simple but potentially slow for large sequential reads.
- Catalog size is capped at one million entries to avoid unbounded allocation.
- Extent size must be a power of two between 512 bytes and 8 MiB.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/bochs.c -->