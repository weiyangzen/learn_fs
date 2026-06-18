<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.c

Purpose: tracepoint instantiation unit for mt76x02. It defines `CREATE_TRACE_POINTS` and includes the mt76x02 trace header so the trace events have exactly one definition.

Important APIs/types/functions: `CREATE_TRACE_POINTS` and inclusion of `mt76x02_trace.h`.

Control flow: no runtime control flow beyond generated tracepoint code. Other modules call trace events declared in the header.

State and persistence: tracepoint registration is kernel instrumentation state; no driver data is persisted here.

Dependencies/integration: Linux tracepoint infrastructure and `mt76x02_trace.h`.

Risks: duplicate or missing instantiation breaks builds or disables trace events. Test signals include kernel build with tracing, enabling mt76x02 trace events, and observing TX status poll/fetch records during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.c -->
