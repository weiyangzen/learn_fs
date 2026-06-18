<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/up.c -->
# sources/distributed-fs/ceph-client/kernel/up.c

Purpose: provides uniprocessor implementations of selected SMP call APIs so common kernel code can use SMP-style helpers even when only CPU 0 exists.

Important APIs: `smp_call_function_single()`, `smp_call_function_single_async()`, `on_each_cpu_cond_mask()`, and `smp_call_on_cpu()` are exported.

Control flow: calls targeting any CPU other than 0 return `-ENXIO`. Synchronous and async single-CPU calls disable local interrupts, invoke the callback directly, and restore interrupts. `on_each_cpu_cond_mask()` disables preemption to mirror SMP calling conditions, tests the optional condition and mask for CPU 0, then calls with interrupts disabled. `smp_call_on_cpu()` optionally pins the vCPU through the hypervisor interface while calling the function.

State and persistence: no persistent state is maintained.

Dependencies and integration: integrates with generic SMP APIs, interrupt state handling, preemption, cpumasks, and hypervisor pinning.

Risks: the async variant ignores the `cpu` argument check present in the sync variant and directly invokes the callback, matching UP assumptions but relying on callers not passing invalid CPU in practice. Test signals include UP builds, callbacks observing interrupts disabled, conditional mask behavior, invalid CPU rejection, and hypervisor physical pin/unpin sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/up.c -->
