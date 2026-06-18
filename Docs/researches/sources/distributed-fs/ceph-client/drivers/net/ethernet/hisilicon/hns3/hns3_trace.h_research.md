# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_trace.h

## Purpose
This header defines HNS3 tracepoints for debugging packet layout, descriptor programming, and RX descriptor consumption. It is included by `hns3_enet.c` with `CREATE_TRACE_POINTS`, making this file the trace event contract for TX descriptor, RX descriptor, TSO, GRO, and over-max-descriptor diagnostics.

## Important APIs, Types, and Functions
- `TRACE_SYSTEM hns3` names the tracepoint subsystem.
- `DESC_NR` computes how many 32-bit words are present in `struct hns3_desc` for descriptor array printing.
- `DECLARE_EVENT_CLASS(hns3_skb_template)` captures SKB head length, total length, fragment count, checksum state, header length, GSO size/segs/type, fraglist flag, and all fragment sizes through `hns3_shinfo_pack()`.
- `DEFINE_EVENT()` instantiates `hns3_over_max_bd`, `hns3_gro`, and `hns3_tso` from the shared SKB template.
- `TRACE_EVENT(hns3_tx_desc)` records queue index, software NTU/NTC, descriptor DMA base, netdev name, and the selected TX descriptor image.
- `TRACE_EVENT(hns3_rx_desc)` records queue index, software NTU/NTC, descriptor DMA base, RX buffer DMA address, netdev name, and the current RX descriptor image.

## Control Flow
The header itself only declares tracepoint metadata. Runtime events are emitted from the enet fast paths: TX descriptor fill/FE marking calls `trace_hns3_tx_desc()`, RX allocation and fragment handling call `trace_hns3_rx_desc()`, TSO setup calls `trace_hns3_tso()`, hardware GRO completion calls `trace_hns3_gro()`, and descriptor-limit handling calls `trace_hns3_over_max_bd()`. When tracing is disabled, these calls compile into low-overhead tracepoint checks; when enabled, the trace subsystem evaluates the fast-assign blocks and formats data through `TP_printk`.

## State and Persistence
Tracepoints persist as kernel instrumentation definitions while the module is loaded. Event records are transient in ftrace/perf buffers. They snapshot selected SKB fields and descriptor contents at the call site; they do not own driver state or change packet/descriptors. The header relies on `ring->tqp->handle->kinfo.netdev->name`, ring indices, descriptor DMA base, and descriptor callback DMA addresses being valid during trace emission.

## Dependencies and Integration Points
This file depends on Linux tracepoint infrastructure and on HNS3 types declared before inclusion, especially `struct hns3_desc`, `struct hns3_enet_ring`, and helper `hns3_shinfo_pack()`. It ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE hns3_trace`, and `<trace/define_trace.h>`, which is the standard pattern for tracepoint generation. It integrates with userspace tracing through ftrace, tracefs, perf, and any tooling that subscribes to `hns3:*` events.

## Risks and Edge Cases
Trace fast-assign blocks dereference live SKB and ring state, so trace calls must only occur while those objects are valid. The SKB template uses TCP header helpers to compute header length and chooses inner headers for encapsulated packets; unusual non-TCP GSO packets may still be represented through these helper assumptions. Descriptor dumping copies the whole descriptor as a 32-bit array, which is useful but hardware-version-sensitive and may require decoder updates as descriptor formats evolve. Because this header defines tracepoints, it must be included with `CREATE_TRACE_POINTS` exactly once in the driver build.

## Test Signals
Compile tests verify tracepoint generation and include ordering. Runtime checks include enabling `hns3:hns3_tx_desc`, `hns3:hns3_rx_desc`, `hns3:hns3_tso`, `hns3:hns3_gro`, and `hns3:hns3_over_max_bd` in tracefs, generating matching TX/RX/TSO/GRO traffic, confirming descriptor words and ring indices match driver state, and ensuring tracing does not crash during reset, close, or heavy traffic.
