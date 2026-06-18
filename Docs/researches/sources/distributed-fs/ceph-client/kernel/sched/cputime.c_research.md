# sources/distributed-fs/ceph-client/kernel/sched/cputime.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cputime.c` implements scheduler CPU-time accounting for user, system, guest, IRQ, softirq, steal, idle, force-idle, tick-based accounting, and virtual CPU accounting modes. It also provides adjusted task and thread-group cputime readers. The file was read as a complete 1100-line source.

## Important APIs, Types, and Functions

IRQ-time accounting is controlled by `sched_clock_irqtime`, `cpu_irqtime`, `enable_sched_clock_irqtime()`, `disable_sched_clock_irqtime()`, `irqtime_account_irq()`, and `irqtime_tick_accounted()`. Core charge APIs are `account_user_time()`, `account_guest_time()`, `account_system_index_time()`, `account_system_time()`, `account_steal_time()`, `account_idle_time()`, and `__account_forceidle_time()`. Tick paths include `account_process_tick()` and `account_idle_ticks()`. Readers/adjusters include `thread_group_cputime()`, `cputime_adjust()`, `task_cputime_adjusted()`, and `thread_group_cputime_adjusted()`. Generic virtual accounting adds `vtime_user_enter/exit()`, `vtime_guest_enter/exit()`, `vtime_task_switch_generic()`, `task_gtime()`, `task_cputime()`, `kcpustat_field()`, and `kcpustat_cpu_fetch()`.

## Control Flow

Runtime accounting classifies elapsed time by execution context. User and guest paths increment task `utime`, group user time, guest time where relevant, and cpustat fields. System time distinguishes hardirq, softirq, normal kernel, and guest VCPU contexts. Tick accounting first subtracts steal and IRQ/softirq time, then charges remaining tick time to user, idle, guest, or system. `thread_group_cputime()` combines dead-thread signal totals with live thread values under RCU and a seqcount-style signal stats lock, refreshing current runtime when querying its own group.

When native virtual accounting is enabled, adjusted readers return raw precise fields. Otherwise `cputime_adjust()` scales tick-derived user/system time to match `sum_exec_runtime` while preserving monotonicity under `prev_cputime::lock`. Generic vtime mode tracks a task state machine (`VTIME_SYS`, `VTIME_USER`, `VTIME_GUEST`, `VTIME_IDLE`, `VTIME_INACTIVE`) using seqcounts and `sched_clock()`, flushing deltas on user/guest transitions and context switches. Kernel cpustat readers fetch pending vtime from the current task on a CPU, retrying if they race with context switch state.

## State and Persistence Behavior

State lives in task fields (`utime`, `stime`, `gtime`, `vtime`, `prev_cputime`), signal/thread-group aggregates, per-CPU `kernel_cpustat`, per-CPU `irqtime`, rq steal-time snapshots, cgroup CPU accounting, and optional schedstats. Counters are in-memory runtime state and monotonic except for task/cgroup lifetime resets.

## Dependencies and Integration Points

The file depends on scheduler clocks, rq state, preempt/IRQ context, paravirt steal clock static calls, cgroup CPU accounting, process accounting, taskstats, seqcounts, RCU, and architecture vtime hooks. It integrates with `cpuacct.c`, `/proc/stat` and task `/proc` readers through `kcpustat_*`, core scheduling through force-idle accounting, and virtualization through guest/steal APIs.

## Risks and Edge Cases

IRQ-time accounting intentionally permits remote readers to race with local IRQ writers, accepting small misattribution to avoid IRQ locks. Tick accounting can account more time than the nominal caller elapsed due to delayed guest/steal clocks. `cputime_adjust()` must preserve monotonic user/system values even when raw tick ratios fluctuate. Vtime readers must retry around context-switch states to avoid double-counting or missing pending time. Nice changes during nohz vtime can make user-vs-nice split approximate.

## Test Signals

Signals include `/proc/stat` and task cputime consistency tests under user/system/guest/irq/softirq/idle workloads; nohz/full-dynticks tests for vtime transitions; KVM guest enter/exit accounting checks; steal-time simulation; cgroup cpuacct hierarchy tests; monotonicity tests for adjusted cputime; and lockdep/KCSAN coverage around seqcount and rq locking.
