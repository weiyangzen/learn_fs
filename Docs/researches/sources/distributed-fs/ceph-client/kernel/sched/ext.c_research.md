# Research: sources/distributed-fs/ceph-client/kernel/sched/ext.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006052`: lines 1-8985, `Docs/researches/chunks/subset-b-006052_research.md`
- `subset-b-006053`: lines 8986-9953, `Docs/researches/chunks/subset-b-006053_research.md`

## Chunk Research

### subset-b-006052: lines 1-8985

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

### subset-b-006053: lines 8986-9953

# sources/distributed-fs/ceph-client/kernel/sched/ext.c lines 8986-9953

## Scope

This chunk covers the final `sched_ext` implementation range in `kernel/sched/ext.c`. It starts with the BPF dispatch-queue iterator helpers and ends at `scx_init()` registration through `__initcall(scx_init)`.

The code is mostly BPF-facing control-plane surface for sched_ext: kfuncs that let BPF schedulers inspect and manipulate dispatch queues, report errors and dumps, query CPU/task state, adjust CPU performance targets, read scheduler event counters, and obtain task cgroups. It also defines the "any-context" kfunc BTF set, verifier-time kfunc context filtering, and boot-time registration of kfunc sets, struct_ops, PM notifier, and `/sys/kernel/sched_ext`.

## Purpose

The range exposes stable kernel helpers to BPF schedulers while constraining where each helper can be used. It bridges BPF programs to SCX internal state such as `struct scx_sched`, `struct scx_dispatch_q`, runqueues, per-CPU event counters, dump buffers, global cpumasks, and cgroup scheduler state.

The major responsibilities are:

- Iterating user dispatch queues from BPF with `bpf_for_each()` while preserving queue ordering and cursor cleanup.
- Allowing lockless DSQ inspection and asynchronous DSQ re-enqueue requests.
- Formatting BPF-provided strings for graceful exits, fatal errors, and debug dump output.
- Providing BPF scheduler introspection helpers for CPU capacity/frequency, CPU count, NUMA node count, cpumasks, task CPU/running state, current tasks, locked runqueues, scheduler time, and aggregated SCX events.
- Returning stable scheduler cgroups for tasks when cgroup scheduling is enabled.
- Publishing the final `scx_kfunc_ids_any` BTF kfunc set and filtering all SCX kfunc calls according to BPF program type and attached `sched_ext_ops` member.
- Initializing the sched_ext BPF surface, idle tracking, struct_ops registration, PM notifications, and sysfs directory at kernel init time.

## Important APIs, Types, and Functions

- `bpf_iter_scx_dsq_new()` initializes an opaque BPF iterator for a user DSQ. It verifies kernel/private iterator layout assumptions with `BUILD_BUG_ON()`, clears `kit->dsq` so `next()` and `destroy()` are safe after failed creation, resolves the active scheduler with `scx_prog_sched(aux)`, rejects unsupported flags, looks up the DSQ with `find_user_dsq()`, and seeds the cursor with `INIT_DSQ_LIST_CURSOR()`.
- `bpf_iter_scx_dsq_next()` returns the next queued `task_struct` by taking the DSQ raw spinlock and calling `nldsq_cursor_next_task()`. The lower-level cursor implementation only exposes tasks that were already queued when the cursor was initialized.
- `bpf_iter_scx_dsq_destroy()` removes the cursor node from the DSQ list if still linked, under the DSQ raw spinlock, and clears `kit->dsq`.
- `scx_bpf_dsq_peek()` returns `rcu_dereference(dsq->first_task)` for a user DSQ. It rejects builtin DSQs and non-existent DSQs with `scx_error()` because a lockless peek on local/global builtin queues is not supported here.
- `scx_bpf_dsq_reenq()` validates `SCX_REENQ_*` flags, defaults no filter bits to `SCX_REENQ_ANY`, resolves a local/user DSQ through `find_dsq_for_dispatch()`, and schedules asynchronous re-enqueue processing with `schedule_dsq_reenq()`.
- `scx_bpf_reenqueue_local___v2()` is the current generic wrapper for re-enqueueing the caller CPU's local DSQ via `scx_bpf_dsq_reenq(SCX_DSQ_LOCAL, 0, aux)`. The older `scx_bpf_reenqueue_local()` in the previous chunk is limited to `ops.cpu_release()`.
- `__bstr_format()` is the shared string formatter for BPF string helpers. It validates packed varargs size, copies arguments with `copy_from_kernel_nofault()`, prepares binary printf data with `bpf_bprintf_prepare()`, writes into a fixed line buffer with `bstr_printf()`, and reports failures through `scx_error()`.
- `bstr_format()` specializes `__bstr_format()` for `struct scx_bstr_buf`.
- `scx_bpf_exit_bstr()` formats a BPF message under `scx_exit_bstr_buf_lock` and calls `scx_exit(..., SCX_EXIT_UNREG_BPF, exit_code, ...)` to request graceful scheduler unregister.
- `scx_bpf_error_bstr()` uses the same serialized format buffer but exits with `SCX_EXIT_ERROR_BPF`, treating the BPF scheduler condition as fatal.
- `scx_bpf_dump_bstr()` appends formatted BPF scheduler dump text into `scx_dump_data.buf.line`, validates that it is called on the dump CPU, and flushes through `ops_dump_flush()` when the buffer fills or reaches a newline.
- `scx_bpf_cpuperf_cap()` and `scx_bpf_cpuperf_cur()` return architecture-provided CPU capacity and current frequency capacity, falling back to `SCX_CPUPERF_ONE` when there is no active scheduler or the CPU is invalid.
- `scx_bpf_cpuperf_set()` validates a target performance value, checks CPU validity, avoids ABBA deadlocks by refusing remote CPU changes while another rq is locked, optionally locks the target rq, updates `rq->scx.cpuperf_target`, and calls `cpufreq_update_util()`.
- `scx_bpf_nr_node_ids()` and `scx_bpf_nr_cpu_ids()` expose kernel topology limits to BPF.
- `scx_bpf_get_possible_cpumask()`, `scx_bpf_get_online_cpumask()`, and `scx_bpf_put_cpumask()` provide trusted global cpumask pointers for BPF verifier acquire/release semantics. `put` is intentionally empty because the masks are global and not actually refcounted.
- `scx_bpf_task_running()` and `scx_bpf_task_cpu()` expose task runtime state using `task_rq(p)->curr == p` and `task_cpu(p)`.
- `scx_bpf_cpu_rq()` returns `cpu_rq(cpu)` after scheduler and CPU validation, but emits a one-time deprecation warning through `sch->warned_deprecated_rq`.
- `scx_bpf_locked_rq()` returns `scx_locked_rq()` only when SCX currently holds an rq lock; otherwise it reports an SCX error and returns `NULL`.
- `scx_bpf_cpu_curr()` returns a remote CPU's current task through `rcu_dereference(cpu_rq(cpu)->curr)` after active scheduler and CPU validation.
- `scx_bpf_now()` gives BPF schedulers a fast per-CPU scheduler clock. With preemption disabled, it uses cached `rq->scx.clock` when `SCX_RQ_CLK_VALID` is set, otherwise reads `sched_clock_cpu(cpu_of(rq))`.
- `scx_read_events()` aggregates per-CPU `struct scx_event_stats` from `sch->pcpu` into one system-wide result with `scx_agg_event()` for the enumerated `SCX_EV_*` counters.
- `scx_bpf_events()` RCU-reads `scx_root`, returns zeroed counters if sched_ext is inactive, and copies only `min(events__sz, sizeof(*events))` bytes to tolerate BPF programs built against different `vmlinux.h` layouts.
- `scx_bpf_task_cgroup()` is compiled under `CONFIG_CGROUP_SCHED`. It validates the BPF scheduler context and task authority with `scx_kf_arg_task_ok()`, returns the task scheduler cgroup from `p->sched_task_group`, and always takes a cgroup reference with `cgroup_get()`.
- `scx_kfunc_ids_any` is the final BTF kfunc ID set for helpers allowed broadly across SCX contexts, tracing, and syscall test programs. It includes DSQ observation/re-enqueue, BPF iterators, exit/error/dump strings, CPU performance helpers, topology/cpumask helpers, task/CPU/rq helpers, clock/event helpers, and optionally task cgroup access.
- `enum scx_kf_allow_flags` and `scx_kf_allow_flags[]` define verifier-time permissions for context-sensitive kfunc groups by `sched_ext_ops` member.
- `scx_kfunc_context_filter()` is the central BPF verifier filter. It identifies which SCX kfunc set contains the target kfunc, permits or denies by BPF program type, handles early verification before `prog->aux->st_ops` is populated, rejects non-SCX struct_ops, and finally checks the attached op's allow flags.
- `scx_init()` registers all SCX kfunc sets, initializes idle tracking, registers `bpf_sched_ext_ops`, registers the PM notifier, creates `/sys/kernel/sched_ext`, and installs the global sysfs attribute group.

Key state carriers referenced in this chunk include `struct scx_sched`, `struct scx_dispatch_q`, `struct bpf_iter_scx_dsq_kern`, `struct bpf_iter_scx_dsq`, `struct scx_dsq_list_node`, `struct scx_bstr_buf`, `struct scx_dump_data`, `struct scx_event_stats`, `struct scx_sched_pcpu`, `struct rq`, `struct task_struct`, `struct task_group`, `struct cgroup`, `struct bpf_prog`, `struct bpf_prog_aux`, and `struct btf_kfunc_id_set`.

## Control Flow

DSQ iterator creation starts from a BPF-visible `struct bpf_iter_scx_dsq`. The kernel casts it to `struct bpf_iter_scx_dsq_kern`, proves that the hidden kernel layout fits the opaque BPF layout, initializes the iterator as failed-safe, and then binds it to a user DSQ if the calling BPF program has an active `struct scx_sched`. Iteration steps take the DSQ lock, advance the cursor through `nldsq_cursor_next_task()`, and return one task at a time. Destruction is called regardless of creation success, so both `new()` and `destroy()` are defensive around `kit->dsq == NULL`.

DSQ observation and re-enqueue have different consistency models. `scx_bpf_dsq_peek()` is explicitly lockless and returns only a point-in-time first-task pointer for user DSQs. `scx_bpf_dsq_reenq()` instead schedules deferred work: it disables preemption for stable current-CPU/rq assumptions, validates flags, resolves the DSQ, and delegates to `schedule_dsq_reenq()`. The deferred path records local or user DSQ re-enqueue requests in per-rq lists and kicks deferred processing, avoiding direct queue walking from arbitrary BPF call contexts.

The BPF string helpers run through a shared formatting pipeline. `__bstr_format()` treats the BPF-supplied data as packed 64-bit varargs, rejects misaligned or oversized argument blocks, copies the data through nofault kernel reads, prepares the format with the BPF bprintf machinery, writes into a bounded line buffer, and cleans up temporary printf state. Exit and error helpers serialize access to the global `scx_exit_bstr_buf` before calling `scx_exit()`. Dump helpers use the per-dump `scx_dump_data` buffer, append at `dd->cursor`, and flush through `ops_dump_flush()` on newline or overflow.

CPU performance helpers first establish scheduler and CPU validity. Read helpers simply return architecture capacity/frequency scale values. The setter additionally handles lock ordering: if an SCX callback already holds an rq lock, it only allows setting the same rq's target to avoid cross-rq ABBA deadlocks. Without an existing locked rq, it locks the target rq, updates the rq clock, writes `rq->scx.cpuperf_target`, notifies schedutil via `cpufreq_update_util()`, and unlocks.

Topology, cpumask, task, and rq helpers are small read paths but carry verifier and locking assumptions. Cpumask getters use BPF acquire/release annotations even though the returned masks are immutable globals. `scx_bpf_locked_rq()` requires an SCX-held rq lock and emits an SCX error otherwise. `scx_bpf_cpu_curr()` is RCU-protected to safely read a remote rq's `curr`. `scx_bpf_now()` disables preemption so `this_rq()` and the cached rq clock belong to a stable CPU for the whole read.

Event aggregation flows from BPF into `scx_bpf_events()`, then under RCU to the current root scheduler. If `scx_root` is present, `scx_read_events()` walks all possible CPUs and aggregates the explicitly listed event counters from each `sch->pcpu`. If not, the output is zeroed. The final copy is size-clamped so BPF-side ABI size drift cannot corrupt memory.

Cgroup lookup under `CONFIG_CGROUP_SCHED` reads the scheduler's task-group view rather than the generic task cgroup pointer. The function defaults to the root cgroup, validates scheduler/task authority, selects `tg_cgrp(p->sched_task_group)` when allowed, takes a reference, and returns a non-NULL cgroup pointer to BPF.

Verifier filtering starts by classifying the kfunc ID against all SCX BTF sets: unlocked, select_cpu, enqueue/dispatch, dispatch, cpu_release, idle, and any. Non-SCX kfuncs are allowed. `BPF_PROG_TYPE_SYSCALL` can call unlocked, select_cpu, idle, and any helpers, which supports BPF test-run style programs. Non-struct_ops programs can only call always-safe `any` or idle helpers. SCX struct_ops programs are allowed through if the target kfunc is in `any` or idle; otherwise the attached struct_ops member offset indexes `scx_kf_allow_flags[]`, and the matching bit must allow the context-sensitive set.

Initialization is ordered around BPF visibility. `scx_init()` first registers all kfunc ID sets needed by verifier lookup, then initializes idle tracking, then registers `sched_ext_ops` as BPF struct_ops. Only after that does it register PM notifications and create the `/sys/kernel/sched_ext` kset and global sysfs group. Failures return immediately with `pr_err()` and prevent later initialization stages from publishing partial interfaces.

## State and Persistence Behavior

DSQ iterator state is temporary and owned by the BPF iterator object. The hidden kernel state stores a cursor node, target DSQ pointer, and optional slice/vtime fields used by DSQ move helpers defined earlier. Cursor list linkage persists across `next()` calls and is removed by either iteration exhaustion or `destroy()`.

`struct scx_dispatch_q` state is persistent while the scheduler and its custom DSQs live. This chunk reads `dsq->first_task`, `dsq->nr`, `dsq->lock`, and list/cursor state. It does not create DSQs, but it can trigger deferred re-enqueue processing for local and user DSQs.

`scx_exit_bstr_buf` is a single global formatting buffer protected by `scx_exit_bstr_buf_lock`. It persists for module lifetime and serializes BPF exit/error message formatting to avoid concurrent helper calls corrupting the shared line/data buffers.

`scx_dump_data` is a global dump-session carrier. Earlier dump setup marks the dump CPU and initializes cursor/prefix/seq buffer fields; this chunk's dump kfunc appends into it and flushes lines. The dump CPU gate prevents arbitrary CPUs from writing into an active dump session.

CPU performance target state persists in `rq->scx.cpuperf_target` until overwritten. Reads of CPU capacity/frequency are transient architecture queries; `cpufreq_update_util()` integrates the target with schedutil/cpufreq state outside this file.

The global cpumask helpers return persistent kernel masks, not dynamically allocated references. The BPF verifier's acquire/release model is simulated so BPF can treat the pointers as trusted while kernel memory management remains unchanged.

Event counters persist per scheduler per CPU in `sch->pcpu[*].event_stats`. `scx_bpf_events()` creates a stack aggregate and copies it to BPF without mutating the source counters.

`scx_kfunc_ids_any`, the context-sensitive kfunc ID sets from earlier chunks, `scx_kf_allow_flags[]`, and `scx_kfunc_context_filter()` are long-lived registration metadata used by the BPF verifier after `scx_init()`. They do not change at runtime.

`scx_kset` persists after successful init as the `/sys/kernel/sched_ext` kset. The global sysfs attribute group installed in this chunk exposes sched_ext state and control files defined earlier in the source.

## Dependencies and Integration Points

- BPF kfunc infrastructure: `__bpf_kfunc`, `__bpf_kfunc_start_defs()`, `__bpf_kfunc_end_defs()`, `BTF_KFUNCS_START/END`, `BTF_ID_FLAGS`, kfunc flags such as `KF_IMPLICIT_ARGS`, `KF_RCU`, `KF_RCU_PROTECTED`, `KF_RET_NULL`, `KF_ITER_NEW/NEXT/DESTROY`, `KF_ACQUIRE`, and `KF_RELEASE`, and `register_btf_kfunc_id_set()`.
- BPF struct_ops integration: `bpf_sched_ext_ops`, `sched_ext_ops`, `register_bpf_struct_ops()`, `BPF_PROG_TYPE_STRUCT_OPS`, `prog->aux->st_ops`, and `prog->aux->attach_st_ops_member_off`.
- BPF verifier and test-run integration: `BPF_PROG_TYPE_SYSCALL`, `BPF_PROG_TYPE_TRACING`, `btf_id_set8_contains()`, and the early verification pass where `prog->aux->st_ops` is not yet set.
- DSQ internals: `find_user_dsq()`, `find_dsq_for_dispatch()`, `nldsq_cursor_next_task()`, `INIT_DSQ_LIST_CURSOR()`, DSQ locks, DSQ list nodes, `SCX_DSQ_*` IDs, and deferred re-enqueue helpers.
- Scheduler/runqueue state: `this_rq()`, `cpu_rq()`, `task_rq()`, `scx_locked_rq()`, rq locks, `rq->scx.clock`, `rq->scx.flags`, `SCX_RQ_CLK_VALID`, and `rq->scx.cpuperf_target`.
- CPU and topology APIs: `ops_cpu_valid()`, `nr_cpu_ids`, `nr_node_ids`, `cpu_possible_mask`, `cpu_online_mask`, `arch_scale_cpu_capacity()`, `arch_scale_freq_capacity()`, `sched_clock_cpu()`, and `smp_processor_id()`.
- cpufreq/schedutil integration: `cpufreq_update_util()` is invoked when BPF changes the SCX CPU performance target.
- Exit and dump machinery: `scx_exit()`, `scx_error()`, `SCX_EXIT_UNREG_BPF`, `SCX_EXIT_ERROR_BPF`, `ops_dump_flush()`, `dump_line()`, and the dump setup/teardown logic earlier in `ext.c`.
- BPF string formatting internals: `copy_from_kernel_nofault()`, `bpf_bprintf_prepare()`, `bstr_printf()`, `bpf_bprintf_cleanup()`, `MAX_BPRINTF_VARARGS`, and `SCX_EXIT_MSG_LEN`.
- RCU and locking: `guard(rcu)`, `guard(preempt)`, raw spinlocks with IRQ save/restore, `rcu_dereference()`, `smp_load_acquire()`, `READ_ONCE()`, and rq lock helpers.
- Cgroup scheduler integration: `CONFIG_CGROUP_SCHED`, `p->sched_task_group`, `tg_cgrp()`, `cgrp_dfl_root`, `cgroup_get()`, and `scx_kf_arg_task_ok()`.
- Subsystem init: `scx_idle_init()`, `register_pm_notifier(&scx_pm_notifier)`, `kset_create_and_add()`, `scx_uevent_ops`, `kernel_kobj`, `sysfs_create_group()`, and `scx_global_attr_group`.

## Risks and Edge Cases

- BPF iterator cleanup must be correct after both successful and failed `new()`. The BPF iterator contract calls `next()` and `destroy()` regardless of `new()` result, so `kit->dsq` must be initialized to `NULL` before any failure path.
- The opaque BPF iterator ABI depends on `struct bpf_iter_scx_dsq_kern` fitting inside `struct bpf_iter_scx_dsq` with matching alignment. Any future hidden-state expansion must preserve these compile-time checks or deliberately change the BPF ABI.
- DSQ iteration intentionally excludes tasks enqueued after iterator creation. Changing cursor sequencing or list movement could expose newly queued tasks, loop indefinitely, or make virtual-time iteration appear to move backward.
- `scx_bpf_dsq_peek()` is lockless and can return a stale snapshot. BPF schedulers must not assume the returned task remains queued or first by the time a later locked operation runs.
- `scx_bpf_dsq_peek()` treats invalid use as scheduler errors for builtin or missing DSQs. A BPF scheduler probing IDs without care can self-disable through `scx_error()`.
- `scx_bpf_dsq_reenq()` uses `find_dsq_for_dispatch()`, which falls back to a global DSQ after reporting some invalid dispatch targets. That behavior is appropriate for dispatch verdicts but should be understood by callers expecting a hard failure for every bad DSQ ID.
- Re-enqueue scheduling is blocked while bypass depth is nonzero. BPF logic that relies on reenqueues during PM or disable bypass may observe no effect.
- The string helpers format under raw spinlocks for exit/error. Formatting work must remain bounded and non-sleeping; adding sleepable operations there would be invalid.
- BPF-provided string varargs are copied from kernel memory with nofault semantics. Incorrect `data__sz` validation would risk bad reads or formatting corruption, so size, alignment, and NULL checks are security relevant.
- `scx_bpf_dump_bstr()` is CPU-affine to the active dump CPU. Calling it from any other context is treated as an SCX error, which can turn a diagnostic misuse into scheduler disablement.
- `scx_bpf_cpuperf_set()` must preserve rq lock ordering. Allowing remote rq changes while a different rq is locked would risk ABBA deadlock in scheduler callbacks.
- `scx_bpf_cpu_rq()` is deprecated because returning raw remote rq pointers is easy to misuse. New code should prefer `scx_bpf_locked_rq()` for locked local rq access or `scx_bpf_cpu_curr()` for remote current-task reads.
- `scx_bpf_now()` is only monotonic non-decreasing for calls on the same CPU. BPF schedulers comparing timestamps across CPUs can still observe time going backward.
- `scx_bpf_events()` intentionally clamps output size. New fields added to `struct scx_event_stats` will be silently omitted for older BPF programs, and zero-filled/missing fields should be handled in user space.
- `scx_bpf_task_cgroup()` returns a referenced cgroup even on fallback to root. BPF callers must pair it with the expected release path or leak verifier-tracked references.
- `scx_kfunc_context_filter()` indexes `scx_kf_allow_flags[]` by attached struct_ops member offset. The table must remain synchronized with `struct sched_ext_ops` op indices and context-sensitive BTF sets; missing an op entry denies its context-sensitive helpers.
- The verifier filter deliberately allows all SCX kfuncs during an early pass before `st_ops` is set, expecting a later verifier pass to enforce restrictions. If BPF core behavior changes, this may need revisiting.
- `scx_init()` has no cleanup for some earlier successful registration steps if a later stage fails. That follows common initcall assumptions but means partial init failure paths should be scrutinized if sched_ext becomes unloadable or retryable.

## Test Signals

- BPF iterator tests should cover successful user DSQ iteration, reverse iteration, invalid flags returning `-EINVAL`, missing scheduler returning `-ENODEV`, missing DSQ returning `-ENOENT`, `next()` after failed `new()`, and `destroy()` after partial iteration.
- Iterator ordering tests should enqueue tasks before and after iterator creation and verify that only the pre-existing tasks are returned.
- DSQ peek tests should cover user DSQ first-task snapshots, empty DSQs returning `NULL`, builtin DSQ rejection, missing DSQ rejection, and RCU-safe use from BPF contexts with `KF_RCU_PROTECTED`.
- Re-enqueue tests should validate defaulting zero filter flags to `SCX_REENQ_ANY`, rejection of invalid flags, local DSQ re-enqueue, `SCX_DSQ_LOCAL_ON | cpu`, user DSQ re-enqueue, builtin unsupported DSQ errors, and no-op behavior while bypassing.
- Exit/error string tests should cover valid formatted messages, misaligned `data__sz`, oversized varargs, NULL data with nonzero size, invalid format preparation, nofault copy failure, graceful `SCX_EXIT_UNREG_BPF`, and fatal `SCX_EXIT_ERROR_BPF`.
- Dump tests should cover calls only from `ops.dump()`/`dump_cpu()`/`dump_task()` on the configured CPU, multi-call line assembly, newline flushing, buffer overflow flushing, and formatting failure diagnostic output.
- CPU performance tests should cover valid capacity/current reads, invalid CPUs falling back to `SCX_CPUPERF_ONE`, rejecting `perf > SCX_CPUPERF_ONE`, same-rq updates while rq lock is held, remote-rq rejection while another rq is locked, unlocked remote updates, and observable schedutil target changes.
- Topology/cpumask tests should verify `nr_cpu_ids`, `nr_node_ids`, possible/online cpumask acquire/release verifier behavior, and safe reads across CPU hotplug.
- Task/rq helper tests should cover running versus queued/sleeping tasks, task CPU reads under RCU, deprecated `scx_bpf_cpu_rq()` warning only once per scheduler, `scx_bpf_locked_rq()` success under SCX rq lock, and error return without a locked rq.
- Clock tests should verify that repeated `scx_bpf_now()` calls on one CPU do not go backward, use cached rq clock while `SCX_RQ_CLK_VALID` is set, and fall back to `sched_clock_cpu()` outside valid rq-clock windows.
- Event counter tests should cover zero output with no `scx_root`, aggregation across all possible CPUs, each listed `SCX_EV_*` counter, and truncated copy behavior with smaller BPF-side struct sizes.
- Cgroup tests should cover valid task cgroup returns, fallback to root when scheduler/task validation fails, reference acquisition/release, and stability across concurrent cgroup moves as seen through `p->sched_task_group`.
- Verifier tests should cover non-SCX kfunc passthrough, syscall program permissions, tracing program access to `any` helpers, non-SCX struct_ops rejection, early `st_ops == NULL` allowance followed by final enforcement, each `sched_ext_ops` op's allowed kfunc groups, and denial of context-sensitive helpers from unlisted ops.
- Init tests should cover failure injection for each kfunc set registration, `scx_idle_init()`, `register_bpf_struct_ops()`, PM notifier registration, kset creation, and sysfs group creation, plus successful creation of `/sys/kernel/sched_ext`.

## Chunk Boundary Notes

This chunk depends heavily on earlier `ext.c` sections for scheduler enable/disable, DSQ allocation and movement, deferred re-enqueue processing, dump setup, task authority checks, per-CPU event accounting, cgroup scheduler plumbing, and the context-sensitive kfunc sets registered before `scx_kfunc_ids_any`. The final per-file document should merge this chunk with the previous kfunc sections so the BPF scheduler API, verifier restrictions, and init sequence read as one continuous sched_ext control-plane surface.
