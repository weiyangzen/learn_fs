<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/trace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/trace.h

Purpose: Defines RISC-V trace helpers/events for architecture-specific tracing.

Important APIs/types/functions: Contains tracepoint declarations/macros for arch events and includes tracepoint plumbing.

Control flow: Trace callsites emit events when enabled; disabled tracepoints compile to static branches/no-ops.

State and persistence: State is tracepoint enablement and ring-buffer data outside this header.

Dependencies and integration points: Integrates with ftrace/perf/tracefs and architecture callsites.

Risks: Trace ABI field changes can break tooling; tracing in sensitive paths must preserve registers and timing.

Test signals: tracefs event enablement, perf record, ftrace, and build checks with tracing disabled/enabled.

Source read size: 54 lines, 1054 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/trace.h -->
