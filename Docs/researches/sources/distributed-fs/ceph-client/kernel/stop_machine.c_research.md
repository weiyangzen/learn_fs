# sources/distributed-fs/ceph-client/kernel/stop_machine.c

## Purpose
`stop_machine.c` implements high-priority per-CPU stopper threads and the `stop_machine()` family. It can run callbacks with one or many CPUs monopolized, including full-machine stop phases for text patching, CPU hotplug, migration, and other synchronization-heavy kernel operations.

## Important APIs, types, and functions
- `struct cpu_stopper`: per-CPU stopper state, including stopper thread, raw spinlock, enabled flag, pending work list, static `stop_work`, caller, and current function.
- `struct cpu_stop_done`: shared completion and return aggregation for queued stopper works.
- Public APIs: `stop_one_cpu()`, `stop_two_cpus()`, `stop_one_cpu_nowait()`, `stop_machine_cpuslocked()`, `stop_machine()`, optional `stop_core_cpuslocked()`, and `stop_machine_from_inactive_cpu()`.
- State machine: `enum multi_stop_state`, `struct multi_stop_data`, `set_state()`, `ack_state()`, and `multi_cpu_stop()`.
- Hotplug integration: `cpu_stop_threads`, `cpu_stop_init()`, `stop_machine_park()`, `stop_machine_unpark()`.

## Control flow
`cpu_stop_init()` initializes per-CPU locks/lists, registers `migration/%u` stopper threads via smpboot, and enables the boot CPU stopper. Single-CPU stop queues a work item and waits on completion. Multi-CPU stop initializes `multi_stop_data`, queues work on target stoppers under serialization, and each stopper advances through prepare, IRQ-disable, run, and exit phases using an atomic acknowledgement counter. `stop_machine()` holds the CPU hotplug read lock and queues `multi_cpu_stop` on all online CPUs; early boot falls back to direct local execution with IRQs disabled. Inactive CPU hotplug callers busy-wait on `stop_cpus_mutex`, queue active CPUs, and execute locally without sleeping.

## State and persistence behavior
Runtime state is per-CPU and transient: stopper work queues, enabled flags, current callback/caller for diagnostics, and completion counters. `stop_cpus_mutex` serializes multi-CPU stop requests using static work storage. `stop_machine_initialized` gates early-boot fallback.

## Dependencies and integration points
The implementation integrates with smpboot hotplug threads, scheduler stop tasks, CPU masks, CPU hotplug locks, raw spinlocks, completions, NMI watchdog/RCU stall suppression, SMT sibling masks, and diagnostic `print_stop_info()`. It is a common substrate for kernel text patching and CPU migration machinery.

## Risks
Stopper callbacks must not sleep; the stopper thread increments preempt count to enforce atomic-like context and warns if callbacks leak preempt count. Queue ordering between `stop_two_cpus()` and `stop_cpus()` is deadlock-sensitive and guarded by `stop_cpus_in_progress`. Offline CPUs can cause `-ENOENT` or partial execution, so callers must hold appropriate hotplug locks when CPU stability matters.

## Test signals
CPU hotplug stress, stop_machine users such as static key/text patching, SMT stop-core tests, lockdep, and watchdog behavior are key. Warnings for leaked preempt count, non-empty work lists at park, or deadlocked stop operations indicate regressions.
