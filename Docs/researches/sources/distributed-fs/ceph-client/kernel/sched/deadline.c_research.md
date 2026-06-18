# sources/distributed-fs/ceph-client/kernel/sched/deadline.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/deadline.c` implements the `SCHED_DEADLINE` scheduling class: earliest-deadline-first selection, Constant Bandwidth Server enforcement, GRUB reclaiming, deadline bandwidth admission control, push/pull migration, CPU hotplug handling, cpuset/root-domain accounting, and deadline-server support for fair and sched-ext classes. The file was read as a complete 3879-line source.

## Important APIs, Types, and Functions

Core helpers map deadline entities to runqueues (`rq_of_dl_se()`, `dl_rq_of_se()`), manage root-domain bandwidth (`init_dl_bw()`, `__dl_add()`, `__dl_sub()`, `sched_dl_overflow()`), and update rq bandwidth (`add_rq_bw()`, `add_running_bw()`, `dl_rq_change_utilization()`). CBS and timers are handled by `setup_new_dl_entity()`, `replenish_dl_entity()`, `update_dl_entity()`, `start_dl_timer()`, `dl_task_timer()`, `inactive_task_timer()`, and `update_curr_dl_se()`. Deadline servers use `dl_server_start()`, `dl_server_stop()`, `dl_server_init()`, `sched_init_dl_servers()`, and `dl_server_apply_params()`. Scheduler-class methods are collected in `DEFINE_SCHED_CLASS(dl)`: enqueue/dequeue/yield, wakeup preemption, pick/set/put task, balance, migration, rq online/offline, tick, priority changes, and class switches. Admission and ABI helpers include `sched_dl_global_validate()`, `sched_dl_do_global()`, `__setparam_dl()`, `__getparam_dl()`, `__checkparam_dl()`, `dl_cpuset_cpumask_can_shrink()`, `dl_bw_alloc()`, `dl_bw_free()`, and `dl_bw_deactivate()`.

## Control Flow

Enqueueing a deadline entity updates sleeper stats, handles constrained-deadline activation, adds bandwidth on restore/migration, handles throttled entities, applies CBS wakeup/replenishment rules, then inserts the entity in an rb-tree ordered by absolute deadline. `inc_dl_deadline()` updates the rq's earliest deadline, `cpudl`, and `cpupri`. Dequeue removes the rb-node, updates counts and deadline indices, and on sleep starts the inactive/0-lag path via `task_non_contending()`. Picking chooses the leftmost rb-node; if it is a deadline server, the server asks its client class for a task and stops itself if none is available.

Runtime accounting flows through `update_curr_dl()`, which uses scheduler execution delta, scales by GRUB reclaim or CPU/frequency capacity, subtracts from runtime, throttles overrun or yielded entities, dequeues them, and starts replenishment timers. `dl_task_timer()` replenishes throttled tasks, migrates them if their rq went offline, re-enqueues them, and reschedules if needed. `inactive_task_timer()` removes active bandwidth after 0-lag or clears bandwidth for dead/non-deadline tasks.

Migration is split into wakeup placement (`select_task_rq_dl()`), push (`push_dl_task()`), and pull (`pull_dl_task()`). `find_later_rq()` queries `cpudl`, honors affinity/topology, and `find_lock_later_rq()` revalidates under double rq locks. Pushable tasks are kept in an rb-tree ordered by deadline. Pulling scans overloaded rqs, moves earlier-deadline pushable tasks, or uses stopper work for migration-disabled tasks.

Admission control calculates bandwidth ratios per root domain and CPU capacity. `sched_dl_overflow()` reserves or updates bandwidth on policy changes; cpuset/hotplug helpers allocate, free, deactivate, and rebuild bandwidth across root domains. Global RT runtime settings also set the deadline bandwidth cap because deadline and RT bandwidth remain linked in parts of the scheduler.

## State and Persistence Behavior

State is in `sched_dl_entity`, per-rq `dl_rq`, root-domain `dl_bw`, `cpudl`, `cpupri`, pushable rb-trees, hrtimers, and cpuset task counts. Deadline task parameters persist in task_struct until policy changes or the entity is cleared. Runtime, absolute deadline, throttling, yielding, non-contending, and server-defer flags are transient in-memory scheduler state. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on scheduler core locks/classes, hrtimers, cpusets, housekeeping masks, root domains, `cpudeadline.c`, `cpupri.c`, cpufreq utilization updates, PELT load updates, RT bandwidth, uclamp/capacity scaling, schedstats, tracepoints, and optional RT mutex PI and sched-ext support. User ABI integration comes through `sched_setattr()`/`sched_getattr()`, sysctl deadline period limits, and debugfs server tuning implemented in `debug.c`.

## Risks and Edge Cases

Deadline correctness depends on maintaining rb-tree order, rq bandwidth invariants, and root-domain bandwidth under many races. Timer callbacks hold task references and must balance `get_task_struct()`/`put_task_struct()` even when cancellation races. Constrained-deadline tasks after deadline but before next period need special throttling to avoid admission-test violations. PI boosting can temporarily override throttling. Offline migration must preserve running and reserved bandwidth across rqs and root domains. Shared RT/deadline bandwidth and asymmetric capacity admission are particularly sensitive to overflow, CPU hotplug, and cpuset partition changes.

## Test Signals

Signals include `sched_setattr()` parameter validation and admission tests; runtime overrun/yield CBS replenishment tests; constrained-deadline self-suspension tests; GRUB reclaim and frequency/capacity scaling benchmarks; push/pull migration tests across affinity, topology, and overloaded rqs; CPU hotplug and cpuset partition stress; PI boosting with throttled deadline tasks; deadline server debugfs tuning tests; and tracepoint/schedstat validation for throttle, replenish, and migration events.
