# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/trace.h

Purpose: declares tracepoints for Thunderbolt/USB4 networking frame allocation/free, ThunderboltIP frame headers, and skb Tx/Rx lifecycle.

Important APIs/types/functions: trace system is `thunderbolt_net`. Event classes are `tbnet_frame`, `tbnet_ip_frame`, and `tbnet_skb`. Concrete events are `tbnet_alloc_rx_frame`, `tbnet_alloc_tx_frame`, `tbnet_free_frame`, `tbnet_rx_ip_frame`, `tbnet_invalid_rx_ip_frame`, `tbnet_tx_ip_frame`, `tbnet_rx_skb`, `tbnet_tx_skb`, and `tbnet_consume_skb`.

Control flow: `main.c` calls these tracepoints around DMA buffer allocation/free, invalid/valid Rx frame processing, Tx frame preparation, Rx skb delivery, Tx skb start, and Tx skb consumption. The header ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace`, and `<trace/define_trace.h>` for standard tracepoint generation.

State and persistence: trace events capture transient fields: ring index, page pointer, DMA address, DMA direction, ThunderboltIP frame size/id/index/count, skb address, length, data length, and fragment count. No driver state is owned by the header.

Dependencies and integration: depends on Linux tracepoint macros, DMA direction names, skbuff helpers, and local include behavior from the Makefile. Included normally by `main.c` and with `CREATE_TRACE_POINTS` by `trace.c`.

Risks: tracepoint field types must match call-site argument types; header path macros require the file to remain in the expected directory. Pointer and DMA address tracing is diagnostic and may be sensitive in production traces.

Test signals: compile tracepoints, enable each event in ftrace/perf, verify allocation/free pairs, observe invalid Rx frame traces on injected bad descriptors, and correlate `tbnet_tx_skb`/`tbnet_tx_ip_frame`/`tbnet_consume_skb` during large-packet Tx.
