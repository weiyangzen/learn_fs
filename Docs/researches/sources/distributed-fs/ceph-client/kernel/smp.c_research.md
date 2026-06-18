# sources/distributed-fs/ceph-client/kernel/smp.c

## Purpose

`kernel/smp.c` implements generic SMP call-function infrastructure. It queues callbacks to run on one CPU, many CPUs, all other CPUs, or a selected CPU via workqueue; sends the required IPIs; flushes per-CPU callback queues; manages callback data through CPU hotplug; provides debug detection for stuck call-single-data locks; and handles boot-time SMP activation parameters.

## Important APIs, Types, and Functions

Key state includes per-CPU `struct call_function_data cfd_data`, per-CPU `llist_head call_single_queue`, per-CPU reusable `call_single_data_t csd_data`, and optional CSD lock-debug state (`cur_csd`, `cur_csd_func`, `cur_csd_info`, `trigger_backtrace`, `n_csd_lock_stuck`). `struct call_function_data` owns per-target CSD storage and two cpumasks used by multi-CPU calls.

Public APIs include `smpcfd_prepare_cpu()`, `smpcfd_dead_cpu()`, `smpcfd_dying_cpu()`, `call_function_init()`, `__smp_call_single_queue()`, `generic_smp_call_function_single_interrupt()`, `flush_smp_call_function_queue()`, `smp_call_function_single()`, `smp_call_function_single_async()`, `smp_call_function_any()`, `smp_call_function_many()`, `smp_call_function()`, `setup_nr_cpu_ids()`, `smp_init()`, `on_each_cpu_cond_mask()`, `kick_all_cpus_sync()`, `wake_up_all_idle_cpus()`, `cpus_peek_for_pending_ipi()`, and `smp_call_on_cpu()`.

Internal helpers include `send_call_function_single_ipi()`, `send_call_function_ipi_mask()`, `csd_do_func()`, `csd_lock()`, `csd_unlock()`, `csd_lock_wait()`, `generic_exec_single()`, `__flush_smp_call_function_queue()`, and `smp_call_function_many_cond()`.

## Control Flow

Single-CPU calls use `smp_call_function_single()`. The caller disables preemption with `get_cpu()`, warns about contexts that can deadlock, chooses an on-stack synchronous CSD or a per-CPU asynchronous CSD, fills `func` and `info`, and calls `generic_exec_single()`. Same-CPU calls execute directly with IRQs disabled after unlocking the CSD. Remote calls validate CPU online state, queue the CSD on the target CPU's lockless list, and send an IPI if the queue was previously empty. Synchronous callers wait for the target to clear the CSD lock.

Asynchronous single calls use a caller-owned CSD and return `-EBUSY` if its lock flag is still set from a prior invocation. Multi-CPU calls run through `smp_call_function_many_cond()`, which requires preemption disabled and IRQs enabled in normal online contexts. It builds an online remote mask, optionally filters CPUs with `cond_func`, locks and fills per-target CSDs, queues them, chooses single-IPI versus mask-IPI sending, optionally executes locally, and waits for remote CSD unlocks when requested.

Target CPUs handle IPIs in `generic_smp_call_function_single_interrupt()`, which calls `__flush_smp_call_function_queue()` with IRQs disabled. The flush path detaches and reverses the per-CPU llist, warns once for callbacks on offline CPUs, executes synchronous callbacks first, then asynchronous and IRQ-work callbacks, and finally batches scheduler TTWU callbacks through `sched_ttwu_pending()`. This ordering wakes synchronous waiters promptly while preserving special handling for task wakeups.

CPU hotplug preparation allocates cpumasks and per-CPU CSD arrays. Dying CPUs explicitly flush pending call-function queues and irq work with interrupts disabled so no callbacks remain queued as the CPU leaves. Boot-time code parses `nosmp`, `nr_cpus=`, and `maxcpus=`, initializes idle and CPU hotplug threads, brings up nonboot CPUs, and calls `smp_cpus_done()`.

## State and Persistence

Persistent state is per-CPU and boot-global. `call_single_queue` holds pending callback nodes until an IPI or explicit flush runs them. CSD lock bits serialize ownership of reusable CSD objects and act as completion state for waiters. `setup_max_cpus` and `nr_cpu_ids` persist boot-time SMP limits. Optional debug counters and module parameters persist CSD stall detection settings.

## Dependencies and Integration Points

This file integrates with architecture IPI hooks (`arch_send_call_function_single_ipi()`, `arch_send_call_function_ipi_mask()`), scheduler TTWU batching, irq work, CPU hotplug, cpumasks, NUMA CPU selection, idle wakeups, tracepoints for IPI and CSD events, hypervisor vCPU pinning, system per-CPU workqueue, RCU/list primitives, NMI backtraces, and boot parameter parsing.

## Risks and Edge Cases

The major risks are deadlocks and missed IPIs. Call-function APIs warn against use from interrupt-disabled or non-task contexts because synchronous waits can deadlock if interrupted between queueing and IPI sending, and asynchronous paths can reuse the same per-CPU CSD. CPU online/offline races are controlled by preemption disabling and explicit dying-CPU flushes. CSD lock debug deliberately sends backtraces and may resend IPIs when a remote CPU appears stuck. Queue flushing must handle callbacks queued to offline CPUs and must preserve type-specific unlock timing. Multi-CPU calls can see concurrent mask changes, so zero remote IPIs after filtering is valid.

## Test Signals

Useful tests include same-CPU and remote `smp_call_function_single()` with wait and no-wait modes, async `-EBUSY` behavior, multi-CPU calls with masks and conditional callbacks, local execution via `on_each_cpu_cond_mask()`, CPU hotplug while callbacks are queued, idle polling CPUs receiving pending work, CSD lock debug timeout paths, offline CPU warning paths, boot parameter limits, `kick_all_cpus_sync()`, `wake_up_all_idle_cpus()`, and `smp_call_on_cpu()` with and without physical vCPU pinning.
