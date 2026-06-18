# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/irq_vectors.h

Purpose: tracepoint definitions for x86 local APIC vector handlers and IRQ vector allocation/lifecycle operations.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(x86_irq_vector)`, `DEFINE_IRQ_VECTOR_EVENT()`, entry/exit events for local timer, spurious APIC, error APIC, platform IPI, IRQ work, reschedule, call-function vectors, MCE/thermal vectors, plus `vector_config`, `vector_update`, `vector_clear`, reserve/alloc/activate/deactivate/teardown/setup/free-moved events.

Control flow: when `CONFIG_X86_LOCAL_APIC` is enabled, shared event classes capture vector numbers and IRQ/vector/cpu/apic destination transitions. Optional blocks follow IRQ work, SMP, MCE, AMD deferred error, and thermal-vector configs. `irq_work_exit` denies sampling perf events to prevent recursive irq_work generation.

State/persistence: no persistent state; the payload records the live vector allocator and interrupt-handler state passed by IRQ/APIC code.

Dependencies/integration: depends on Linux tracepoints, APIC vector management, SMP IPI code, perf sampling permission hooks, and generated trace include conventions.

Risks/test signals: the main risk is tracing recursion or stale event schemas for IRQ allocation debugging. Test with ftrace/perf enabled during IRQ affinity changes, managed IRQ allocation, CPU hotplug, timer/IPI interrupts, irq_work, and APIC error/spurious paths; verify the perf sampling permission on `irq_work_exit`.
