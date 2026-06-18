# sources/distributed-fs/ceph-client/kernel/sched/membarrier.c

## Purpose
Implements the `membarrier(2)` syscall commands that force memory-ordering points across threads, processes, restartable sequences, and architecture core-synchronization paths. It bridges userspace ABI requests to scheduler runqueue state and inter-processor interrupts.

## APIs, Control Flow, and State
The file defines `SYSCALL_DEFINE3(membarrier)`, `membarrier_exec_mmap()`, and `membarrier_update_current_mm()`. Supported command bits are built from UAPI `MEMBARRIER_CMD_*` values, conditionally including sync-core and RSEQ commands. Registration commands set bits in `mm->membarrier_state` and call `sync_runqueues_membarrier_state()` so currently running threads using that `mm` have matching `rq->membarrier_state`. `membarrier_exec_mmap()` clears state during exec and updates the current runqueue.

Expedited global and private commands take a full barrier before and after targeting CPUs. `membarrier_global_expedited()` scans online CPUs whose runqueue state advertises global expedited registration and whose current task has an `mm`, then sends `ipi_mb()`. `membarrier_private_expedited()` verifies the caller's registration, optionally selects `ipi_sync_core()` or `ipi_rseq()`, targets either all CPUs currently running the caller's `mm` or a specific CPU for RSEQ, and waits for the IPI callbacks. The IPI callbacks provide full barriers, deferred core sync, or RSEQ event forcing. A mutex serializes IPI command execution; CPU hotplug and RCU locks stabilize target CPUs and `rq->curr`.

## Dependencies and Integration Points
Depends on UAPI membarrier definitions, `mm_struct`, scheduler runqueues, CPU hotplug read locks, RCU, cpumasks, SMP call functions, sync-core arch hooks, RSEQ, and nohz full query behavior. Integration points are the syscall table, exec/mmap lifecycle, context switch updates through `membarrier_update_current_mm()`, scheduler barriers around `rq->curr`, and userspace runtimes that use membarrier for memory reclamation, JIT synchronization, or RSEQ aborts.

## Risks and Test Signals
This is memory-model-sensitive code. Risks include missing pre/post barriers, targeting stale or wrong `mm` users, CPU hotplug races, incorrect nohz-full compatibility for global commands, registration bits becoming visible out of order, sync-core running too late, and RSEQ CPU-target validation errors. Test signals include Linux membarrier selftests, RSEQ selftests, litmus-style ordering tests, CPU hotplug stress while issuing commands, single-thread and multi-`CLONE_VM` cases, nohz_full configurations, and architecture sync-core validation.
