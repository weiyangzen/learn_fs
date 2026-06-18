<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stop_task.c -->
# sources/distributed-fs/ceph-client/kernel/sched/stop_task.c

## Purpose
`stop_task.c` implements the scheduler class for per-CPU stop tasks used by `stop_machine` and CPU control paths. Stop tasks are the highest-priority scheduler entities: once runnable they preempt everything else and are not themselves preempted by normal classes.

## Important APIs, Types, And Functions
The file defines the `stop_sched_class` through `DEFINE_SCHED_CLASS(stop)`. Class hooks include `select_task_rq_stop`, `balance_stop`, `wakeup_preempt_stop`, `set_next_task_stop`, `pick_task_stop`, `enqueue_task_stop`, `dequeue_task_stop`, `yield_task_stop`, `put_prev_task_stop`, `task_tick_stop`, `switching_to_stop`, `prio_changed_stop`, and `update_curr_stop`.

## Control Flow
Stop tasks never migrate through this class; `select_task_rq_stop` returns the current task CPU. `pick_task_stop` returns `rq->stop` only when `sched_stop_runnable(rq)` says the stop task is queued. Enqueue/dequeue simply adjusts `rq->nr_running`. `set_next_task_stop` records `exec_start`; `put_prev_task_stop` updates common current-runtime accounting. Yield, switching into the class, and priority changes are treated as impossible and call `BUG()`.

## State And Persistence
The class uses per-runqueue `rq->stop`, `rq->nr_running`, and the stop task's `se.exec_start`. It does not allocate or persist state.

## Dependencies And Integration Points
It depends on `sched.h`, the scheduler class linker ordering, `sched_stop_runnable`, runqueue runnable accounting, `update_curr_common`, `set_cpus_allowed_common`, and the stop-machine infrastructure that creates and wakes per-CPU stop tasks.

## Risks And Edge Cases
This class relies on strong invariants: stop tasks must not yield, change class, change priority, or migrate through normal balancing. Violating those invariants triggers `BUG()` and can panic the kernel. Empty tick/update hooks are intentional because stop tasks are special control threads, but runtime accounting must still be advanced when switching away.

## Test Signals
Signals include CPU hotplug, stop_machine users, active balancing, migration stopper workloads, lockdep during stopper execution, and absence of `BUG()` paths. Build/link ordering should place stop above deadline, RT, fair, and idle classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/stop_task.c -->
