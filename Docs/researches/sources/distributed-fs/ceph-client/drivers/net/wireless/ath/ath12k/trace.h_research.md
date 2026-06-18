## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.h

Purpose: declares ath12k trace events for HTT packet log payloads, PPDU stats, RX descriptors, and WMI diagnostics.

Important APIs/types: trace events are `ath12k_htt_pktlog`, `ath12k_htt_ppdu_stats`, `ath12k_htt_rxdesc`, and `ath12k_wmi_diag`. When `CONFIG_ATH12K_TRACING` is off, `TRACE_EVENT` is replaced with empty inline functions.

Control flow: each event captures device/driver names and dynamic payload data. PPDU/RX descriptor events also snapshot pdev timestamp fields (`sync_timestamp_*`, MLO offsets, compensation values). The header sets `TRACE_SYSTEM ath12k` and custom include path/file values for `define_trace.h`.

State and persistence: trace records are transient kernel tracing data. The event payload copies buffers at trace time, so consumers see a snapshot independent of later skb/descriptor lifetime.

Dependencies/integration: depends on Linux tracepoint macros, `core.h`, and callers in WMI/HTT/datapath code. It integrates with tracefs/perf tooling and packet-log diagnostics.

Risks: dynamic arrays copy caller-provided lengths; callers must pass valid buffers and bounded sizes. Timestamp assignments appear to store `sync_timestamp_hi_us` into the low field and vice versa, which should be verified against struct naming. Disabled tracing stubs remove runtime overhead but can hide unused parameter warnings differently from enabled builds.

Test signals: compile tracing on/off, enable events under tracefs, generate HTT pktlog/PPDU/RX/WMI traffic, and validate payload lengths and timestamp fields in captured traces.
