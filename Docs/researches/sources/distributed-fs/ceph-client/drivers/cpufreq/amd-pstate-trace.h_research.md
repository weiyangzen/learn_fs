# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-trace.h

Purpose: declares Linux trace events used by the AMD pstate cpufreq driver for performance requests, EPP state, and CPPC request diagnostics.

Important APIs/types/functions: sets `TRACE_SYSTEM amd_cpu` and `TRACE_INCLUDE_FILE amd-pstate-trace`. Declares `TRACE_EVENT(amd_pstate_perf)` with min/target/capacity/frequency/MPERF/APERF/TSC/cpu/fast-switch fields; `TRACE_EVENT(amd_pstate_epp_perf)` with CPU, highest/min/max perf, EPP, boost, and changed fields; and `TRACE_EVENT(amd_pstate_cppc_req2)` with CPU, floor perf, changed, and error code. Ends by including `<trace/define_trace.h>` outside the guard.

Control flow: AMD pstate code includes this header to get tracepoint prototypes and uses generated `trace_amd_pstate_*()` calls. `amd-pstate-trace.c` includes it with `CREATE_TRACE_POINTS` to instantiate definitions. Each event maps input arguments into trace entry fields and formats them with `TP_printk`.

State and persistence: no driver state; trace event metadata is compiled into the kernel/module and tracing buffers store runtime samples when enabled.

Dependencies and integration: depends on `linux/cpufreq.h`, `linux/tracepoint.h`, `linux/trace_events.h`, and trace include-path conventions. Integrated into the AMD pstate module through the cpufreq Makefile.

Risks: tracepoint ABI names and field meanings are consumed by tracing tools, so renames or format changes can break scripts. Field widths use `u8` for performance values and must match AMD pstate data ranges. The include guard plus `TRACE_HEADER_MULTI_READ` pattern must remain correct for trace generation.

Test signals: build with AMD pstate enabled, confirm events appear in tracing (`amd_cpu:amd_pstate_perf`, `amd_cpu:amd_pstate_epp_perf`, `amd_cpu:amd_pstate_cppc_req2`), run frequency/EPP changes, and verify field values and format strings match driver inputs.
