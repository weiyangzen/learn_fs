
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_trace.h

## Purpose

This header defines the HIBMCGE tracepoint used to inspect RX descriptors.

## Important APIs, Types, and Functions

- `TRACE_SYSTEM hibmcge` names the trace subsystem.
- `TRACE_EVENT(hbg_rx_desc, ...)` records PCI name, netdev name, ring index, port number, packet length, valid size, IP offset, VLAN, parse mode, and L2/L3/L4 error codes extracted from `struct hbg_rx_desc`.
- `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE hbg_trace` support tracepoint generation from the local source directory.

## Control Flow

The header contributes tracepoint definitions. `hbg_txrx.c` defines `CREATE_TRACE_POINTS` before including it, and calls `trace_hbg_rx_desc()` for received descriptors.

## State and Persistence

No persistent driver state is stored here. Trace records are emitted only when the tracepoint infrastructure records them.

## Dependencies and Integration Points

It depends on tracepoint APIs, PCI naming, bitfield extraction, and descriptor masks from `hbg_reg.h`. It integrates with RX polling in `hbg_txrx.c`.

## Risks and Edge Cases

Trace field extraction must stay synchronized with descriptor format masks. Tracepoint definitions can affect build output, so only one C file should define `CREATE_TRACE_POINTS`. High-rate RX tracing can be expensive when enabled.

## Test Signals

Signals include successful build of tracepoints, `trace_hbg_rx_desc` availability under ftrace/perf, and trace output matching RX packet descriptors during traffic.
