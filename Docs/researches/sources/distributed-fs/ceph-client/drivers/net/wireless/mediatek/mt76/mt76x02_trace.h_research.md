<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.h

Purpose: trace event declarations for mt76x02-specific diagnostics, primarily TX status polling/fetching.

Important APIs/types/functions: `TRACE_SYSTEM mt76x02`, `DECLARE_EVENT_CLASS(dev_evt)`, `DEFINE_EVENT(mac_txstat_poll)`, and `TRACE_EVENT(mac_txstat_fetch)` with WCID, pktid, rate, retry, ack, success, aggregation, and validity fields.

Control flow: trace macros generate static tracepoints used by `mt76x02_mac_poll_tx_status()` and `mt76x02_mac_load_tx_status()`.

State and persistence: trace events capture transient runtime state into the kernel tracing buffers when enabled; no device state is changed.

Dependencies/integration: Linux tracepoint API, `mt76x02_tx_status`, and include path/file macros for trace generation.

Risks: field layout must match the status struct; tracing must remain low-overhead when disabled. Test signals include building with tracepoints, enabling `mt76x02:*`, and validating txstat fetch/poll events against TX status debug behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.h -->
