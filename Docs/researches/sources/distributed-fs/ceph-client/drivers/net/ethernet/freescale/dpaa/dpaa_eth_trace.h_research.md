# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_trace.h

## Purpose
This trace header declares DPAA1 Ethernet tracepoints for QMan frame descriptors on TX, RX, and TX confirmation paths.

## Important APIs, Types, and Functions
The trace system is `dpaa_eth`. `DECLARE_EVENT_CLASS(dpaa_eth_fd)` captures FQID, frame descriptor address, format, offset, length, status, and netdev name. `DEFINE_EVENT()` instantiates `dpaa_tx_fd`, `dpaa_rx_fd`, and `dpaa_tx_conf_fd`. `fd_format_list` renders contiguous and SG frame descriptor formats.

## Control Flow
There is no normal control flow. `dpaa_eth.c` defines `CREATE_TRACE_POINTS` before including this header, causing tracepoint definitions to be emitted once. Other source files can include it for declarations.

## State and Persistence
Tracepoints record transient event data into the kernel tracing infrastructure when enabled. They do not persist state themselves.

## Dependencies and Integration Points
The header depends on Linux tracepoint macros, skbuff/netdev headers, QMan FD helpers from `dpaa_eth.h`, and `TRACE_INCLUDE_PATH .` plus `TRACE_INCLUDE_FILE dpaa_eth_trace` so generated trace code can find the local header.

## Risks
Trace field extraction must avoid side effects and must stay compatible with QMan FD layout. Include recursion and `TRACE_HEADER_MULTI_READ` guards must remain correct. Renaming the file or changing Makefile include flags can break trace generation.

## Test Signals
Build with tracing enabled, verify events appear under tracing/events/dpaa_eth, and enable `dpaa_tx_fd`, `dpaa_rx_fd`, and `dpaa_tx_conf_fd` during traffic to confirm sane FQID/address/format output.
