# sources/distributed-fs/ceph-client/lib/nmi_backtrace.c

## Purpose
Provides generic NMI-triggered CPU backtrace support for architectures that define `arch_trigger_cpumask_backtrace`. It coordinates cross-CPU stack dumps for lockup diagnostics.

## APIs, Control Flow, and State
The main APIs are `nmi_trigger_cpumask_backtrace()` and `nmi_cpu_backtrace()`. Global state consists of `backtrace_mask`, `backtrace_flag`, and module parameter `backtrace_idle`. The trigger path serializes concurrent dumps, copies the requested CPU mask, optionally excludes one CPU, handles the current CPU locally, invokes the architecture-provided NMI raiser for remaining CPUs, waits up to 10 seconds while touching the softlockup watchdog, performs stall checks, flushes printk buffers, and clears the flag. The CPU callback prints registers or a stack, skips idle CPUs unless configured, clears its bit in the shared mask, and is marked `NOKPROBE_SYMBOL`.

## Dependencies, Integration, Risks, and Tests
Depends on cpumasks, NMI architecture hooks, printk CPU synchronization, scheduler debug helpers, stall snapshots/checks, and softlockup watchdog touch points. Risks include stalled CPUs leaving mask bits set, noisy or skipped idle backtraces, architecture raisers failing to call back, and printk recursion during NMI context. Test signals include forced all-CPU backtraces, exclude-CPU behavior, idle CPU skip toggling via `backtrace_idle`, concurrent trigger suppression, and architecture NMI watchdog tests.
