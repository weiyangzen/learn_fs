# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace_clock.h

Purpose: exposes an architecture trace clock backed by the x86 TSC when TSC support is configured.

Important APIs/types/functions: `trace_clock_x86_tsc()` and `ARCH_TRACE_CLOCKS`.

Control flow: `CONFIG_X86_TSC` builds register `{ trace_clock_x86_tsc, "x86-tsc", .in_ns = 0 }` with generic trace clock infrastructure. Non-TSC builds define no x86-specific trace clocks.

State/persistence: no owned state. The clock reads TSC-derived time from the implementation declared elsewhere.

Dependencies/integration: depends on compiler/types headers and the trace clock registry. It integrates with ftrace/perf timestamp selection.

Risks/test signals: TSC reliability and cross-CPU synchronization determine trace ordering quality. Test by selecting the `x86-tsc` trace clock, running multi-CPU tracing, and comparing event ordering against stable clocks on systems with stable and unstable TSCs.
