# Group Research: Linux Block Multiqueue Scheduling, Tags, Queue Limits, PM, QoS, and Stats

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-sched.c -->
# File Research: sources/os/linux/linux/block/blk-mq-sched.c

Purpose: Implements the blk-mq I/O scheduler bridge: dispatching requests from elevator queues or per-CPU software queues into hardware queues, scheduler tag allocation, scheduler initialization/teardown, and scheduler debugfs registration.

Key responsibilities:
- Tracks scheduler restart state with `BLK_MQ_S_SCHED_RESTART`, using memory barriers to avoid missed dispatch after requests are added to `hctx->dispatch`.
- Dispatches scheduler-owned requests through `blk_mq_do_dispatch_sched()` and non-elevator software-queue requests through `blk_mq_do_dispatch_ctx()`.
- Handles residual dispatch-list requests before pulling new requests from the scheduler to preserve merge/sort opportunities.
- Supports schedulers that can dispatch requests mapped to multiple hardware contexts by sorting and batching by `rq->mq_hctx`.
- Implements default software-queue bio merge fallback when no elevator `bio_merge` op exists.
- Allocates and frees scheduler request tags through `elevator_tags`, including shared-tag mode.
- Coordinates batch scheduler resource allocation during hardware queue count changes.
- Initializes and exits scheduler instances through elevator ops `init_sched`, `init_hctx`, `exit_hctx`, and `exit_sched`.

Concurrency and lifecycle notes:
- Uses `list_empty_careful()`, `hctx->lock`, scheduler restart bits, and explicit `smp_mb()` pairing with core dispatch.
- Batch scheduler resource code assumes `set->update_nr_hwq_lock` write ownership and documents safe unlocked elevator access under that lock.
- Scheduler tag teardown clears `hctx->sched_tags` and `q->sched_shared_tags` before resources are freed.

Dependencies:
- Internal blk-mq core helpers from `blk-mq.h`.
- Elevator interfaces from `elevator.h`.
- Debugfs hooks from `blk-mq-debugfs.h`.
- Writeback throttling header `blk-wbt.h`.

Filesystem/block relevance:
- This is the policy insertion point between filesystem bios and hardware dispatch when an I/O scheduler is configured.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-sched.h -->
# File Research: sources/os/linux/linux/block/blk-mq-sched.h

Purpose: Internal header for blk-mq scheduler integration.

Key contents:
- Declares scheduler merge, dispatch, restart, init, exit, and resource allocation APIs.
- Defines `MAX_SCHED_RQ` as the upper scheduler request tag allocation size.
- Provides inline wrappers for scheduler-specific allocation/free callbacks.
- Provides inline scheduler hooks for completion, requeue, allow-merge, and work detection.
- Provides `blk_mq_sched_restart()` restart-bit check and dispatch restart path.
- Provides helpers for setting minimum shallow depth across scheduler tag bitmaps.
- Provides `blk_mq_is_sync_read()` for scheduler policy decisions.

Concurrency and lifecycle notes:
- Inline hooks rely on `RQF_USE_SCHED` to decide whether elevator callbacks are valid.
- `blk_mq_set_min_shallow_depth()` assumes `hctx->sched_tags` is initialized for all hardware queues.

Dependencies:
- Includes `elevator.h` and `blk-mq.h`.

Filesystem/block relevance:
- Defines the narrow internal contract used by blk-mq core and elevator implementations to cooperate on queueing and dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-sched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-sysfs.c -->
# File Research: sources/os/linux/linux/block/blk-mq-sysfs.c

Purpose: Owns sysfs exposure and kobject lifetime for blk-mq queue topology under each disk’s `mq/` directory.

Key responsibilities:
- Creates `mq/`, hardware context kobjects, and per-CPU context child kobjects.
- Exposes hardware context attributes: `nr_tags`, `nr_reserved_tags`, and `cpu_list`.
- Initializes and releases `blk_mq_ctxs`, per-CPU `blk_mq_ctx` kobjects, and `blk_mq_hw_ctx` kobjects.
- Registers and unregisters all hardware contexts when a disk queue is registered/unregistered.
- Supports unregister/register of only hctx nodes during hardware queue remapping.

Concurrency and lifecycle notes:
- `blk_mq_hw_sysfs_show()` takes `q->elevator_lock` while reading hctx scheduler-sensitive state.
- Full registration is protected by `q->tag_set->tag_list_lock`.
- Release functions free per-CPU contexts, hctx cpumasks, ctx maps, and hctx arrays at kobject final release.

Dependencies:
- Internal blk-mq structures from `blk-mq.h`.
- Generic kernel kobject/sysfs infrastructure.

Filesystem/block relevance:
- Provides observability of blk-mq topology and tag capacities used by block devices backing filesystems.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-tag.c -->
# File Research: sources/os/linux/linux/block/blk-mq-tag.c

Purpose: Implements blk-mq driver/scheduler tag allocation, freeing, wakeups, active-queue fairness, request iteration, and tag-map allocation.

Key responsibilities:
- Uses `sbitmap_queue` for normal and reserved tag pools.
- Tracks active queues for shared-tag fairness and recalculates wake batches.
- Allocates single tags, batched tags, and reserved tags.
- Sleeps on tag wait queues unless allocation is `BLK_MQ_REQ_NOWAIT`.
- Revalidates CPU-to-hctx mapping after sleeping because CPU hotplug may remap the allocation target.
- Frees tags singly or in batches.
- Iterates busy requests safely for queue/tagset timeout, inflight, and teardown logic.
- Allocates and frees `blk_mq_tags`, including delayed freeing of request pages through SRCU callbacks.
- Resizes shared hardware and scheduler tag bitmaps.
- Builds queue-wide unique tags from hctx index plus per-hctx tag.

Concurrency and lifecycle notes:
- Request iteration increments request refs unless iterating static request arrays.
- `tags_srcu` protects tag maps and delayed freeing of request memory.
- `__blk_mq_tag_busy()` / `__blk_mq_tag_idle()` maintain shared-user accounting under `tags->lock`.
- Allocation handles inactive hctx by releasing the tag and returning `BLK_MQ_NO_TAG`.

Dependencies:
- Internal blk-mq helpers and scheduler tag helpers.
- Kernel `sbitmap_queue`, RCU/SRCU, kmemleak, and page allocation.

Filesystem/block relevance:
- Tags are the scarce per-device queue slots that gate request submission from filesystem bios to drivers.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-tag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq.c -->
# File Research: sources/os/linux/linux/block/blk-mq.c

Purpose: Core Linux block multiqueue implementation. It covers request allocation, bio submission, dispatch, completion, queue freeze/quiesce, CPU hotplug, hctx lifecycle, tag-set allocation, scheduler switching during topology updates, and polling.

Key responsibilities:
- Freezes/unfreezes queues through `q_usage_counter`, `mq_freeze_depth`, and lockdep ownership tracking.
- Quiesces queues/tagsets to stop dispatch while allowing completions.
- Allocates requests from hardware or scheduler tags, including plug-cached batched allocation.
- Converts bios to requests, handles splitting to queue limits, integrity preparation, blk-crypto keyslot handling, rq-qos throttling/tracking, zone write plugging, and flush insertion.
- Attempts plug and scheduler merges before allocating new requests.
- Dispatches directly when budgets and driver tags are available, otherwise inserts into elevator queues, per-CPU software queues, or `hctx->dispatch`.
- Handles dispatch failures from drivers (`BLK_STS_RESOURCE`, `BLK_STS_DEV_RESOURCE`, hard errors) and schedules restarts/delays.
- Tracks request start, timeout, requeue, completion, batched completion, stats, partition accounting, and rq-qos callbacks.
- Routes completions locally, by softirq, or by IPI depending on queue flags and CPU/cache topology.
- Manages per-CPU software queues, hardware context allocation/reuse, flush queues, CPU hotplug callbacks, and software-to-hardware queue mapping.
- Allocates/frees tag sets and request maps, including memory-pressure depth reduction.
- Updates hardware queue counts by temporarily switching elevators to `none`, reallocating hctxs/tags, remapping queues, then restoring elevators.
- Implements sync and async passthrough request execution, cloned request submission for stacking drivers, request cloning helpers, and polled I/O.

Concurrency and lifecycle notes:
- Dispatch uses RCU or SRCU depending on `BLK_MQ_F_BLOCKING`.
- Several memory barriers pair restart/stopped/tag-wait state with dispatch-list insertion to prevent missed queue runs.
- `q_usage_counter` protects queue lifetime during submission, timeout walking, polling, and hctx remapping.
- CPU hotplug marks hctx inactive before draining requests and moves dead-CPU software queue entries to hctx dispatch.
- Request memory is page-backed and freed only after tag SRCU grace periods.
- Queue destruction sets dying state, drains, freezes, syncs work, cancels delayed work, and exits mq resources.

Dependencies:
- Internal block headers: `blk.h`, `blk-mq.h`, `blk-pm.h`, `blk-stat.h`, `blk-mq-sched.h`, `blk-rq-qos.h`.
- Integrates with blk-integrity, blk-crypto, blk-cgroup timing, partition stats, flush state machine, zone write plugging, debugfs/sysfs, CPU hotplug, workqueues, softirqs, and scheduler/elevator ops.

Filesystem/block relevance:
- This is the central path from filesystem bio submission to driver `queue_rq`, and the central completion path back to bios and filesystem I/O waiters.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq.h -->
# File Research: sources/os/linux/linux/block/blk-mq.h

Purpose: Internal blk-mq header defining software queue state, allocation metadata, tag APIs, dispatch helpers, queue mapping helpers, and fast inline utilities.

Key contents:
- Defines `blk_mq_ctxs` and `blk_mq_ctx`, the per-CPU software queue state.
- Defines tag constants and internal insertion flags.
- Declares core blk-mq submission, polling, dispatch, sysfs, tag, request-map, and scheduler resource APIs.
- Provides queue mapping helpers for default, read, and poll hardware context types.
- Defines `blk_mq_alloc_data`, used for request/tag allocation.
- Provides tag helpers for reserved tags, shared tags, active request accounting, dispatch budgets, and driver tag acquisition/release.
- Provides `hctx_may_queue()` fairness logic for shared tags.
- Provides dispatch critical-section macro selecting RCU vs SRCU.
- Provides `blk_mq_can_poll()` based on queue limits and poll queue map.

Concurrency and lifecycle notes:
- `blk_mq_hctx_stopped()` includes a memory barrier paired with restart/start paths.
- Active request counters are per-hctx or queue-wide depending on shared-tag mode.
- Shared-tag fairness is enforced before normal driver tag allocation.

Dependencies:
- Public `linux/blk-mq.h`.
- Internal `blk-stat.h`.

Filesystem/block relevance:
- Defines the internal data structures that connect CPU-local bio submission to hardware queue dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-pm.c -->
# File Research: sources/os/linux/linux/block/blk-pm.c

Purpose: Implements request-based runtime power management support for block queues.

Key responsibilities:
- Initializes queue runtime PM state and enables autosuspend with an initial impossible delay.
- Pre-suspend path marks the queue `RPM_SUSPENDING`, sets PM-only mode, freezes the queue, switches usage ref to atomic mode, and permits suspend only if usage count is zero.
- On failed pre-suspend, restores `RPM_ACTIVE`, marks the device last busy, and clears PM-only mode.
- Post-suspend records `RPM_SUSPENDED` or returns to active on error.
- Pre-resume marks `RPM_RESUMING`.
- Post-resume marks active, records last busy, requests autosuspend, and clears PM-only if needed.

Concurrency and lifecycle notes:
- Uses `q->queue_lock` around `rpm_status` transitions.
- Uses queue freeze and `percpu_ref_switch_to_atomic_sync()` so later queue-enter callers observe PM-only state.
- Designed for request-based drivers, not bio-direct drivers.

Dependencies:
- Public runtime PM API and internal blk-mq freeze helpers.

Filesystem/block relevance:
- Prevents normal filesystem I/O from entering a queue while the underlying block device is runtime-suspended or suspending.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-pm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-pm.h -->
# File Research: sources/os/linux/linux/block/blk-pm.h

Purpose: Internal inline helpers for blk runtime PM gating in queue entry and request completion paths.

Key contents:
- `blk_pm_resume_queue()` allows queue entry when no PM gating is active, allows PM requests during non-suspended states, otherwise requests device resume and denies entry.
- `blk_pm_mark_last_busy()` marks runtime PM last-busy for non-PM requests.
- Provides no-op stubs when `CONFIG_PM` is disabled.

Concurrency and lifecycle notes:
- Relies on queue PM-only state and `rpm_status` maintained by `blk-pm.c`.
- Separates PM requests (`RQF_PM`) from normal requests to avoid blocking resume-related I/O.

Dependencies:
- Runtime PM API.

Filesystem/block relevance:
- Small but important hook that keeps normal filesystem I/O from racing runtime suspend/resume.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-pm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-rq-qos.c -->
# File Research: sources/os/linux/linux/block/blk-rq-qos.c

Purpose: Implements the request-queue QoS framework used by writeback throttling, latency control, and cost-based controllers.

Key responsibilities:
- Provides callback-chain dispatch for cleanup, done, issue, requeue, throttle, track, merge, done_bio, and queue-depth-changed events.
- Provides atomic inflight accounting helper `rq_wait_inc_below()`.
- Implements scalable depth adjustment through `rq_depth_calc_max_depth()`, `rq_depth_scale_up()`, and `rq_depth_scale_down()`.
- Implements `rq_qos_wait()` for sleeping until inflight budget is available.
- Adds/removes QoS modules under `q->rq_qos_mutex` with queue freeze protection.
- Exits all QoS modules and clears `QUEUE_FLAG_QOS_ENABLED`.

Concurrency and lifecycle notes:
- Wait wakeup path deliberately acquires budget in the wake function and removes wait entries carefully to avoid use-after-free.
- `rq_qos_add()` and `rq_qos_del()` freeze the blk-mq queue because no I/O may be in flight while changing the chain.
- Callback traversal follows the singly linked `q->rq_qos` chain.

Dependencies:
- `blk-rq-qos.h`.
- blk-mq freeze helpers and queue flags.

Filesystem/block relevance:
- Provides throttling and latency feedback hooks that can shape filesystem writeback and application I/O behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-rq-qos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-rq-qos.h -->
# File Research: sources/os/linux/linux/block/blk-rq-qos.h

Purpose: Header defining request QoS IDs, structures, operations, and inline invocation helpers.

Key contents:
- Defines QoS IDs: writeback throttling, latency, and cost.
- Defines `rq_wait`, `rq_qos`, `rq_qos_ops`, and `rq_depth`.
- Provides lookup helpers `rq_qos_id()`, `wbt_rq_qos()`, and `iolat_rq_qos()`.
- Declares QoS add/delete, wait, depth scaling, and callback-chain functions.
- Provides inline fast-path guards checking `QUEUE_FLAG_QOS_ENABLED` and `q->rq_qos`.
- Marks bios with `BIO_QOS_THROTTLED` and `BIO_QOS_MERGED` so bio completion can notify QoS modules.

Concurrency and lifecycle notes:
- `rq_qos_done_bio()` defensively rechecks queue QoS state because stacked devices may propagate BIO_QOS flags across queues where the top queue has no QoS module.
- Inline request-done skips passthrough requests.

Dependencies:
- Public block, bio, atomic, waitqueue headers.
- Debugfs attribute declarations.

Filesystem/block relevance:
- Defines the extension contract for block-layer QoS controllers affecting filesystem I/O latency and throughput.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-rq-qos.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-settings.c -->
# File Research: sources/os/linux/linux/block/blk-settings.c

Purpose: Validates, initializes, commits, and stacks block queue limits and related queue properties.

Key responsibilities:
- Sets request timeout through `blk_queue_rq_timeout()`.
- Initializes stacking-device limits with conservative inherit/maximum values.
- Applies queue limits to backing device readahead and I/O page settings.
- Validates zoned-device limits, integrity metadata/protection information, atomic write constraints, discard, segment, DMA, and block-size constraints.
- Calculates effective `max_sectors`, discard limits, write-zeroes limits, zone append limits, and atomic-write limits.
- Commits queue limit updates under `q->limits_lock`, optionally freezing the queue.
- Stacks bottom-device limits into top-device limits for MD/DM-like stacking drivers.
- Stacks integrity profiles only when compatible.
- Updates queue depth and notifies rq-qos modules.
- Computes partition-aware alignment and discard alignment.

Concurrency and lifecycle notes:
- Limit commits require `q->limits_lock`; frozen variant freezes blk-mq around the update.
- Inline encryption and integrity are rejected together when unsupported.
- Stacking code tracks misalignment through `BLK_FLAG_MISALIGNED` and returns warning status while still producing safe limits.

Dependencies:
- Core block headers, blk-integrity, T10 PI, CRC64 PI, rq-qos, writeback throttling.
- Math helpers for gcd/lcm and power-of-two constraints.

Filesystem/block relevance:
- Queue limits determine bio splitting, alignment validity, discard behavior, integrity handling, zoned write sizing, and maximum I/O sizes visible to filesystems and stacking drivers.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-settings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-stat.c -->
# File Research: sources/os/linux/linux/block/blk-stat.c

Purpose: Implements per-queue request latency/stat callbacks used by block throttling and monitoring features.

Key responsibilities:
- Defines `blk_queue_stats`, holding callback list, lock, and accounting reference count.
- Initializes, sums, and updates `blk_rq_stat` min/max/mean/sample data.
- Records request latency samples in per-CPU per-bucket stats on completion.
- Aggregates per-CPU stats on timer expiration and invokes callback timer function.
- Allocates, registers, removes, and RCU-frees stat callbacks.
- Enables/disables accounting and maintains `QUEUE_FLAG_STATS`.
- Allocates and frees queue stats containers.

Concurrency and lifecycle notes:
- Completion sampling walks callbacks under RCU and uses `get_cpu()` for per-CPU stat access.
- Callback registration/removal uses `q->stats->lock` plus RCU list operations.
- Callback freeing is deferred with `call_rcu()`.
- Timer is synchronously deleted during callback removal.

Dependencies:
- `blk-stat.h`, `blk-mq.h`, and core block queue flags.

Filesystem/block relevance:
- Supplies latency samples consumed by block-layer policy mechanisms that influence filesystem I/O scheduling and throttling.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-stat.c -->