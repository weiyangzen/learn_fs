# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.c

Purpose: creates the concrete brcmsmac tracepoint definitions in exactly one translation unit.

Important APIs and flow: includes `linux/module.h` for tracepoint infrastructure, skips body under sparse `__CHECKER__`, includes `mac80211_if.h`, defines `CREATE_TRACE_POINTS`, then includes `brcms_trace_events.h`.

Control flow: build-time tracepoint materialization only. Runtime tracepoint execution is driven by call sites in other files.

State and persistence: no driver runtime state.

Dependencies and integration: must be linked into `brcmsmac-y` so trace symbols exist when tracing is enabled. It aggregates the individual trace headers through `brcms_trace_events.h`.

Risks and test signals: defining `CREATE_TRACE_POINTS` in more than one file would duplicate symbols; omitting this object would leave tracepoints undefined. Test module builds with `CONFIG_BRCM_TRACING` enabled and disabled.
