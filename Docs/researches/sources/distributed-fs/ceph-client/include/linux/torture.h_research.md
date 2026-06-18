<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/torture.h -->
# sources/distributed-fs/ceph-client/include/linux/torture.h

## Purpose
declares common infrastructure for in-kernel torture tests, especially RCU/locking stress modules: parameter macros, logging, CPU hotplug exercise, randomization, high-resolution timeout fuzzing, task shuffling, shutdown/stutter control, and kthread lifecycle helpers.

## Important APIs, Types, and Functions
The file is 138 lines and exports these visible symbol families: types/enums `torture_random_state`, `torture_ofl_func`; macros/constants `TORTURE_FLAG`; function-like macros `torture_param`, `TOROUT_STRING`, `VERBOSE_TOROUT_STRING`, `TOROUT_ERRSTRING`, `torture_init_error`, `DEFINE_TORTURE_RANDOM`, `DEFINE_TORTURE_RANDOM_PERCPU`, `torture_create_kthread`, `torture_create_kthread_cb`, `torture_stop_kthread`, `torture_preempt_schedule`; inline helpers `torture_num_online_cpus`, `torture_random_init`; external prototypes `verbose_torout_sleep`, `pr_alert`, `torture_num_online_cpus`, `torture_ofl_func`, `torture_offline`, `torture_online`, `torture_onoff_init`, `torture_onoff_stats`, `torture_onoff_failures`, `torture_random`, `torture_hrtimeout_ns`, `torture_hrtimeout_us`, `torture_hrtimeout_ms`, `torture_hrtimeout_jiffies`, and 18 more.

## Control Flow
A torture module calls init-begin/end helpers, creates worker kthreads with macros, optionally starts CPU on/offline, shuffler, stutter, and auto-shutdown facilities, logs through TOROUT macros, and stops through cleanup/must-stop checks.

## State and Persistence Behavior
State is held by torture implementation code in worker tasks, hotplug counters, random states, shutdown timers, stutter state, and global torture type/verbosity settings. `torture_random_state` can be global or per-CPU.

## Dependencies and Integration Points
It depends on modules, cpumasks, completions, hrtimers, spinlocks, seqlocks, debugobjects, threads, lockdep, and optional RCU/lock torture configs. Direct includes are `linux/types.h`, `linux/cache.h`, `linux/spinlock.h`, `linux/threads.h`, `linux/cpumask_types.h`, `linux/seqlock.h`, `linux/lockdep.h`, `linux/completion.h`, `linux/debugobjects.h`, `linux/bug.h`, `linux/compiler.h`, `linux/hrtimer.h`.

## Risks and Edge Cases
Torture code intentionally stresses hotplug, scheduler, timers, and locking; cleanup ordering must reliably stop kthreads and undo hotplug/shuffle state. Logging can be high volume and timing-sensitive.

## Test Signals
Run rcutorture and locktorture scenarios with CPU hotplug, stutter, shuffle, timeout fuzzing, preemption variants, and module/built-in initialization failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/torture.h -->
