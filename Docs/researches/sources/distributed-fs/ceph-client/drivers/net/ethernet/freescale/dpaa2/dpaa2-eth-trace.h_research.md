# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-trace.h

## Purpose
This trace header declares DPAA2 Ethernet tracepoints for frame descriptors and raw buffer pool seeding events, including AF_XDP-specific paths.

## Important APIs, Types, and Functions
Trace system is `dpaa2_eth`. Event class `dpaa2_eth_fd` captures FD address, length, offset, and netdev name; events include `dpaa2_tx_fd`, `dpaa2_tx_xsk_fd`, `dpaa2_rx_fd`, `dpaa2_rx_xsk_fd`, and `dpaa2_tx_conf_fd`. Event class `dpaa2_eth_buf` captures virtual address, size, DMA address, DMA map size, BPID, and netdev name; events include `dpaa2_eth_buf_seed` and `dpaa2_xsk_buf_seed`.

## Control Flow
No normal control flow exists. The main DPAA2 source defines `CREATE_TRACE_POINTS` once, and the tracing framework expands this header into tracepoint definitions. Other files include it for declarations.

## State and Persistence
Tracepoints emit transient records only when enabled by ftrace/perf infrastructure. They own no persistent state.

## Dependencies and Integration Points
The header depends on Linux tracepoint macros, netdev/skbuff headers, DPAA2 FD accessor functions, and `TRACE_INCLUDE_PATH .`/`TRACE_INCLUDE_FILE dpaa2-eth-trace`. It integrates with main DPAA2 TX/RX, TX confirmation, buffer seeding, and AF_XDP code paths.

## Risks
Trace definitions must match the available `struct dpaa2_fd` accessors and local include path. Printing DMA address by pointer to `__entry->dma_addr` must stay compatible with `%pad`. Header guard and `TRACE_HEADER_MULTI_READ` handling are important for trace generation.

## Test Signals
Build with tracing enabled, inspect tracing/events/dpaa2_eth, enable each FD and buffer event during normal and AF_XDP traffic, and verify address/length/offset/BPID fields are plausible.
