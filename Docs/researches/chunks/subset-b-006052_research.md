# sources/distributed-fs/ceph-client/kernel/sched/ext.c lines 1-8985

## Scope

This chunk covers the first 8,985 lines of `kernel/sched/ext.c`, the Linux
sched_ext implementation carried in the Ceph client kernel source snapshot. It
starts at global scheduler state, dispatch queue management, scheduler-class
callbacks, task/cgroup lifecycle, enable/disable, sysfs, watchdog, BPF
`struct_ops` registration, system integration, and the first BPF kfunc groups.
The range ends inside the kfunc section immediately after
`scx_bpf_destroy_dsq()`; DSQ iterators, BPF string/dump helpers, CPU
performance helpers, generic query helpers, kfunc registration, and module init
continue in chunk `subset-b-006053`.

Although this repository is Ceph-oriented, this file is generic kernel
scheduling infrastructure. CephFS workloads can run under sched_ext, but no
Ceph filesystem logic is implemented here.

## Purpose

`ext.c` implements the BPF extensible scheduler class. It lets a BPF
`struct sched_ext_ops` program choose where runnable tasks wait and how CPUs
pull runnable work, while the kernel keeps safety, task lifecycle, CPU hotplug,
cgroup, and scheduler-class integration under kernel control.

The chunk provides:

- Global sched_ext enable state, root/sub-scheduler registries, watchdog state,
  sysfs attributes, and task tracking.
- Dispatch queues (DSQs): per-CPU local DSQs, per-node global DSQs, per-CPU
  bypass DSQs, and BPF-created user DSQs.
- The core enqueue/dequeue/dispatch/pick path for `ext_sched_class`.
- Task ownership tracking between the kernel SCX core and BPF scheduler through
  `p->scx.ops_state`.
- Bypass mode, which guarantees forward progress without trusting BPF policy
  during disable, errors, suspend/resume, and sub-scheduler transitions.
- Task, cgroup, fork, exit, CPU hotplug, tick, and core-scheduling callbacks.
- Root scheduler and sub-scheduler enable/disable flows.
- BPF `struct_ops` plumbing for loading `sched_ext_ops`.
- Initial kfunc APIs for DSQ insertion/movement, user DSQ creation/destruction,
  task slice/vtime mutation, CPU kicking, and queue length queries.

The code is latency and correctness critical. Many paths run with rq locks,
raw spinlocks, IRQs disabled, RCU protection, or scheduler hotplug locks.

## Important APIs, Types, And Functions

Global state and synchronization:

- `scx_root` is the current root scheduler instance. During the transition to
  multi-scheduler support, many root dereferences are intentionally direct and
  marked for future instance-specific replacement.
- `scx_sched_all`, `scx_sched_hash`, `scx_sched_lock`, and
  `scx_enable_mutex` maintain all root/sub scheduler instances and serialize
  enable/disable/link operations.
- `scx_tasks` plus `scx_tasks_lock` tracks every task from fork to free so
  enable/disable can visit all tasks, including tasks that lost PIDs while
  exiting.
- `scx_enable_state_var`, `__scx_enabled`, `__scx_switched_all`,
  `scx_fork_rwsem`, `scx_init_task_enabled`, and `scx_switching_all` govern
  global scheduler activation.
- `scx_bypass_lock`, per-scheduler `bypass_depth`, and
  `bypass_dsp_enable_depth` coordinate forward-progress bypass.
- `scx_watchdog_work`, `scx_watchdog_interval`, and
  `scx_watchdog_timestamp` detect runnable tasks that are not scheduled and a
  wedged watchdog worker.
- Per-CPU `scx_kick_syncs`, `cpus_to_kick*` masks, and `kick_cpus_irq_work`
  implement asynchronous CPU kicks and optional synchronous wait semantics.

Scheduler instances and DSQs:

- `struct scx_sched` owns the BPF `sched_ext_ops`, enabled op bitmap,
  per-node global DSQs, per-CPU scheduler data, user DSQ hash table, bypass
  state, watchdog timeout, exit info, sysfs kobject, helper worker, and
  optional sub-scheduler cgroup hierarchy metadata.
- `struct scx_dispatch_q` instances are initialized by `init_dsq()` and freed
  through `exit_dsq()`, `destroy_dsq()`, irq work, and RCU. Built-in IDs
  include `SCX_DSQ_LOCAL`, `SCX_DSQ_GLOBAL`, and `SCX_DSQ_BYPASS`; BPF-created
  DSQs live in `sch->dsq_hash`.
- `find_global_dsq()`, `find_user_dsq()`, `bypass_dsq()`,
  `bypass_enq_target_dsq()`, and `find_dsq_for_dispatch()` resolve destination
  queues from scheduler instance, CPU, and DSQ id.
- `dispatch_enqueue()`, `dispatch_dequeue()`, `task_unlink_from_dsq()`, and
  `dispatch_dequeue_locked()` mutate DSQ membership, FIFO/priority-queue state,
  `dsq->nr`, `dsq->first_task`, `p->scx.dsq`, and task-local DSQ flags.
- `nldsq_next_task()`, `nldsq_cursor_next_task()`, and
  `nldsq_cursor_lost_task()` support bounded, cursor-based iteration over
  non-local DSQs, including iterator cursor list nodes inserted by BPF-visible
  DSQ iterators.

Task state and scheduler callbacks:

- `scx_get_task_state()` and `scx_set_task_state()` validate transitions among
  `SCX_TASK_NONE`, `INIT_BEGIN`, `INIT`, `READY`, `ENABLED`, and `DEAD`.
- `ops_state` tracks ownership: `SCX_OPSS_NONE` is owned by SCX core,
  `QUEUEING` is in transit to BPF, `QUEUED` is owned by BPF, and
  `DISPATCHING` is in transit back to SCX. QSEQ bits detect stale dispatches.
- `SCX_CALL_OP*()` wrappers track the locked rq and task arguments so kfuncs can
  validate callback context and subject task authority.
- `do_enqueue_task()`, `enqueue_task_scx()`, `ops_dequeue()`,
  `dequeue_task_scx()`, `yield_task_scx()`, `yield_to_task_scx()`,
  `wakeup_preempt_scx()`, `set_next_task_scx()`, `put_prev_task_scx()`,
  `pick_task_scx()`, `task_tick_scx()`, `select_task_rq_scx()`, and
  `set_cpus_allowed_scx()` are the main `ext_sched_class` operations.
- `DEFINE_SCHED_CLASS(ext)` wires sched_ext into the generic scheduler class
  interface.
- `update_curr_scx()` charges runtime, consumes `p->scx.slice`, updates
  core-sched timestamps on slice exhaustion, and advances the deadline-server
  entity.
- `scx_prio_less()` supplies core-scheduler ordering, using either
  `ops.core_sched_before()` or FIFO-style `p->scx.core_sched_at`.

Dispatch and balancing:

- `direct_dispatch_task`, `mark_direct_dispatch()`, `direct_dispatch()`, and
  `clear_direct_dispatch()` support immediate DSQ insertion from
  `ops.select_cpu()` or `ops.enqueue()` without going through BPF custody.
- `finish_dispatch()` finalizes buffered `scx_bpf_dsq_insert()` requests after
  `ops.dispatch()` returns. It claims a `QUEUED` task via QSEQ and
  `DISPATCHING`, rejects stale dispatches, and routes the task to local,
  global, or user DSQs.
- `flush_dispatch_buf()` drains per-CPU dispatch buffers; `scx_dsp_ctx.cursor`
  is bounded by `ops.dispatch_max_batch`.
- `consume_dispatch_q()` and `consume_global_dsq()` pull from non-local DSQs
  into the current CPU's local DSQ, including remote task migration when
  affinity and online state allow it.
- `dispatch_to_local_dsq()`, `move_remote_task_to_local_dsq()`,
  `move_task_between_dsqs()`, and `unlink_dsq_and_lock_src_rq()` implement the
  lock ordering and `p->scx.holding_cpu` protocol needed to move tasks across
  rqs while racing dequeue.
- `scx_dispatch_sched()` first consumes global DSQs, then bypass DSQs when
  active, then calls `ops.dispatch()` in a bounded loop. It kicks the CPU after
  too many dispatch loops to avoid watchdog starvation.
- `balance_one()` is the central pick-path balancer: it handles CPU acquire,
  keeps runnable previous tasks with remaining slice, consumes local/global/BPF
  dispatch work, and implements `SCX_OPS_ENQ_LAST` fallback behavior.

Deferred work and reenqueue:

- `schedule_deferred()` and `schedule_deferred_locked()` choose balance
  callbacks, wakeup-hook execution, or irq work to run deferred rq work.
- `process_ddsp_deferred_locals()` completes direct dispatches that targeted a
  remote local DSQ and could not be performed under the original rq lock.
- `schedule_dsq_reenq()`, `reenq_local()`,
  `process_deferred_reenq_locals()`, `reenq_user()`, and
  `process_deferred_reenq_users()` requeue tasks from local or user DSQs back
  through `ops.enqueue()`. This supports `SCX_ENQ_IMMED`, explicit kfunc-driven
  reenqueue, and repeated-cycle detection.
- `run_deferred()` is the common rq-locked drain point for deferred direct
  dispatch and reenqueue operations.

Bypass, disable, and lockup handling:

- `scx_bypass()` flips a scheduler and descendants into or out of bypass mode,
  updates per-CPU bypass flags, cycles queued tasks through dequeue/enqueue,
  reschedules CPUs, and enables or disables bypass DSQ dispatch.
- `bypass_lb_cpu()`, `bypass_lb_node()`, and `scx_bypass_lb_timerfn()` balance
  overloaded per-CPU bypass DSQs within NUMA nodes during bypass mode.
- `handle_lockup()`, `scx_rcu_cpu_stall()`, `scx_softlockup()`, and
  `scx_hardlockup()` try to abort a bad scheduler before generic lockup
  handling escalates.
- `scx_claim_exit()`, `scx_disable()`, `scx_disable_irq_workfn()`,
  `scx_disable_workfn()`, and `scx_flush_disable_work()` claim an exit reason,
  mark schedulers aborting, propagate exit to descendants, collect optional
  dumps, and run teardown on the scheduler helper kthread.
- `scx_root_disable()` disables the root scheduler by entering bypass,
  draining sub-schedulers, switching tasks back to their normal classes,
  shutting down cgroup state, disabling static branches, clearing `scx_root`,
  deleting sysfs kobjects, freeing kick-sync arrays, and releasing bypass.
- `scx_sub_disable()` moves tasks from a sub-scheduler back to its parent,
  handles parent init failures, unlinks the child scheduler, invokes
  `ops.sub_detach()` and `ops.exit()`, and removes child sysfs objects.

Enable and lifecycle:

- `scx_alloc_and_add_sched()` allocates a scheduler instance, exit info, DSQ
  hash, per-node global DSQs, per-CPU dispatch/bypass data, helper worker,
  bypass load-balance masks, kobject, and optional sub-scheduler cgroup state.
- `scx_root_enable_workfn()` is the staged root enable path. It allocates kick
  syncs, allocates and links `scx_sched`, calls `ops.init()`, validates flags
  and hotplug sequence, enters bypass, initializes cgroups and all live tasks,
  enables static branches, switches eligible tasks to `ext_sched_class`, leaves
  bypass, marks enabled, emits a uevent, and increments `scx_enable_seq`.
- `scx_sub_enable_workfn()` attaches a scheduler to a cgroup subtree, asks the
  parent through `ops.sub_attach()`, initializes child tasks without losing the
  ability to revert to the parent, then transfers ownership from parent to child.
- `scx_enable()` dispatches root or sub enable work to a FIFO helper so the
  enabling task cannot be starved after switching classes.
- `__scx_init_task()`, `__scx_enable_task()`, `scx_enable_task()`,
  `scx_disable_task()`, `scx_disable_and_exit_task()`,
  `scx_sub_init_cancel_task()`, `scx_pre_fork()`, `scx_fork()`,
  `scx_post_fork()`, `scx_cancel_fork()`, and `sched_ext_dead()` manage task
  preparation, enable/disable callback pairing, fork races, dead tasks, and
  task-list membership.
- `task_should_scx()`, `scx_check_setscheduler()`, `switching_to_scx()`, and
  `switched_from_scx()` integrate sched_ext with policy changes.

Cgroup and sub-scheduler integration:

- Under `CONFIG_EXT_GROUP_SCHED`, `scx_tg_init()`, `scx_tg_online()`,
  `scx_tg_offline()`, `scx_cgroup_can_attach()`, `scx_cgroup_move_task()`,
  `scx_cgroup_cancel_attach()`, `scx_group_set_weight()`,
  `scx_group_set_idle()`, and `scx_group_set_bandwidth()` mirror cgroup
  lifecycle and CPU controller settings into BPF callbacks.
- `scx_cgroup_init()` and `scx_cgroup_exit()` bulk-initialize and exit all
  online task groups while loading/unloading a scheduler.
- Under `CONFIG_EXT_SUB_SCHED`, `scx_parent()`,
  `scx_next_descendant_pre()`, `scx_find_sub_sched()`, `set_cgroup_sched()`,
  `find_parent_sched()`, and `scx_cgroup_lifetime_notify()` maintain the
  hierarchy of schedulers attached to cgroup subtrees and shoot down a
  scheduler when its cgroup goes offline.

BPF `struct_ops` and kfuncs:

- `bpf_sched_ext_ops` registers `sched_ext_ops` as a BPF `struct_ops` type.
  `bpf_scx_reg()` calls `scx_enable()`, `bpf_scx_unreg()` disables the scheduler
  and clears `ops->priv`, and `bpf_scx_update()` rejects live updates.
- `bpf_scx_is_valid_access()` and `bpf_scx_btf_struct_access()` restrict BPF
  access to callback context and writable task fields. Direct writes to
  `p->scx.slice` and `p->scx.dsq_vtime` are accepted only for compatibility and
  warn in favor of kfuncs.
- `bpf_scx_init_member()` validates copied `sched_ext_ops` data fields such as
  flags, name, timeout, dump length, hotplug sequence, dispatch batch size, and
  sub-cgroup id.
- `bpf_scx_check_member()` rejects sleepable programs for non-sleepable
  callbacks and requests a private stack for dispatch recursion when
  sub-schedulers are enabled.
- `scx_bpf_dsq_insert___v2()`, legacy `scx_bpf_dsq_insert()`,
  `__scx_bpf_dsq_insert_vtime()`, and legacy `scx_bpf_dsq_insert_vtime()`
  insert tasks into FIFO or vtime-ordered DSQs from enqueue/select/dispatch
  contexts.
- `scx_bpf_dispatch_nr_slots()`, `scx_bpf_dispatch_cancel()`,
  `scx_bpf_dsq_move_to_local___v2()`, legacy
  `scx_bpf_dsq_move_to_local()`, `scx_bpf_dsq_move_set_slice()`,
  `scx_bpf_dsq_move_set_vtime()`, `scx_bpf_dsq_move()`,
  `scx_bpf_dsq_move_vtime()`, and `scx_bpf_sub_dispatch()` make up the dispatch
  kfunc set.
- `scx_bpf_reenqueue_local()` is exposed only for `ops.cpu_release()`.
- `scx_bpf_create_dsq()` creates BPF user DSQs in sleepable contexts and
  inserts them into the scheduler hash table.
- `scx_bpf_task_set_slice()`, `scx_bpf_task_set_dsq_vtime()`,
  `scx_bpf_kick_cpu()`, `scx_bpf_dsq_nr_queued()`, and
  `scx_bpf_destroy_dsq()` are the first generic kfuncs in the `any` group; this
  chunk ends before the rest of that group is defined and registered.

System integration:

- Sysfs global attributes expose `state`, `switch_all`, `nr_rejected`,
  `hotplug_seq`, and `enable_seq`; per-scheduler attributes expose `ops` and
  event counters.
- SysRq `S` disables sched_ext and reverts tasks; SysRq `D` dumps scheduler
  state for every linked scheduler.
- `print_scx_info()` prints the enabled scheduler and task-specific SCX state
  during generic task diagnostics.
- `scx_pm_handler()` enters bypass before suspend/hibernate/restore and exits
  bypass after PM completion.
- `init_sched_ext_class()` initializes local DSQs, rq lists, cpumasks, irq
  work, sysrq keys, watchdog work, idle masks, and optional scheduler hash
  structures during scheduler-class initialization.

## Control Flow

The normal wake/enqueue path starts in `select_task_rq_scx()` for wakeups. If
`ops.select_cpu()` exists and the scheduler is not bypassing, the BPF program
chooses a CPU and may direct-dispatch by calling `scx_bpf_dsq_insert()`. If not,
the default idle picker in `ext_idle.c` may select an idle CPU and set up a
direct local dispatch. The generic scheduler then calls `enqueue_task_scx()`,
which marks the task runnable, calls `ops.runnable()`, starts the deadline
server if needed, and delegates to `do_enqueue_task()`.

`do_enqueue_task()` decides where the task goes. Internal restores and sticky
CPU moves go straight to the local DSQ. Offline rq, bypass mode, exiting tasks,
migration-disabled tasks, or missing `ops.enqueue()` fall back to local,
bypass, or per-node global DSQs. Otherwise it enters `SCX_OPSS_QUEUEING`, calls
`ops.enqueue()`, allows direct dispatch through the per-CPU
`direct_dispatch_task` marker, and leaves the task either in a DSQ or in BPF
custody as `SCX_OPSS_QUEUED`.

The pick path goes through `pick_task_scx()` and `do_pick_task_scx()`.
`balance_one()` may keep the previous SCX task if it is still runnable with a
slice, consume local/global/bypass DSQs, or invoke `ops.dispatch()` through
`scx_dispatch_sched()`. BPF dispatch inserts are buffered during
`ops.dispatch()` and finalized by `flush_dispatch_buf()` after the callback
returns. Once a task is selected, `set_next_task_scx()` removes it from DSQ and
runnable accounting, calls `ops.running()`, updates nohz tick state, and allows
the task to run until its slice is consumed, it blocks, or a higher class
preempts it.

The dequeue path uses `dequeue_task_scx()` and `ops_dequeue()`. It clears
runnable state, synchronizes against `QUEUEING` and `DISPATCHING`, calls
`ops.dequeue()` only when the task is still in BPF custody, emits
`ops.stopping()` and `ops.quiescent()` as appropriate, updates rq runnable
counts, removes the task from DSQs, and clears stale direct-dispatch state.

Moving a task to another CPU's local DSQ is the most delicate flow. If a task is
already in a non-local DSQ, `unlink_dsq_and_lock_src_rq()` unlinks it under the
DSQ lock, marks `holding_cpu`, drops the DSQ lock, locks the source rq, and
checks whether dequeue won the race. If a task is in `DISPATCHING`,
`dispatch_to_local_dsq()` sets `holding_cpu`, clears `ops_state` with release
ordering to let dequeue proceed, then switches rq locks. In both cases,
`move_remote_task_to_local_dsq()` performs a deactivate/set_cpu/activate cycle
and passes SCX-specific enqueue flags through `rq->scx.extra_enq_flags`.

Enable is deliberately staged. `scx_enable()` queues work to a FIFO helper.
Root enable allocates and links a scheduler, publishes `scx_root` under CPU
read lock, calls `ops.init()`, validates the hotplug sequence and flags, enters
bypass, blocks forks and cgroup movement, initializes cgroups and all existing
tasks, then enables the static branch and switches eligible tasks into
`ext_sched_class`. Only after tasks are switched does it leave bypass and mark
the state `SCX_ENABLED`. Sub-scheduler enable follows a similar pattern for a
cgroup subtree, but first asks the parent through `ops.sub_attach()` and keeps
tasks initialized for both parent and child until the transfer can be committed.

Disable starts from `scx_exit()`, `scx_error()`, SysRq, BPF unregister, lockup
handlers, PM/cgroup events, or parent propagation. `scx_claim_exit()` marks
the scheduler aborting and recursively propagates parent exits to descendants.
The irq-work stage optionally captures dumps and queues helper work. Root
disable enters bypass, drains descendants, disables cgroup callbacks, locks out
forks, switches every tracked task back to its regular scheduler class, exits
tasks, disables static branches, flushes RCU, removes sysfs/kobjects, clears
`scx_root`, frees kick-sync arrays, and exits bypass. Sub-scheduler disable
instead migrates tasks back to the parent scheduler and unlinks the child.

Bypass mode is both a recovery and transition mechanism. It increments bypass
depth on a scheduler and descendants, enables bypass DSQ consumption on the
nearest host, updates per-CPU bypass flags, cycles runnable tasks through
scheduler dequeue/enqueue so they land in bypass DSQs, and reschedules CPUs.
While bypassing, BPF `select_cpu`, `enqueue`, `dispatch`, custom core ordering,
and kicks are suppressed or ignored, and tasks run with a short default slice.
A timer load-balances bypass DSQs to reduce stalls caused by skewed queues.

Kfunc calls first recover the calling scheduler through `scx_prog_sched(aux)`
or root fallback for compatibility. Insert kfuncs validate task authority,
enqueue flags, and batch capacity, then either mark direct dispatch or append a
dispatch buffer entry. Move kfuncs operate through DSQ iterators and apply
optional slice/vtime overrides before calling the same DSQ transfer helpers used
by the core. Kick kfuncs set per-rq CPU masks and defer lock-heavy work to irq
work.

## State And Persistence Behavior

Most state is in-memory kernel scheduler state. There is no disk persistence in
this chunk.

Persistent runtime state includes:

- Global enable state, static keys, scheduler instance lists, root pointer,
  hotplug/enable/reject counters, watchdog timestamp/interval, and sysfs
  objects.
- Each `struct scx_sched`: copied BPF ops, op bitmap, DSQ hash, per-node global
  DSQs, per-CPU scheduler state, bypass depth/timestamps, exit info/dump
  buffers, helper worker, timer, kobject, and optional sub-scheduler hierarchy.
- Per-task `p->scx`: task state flags, task scheduler pointer, DSQ membership,
  runnable list node, slice, vtime, weight, direct-dispatch verdict, selected
  CPU, sticky/holding CPU, cgroup move state, and BPF ownership state.
- Per-rq `rq->scx`: local DSQ, runnable list, deferred direct dispatch and
  reenqueue lists, kick masks, kick-sync sequence, CPU released state,
  dispatch/wakeup/balance flags, and event-local bookkeeping.
- DSQ contents and metadata: FIFO list, optional vtime rb-tree, queue count,
  first-task RCU pointer, sequence number, per-CPU deferred reenqueue nodes, and
  user DSQ hash membership.
- Cgroup task-group SCX fields such as weight, bandwidth, idle state, online
  and initialized flags, plus optional `cgroup->scx_sched` pointers for
  sub-scheduler routing.
- BPF `sched_ext_ops->priv` points to the active `scx_sched` and is cleared only
  after disable/unregister completes.

State transitions are protected through a mix of raw rq locks, DSQ locks,
`scx_tasks_lock`, `scx_sched_lock`, `scx_bypass_lock`, `scx_enable_mutex`,
per-CPU rwsems, cgroup locks, RCU, refcounts, irq work, kthread work, and
explicit acquire/release atomics. Important memory ordering appears in
`ops_state` transitions, deferred reenqueue scheduling, kick-sync waiting, and
RCU-published scheduler/DSQ pointers.

Sysfs and trace output make some state observable but do not persist it beyond
object lifetime. Scheduler exit info stores a message, backtrace, and dump in
memory until the scheduler kobject is released.

## Dependencies And Integration Points

- Generic scheduler core: rq locks, `sched_class`, enqueue/dequeue flags,
  task policy changes, `activate_task()`, `deactivate_task()`, `set_task_cpu()`,
  wakeup preemption, core scheduling, load averages, deadline server support,
  nohz tick dependencies, and CPU hotplug rq callbacks.
- BPF: `bpf_struct_ops`, BTF kfunc registration, verifier access checks,
  callback sleepability, implicit `bpf_prog_aux`, BPF object-name validation,
  BPF private stack recursion detection, and CFI stubs.
- Cgroups: task groups, cgroup tasksets, `cgroup_lock()`, cgroup lifetime
  notifier, cgroup ids, default hierarchy, cgroup CSS iteration, cgroup CPU
  weight/bandwidth/idle callbacks, and optional subtree-attached schedulers.
- RCU and workqueues: RCU-published scheduler pointers, DSQ first-task pointers,
  delayed watchdog work, irq work for kicks/free/disable, kthread workers for
  enable/disable, and RCU work for scheduler object release.
- CPU topology and hotplug: `cpu_possible`, `cpu_active`, `cpu_online`,
  NUMA nodes, per-node global DSQs, hotplug sequence checks, and idle-selection
  topology from `ext_idle.c`.
- Power management: PM notifier enters bypass while userspace is frozen for
  suspend, hibernation, or restore.
- Diagnostics: tracepoints from `trace/events/sched_ext.h`, SysRq handlers,
  `print_scx_info()`, sysfs attributes, stack traces, and BPF dump callbacks.
- Kernel parameters: `sched_ext.slice_bypass_us` and
  `sched_ext.bypass_lb_intv_us` tune bypass slices and bypass load balancing.

## Risks And Edge Cases

- A BPF scheduler that owns a task in `SCX_OPSS_QUEUED` but never dispatches it
  can stall tasks. The watchdog detects long-runnable tasks and disables the
  scheduler, but detection is delayed by timeout settings.
- Dispatch and dequeue races are subtle. Incorrect release/acquire ordering,
  QSEQ handling, or `holding_cpu` logic can lead to tasks being inserted after
  dequeue, lost tasks, deadlocks, or invalid cross-CPU migration.
- DSQ misuse is guarded but dangerous: mixing FIFO and priority-queue use,
  destroying non-empty DSQs, dispatching to invalid CPU/local DSQs, using
  `SCX_ENQ_IMMED` on non-local DSQs, or overflowing dispatch buffers triggers
  scheduler errors and disable.
- Bypass must work when the BPF scheduler is already misbehaving. It avoids
  sleeping locks where possible, walks possible CPUs instead of online CPUs, and
  suppresses kicks during PM bypass because irq work may not be reliable.
- Root enable has multiple failure points after publishing partial state. The
  code intentionally routes late failures through disable so `ops.exit()` sees
  rich exit info, while early failures unwind allocations directly.
- Sub-scheduler enable/disable has additional failure modes: cgroup going
  offline, parent rejection, parent init failure while migrating child tasks
  back, duplicate task iteration during exit races, and nested bypass-depth
  propagation.
- Task death can race enable or sub-enable between `ops.init_task()` and rq-lock
  reacquisition. `SCX_TASK_INIT_BEGIN`, `SCX_TASK_DEAD`, and
  `SCX_TASK_SUB_INIT` exist to pair owed `exit_task()` callbacks correctly.
- CPU hotplug can race scheduler loading. `ops.hotplug_seq`, CPU read locks,
  and hotplug callbacks limit the race, but a scheduler that cannot handle
  hotplug is deliberately exited.
- `SCX_KICK_WAIT` can deadlock if waiting is done directly in hardirq or while
  holding the wrong rq lock. The implementation defers synchronous waiting to a
  balance callback and keeps advancing the waiter's own `kick_sync`.
- Compatibility kfuncs and deprecated direct writes to `p->scx.slice` and
  `p->scx.dsq_vtime` are temporary ABI risks and are explicitly warned as
  planned removals in future kernel versions.
- Queue length reads use `READ_ONCE()` without full queue locking, so BPF sees
  approximate live counts suitable for policy decisions but not stable proofs.

## Test Signals

Useful validation signals for this chunk include:

- Loading and unloading a simple sched_ext BPF scheduler, verifying sysfs
  `state`, `switch_all`, `enable_seq`, per-scheduler `ops`, and event counters.
- Exercising both full switch-all mode and `SCX_OPS_SWITCH_PARTIAL` with
  `SCHED_EXT` policy transitions, task fork/exit, and failed fork cleanup.
- Stressing enqueue/dequeue races with affinity changes, priority changes,
  migration-disabled tasks, exiting tasks, and `sched_setaffinity()` while tasks
  sit in BPF/user/global/local DSQs.
- Testing DSQ APIs: FIFO insert, vtime insert, dispatch batch limits,
  dispatch cancel, move-to-local, iterator move, user DSQ create/destroy,
  invalid DSQ ids, invalid CPU ids, and non-empty destroy rejection.
- Forcing `SCX_ENQ_IMMED`, higher-class preemption, and repeated local
  reenqueues; watch `SCX_EV_REENQ_IMMED` and
  `SCX_EV_REENQ_LOCAL_REPEAT`.
- CPU hotplug while enabling and while enabled; verify `hotplug_seq`, CPU
  online/offline callbacks, and graceful restart exit codes.
- Cgroup attach/move/weight/bandwidth/idle tests under
  `CONFIG_EXT_GROUP_SCHED`, including cancellation paths after
  `cgroup_prep_move()` failure.
- Sub-scheduler attach/detach tests under `CONFIG_EXT_SUB_SCHED`, including
  parent rejection, cgroup offline teardown, and nested bypass behavior.
- Watchdog and lockup tests with an intentionally stalled BPF scheduler; verify
  error exit, dump content, task/rq state, backtrace, and recovery to CFS.
- Suspend/hibernate smoke tests while sched_ext is enabled to confirm PM bypass
  prevents scheduler-dependent userspace freezes from wedging the system.
- SysRq `D` and `S` tests to confirm debug dump and forced disable behavior.
- Kernel selftests and BPF scheduler examples that cover verifier restrictions,
  callback context filters, kfunc availability by callback type, and rejection
  of sleepable programs on non-sleepable callbacks.

## Cross-Chunk Notes

The next chunk starts at line 8986, immediately after the
`scx_bpf_destroy_dsq()` declaration comment block. It should cover the DSQ BPF
iterator constructors/destructors, DSQ peek/reenqueue helpers, BPF exit/error
string formatting, CPU performance kfuncs, cpumask/task/rq query kfuncs, event
aggregation, kfunc id-set registration, context filtering, and `scx_init()`.
The final per-file report should merge this chunk's scheduler lifecycle and DSQ
core with that later BPF helper/registration tail.
