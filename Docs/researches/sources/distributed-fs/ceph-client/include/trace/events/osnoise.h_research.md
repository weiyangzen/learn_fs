# sources/distributed-fs/ceph-client/include/trace/events/osnoise.h

Purpose: Defines osnoise/timerlat tracing events that measure operating-system interference, interrupt noise, thread noise, NMI noise, and threshold samples for latency analysis.

Important APIs/types/functions: Events include `osnoise_sample`, `timerlat_sample`, `thread_noise`, `softirq_noise`, `irq_noise`, `nmi_noise`, and `sample_threshold`. They record runtime, noise, max samples, hardware counter usage, IRQ/thread identifiers, vectors, descriptions, and latency thresholds.

Control flow: The tracing/osnoise monitor emits samples at periodic measurement points and emits noise events when a thread, IRQ, softirq, or NMI contributes latency. Timerlat paths report timer wakeup latency and threshold crossing information.

State and persistence: No state is stored in the header. Runtime state is in tracer instances, per-CPU counters, and timing measurements; trace records are ephemeral.

Dependencies and integration points: Depends on tracepoints and integrates with kernel tracing, latency analysis, IRQ/softirq/NMI accounting, and real-time workload validation.

Risks and test signals: Risks include measurement perturbation, incorrect attribution between interrupt classes, CPU hotplug interactions, and clock-source inconsistencies. Test osnoise/timerlat tracers under idle and loaded systems, IRQ storms, softirq load, RT scheduling, CPU isolation/nohz_full, and threshold configuration changes.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/osnoise.h` completely for this pass (238 lines, 5394 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/osnoise.h_research.md`.
