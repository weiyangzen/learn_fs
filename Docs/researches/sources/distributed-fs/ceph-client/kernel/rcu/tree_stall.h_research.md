# sources/distributed-fs/ceph-client/kernel/rcu/tree_stall.h

## Purpose
`tree_stall.h` implements normal tree-RCU CPU stall detection, reporting, panic policy, sysctl/sysfs controls, forward-progress diagnostics, and optional stall notifier chains. It tracks grace-period start and stall deadlines, detects self and remote stalls, prints CPU/task/kthread state, and kicks RCU machinery to recover.

## Important APIs, Types, and Functions
- Controls: sysctls `panic_on_rcu_stall` and `max_rcu_stall_to_panic`, module parameters such as `csd_lock_suppress_rcu_stall` and `sysrq_rcu`, and sysfs `rcu_stall_count`.
- Timeout helpers: `rcu_jiffies_till_stall_check()` and `rcu_exp_jiffies_till_stall_check()` clamp configured timeouts; `record_gp_stall_check_time()` records GP deadlines.
- Suppression and panic: `rcu_sysrq_start()`, `rcu_sysrq_end()`, `rcu_panic()`, `panic_on_rcu_stall()`, and `rcu_cpu_stall_reset()`.
- Detection/reporting: `check_cpu_stall()`, `print_cpu_stall()`, `print_other_cpu_stall()`, `print_cpu_stall_info()`, `rcu_dump_cpu_stacks()`, and `rcu_print_task_stall()`.
- Kthread diagnostics: `rcu_check_gp_kthread_starvation()`, `rcu_check_gp_kthread_expired_fqs_timer()`, `show_rcu_gp_kthreads()`, and `rcu_fwd_progress_check()`.
- Optional notifier API: `rcu_stall_chain_notifier_register()`, `rcu_stall_chain_notifier_unregister()`, and `rcu_stall_notifier_call_chain()`.

## Control Flow
At each grace-period start, `record_gp_stall_check_time()` snapshots `gp_start`, computes `jiffies_stall`, and records force-QS counters. Periodic RCU clock/softirq paths call `check_cpu_stall()`, which first suppresses warnings when requested, rejects false positives using ordered reads of `gp_seq`, `jiffies_stall`, and `gp_start`, and then uses `cmpxchg()` on `jiffies_stall` so only one CPU reports a given stall.

If the current CPU is part of the outstanding `qsmask`, `print_cpu_stall()` emits a self-detected stall. Otherwise, after a rat delay, `print_other_cpu_stall()` reports CPUs and tasks blocking the GP. Both paths print queue length, online CPU count, GP sequence, per-CPU idle/softirq/FQS data, stack traces, GP-kthread starvation information, and optional ftrace dumps, then either force quiescent states or request rescheduling.

For preemptible RCU, blocked task reporting walks `rnp->gp_tasks` through `blkd_tasks`, grabs task references, and optionally calls `sched_show_task()`. Forward-progress checks used by rcutorture call `show_rcu_gp_kthreads()` during active GPs or `rcu_check_gp_start_stall()` when requested GPs fail to start.

## State and Persistence
State is runtime-only in `rcu_state` (`gp_start`, `jiffies_stall`, `gp_activity`, `gp_req_activity`, `gp_flags`, `n_force_qs`, `gp_kthread`, `gp_state`), per-CPU `rcu_data` (`ticks_this_gp`, `softirq_snap`, `rcu_iw_pending`, cputime snapshots), and per-node masks/task pointers. Sysctl and sysfs values persist only as live kernel tunables.

## Dependencies and Integration Points
This file depends on printk/nbcon emergency sections, sysctl, sysfs, panic notifiers, KVM guest pause detection, BPF scheduler stall handling, CSD-lock diagnostics, softirq and IRQ statistics, RCU task and NOCB diagnostics, sysrq, ftrace dumping, and optional stall notifier infrastructure. It integrates with grace-period initialization, FQS loops, scheduler clock paths, rcutorture, and exported debug entry points.

## Risks
Risks include false stall reports from stale jiffies, VM pauses, slow consoles, expired timers, or GP sequence races; the file counters these with memory barriers, suppression flags, KVM pause checks, and deadline rewriting. Diagnostic printing occurs under emergency conditions and must avoid hard lockups while holding RCU-node locks. Panic-on-stall policy can intentionally crash systems, so sysctl bounds and count thresholds matter. Notifier users can suppress or alter warning behavior and are intentionally warned as risky.

## Test Signals
Signals include sysctl clamping behavior, `/sys/kernel/rcu_stall_count`, generated stall warnings, rcutorture forward-progress checks, sysrq `y` dumps when enabled, panic notifier suppression during panic, ftrace dumps on stall, and output from `show_rcu_gp_kthreads()` showing GP state, qsmasks, boost/task blockers, NOCB state, and callback counts.
