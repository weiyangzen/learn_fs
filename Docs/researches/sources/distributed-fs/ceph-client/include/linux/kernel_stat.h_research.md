# sources/distributed-fs/ceph-client/include/linux/kernel_stat.h

## Purpose
Defines per-CPU kernel accounting structures and APIs for CPU time, context switches, interrupts, softirqs, idle time, steal time, and scheduler accounting.

## Important APIs, Types, And Functions
`enum cpu_usage_stat` defines accounting buckets for user, nice, system, softirq, irq, idle, iowait, steal, guest, guest nice, and optional force-idle. `struct kernel_cpustat` stores per-bucket counters; `struct kernel_stat` stores IRQ and softirq counters. Macros access per-CPU `kstat` and `kernel_cpustat`. APIs include context switch counters, IRQ/softirq accessors, snapshot helpers, cputime fetch helpers, account_* functions, idle time retrieval, and process tick accounting.

## Control Flow
Interrupt and scheduler paths increment per-CPU counters. Readers fetch per-CPU or aggregated values, with virtual CPU accounting builds using helper functions to flush or synthesize precise values. Native vtime builds account process ticks by flushing virtual time.

## State And Persistence
State is per-CPU counters since boot. It is not persistent and can be read by procfs, scheduler, and monitoring paths.

## Dependencies And Integration Points
Depends on SMP, percpu, interrupt, scheduler, vtime, thread, and architecture IRQ definitions. Integrates with `/proc/stat`, scheduler accounting, irq accounting, virtualization steal/guest time, and core scheduling force-idle stats.

## Risks
Per-CPU direct access requires preemption disabled for meaningful current-CPU results. Counter readers must account for virtual CPU accounting modes. Optional fields change `NR_STATS` under `CONFIG_SCHED_CORE`.

## Test Signals
Signals include `/proc/stat` accounting, interrupt/softirq counters, context switch totals, vtime configurations, idle/iowait accounting, steal/guest time tests, and preemption-sensitive per-CPU access checks.
