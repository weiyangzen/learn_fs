# Group Research: group_686_linux_sources_os_linux_linux_block_Kconfig_sources_os_linux_linux_bl_e7c3ec1ab6ba

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`, block-layer files listed in the work item. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/Kconfig -->
# File Research: sources/os/linux/linux/block/Kconfig

This Kconfig file defines the core Linux block-layer configuration surface. `menuconfig BLOCK` enables the block layer, selects `FS_IOMAP` and `SBITMAP`, and gates all block-layer features in this file. Disabling it removes block device usability and disables storage stacks that rely on block-layer definitions.

Key options:
- `BLOCK_LEGACY_AUTOLOAD`: deprecated legacy module/device autoloading through device-node access.
- `BLK_DEV_INTEGRITY`: enables block data-integrity hooks and selects `CRC_T10DIF` and `CRC64`.
- `BLK_DEV_WRITE_MOUNTED`: controls whether mounted block devices may be written directly, with boot override `bdev_allow_write_mounted=`.
- `BLK_DEV_ZONED`: enables ZAC/ZBC/ZNS zoned block device support.
- `BLK_DEV_THROTTLING`, `BLK_CGROUP_IOLATENCY`, `BLK_CGROUP_IOCOST`, `BLK_CGROUP_IOPRIO`, `BLK_CGROUP_FC_APPID`: cgroup-based I/O policy and accounting features.
- `BLK_WBT` and `BLK_WBT_MQ`: writeback throttling and default enablement for request-based devices.
- `BLK_DEBUG_FS`: debugfs block-layer state.
- `BLK_SED_OPAL`: Opal self-encrypting drive support.
- `BLK_INLINE_ENCRYPTION` and fallback: blk-crypto and kernel crypto fallback.
- `BLK_PM`, `BLOCK_HOLDER_DEPRECATED`, `BLK_MQ_STACKING`: internal support switches.

It also includes `block/partitions/Kconfig` and `block/Kconfig.iosched`, so partition support and I/O scheduler choices are configured below this block-layer gate.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/Makefile -->
# File Research: sources/os/linux/linux/block/Makefile

This Makefile assembles the Linux block-layer core and conditional subfeatures.

Always-built objects include core block-device lifetime and I/O infrastructure: `bdev.o`, `fops.o`, `bio.o`, `elevator.o`, `blk-core.o`, `blk-sysfs.o`, flush/settings/ioc/map/merge/timeout/lib/mq/tag/dma/stat/sysfs/cpumap/sched support, `ioctl.o`, `genhd.o`, `ioprio.o`, `badblocks.o`, `partitions/`, `blk-rq-qos.o`, `disk-events.o`, `blk-ia-ranges.o`, and `early-lookup.o`.

Conditional build links:
- BSG: `bsg.o`, `bsg-lib.o`.
- blk-cgroup controllers: `blk-cgroup.o`, `blk-cgroup-rwstat.o`, `blk-cgroup-fc-appid.o`, `blk-throttle.o`, `blk-ioprio.o`, `blk-iolatency.o`, `blk-iocost.o`.
- schedulers: `mq-deadline.o`, `kyber-iosched.o`, and composite `bfq.o` built from `bfq-iosched.o bfq-wf2q.o bfq-cgroup.o`.
- integrity: `bio-integrity.o`, `blk-integrity.o`, `t10-pi.o`, `bio-integrity-auto.o`, `bio-integrity-fs.o`.
- zoned, writeback throttling, debugfs, Opal SED, power management, blk-crypto, crypto fallback, and deprecated holder support.

This file establishes that `badblocks.c` and `bdev.c` are core block-layer code, while BFQ and bio-integrity helpers are feature-gated.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/badblocks.c -->
# File Research: sources/os/linux/linux/block/badblocks.c

`badblocks.c` implements generic bad-sector range tracking for block devices. It is based on MD badblocks code and stores bad ranges in a compact, sorted table of 64-bit entries: offset, length, and acknowledged state.

Core model:
- Ranges are tracked in sectors, optionally shifted to represent larger units.
- Entries can be acknowledged or unacknowledged.
- `MAX_BADBLOCKS` limits table capacity; each entry length is capped by `BB_MAX_LEN`.
- A seqlock protects readers and writers; readers retry on concurrent writes.
- The table is kept ordered and opportunistically merged to conserve entries.

Set path:
- `_badblocks_set()` handles all range insertion logic under `write_seqlock_irqsave`.
- It rounds start/end according to `bb->shift`, rejects disabled or zero-length input, and processes large ranges piece by piece.
- Helpers include `prev_badblocks()`, `prev_by_hint()`, `can_merge_front()`, `front_merge()`, `can_combine_front()`, `front_combine()`, `overlap_front()`, `overlap_behind()`, `can_front_overwrite()`, `front_overwrite()`, `insert_at()`, and `try_adjacent_combine()`.
- The algorithm handles non-overlap, overlap, acknowledged-over-unacknowledged overwrite, adjacent merges, full-table pressure, and post-overwrite front/behind combines.
- `badblocks_set()` exports this behavior and returns false for failure or partial failure.

Clear path:
- `_badblocks_clear()` removes or shrinks bad ranges under `write_seqlock_irq`.
- Clearing rounds conservatively: start up, end down, so blocks are not falsely marked good.
- `front_clear()` shrinks or deletes a range.
- `front_splitting_clear()` splits one range into two if clearing a middle segment and there is room.
- Clearing non-bad areas is treated as success; if a full table prevents a required split, the request is effectively dropped and can report failure.

Check path:
- `_badblocks_check()` searches for bad ranges intersecting a requested sector span.
- `badblocks_check()` wraps it in a seqlock read/retry loop.
- Return values: `0` no bad blocks, `1` only acknowledged bad blocks, `-1` at least one unacknowledged bad block.
- It reports the first overlapping bad range through `first_bad` and `bad_sectors`.

Acknowledgement and sysfs:
- `ack_all_badblocks()` marks all unacknowledged entries acknowledged only if `bb->changed` is clear, then merges adjacent compatible entries.
- `badblocks_show()` prints ranges, optionally only unacknowledged ranges, scaling offsets/lengths by `bb->shift`.
- `badblocks_store()` parses `"sector length"` and calls `badblocks_set()` with acknowledged state derived from the `unack` argument.

Lifetime:
- `badblocks_init()` and `devm_init_badblocks()` allocate the page-sized table and initialize the seqlock.
- `badblocks_exit()` frees the table, using device-managed or normal allocation depending on initialization mode.
- Exported symbols provide a reusable bad-range service for block/storage consumers.

Important behavior notes:
- Acknowledged state is ordered: acknowledged ranges may overwrite unacknowledged ranges, but unacknowledged ranges do not overwrite acknowledged ones.
- The implementation favors correctness over perfect compaction; rare unoptimized full-table cases may fail or leave merge opportunities unused.
- `bb->unacked_exist` is a cache that is recomputed when acknowledged ranges are updated or shown.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/badblocks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bdev.c -->
# File Research: sources/os/linux/linux/block/bdev.c

`bdev.c` implements Linux block-device inode objects, pseudo-filesystem backing, open/claim/release logic, cache invalidation, freeze/thaw, block-size management, lookup helpers, and statx support.

Block device object model:
- `struct bdev_inode` embeds `struct block_device` plus the VFS inode.
- `I_BDEV()` maps a block-device inode to `struct block_device`; `file_bdev()` maps an open block-device file to its bdev.
- The block device pseudo filesystem `bd_type` is mounted during `bdev_cache_init()`, and `blockdev_superblock` is exported for writeback.
- `bdev_alloc()` creates internal bdev inodes, initializes locks/counters/stats, sets the queue, and associates whole-disk or partition state.
- `bdev_add()`, `bdev_unhash()`, `bdev_drop()`, and `disk_live()` manage visibility and lifetime.

Cache and block size:
- `invalidate_bdev()` invalidates clean cached pages/buffers.
- `truncate_bdev_range()` drops cache for a byte range, temporarily claiming exclusivity when needed to avoid invalidating live filesystem buffers.
- `kill_bdev()` truncates all pagecache and buffer state.
- `sync_blockdev_nowait()`, `sync_blockdev()`, and `sync_blockdev_range()` flush block-device mappings.
- `set_blocksize()`, `sb_set_blocksize()`, and `sb_min_blocksize()` validate block sizes, flush/kill cached folios under inode and invalidation locks, and update mapping minimum folio order.
- Large block sizes require filesystem `FS_LBS` support and transparent hugepages.

Freeze/thaw:
- `bdev_freeze()` increments `bd_fsfreeze_count`, invokes holder `freeze` if present, otherwise syncs the block device.
- `bdev_thaw()` decrements the count and invokes holder `thaw` when the last freeze is released.
- `bd_fsfreeze_mutex` serializes freeze/thaw state.

Claim and exclusivity:
- Global `bdev_lock` serializes block-device holder state.
- `bd_prepare_to_claim()` waits for in-progress claims and rejects conflicting holders.
- `bd_finish_claiming()` records holder and holder ops, increments holder counters on whole and target bdev.
- `bd_abort_claiming()` cancels a prepared claim.
- `bd_end_claim()` releases holder state and unblocks disk events for write holders.
- Holder ops provide callbacks for freeze, thaw, and mark-dead.

Open/release:
- `bdev_permission()` checks device-cgroup permissions and validates write-restriction rules.
- `blkdev_get_no_open()` looks up an existing block-device inode by `dev_t`, optionally using deprecated legacy autoloading.
- `bdev_open()` handles exclusive claim setup, disk event blocking, module refcounting, live-disk checks, write policy checks, whole/partition open, write-access accounting, file setup, and error unwinding.
- `bdev_file_open_by_dev()` and `bdev_file_open_by_path()` allocate pseudo files and call `bdev_open()`.
- `bdev_release()` syncs if likely last opener, yields write access and holder claim, flushes media-change events, closes whole/partition references, drops the module, and releases the no-open reference.
- `bdev_fput()` synchronously yields claims before deferred `fput()`.

Mounted-device write policy:
- `bdev_allow_write_mounted` defaults from `CONFIG_BLK_DEV_WRITE_MOUNTED` and is controlled by `bdev_allow_write_mounted=`.
- If disabled, `bd_writers` tracks normal writers and write-restricting holders. Direct writes can be blocked while a restricting holder exists, and restricting holders are denied while writers exist.

Other services:
- `lookup_bdev()` resolves a path in the current namespace to a block-device `dev_t`.
- `bdev_mark_dead()` notifies holder ops or syncs, then invalidates cached data.
- `sync_bdevs()` iterates all block-device inodes and either starts or waits for writeback.
- `bdev_statx()` fills direct-I/O alignment and atomic-write statx fields by looking up the internal bdev from the device-node inode.
- `block_size()` returns the current internal inode block size.

Key dependencies include VFS inode/pagecache APIs, blkdev/gendisk APIs, device cgroups, security hooks, disk events, module refs, and filesystem holder callbacks.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bfq-cgroup.c -->
# File Research: sources/os/linux/linux/block/bfq-cgroup.c

`bfq-cgroup.c` provides cgroup integration for the BFQ I/O scheduler. It maps blk-cgroup policy objects to BFQ groups, handles per-cgroup weights and stats, migrates BFQ queues across cgroups, reparents queues on cgroup offline, and supplies no-op/root-only fallbacks when group scheduling is disabled.

Statistics:
- Under `CONFIG_BFQ_CGROUP_DEBUG`, `struct bfq_stat` wraps a percpu counter plus auxiliary atomic count.
- Debug stats include merged I/O, service time, wait time, queued I/O, disk time, average queue size, dequeue count, group wait time, idle time, and empty time.
- Base stats always include bytes and I/O counts through `blkg_rwstat`.
- Dead group stats are transferred to the parent’s auxiliary counters in `bfqg_stats_xfer_dead()` so recursive stats do not lose historical usage.
- Public update helpers include `bfqg_stats_update_io_remove()`, `bfqg_stats_update_io_merged()`, `bfqg_stats_update_completion()`, `bfqg_stats_update_dequeue()`, and debug-only queue/idle/empty timing helpers.

Policy object mapping:
- `bfq_group_data` stores blkcg-level default weight.
- `bfq_group` stores per-device/per-cgroup scheduler state, async queues, rq position tree, stats, active entity counts, and pending-request counts.
- Helpers convert among `blkcg`, `blkcg_gq`, `blkg_policy_data`, `bfq_group_data`, and `bfq_group`.
- `bfq_cpd_alloc/free()` allocate per-blkcg data.
- `bfq_pd_alloc/init/free/reset_stats/offline()` allocate and manage per-device group state.
- `bfq_create_group_hierarchy()` activates `blkcg_policy_bfq` on the disk and returns the root BFQ group.

Queue/group binding:
- `bfq_init_entity()` initializes entity weight, original weight, queue ioprio fields, parent entity, and scheduler data; queue entities pin their BFQ group and blkcg_gq.
- `bfq_bio_bfqg()` selects the online BFQ group associated with a bio’s blkcg, falling back up the hierarchy or to root.
- `bfq_link_bfqg()` fixes internal BFQ parent links for groups that may not yet be connected to the scheduler hierarchy.

Migration:
- `bfq_bic_update_cgroup()` detects task cgroup changes via blkcg serial numbers and moves associated BFQ queues.
- `__bfq_bic_change_cgroup()` handles all actuators and async/sync queues.
- `bfq_sync_bfqq_move()` either moves an unshared sync queue or breaks invalid cooperative merge chains that cross cgroup boundaries.
- `bfq_bfqq_move()` is the main migration routine: it preserves references, updates pending-request accounting, expires/deactivates old scheduling state, drops the old group reference, assigns the new parent/sched_data, reactivates if busy, schedules dispatch when needed, and releases the temporary queue ref.

Cgroup offline:
- `bfq_pd_offline()` runs under scheduler locking, reparents active leaf queues to root, flushes idle trees, deactivates the group entity, releases async queues, and transfers stats.
- `bfq_reparent_active_queues()` and `bfq_reparent_leaf_entity()` walk active trees and in-service entities to find leaf queues.

Weights and files:
- `bfq_group_set_weight()` updates device-specific or default group weight, using a write memory barrier before setting `prio_changed`.
- Legacy files include `bfq.weight`, `bfq.weight_device`, I/O byte/count stats, and many debug stats/recursive stats.
- cgroup v2 exposes `bfq.weight`.
- Allowed weight range is `BFQ_MIN_WEIGHT` to `BFQ_MAX_WEIGHT`.

Fallback without `CONFIG_BFQ_GROUP_IOSCHED`:
- Group movement and blkcg refs become no-ops.
- All bios and queues map to `root_group`.
- A single root `bfq_group` is allocated and service trees initialized.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bfq-cgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bfq-iosched.h -->
# File Research: sources/os/linux/linux/block/bfq-iosched.h

`bfq-iosched.h` is the shared BFQ scheduler header. It defines constants, data structures, state flags, logging macros, and function prototypes used by BFQ’s main scheduler, WF2Q core, and cgroup layer.

Constants:
- BFQ supports three I/O priority classes and weights from `1` to `1000`.
- Ioprio-to-weight conversion uses coefficient `10`.
- Default queue ioprio is `4`; default group class is best-effort.
- Soft real-time queues can receive a large weight factor.
- `BFQ_MAX_ACTUATORS` is `8`, supporting per-actuator queueing and injection.

Scheduling structures:
- `bfq_service_tree`: per-ioprio-class active and idle rbtrees, first/last idle entity, virtual time, and weight sum.
- `bfq_sched_data`: a scheduler node containing three service trees, `in_service_entity`, `next_in_service`, and idle-class service timestamp.
- `bfq_entity`: generic schedulable node for either a queue or a group. It stores rb-node membership, B-WF2Q+ timestamps, service/budget, allocated requests, weight state, parent/sched_data links, priority-change state, and last child queue hints.
- `bfq_queue`: leaf request queue. It tracks references, ioprio, merge/cooperation state, request trees/fifo, budget and dispatch counters, flags, timing/thinktime stats, weight raising, waker relationships, burst membership, and actuator index.
- `bfq_io_cq`: per request-queue/io-context state, with async/sync queue matrices per actuator and persistent saved state for queue merge/split restoration.
- `bfq_data`: per-device scheduler state: dispatch list, root group, weight tree, busy queues, in-driver counts, hardware queueing samples, timers, in-service queue, dispatch/rate estimation, active/idle queues, tunables, low-latency and weight-raising state, OOM fallback queue, locks, bio merge context, async depths, and independent-access-range actuator data.

Cgroup/stat structures:
- `bfq_stat` and `bfqg_stats` store per-group accounting, with extra debug counters under `CONFIG_BFQ_CGROUP_DEBUG`.
- With group scheduling, `bfq_group_data` stores per-blkcg weight and `bfq_group` stores per-device group scheduler state, async queues, active/pending counters, rq-position tree, and stats.
- Without group scheduling, `bfq_group` is a minimal root-like container.

State and interfaces:
- `enum bfqq_state_flags` defines queue flags such as busy, wait_request, fifo_expire, short think time, sync, IO_bound, large burst, cooperative merge, split_coop, and soft-real-time update.
- `enum bfqq_expiration` lists expiration reasons: too idle, budget timeout, budget exhausted, no more requests, preempted.
- Prototypes connect BFQ components: queue lookup, weights tree operations, expiration, queue put/ref release, dispatch scheduling, async queues, cgroup updates, entity initialization, hierarchical WF2Q operations, queue activation/deactivation, busy accounting, and pending-group accounting.

Logging:
- `bfq_bfqq_name()` formats queue names for trace messages.
- `bfq_log_bfqq()` emits cgroup-aware trace messages when group scheduling is enabled, otherwise plain block trace messages.
- `bfq_log()` emits scheduler-level trace messages.

This header is the type contract for `bfq-cgroup.c`, `bfq-wf2q.c`, and the main BFQ scheduler implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bfq-iosched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bfq-wf2q.c -->
# File Research: sources/os/linux/linux/block/bfq-wf2q.c

`bfq-wf2q.c` implements BFQ’s hierarchical Budget Worst-case Fair Weighted Fair Queueing engine. It schedules generic `bfq_entity` objects, which may be leaf queues or cgroup/group entities, across per-priority-class service trees.

Timestamp and tree foundation:
- `bfq_gt()` compares virtual timestamps with wraparound handling.
- `WFQ_SERVICE_SHIFT` controls fixed-point virtual-time precision.
- `bfq_delta()` converts service to virtual time using weight.
- `bfq_calc_finish()` computes entity finish timestamps from start, service/budget, and weight.
- Active and idle entities are stored in rbtree structures ordered by finish time.
- Active tree nodes also maintain `min_start` for efficient eligibility lookup.
- Helpers insert/extract active and idle entities, update active-tree min-start state, and track first/last idle entries.
- `bfq_forget_idle()` advances virtual time and removes expired idle entities to bound idle-tree growth.

Entity weights and priority:
- `bfq_ioprio_to_weight()` maps I/O priority to BFQ weight.
- `__bfq_entity_update_weight_prio()` lazily applies weight/ioprio/ioprio-class changes, handles cgroup weight changes, updates service-tree weight sums, adjusts queue weight counters, and preserves class-tree consistency.

Activation and requeue:
- `__bfq_activate_entity()` activates a previously inactive entity, possibly extracting it from idle, assigning start time, adding service reference, and inserting it into active tree.
- `bfq_update_fin_time_enqueue()` recalculates finish time and handles backshifted timestamps for non-blocking wait reactivations.
- `__bfq_requeue_entity()` repositions in-service or active entities after service/budget changes.
- `bfq_activate_requeue_entity()` propagates activation/requeue up the hierarchy and updates cached `next_in_service`.
- Wrappers `bfq_activate_bfqq()` and `bfq_requeue_bfqq()` apply this to leaf queues.

Deactivation:
- `__bfq_deactivate_entity()` removes an entity from active/idle/in-service state, optionally inserting it into idle tree if finish time is still in the future.
- `bfq_deactivate_entity()` propagates deactivation up the hierarchy, then requeues/repositions ancestors whose child `next_in_service` changed.
- `bfq_deactivate_bfqq()` applies this to a leaf queue.

Service accounting:
- `bfq_bfqq_served()` charges actual served sectors to the queue and all ancestors, updates service counters, virtual time, idle cleanup, weight-raising service, and backlogged service.
- `bfq_bfqq_charge_time()` converts elapsed service time into an equivalent service amount for slow queues, preserving time fairness when throughput fairness would hurt performance.

Candidate selection:
- `bfq_update_next_in_service()` maintains each sched_data’s cached next entity, often avoiding full lookup when only one entity changed.
- `bfq_calc_vtime_jump()` and `bfq_update_vtime()` ensure at least one entity is eligible.
- `bfq_first_active_entity()` finds the eligible active entity with smallest finish time in O(log N) using `min_start`.
- `bfq_lookup_next_entity()` chooses among priority classes, occasionally serving idle class to guarantee minimum bandwidth and reduce priority inversion.
- `next_queue_may_preempt()` reports whether cached next differs from current in-service entity.
- `bfq_get_next_queue()` walks from root sched_data to a leaf queue, sets each entity along the path in service, extracts no-longer-candidate entities, then updates next-service caches upward.

In-service reset and busy accounting:
- `__bfq_bfqd_reset_in_service()` clears wait state, cancels idle timer, resets in-service entity pointers along the hierarchy, and drops service refs if appropriate.
- `bfq_add_bfqq_busy()` activates a queue, marks it busy, updates busy counts, pending-group counts, weight counters, weight-raised counts, and waker-list ordering.
- `bfq_del_bfqq_busy()` clears busy state, decrements counts, updates dequeue stats, deactivates the queue, removes pending-group state and weight counters when no dispatched requests remain.
- `bfq_add_bfqq_in_groups_with_pending_reqs()` and `bfq_del_bfqq_in_groups_with_pending_reqs()` maintain group-level pending-request counts under group scheduling.

Group scheduling conditionals:
- With `CONFIG_BFQ_GROUP_IOSCHED`, parent budgets and active entity counts are maintained, and non-leaf entities can remain next-service candidates if they have multiple active children.
- Without group scheduling, parent budget updates and active entity count hooks are no-ops.

The file is the core fairness engine behind BFQ’s service guarantees and latency/throughput behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bfq-wf2q.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bio-integrity-auto.c -->
# File Research: sources/os/linux/linux/block/bio-integrity-auto.c

`bio-integrity-auto.c` automatically generates and verifies block integrity metadata for bios whose submitter did not provide protection information. It lets the kernel use PI-capable devices even when the filesystem or bio submitter is not explicitly PI-aware.

Data model:
- `struct bio_integrity_data` wraps the target bio, saved data iterator, deferred work item, embedded `bio_integrity_payload`, and one bio_vec.
- A slab cache and mempool provide allocation reliability.
- `kintegrityd_wq` runs verification in process context.

Preparation:
- `bio_integrity_prep()` allocates `bio_integrity_data`, initializes the bio’s integrity payload, marks `BIP_BLOCK_INTEGRITY`, allocates an integrity buffer, sets default guard/ref-tag checks when requested, and either generates metadata for writes or saves the data iterator for later read verification.
- It exports `bio_integrity_prep`.

Completion:
- `__bio_integrity_endio()` is called on integrity I/O completion.
- For successful reads with check flags, it queues work to verify metadata asynchronously and returns false to delay `bio_endio()`.
- Otherwise it finishes immediately and returns true.
- `bio_integrity_verify_fn()` performs verification, stores the resulting block status in `bio->bi_status`, frees integrity state, and ends the bio.
- `bio_integrity_finish()` detaches and frees payload/buffer state and clears `REQ_INTEGRITY`.

Initialization:
- `blk_integrity_auto_init()` creates the slab, initializes the mempool, and allocates a high-priority CPU-intensive per-cpu workqueue named `kintegrityd`.
- `blk_flush_integrity()` flushes the workqueue.
- Init runs as `subsys_initcall`.

Important behavior:
- Verification is intentionally deferred out of interrupt context because it may be CPU-expensive.
- Writes generate integrity metadata before submission; reads verify after completion.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bio-integrity-auto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bio-integrity-fs.c -->
# File Research: sources/os/linux/linux/block/bio-integrity-fs.c

`bio-integrity-fs.c` provides filesystem-facing helpers for generating and verifying integrity metadata on bios. It is separate from automatic PI handling and gives filesystem submitters explicit helper calls.

Data model:
- `struct fs_bio_integrity_buf` embeds a `bio_integrity_payload` and one `bio_vec`.
- A slab cache and mempool back allocations.

Allocation/free:
- `fs_bio_integrity_alloc()` computes the needed action via `bio_integrity_action()`. If none is needed, it returns zero. Otherwise it allocates an integrity buffer object, initializes the bio integrity payload, allocates backing metadata storage, applies default check flags, and returns the action mask.
- `fs_bio_integrity_free()` frees the metadata buffer, returns the wrapper to the mempool, clears `bio->bi_integrity`, and clears `REQ_INTEGRITY`.

Generation and verification:
- `fs_bio_integrity_generate()` allocates integrity metadata if needed and then calls `bio_integrity_generate()`. It is exported GPL.
- `fs_bio_integrity_verify()` rebuilds the integrity iterator after driver completion using the remembered sector and size, computes metadata size from the disk integrity profile, and returns an errno converted from `bio_integrity_verify()` status.

Initialization:
- `fs_bio_integrity_init()` creates the slab and mempool at `fs_initcall`.

Important behavior:
- Verification requires the caller to remember the original sector and size because the submitter uses this helper after the driver has advanced bio state.
- The helper assumes the bio still carries the integrity payload allocated earlier.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bio-integrity-fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bio-integrity.c -->
# File Research: sources/os/linux/linux/block/bio-integrity.c

`bio-integrity.c` implements core bio integrity payload allocation, user metadata mapping, cloning/trimming, metadata buffer allocation, and default integrity action selection.

Action selection:
- `__bio_integrity_action()` decides what integrity work a bio needs based on operation and disk integrity profile.
- Reads may need buffering and verification unless `BLK_INTEGRITY_NOVERIFY` allows offload-only behavior.
- Writes skip zero-sector flush-like bios, may need zeroed metadata when generation is disabled, and may need guard/ref-tag checks depending on metadata tuple size.
- Bios with crypto context are rejected for integrity action.

Buffers and defaults:
- `bio_integrity_alloc_buf()` allocates a contiguous integrity buffer sized by `bio_integrity_bytes()`, falling back to a mempool page on allocation failure.
- `bio_integrity_free_buf()` frees kmalloc or mempool-backed storage.
- `bio_integrity_setup_default()` seeds integrity metadata from the bio sector and sets guard, IP checksum, and ref-tag check flags from the disk integrity profile.

Payload allocation:
- `bio_integrity_init()` attaches an existing payload and bvec array to a bio and sets `REQ_INTEGRITY`.
- `bio_integrity_alloc()` allocates a flexible payload with `nr_vecs` integrity segments and exports it.
- `bio_integrity_free()` frees the allocated payload and clears bio integrity state.

User metadata mapping:
- `bio_integrity_map_user()` maps an iov_iter carrying user integrity metadata.
- It rejects preexisting integrity state, too-large metadata, and excessive vector counts.
- It extracts pages from the iterator, handles partial pinning failure, coalesces pages into bvecs, detects P2PDMA pages, and decides whether a bounce copy is needed due to DMA alignment or segment limits.
- `bio_integrity_copy_user()` bounces metadata through kernel memory; for reads it preserves original bvecs for copying data back on completion, and for writes it copies user data in and unpins original pages.
- `bio_integrity_init_user()` attaches pinned user bvecs directly.
- `bio_integrity_unmap_user()` unpins direct mappings or copies read metadata back from bounce buffer and frees bounce state.

`uio_meta` integration:
- `bio_integrity_map_iter()` validates a `uio_meta` object, limits the iterator to metadata matching the current bio’s data sectors, maps it, transfers guard/app/ref tag flags, sets the seed, advances the original iterator, and increments the seed by integrity intervals.
- `bio_uio_meta_to_bip()` maps user integrity flags into `BIP_CHECK_*` flags and app tag.

Vector adjustment and cloning:
- `bio_integrity_advance()` advances integrity iterator state by the integrity bytes corresponding to completed data bytes.
- `bio_integrity_trim()` resets a cloned bio’s integrity size to match current bio sectors and is exported.
- `bio_integrity_clone()` allocates a clone payload that references the source integrity vectors and copies clone-safe flags and app tag.

Initialization:
- `bio_integrity_initfn()` initializes a page mempool sized for `BLK_INTEGRITY_MAX_SIZE`.
- Init runs as `subsys_initcall`.

Important behavior:
- Integrity metadata segment limits honor `queue_max_integrity_segments()`.
- Segment merging respects zone-device compatibility and SG gap constraints.
- P2PDMA metadata sets `REQ_NOMERGE`.
- Bounce-copy paths are used for DMA alignment/padding problems or excessive segment counts.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bio-integrity.c -->