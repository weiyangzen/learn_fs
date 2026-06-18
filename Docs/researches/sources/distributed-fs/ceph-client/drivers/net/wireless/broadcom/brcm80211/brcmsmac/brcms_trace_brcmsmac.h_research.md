# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac.h

Purpose: defines brcmsmac core tracepoints for timers, deferred procedure calls, and MAC interrupt status.

Important APIs and tracepoints: `TRACE_EVENT(brcms_timer)` records timer milliseconds, set flag, and periodic flag. `TRACE_EVENT(brcms_dpc)` records DPC data pointer value. `TRACE_EVENT(brcms_macintstatus)` records device name, ISR context flag, interrupt status, and mask.

Control flow: when `CONFIG_BRCM_TRACING` is enabled, this header participates in tracepoint definition through `trace/define_trace.h`; otherwise stubs are provided by `brcms_trace_events.h`.

State and persistence: no driver state is owned. Trace events are transient kernel tracing records.

Dependencies and integration: depends on Linux tracepoint infrastructure and `struct brcms_timer` fields from mac80211 interface code. Included by aggregate trace header.

Risks and test signals: trace format changes affect tooling. `dev_name()` and timer fields must be valid at trace time. Test by enabling BRCM tracing and confirming timer/DPC/interrupt events appear under ftrace/perf.
