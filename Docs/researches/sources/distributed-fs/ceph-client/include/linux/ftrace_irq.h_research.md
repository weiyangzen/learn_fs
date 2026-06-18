<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_irq.h -->
# sources/distributed-fs/ceph-client/include/linux/ftrace_irq.h

Purpose: Supplies tiny NMI enter/exit hooks used by tracing subsystems that need to observe interrupt-disabled or non-maskable-interrupt latency windows.

Important APIs/types/functions: Exports `ftrace_nmi_enter()` and `ftrace_nmi_exit()`. When configured, they consult `trace_hwlat_callback_enabled` and `trace_osnoise_callback_enabled` and call `trace_hwlat_callback(bool enter)` and `trace_osnoise_callback(bool enter)`.

Control flow: Architecture or IRQ/NMI entry code calls the enter helper at NMI entry and the exit helper on return. Each helper conditionally dispatches to enabled latency tracers with `true` or `false`.

State and persistence behavior: This header owns no persistent state. It reads global boolean enable flags from hwlat and osnoise tracers.

Dependencies and integration points: Integrated with `CONFIG_HWLAT_TRACER` and `CONFIG_OSNOISE_TRACER` tracing subsystems and any low-level IRQ/NMI path that wants to bracket latency accounting.

Risks: The callbacks run in NMI context, so implementations must be NMI-safe and cannot sleep. Missing exit calls would leave tracer state unbalanced.

Test signals: Build with each tracer independently and together; verify NMI entry/exit accounting in hwlat/osnoise tests; inspect lockdep/NMI-safety warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace_irq.h -->
