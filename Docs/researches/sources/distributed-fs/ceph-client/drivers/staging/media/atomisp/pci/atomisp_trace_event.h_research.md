# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_trace_event.h

Purpose: declares atomisp tracepoints for camera memory diagnostics, debug breadcrumbs, and IPU C-state/P-state telemetry.

Important APIs/types/functions: trace events are `camera_meminfo`, `camera_debug`, `ipu_cstate`, and `ipu_pstate`. They use standard Linux tracepoint macros, fixed-size string arrays copied with `strscpy()`, and `TRACE_INCLUDE_FILE`/`TRACE_INCLUDE_PATH` metadata for trace generation.

Control flow: when the header is included in the trace definition compilation path, `TRACE_EVENT` expands to event descriptors. Runtime callers emit trace records through generated `trace_*` functions, for example power state code emits `trace_ipu_cstate()`.

State and persistence: trace records are ephemeral kernel tracing data. The file stores no persistent driver state.

Dependencies and integration: depends on `<linux/tracepoint.h>` and the kernel tracing build convention that includes `<trace/define_trace.h>` outside the include guard. It integrates with atomisp memory accounting and runtime power/frequency paths.

Risks and test signals: fixed 24-byte strings truncate names and debug info. Format changes affect trace consumers, so tests are kernel build coverage with tracing enabled, runtime trace capture during power transitions, and verifying event fields remain stable for scripts.
