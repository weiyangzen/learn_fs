# sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h

Purpose: Provides tracepoints for IRQ and preemption enable/disable transitions. These events support latency analysis and tracing of critical sections.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(preemptirq_template)` backs `irq_disable`, `irq_enable`, `preempt_disable`, and `preempt_enable`. Fields include caller instruction pointer, parent instruction pointer, and symbolic caller/parent output.

Control flow: IRQ/preempt instrumentation emits events when code disables or re-enables interrupts or preemption. The tracepoint records call-site identity so long critical sections can be attributed.

State and persistence: No state is stored. It observes transient CPU-local preempt/IRQ state.

Dependencies and integration points: Depends on ktime, tracepoints, string helpers, and `asm/sections.h` for symbol classification. It integrates with ftrace irqsoff/preemptoff latency tracers and lockdep-style debugging.

Risks and test signals: Risks include recursion in tracing instrumentation, symbol resolution costs, NMI/IRQ context constraints, and config-dependent availability. Test irqsoff/preemptoff tracers, lockdep configs, nested disable/enable, module call sites, and architecture build matrices.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h` completely for this pass (70 lines, 1839 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h_research.md`.
