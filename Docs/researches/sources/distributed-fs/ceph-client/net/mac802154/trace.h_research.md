# sources/distributed-fs/ceph-client/net/mac802154/trace.h

Purpose: declares trace events for mac802154 driver callbacks and scan notifications.

Important APIs and functions: event classes and events include driver return traces, start/stop, channel, CCA, TX power, LBT, short/PAN/extended address, PAN coordinator, CSMA params, frame retries, promiscuous mode, and `802154_scan_event`.

Control flow and state: trace macros capture `wpan_phy_name`, driver parameters, CCA fields, booleans, addresses, and scan coordinator descriptors into trace buffers. It ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` integration.

Dependencies and integration: consumed by driver operation wrappers and `scan.c` (`trace_802154_scan_event`). It depends on kernel tracepoint macros, `net/mac802154.h`, and internal local structures.

Risks and test signals: trace format strings must match captured field types, especially endian-converted addresses. Validation is compile-time trace generation plus runtime ftrace/perf event availability.
