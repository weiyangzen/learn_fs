# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_events.h

Purpose: central trace include for brcmsmac, with no-op stubs when Broadcom tracing is disabled.

Important APIs and flow: includes basic Linux/device/tracepoint and `mac80211_if.h`. If `CONFIG_BRCM_TRACING` is not enabled, it redefines `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` to produce static inline no-op `trace_*` functions. It then includes core, TX, and message trace headers.

Control flow: compile-time selection between real tracepoints and no-op stubs.

State and persistence: no state.

Dependencies and integration: every brcmsmac source needing trace calls can include this header without sprinkling config guards around call sites.

Risks and test signals: stub macro signatures must match real tracepoint prototypes; otherwise disabled-tracing builds can pass while enabled builds fail or vice versa. Test both config modes and call sites using all trace families.
