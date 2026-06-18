# sources/distributed-fs/ceph-client/arch/x86/include/asm/pm-trace.h

Purpose: implements x86 suspend/resume tracing macros that record source location metadata into a `.tracedata` section and call the PM trace generator when tracing is enabled.

Important APIs, types, and functions: defines `TRACE_RESUME(user)` and aliases `TRACE_SUSPEND(user)` to it. The macro references `pm_trace_enabled` and `generate_pm_trace()`.

Control flow: when `pm_trace_enabled` is true, inline assembly stores a local label address in `tracedata`, emits the source line and file pointer into `.tracedata`, returns to normal text, and calls `generate_pm_trace(tracedata, user)`.

State and persistence: the macro creates static trace metadata in the kernel image and updates PM trace state through `generate_pm_trace()`, which is implemented elsewhere and may encode failure breadcrumbs for reboot diagnosis.

Dependencies and integration points: depends on `asm/asm.h` for pointer-sized move/directives and on generic PM trace infrastructure. Used by suspend/resume code paths.

Risks: inline assembly must produce correctly typed section data for both 32-bit and 64-bit. Trace metadata leaks file/line information intentionally for diagnostics and must only run when enabled. Section format must match PM trace decoding.

Test signals: enable PM trace, suspend/resume failure injection, verify trace data points to the last suspend/resume marker, build both 32/64-bit, and inspect `.tracedata` section formatting.
