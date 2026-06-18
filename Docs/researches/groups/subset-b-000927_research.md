# subset-b-000927 Research

Grouped research report for the requested block-layer source subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-throttle.c -->
# sources/distributed-fs/ceph-client/block/blk-throttle.c

Purpose: implements the block cgroup I/O throttling policy for request queues. It enforces per-cgroup read/write BPS and IOPS limits, queues over-limit bios, dispatches them through hierarchical service queues, exposes cgroup v1/v2 control files, and owns the `kthrotld` worker path that eventually resubmits ready bios.

Important APIs, types, and functions: the file defines private `struct throtl_data` for a queue-wide throttling instance and uses `struct throtl_grp`, `struct throtl_service_queue`, and `struct throtl_qnode` from the header. Key routines include `tg_bps_limit()`, `tg_iops_limit()`, `throtl_qnode_add_bio()`, `throtl_pop_queued()`, `tg_update_slice()`, `tg_dispatch_time()`, `tg_update_disptime()`, `tg_dispatch_one_bio()`, `throtl_select_dispatch()`, `throtl_pending_timer_fn()`, `blk_throtl_dispatch_work_fn()`, `tg_set_conf()`, `tg_set_limit()`, `blk_throtl_cancel_bios()`, `__blk_throtl_bio()`, `blk_throtl_exit()`, and module init `throtl_init()`. The exported policy object is `blkcg_policy_throtl`.

Control flow: cgroup file writes lazily initialize throttling on a disk with `blk_throtl_init()`, prepare a `blkcg_gq`, update limits, recompute inherited rule flags, and reschedule pending groups. Submission enters through `blk_throtl_bio()` in the header and then `__blk_throtl_bio()`, which walks from the bio's current `throtl_grp` toward the root. If each ancestor is within limit, the bio is charged and passed upward; otherwise it is queued in the first over-limit group. Pending groups sit in an rbtree sorted by `disptime`. Timer expiry dispatches a bounded quantum, moving bios from child queues to parent queues until the top-level `throtl_data` queue is reached; top-level dispatch work resubmits bios with `submit_bio_noacct_nocheck()`.

State and persistence: all state is in-memory and attached to the request queue and blkcg policy data. The policy tracks queue totals, per-group BPS/IOPS limits, slice start/end jiffies, dispatched byte/io counters, carryover after config changes, pending-tree membership, qnode references, and cgroup rwstats. There is no disk persistence; configuration is represented through cgroupfs control files and runtime policy state.

Dependencies and integration points: depends on blk-cgroup policy registration, `blkcg_gq` lifetime rules, request queue freeze/quiesce, bio flags such as `BIO_BPS_THROTTLED`, `BIO_TG_BPS_THROTTLED`, and `BIO_CGROUP_ACCT`, blktrace cgroup messages, cgroup v1 throttle files, cgroup v2 `io.max`, and block shutdown paths such as `del_gendisk()` and `blk_throtl_exit()`.

Risks and correctness concerns: the dispatch tree and qnode reference model are sensitive to double insertion, premature `blkg_put()`, and cancellation races. BPS and IOPS are split into two queues, so flags must be cleared and charged in the right order or split bios can be undercounted or rethrottled. Carryover math after limit changes uses negative dispatch counters and overflow-aware allowance calculations. Timer scheduling caps long sleeps to keep dynamic limit changes visible. Shutdown must flush bios without corrupting pending rbtrees.

Test signals: useful coverage includes cgroup v1 and v2 throttle file writes, hierarchical default-cgroup limits, mixed read/write fairness, split bios, discard accounting, priority-inversion root-blkg bypass, live limit changes with queued bios, queue teardown after `del_gendisk()`, blkg offline/free, fake low limits such as 1 IOPS, and tracing via `block_bio_queue`/blktrace throttle messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-throttle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-throttle.h -->
# sources/distributed-fs/ceph-client/block/blk-throttle.h

Purpose: declares the internal data structures and inline entry points for the block cgroup throttling policy implemented in `blk-throttle.c`. It also provides stubs when `CONFIG_BLK_DEV_THROTTLING` is disabled.

Important APIs and types: `struct throtl_qnode` holds per-source BPS and IOPS bio lists and pins its owning throttling group. `struct throtl_service_queue` contains parent linkage, read/write qnode lists, queued counts, an rbtree of active child groups, first dispatch time, and the pending timer. `enum tg_state_flags` records pending, queue-empty transition, IOPS-empty transition, and canceling state. `struct throtl_grp` embeds `blkg_policy_data` first, owns service queues, qnodes, limits, rule flags, slice counters, and rwstats. Public helpers are `pd_to_tg()`, `blkg_to_tg()`, `blk_throtl_activated()`, `blk_should_throtl()`, and `blk_throtl_bio()`.

Control flow: callers use `blk_throtl_bio()` from the bio submission path. The inline first checks whether the queue has an active throttling policy, updates legacy cgroup accounting when needed, tests inherited BPS/IOPS rule flags, and calls `__blk_throtl_bio()` only when throttling can apply. This keeps the hot path cheap for queues or cgroups without limits.

State and persistence: the header defines runtime-only objects that are allocated per `blkcg_gq` and per request queue. Rule flags cache whether a group or ancestor has limits, and stats accumulate in blkcg rwstat objects. No state is persisted outside kernel memory and cgroupfs-visible values.

Dependencies and integration points: depends on `blk-cgroup-rwstat.h`, blkcg policy plumbing, bio flags, cgroup default hierarchy detection, `request_queue->td`, and the `blkcg_policy_throtl` object. The first-member layout of `struct throtl_grp` is required by policy-data conversions.

Risks and test signals: layout or flag changes can break the implementation file, cgroup accounting, or queue teardown. `blk_should_throtl()` must not double-account legacy stats and must respect already BPS-throttled bios. Test with throttling configured and unconfigured, disabled config builds, cgroup v1/v2 accounting, and mixed BPS/IOPS limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-throttle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-timeout.c -->
# sources/distributed-fs/ceph-client/block/blk-timeout.c

Purpose: provides generic request timeout support for the block layer plus optional timeout fault injection. It sets request deadlines, rounds queue timer expirations, bounds maximum timeout distance, and exposes abort/fail knobs.

Important APIs and functions: under `CONFIG_FAIL_IO_TIMEOUT`, `__blk_should_fake_timeout()`, boot parameter parsing for `fail_io_timeout=`, debugfs setup, `part_timeout_show()`, and `part_timeout_store()` control `QUEUE_FLAG_FAIL_IO`. Core functions are `blk_abort_request()`, `blk_rq_timeout()`, and `blk_add_timer()`. `blk_timeout_init()` initializes a mask used by timeout rounding.

Control flow: when a request starts, `blk_add_timer()` fills `req->timeout` from the queue default if needed, clears `RQF_TIMED_OUT`, writes `req->deadline`, rounds the queue timer expiry, and updates `q->timeout` only when no timer is pending or the new deadline is meaningfully earlier. `blk_abort_request()` forces a request deadline to current jiffies and schedules queue timeout work. Fault-injection users can cause completion paths such as BSG to skip normal completion and exercise timeout recovery.

State and persistence: state is in request fields, queue timer state, queue flags, and the global `blk_timeout_mask`. Debugfs and sysfs knobs affect runtime behavior only.

Dependencies and integration points: integrates with `blk-mq` timeout work, request queue timers, `blk_should_fake_timeout()`, block partition/device sysfs attributes declared in `blk.h`, and kernel fault-injection infrastructure.

Risks and test signals: deadline writes are intentionally lightweight, so correctness depends on timeout scanning observing `req->deadline`. Timer slack avoids excessive `mod_timer()` churn but can delay recovery if calculated incorrectly. Test request timeout recovery, `blk_abort_request()` from drivers, fault injection through debugfs and `fail_io_timeout=`, sysfs fail toggles, and very large timeouts clamped by `BLK_MAX_TIMEOUT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-wbt.c -->
# sources/distributed-fs/ceph-client/block/blk-wbt.c

Purpose: implements writeback throttling as a `rq_qos` policy. It limits buffered writeback, discard, and swap write concurrency so synchronous reads meet a target latency, loosely following CoDel-style windowed latency feedback.

Important APIs, types, and functions: private `struct rq_wb` stores enable state, latency windows, min latency target, request wait queues, request-depth controller, sync read tracking, and blk-stat callback. Important routines include `wbt_done()`, `latency_exceeded()`, `scale_up()`, `scale_down()`, `wb_timer_fn()`, `wbt_wait()`, `wbt_track()`, `wbt_issue()`, `wbt_requeue()`, `wbt_init_enable_default()`, `wbt_disable_default()`, `wbt_get_min_lat()`, `wbt_disabled()`, and `wbt_set_lat()`.

Control flow: `wbt_init()` registers an `RQ_QOS_WBT` policy and a blk-stat callback. Bio submission hits `wbt_wait()`, which classifies reads, normal writeback, swap, and discard. Tracked writes wait on an `rq_wait` until inflight count is below a dynamic limit; reads update issue timestamps. Request tracking stores WBT flags on the request. Completion decrements inflight counts and wakes waiters. Periodic blk-stat callbacks evaluate read/write samples and a possible long-issued sync read, then shrink or expand allowed depth and re-arm the sampling window.

State and persistence: runtime state is attached to the disk's rq-qos chain. It records enable mode, depth scale step, background/normal write limits, active window length, unknown-sample count, read issue/completion timestamps, in-flight counters, and debugfs-visible values. Sysfs latency updates are runtime settings; no on-disk state exists.

Dependencies and integration points: depends on blk-stat, `rq_qos`, queue depth updates, backing-device dirty throttling signals, blk-mq queue freeze/quiesce for latency changes, debugfs rq-qos registration, tracepoints in `trace/events/wbt.h`, and elevator code that disables default WBT for schedulers that choose to do so.

Risks and test signals: depth feedback can overthrottle writeback or starve throughput if sample validity, sync read tracking, or wake thresholds regress. Writes with `REQ_SYNC|REQ_IDLE` are treated as direct I/O and bypass throttling. Test rotational and non-rotational default latency, sysfs latency -1/0/positive values, queue-depth changes, read/write mixed workloads, write-only workloads with negative scale steps, swap/discard paths, scheduler switching, debugfs counters, and tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-wbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-wbt.h -->
# sources/distributed-fs/ceph-client/block/blk-wbt.h

Purpose: exposes the small writeback-throttling control surface to the rest of the block layer and provides no-op stubs when `CONFIG_BLK_WBT` is disabled.

Important APIs: `wbt_init_enable_default()` creates and enables the default WBT policy when queue attributes allow it. `wbt_disable_default()` disables a default-enabled policy without removing it. `wbt_enable_default()` checks or flips default enablement. `wbt_get_min_lat()`, `wbt_disabled()`, and `wbt_set_lat()` query and set the latency target.

Control flow and integration: disk setup and sysfs latency handlers call these functions to install or adjust `RQ_QOS_WBT`. Elevator switching and queue setup can disable or avoid default WBT. With the config disabled, only the default enable/disable functions are present as empty stubs, so callers must not rely on query functions unless `CONFIG_BLK_WBT` is enabled.

State and persistence: the header owns no storage. All state lives in `struct rq_wb` inside `blk-wbt.c` and the queue rq-qos chain.

Risks and test signals: prototypes must match callers and the disabled-config surface must compile across queue setup paths. Test build matrices with `CONFIG_BLK_WBT=y/n`, sysfs latency operations, default policy activation, and scheduler interactions that call enable/disable hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-wbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-zoned.c -->
# sources/distributed-fs/ceph-client/block/blk-zoned.c

Purpose: implements generic zoned block device support: reporting zones, issuing zone management operations, caching zone conditions, validating zoned geometry, handling zone append emulation, and serializing sequential writes with per-zone write plugs.

Important APIs, types, and functions: `struct blk_zone_wplug` tracks one zone's plugged bios, write pointer offset, condition, references, flags, and worker state. Public/exported functions include `blk_zone_cond_str()`, `bdev_zone_is_seq()`, `blkdev_report_zones()`, `blkdev_zone_mgmt()`, `blkdev_report_zones_ioctl()`, `blkdev_zone_mgmt_ioctl()`, `disk_report_zone()`, `blkdev_get_zone_info()`, `blkdev_report_zones_cached()`, `blk_zone_plug_bio()`, `blk_zone_append_update_request_bio()`, `blk_zone_write_plug_bio_endio()`, `blk_zone_write_plug_finish_request()`, `disk_init_zone_resources()`, `disk_free_zone_resources()`, `blk_revalidate_disk_zones()`, `blk_zone_issue_zeroout()`, and debugfs `queue_zone_wplugs_show()`.

Control flow: user report ioctls either call driver `report_zones` or build cached reports from `zones_cond` and active write plugs. Zone management validates write access and alignment, may use `REQ_OP_ZONE_RESET_ALL`, and updates cached state on completion. Bio submission invokes `blk_zone_plug_bio()` for zoned queues. Sequential writes and emulated append operations acquire or allocate a zone write plug, validate ordering against `wp_offset`, either submit immediately or queue on the plug, and advance the cached write pointer. Completion clears plug flags, restores emulated append opcodes, handles errors by aborting queued bios and marking write pointer update needed, and schedules the next bio. Rotational QD1 devices use a per-disk worker thread; other devices use per-plug workqueue jobs.

State and persistence: disk state includes `zones_cond` under RCU, zone capacity, last-zone capacity, number of zones, a hash table and mempool of `blk_zone_wplug`, active plug count, plug workqueue, QD1 worker, and `GD_ZONE_APPEND_USED`. Plug state persists only while a zone is partially active or has queued/in-flight bios. It is reconstructed by zone revalidation and driver reports.

Dependencies and integration points: depends on driver `report_zones`, block device ioctls, blk-mq request merging, bio splitting at zone boundaries, request completion hooks declared in `blk.h`, queue limits for zone size/open/active zones, mempool/kthread/freezer APIs, RCU, debugfs, and tracepoints under `trace/events/block.h`.

Risks and test signals: highest-risk areas are plug reference counting, RCU hash removal, mixing native zone append and regular writes, write errors that require report-zone recovery, reset/finish racing with writes, and cached condition drift. Test zone report ioctl v1/v2, cached reports, revalidation failures for invalid zone geometry, sequential write ordering, emulated append sector reporting, native append mixed with writes, NOWAIT bios, rotational QD1 worker behavior, zone reset/finish completion, zeroout fallback, teardown with active plugs, and debugfs plug dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-zoned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk.h -->
# sources/distributed-fs/ceph-client/block/blk.h

Purpose: is the block layer's internal header for queue lifetime, bio splitting, merging, flushing, zoned hooks, disk events, partition helpers, integrity, debugfs locking, and request reference/timestamp helpers. It is not a standalone implementation but defines contracts shared by many block source files.

Important APIs and types: declarations include flush queue allocation, queue freeze/unfreeze helpers, `submit_bio_noacct_nocheck()`, `bio_queue_enter()`, `blk_wait_io()`, bio split helpers, merge helpers, elevator hooks, partition sysfs handlers, timeout functions, disk event lifecycle, ioctl/uring entry points, block device open/close helpers, integrity functions, zoned hooks, and fault injection hooks. Important inline helpers include `blk_try_enter_queue()`, `biovec_phys_mergeable()`, `zone_device_pages_compatible()`, `rq_mergeable()`, `blk_queue_get_max_sectors()`, `bio_may_need_split()`, `__bio_split_to_limits()`, request refcount helpers, `blk_time_get_ns()`, and debugfs NOIO locks.

Control flow and integration: most implementation files include this header to access internal state while keeping public `blkdev.h` smaller. Bio submission uses queue-enter helpers before splitting and issuing. Merge paths use request merge predicates and elevator callbacks. Zoned completion and request finishing call the inline zoned hooks. Debugfs registration uses NOIO wrappers to avoid reclaim recursion against frozen queues.

State and persistence: the header defines no independent storage but operates on `request_queue`, `gendisk`, `bio`, `request`, block device, flush queue, and current task plug state. Timestamp caching in `blk_time_get_ns()` stores the current ktime in `current->plug` for a submission batch.

Dependencies and risks: because it is a central internal ABI, signature drift breaks many block files. Merge helpers must respect hardware limits, P2PDMA pgmap compatibility, Xen constraints, integrity vectors, zoned append non-mergeability, and atomic write limits. Queue entry helpers must obey PM-only and freeze/drain state. Test broad block build configs, bio splitting by operation type, merge boundary cases, zoned enabled/disabled builds, lockdep around queue freeze, integrity enabled/disabled, Xen/KMSAN/P2PDMA cases, and debugfs registration under frozen queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bsg-lib.c -->
# sources/distributed-fs/ceph-client/block/bsg-lib.c

Purpose: provides a helper library for block SCSI generic (BSG) transport queues. It turns SG_IO v4 userspace commands into blk-mq driver requests, maps payload buffers, manages `struct bsg_job` lifetime, and creates/removes BSG request queues for lower-level drivers.

Important APIs and functions: private `struct bsg_set` wraps a `blk_mq_tag_set`, registered `bsg_device`, job callback, and timeout callback. Public functions are `bsg_job_put()`, `bsg_job_get()`, `bsg_job_done()`, `bsg_remove_queue()`, and `bsg_setup_queue()`. Core internals include `bsg_transport_sg_io_fn()`, `bsg_teardown_job()`, `bsg_prepare_job()`, `bsg_queue_rq()`, `bsg_init_rq()`, `bsg_exit_rq()`, and `bsg_timeout()`.

Control flow: `bsg_setup_queue()` creates a blocking blk-mq queue with per-request `struct bsg_job` storage and registers a `/dev/bsg` node through `bsg_register_queue()`. SG_IO v4 validates protocol/subprotocol and `CAP_SYS_RAWIO`, allocates request and optional bidirectional request, copies the command block from userspace, maps dout/din buffers, executes the request synchronously, copies reply data back, unmaps bios, and frees requests. Driver-submitted jobs flow through `bsg_queue_rq()`, which prepares scatterlists, takes device references, invokes the driver job callback, and completes through `bsg_job_done()`.

State and persistence: queue state lives in `bsg_set`, blk-mq tag set storage, per-request `bsg_job`, scatterlist allocations, reply buffers, and device references. No persistent storage exists.

Dependencies and integration points: depends on blk-mq, BSG core registration from `bsg.c`, SG_IO v4 structures, SCSI sense/status helpers, user copy APIs, request timeout and fake-timeout support, and driver-provided job/timeout callbacks.

Risks and test signals: this is a privileged passthrough path, so user pointer validation, buffer mapping/unmapping symmetry, bidirectional request cleanup, kref/device-reference balance, and timeout behavior are critical. Test invalid protocol/subprotocol, missing `CAP_SYS_RAWIO`, unidirectional and bidirectional transfers, user copy failures, driver job errors, fake timeouts, queue removal with in-flight jobs, and per-request reply allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bsg-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bsg.c -->
# sources/distributed-fs/ceph-client/block/bsg.c

Purpose: implements the userspace-facing BSG character device layer for SG v4 passthrough. It registers the `bsg` class/major, creates character devices, handles legacy sg ioctls, and forwards SG_IO or io_uring commands to queue-specific callbacks.

Important APIs and functions: `struct bsg_device` stores the backing request queue, device and cdev, queue limits visible to userspace, timeout/reserved-size settings, and SG_IO/io_uring callbacks. Public functions are `bsg_register_queue()` and `bsg_unregister_queue()`. Core routines include `bsg_timeout()`, `bsg_sg_io()`, `bsg_open()`, `bsg_release()`, `bsg_ioctl()`, `bsg_check_uring_features()`, `bsg_uring_cmd()`, `bsg_device_release()`, `bsg_devnode()`, and init `bsg_init()`.

Control flow: `bsg_init()` registers the class and char-device range. A caller registers a queue, gets a minor from an IDA, initializes a cdev/device, and optionally links `/sys/block/<disk>/queue/bsg` to the device. Open pins the request queue with `blk_get_queue()`. Ioctl handles SG queue depth, version, timeout, reserved size, `SG_IO`, and rejects unsupported `SCSI_IOCTL_SEND_COMMAND`. SG_IO copies `sg_io_v4`, checks guard byte `Q`, calls the queue callback, and copies the modified header back. io_uring passthrough requires big SQE/CQE support and a queue callback.

State and persistence: state is per registered BSG device and includes minor allocation, queue reference lifetime, timeout, max queue, and reserved size. It is removed by `bsg_unregister_queue()` and freed by device release.

Dependencies and integration points: integrates with `bsg-lib.c`, block request queues, Linux cdev/device model, sysfs, io_uring command infrastructure, SCSI sg ioctl compatibility, and queue maximum bytes.

Risks and test signals: queue lifetime during open/unregister, IDA minor cleanup, sysfs link cleanup, userspace copy failures, timeout conversions, and io_uring feature validation are important. Test SG_IO with valid/invalid guard, reserved-size bounds, timeout set/get, concurrent unregister/open, io_uring without required features, queues without uring callback, and sysfs bsg link creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/disk-events.c -->
# sources/distributed-fs/ceph-client/block/disk-events.c

Purpose: monitors disk events such as media change and eject request, provides sysfs controls for supported events and polling interval, emits uevents, and coordinates synchronous event clearing with asynchronous polling work.

Important APIs and functions: private `struct disk_events` stores the disk, lock, block depth, pending and clearing masks, poll interval, and delayed work. Public functions are `disk_block_events()`, `disk_unblock_events()`, `disk_flush_events()`, `disk_check_media_change()`, `disk_force_media_change()`, `disk_alloc_events()`, `disk_add_events()`, `disk_del_events()`, and `disk_release_events()`. Sysfs attributes are `events`, `events_async`, and `events_poll_msecs`; the module parameter is `block.events_dfl_poll_msecs`.

Control flow: disk allocation creates an initially blocked `disk_events`. Adding the disk links it to the global list and unblocks, optionally scheduling immediate work. Work calls the driver's `check_events()` with a clearing mask, accumulates new pending bits, reschedules polling if enabled, increments disk sequence for media changes, and emits uevents when configured. Synchronous media checks block background work, merge outstanding clearing masks, call the driver, unblock, and return pending bits to the caller.

State and persistence: per-disk state tracks pending events already reported, clearing requests, nested block count, and poll interval. Global state tracks all event-enabled disks and the default polling interval. State is runtime-only; sysfs/module parameters change live behavior.

Dependencies and integration points: depends on gendisk event flags, driver `fops->check_events`, system freezable power-efficient workqueue, kobject uevents, disk sequence counters, block device invalidation through `bdev_mark_dead()`, open mutex conventions for flushing masks, and disk lifecycle hooks.

Risks and test signals: races between `disk_flush_events()` and `disk_clear_events()`, balanced block/unblock nesting, delayed work cancellation, and uevent suppression by flags are key. Test removable media change, eject request, polling disabled/default/device-specific intervals, concurrent sysfs poll writes, disk deletion while work is pending, forced media change invalidation, and partition rescan flagging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/disk-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/early-lookup.c -->
# sources/distributed-fs/ceph-client/block/early-lookup.c

Purpose: resolves early-boot root/device specifiers into `dev_t` before the root filesystem is mounted and prints available partitions when mounting fails.

Important APIs and functions: `early_lookup_bdev()` is the main resolver. Helpers include `devt_from_partuuid()`, `devt_from_partlabel()`, `devt_from_devname()`, `devt_from_devnum()`, `blk_lookup_devt()`, `match_dev_by_uuid()`, `match_dev_by_label()`, `bdevt_str()`, and `printk_all_partitions()`.

Control flow: `early_lookup_bdev()` recognizes `PARTUUID=`, `PARTLABEL=`, `/dev/...`, decimal major:minor, major:minor:offset syntax, and legacy hexadecimal device numbers. PARTUUID matching can parse `/PARTNROFF=<int>` and derive a relative partition number. `/dev/` names replace slashes with `!`, try an exact disk name, then parse trailing partition numbers including the `pN` convention for disk names ending in digits. Partition listing iterates block-class disks and their xarray partition table under RCU and prints hex devt, size, name, UUID, and driver.

State and persistence: this file stores no lasting state. It reads current block-class devices, disk partition tables, and partition metadata populated by earlier probing.

Dependencies and integration points: depends on the block device class, `disk_type`, `dev_to_bdev()`, `dev_to_disk()`, partition metadata (`bd_meta_info`), `part_devt()`, `new_decode_dev()`, early init annotations, and kernel boot/root mount diagnostics.

Risks and test signals: malformed PARTUUID syntax must fail clearly, UUID matching uses prefix length before optional suffix, and devname parsing must distinguish disk names ending in digits from partition suffixes. Test root by PARTUUID, PARTUUID/PARTNROFF positive and negative offsets, PARTLABEL, `/dev/sda1`, `/dev/nvme0n1p1`, major:minor, hex devt, hidden/empty disks in partition printing, and devices whose partitions appear only after opening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/early-lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/elevator.c -->
# sources/distributed-fs/ceph-client/block/elevator.c

Purpose: implements the block multi-queue elevator core: scheduler registration, scheduler switching, merge hash/rbtree helpers, sysfs `iosched` handling, and default scheduler selection.

Important APIs and functions: exported helpers include `elv_bio_merge_ok()`, `elv_rqhash_del()`, `elv_rqhash_add()`, `elv_rqhash_reposition()`, `elv_rb_add()`, `elv_rb_del()`, `elv_rb_find()`, `elv_register()`, `elv_unregister()`, `elv_rb_former_request()`, and `elv_rb_latter_request()`. Internal control routines include `elevator_find_get()`, `elevator_alloc()`, `elevator_exit()`, `elv_merge()`, `elv_attempt_insert_merge()`, `elv_merged_request()`, `elv_merge_requests()`, `elevator_switch()`, `elevator_change()`, `elevator_change_done()`, `elv_update_nr_hw_queues()`, `elevator_set_default()`, `elevator_set_none()`, `elv_iosched_store()`, and `elv_iosched_show()`.

Control flow: schedulers register `struct elevator_type` instances in a global list, optionally with an io-context slab cache. Merge paths first try queue `last_merge`, then the elevator hash for back/discard merges, then scheduler-specific `request_merge()`. Scheduler switching loads modules before freezing, allocates scheduler resources, freezes and cancels work, exits the old scheduler under `elevator_lock`, initializes the new scheduler or `none`, unfreezes, unregisters old sysfs/debugfs state, and registers new sysfs/debugfs state. Default setup picks `mq-deadline` for single queue or shared-tags devices unless disabled.

State and persistence: global scheduler state is `elv_list`. Per-queue state is `struct elevator_queue`, including type, scheduler tags/data, sysfs kobject, flags, lock, and merge hash. State persists while the queue uses the scheduler and is replaced on switch.

Dependencies and integration points: depends on blk-mq scheduler resource allocation, queue freeze/quiesce, request merging helpers from `blk.h`, blk-cgroup IO contexts, runtime PM headers, WBT interactions, sysfs/kobject/debugfs, request-module autoloading, and the `iosched` queue attribute.

Risks and test signals: switching must avoid kernfs/update-nr-hwq deadlocks, resource leaks on failed initialization, stale hash entries, and module refcount mistakes. Test scheduler register/unregister, duplicate names, sysfs switching to valid/invalid schedulers and `none`, module autoload, switching during disk removal, hardware queue count changes, merge hash correctness after back merges, default `mq-deadline` selection, and debugfs/sysfs teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/elevator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/elevator.h -->
# sources/distributed-fs/ceph-client/block/elevator.h

Purpose: declares the internal elevator/scheduler interfaces used by block multi-queue schedulers and the elevator core.

Important APIs and types: `enum elv_merge` classifies no/front/back/discard merges. `struct elevator_tags` and `struct elevator_resources` carry scheduler tag/data allocations. `struct elv_change_ctx` coordinates scheduler switching. `struct elevator_mq_ops` defines scheduler callbacks for init/exit, hardware-context lifecycle, merging, depth limiting, request prepare/finish, insertion, dispatch, work detection, completion, requeue, rb traversal, and io-context lifecycle. `struct elevator_type` describes a scheduler implementation and module ownership. `struct elevator_queue` stores the active scheduler type, tags/data, sysfs kobject, lock, flags, and merge hash.

Control flow and integration: scheduler modules fill `elevator_type` and call `elv_register()`. The elevator core allocates `elevator_queue`, invokes scheduler ops through block-mq dispatch and merge paths, and exposes per-scheduler sysfs/debugfs attributes. The header also provides module ref helpers, rb helpers, hash declarations, insertion constants, and scheduler debugfs registration declarations.

State and persistence: this header defines runtime objects whose instances live either globally as registered scheduler types or per queue as active scheduler state. It owns no storage itself.

Dependencies and risks: depends on blk-mq, percpu/io-context infrastructure, hash tables, sysfs attributes, modules, and optional debugfs. Callback signature compatibility is critical; missing mandatory ops are rejected by `elv_register()`. Test compile coverage for schedulers, module load/unload, sysfs attributes, merge callbacks, io-context caches, hardware-context hotplug, and disabled debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/elevator.h -->
