# sources/distributed-fs/ceph-client/block/blk-wbt.c

Purpose: implements writeback throttling as a `rq_qos` policy. It limits buffered writeback, discard, and swap write concurrency so synchronous reads meet a target latency, loosely following CoDel-style windowed latency feedback.

Important APIs, types, and functions: private `struct rq_wb` stores enable state, latency windows, min latency target, request wait queues, request-depth controller, sync read tracking, and blk-stat callback. Important routines include `wbt_done()`, `latency_exceeded()`, `scale_up()`, `scale_down()`, `wb_timer_fn()`, `wbt_wait()`, `wbt_track()`, `wbt_issue()`, `wbt_requeue()`, `wbt_init_enable_default()`, `wbt_disable_default()`, `wbt_get_min_lat()`, `wbt_disabled()`, and `wbt_set_lat()`.

Control flow: `wbt_init()` registers an `RQ_QOS_WBT` policy and a blk-stat callback. Bio submission hits `wbt_wait()`, which classifies reads, normal writeback, swap, and discard. Tracked writes wait on an `rq_wait` until inflight count is below a dynamic limit; reads update issue timestamps. Request tracking stores WBT flags on the request. Completion decrements inflight counts and wakes waiters. Periodic blk-stat callbacks evaluate read/write samples and a possible long-issued sync read, then shrink or expand allowed depth and re-arm the sampling window.

State and persistence: runtime state is attached to the disk's rq-qos chain. It records enable mode, depth scale step, background/normal write limits, active window length, unknown-sample count, read issue/completion timestamps, in-flight counters, and debugfs-visible values. Sysfs latency updates are runtime settings; no on-disk state exists.

Dependencies and integration points: depends on blk-stat, `rq_qos`, queue depth updates, backing-device dirty throttling signals, blk-mq queue freeze/quiesce for latency changes, debugfs rq-qos registration, tracepoints in `trace/events/wbt.h`, and elevator code that disables default WBT for schedulers that choose to do so.

Risks and test signals: depth feedback can overthrottle writeback or starve throughput if sample validity, sync read tracking, or wake thresholds regress. Writes with `REQ_SYNC|REQ_IDLE` are treated as direct I/O and bypass throttling. Test rotational and non-rotational default latency, sysfs latency -1/0/positive values, queue-depth changes, read/write mixed workloads, write-only workloads with negative scale steps, swap/discard paths, scheduler switching, debugfs counters, and tracepoints.
