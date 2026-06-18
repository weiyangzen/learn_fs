# sources/distributed-fs/ceph-client/arch/powerpc/kernel/watchdog.c

## Purpose
Implements PowerPC hard-lockup watchdog support using per-CPU hrtimer heartbeats, soft-NMI self-detection, and SMP cross-CPU pending-mask detection.

## Important APIs, Types, And Functions
External hooks are `soft_nmi_interrupt`, `arch_touch_nmi_watchdog`, `watchdog_hardlockup_stop`, `watchdog_hardlockup_start`, `watchdog_hardlockup_probe`, and pseries `watchdog_hardlockup_set_timeout_pct`. Internal logic includes `wd_smp_lock`, `wd_try_report`, `wd_end_reporting`, `wd_lockup_ipi`, `watchdog_smp_panic`, `wd_smp_clear_cpu_pending`, `watchdog_timer_interrupt`, `watchdog_timer_fn`, `start_watchdog`, `stop_watchdog`, and `watchdog_calc_timeouts`.

## Control Flow
Each enabled CPU runs a pinned hrtimer heartbeat that updates its timestamp and clears its bit from the global pending mask. When all enabled non-stuck CPUs clear their bits, the last clearer resets the SMP timestamp and refills pending. Soft-NMI interrupts compare the local timebase against the local heartbeat and self-report hard lockups. The hrtimer path also checks whether the global SMP timestamp has expired and reports CPUs whose pending bits remain set, optionally sending NMI IPIs or all-CPU backtraces before panicking.

## State And Persistence
Global state includes enabled CPU masks, pending/stuck masks, watchdog timeouts in timebase ticks, reporting locks, NMI output flush flags, and pseries timeout percentage. Per-CPU state includes hrtimers and last heartbeat timebase values. No durable storage is used.

## Dependencies And Integration Points
Integrates with Linux lockup detector controls, CPU hotplug state, NMI/backtrace APIs, PowerPC timebase/DEC, PACA soft-NMI accounting, sys_info reporting, panic policy, and pseries timeout tuning.

## Risks And Edge Cases
Runs in soft-NMI and hardlockup contexts, so locking and printk are sensitive. Pending-mask races are handled with barriers; regressions can cause false positives or missed lockups. NMI printk requires a later console flush from another CPU. CPU hotplug and stuck/unstuck transitions are tricky.

## Test Signals
Hard-lockup injection with interrupts soft-disabled and hard-disabled, SMP stuck CPU tests, CPU hotplug start/stop tests, all-CPU backtrace and panic policy validation, pseries timeout-factor changes, and stress under heavy printk/NMI load are important.
