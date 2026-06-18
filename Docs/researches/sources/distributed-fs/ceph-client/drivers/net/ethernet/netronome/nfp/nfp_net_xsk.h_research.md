# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.h

## Purpose

`nfp_net_xsk.h` declares AF_XDP support functions and small ring-space helpers for NFP netdevs. It provides the shared interface between core datapath allocation, NFD datapaths, and the XSK implementation.

## Important APIs, Types, and Functions

It defines `NFP_NET_XSK_TX_BATCH`, `nfp_net_has_xsk_pool_slow()`, `nfp_net_rx_space()`, `nfp_net_tx_space()`, and prototypes for XSK RX buffer unstash/free/drop, pool setup, RX buffer array free, RX freelist fill, and wakeup. The helpers depend on `struct nfp_net_dp`, `struct nfp_net_rx_ring`, `struct nfp_net_tx_ring`, `struct nfp_net_xsk_rx_buf`, and `struct nfp_net_r_vector`.

## Control Flow

Callers use `nfp_net_has_xsk_pool_slow()` to select XSK versus normal RX allocation and free paths. Datapath refill logic uses `nfp_net_rx_space()` and TX logic uses `nfp_net_tx_space()` to preserve one empty ring slot. Netdev XDP setup calls `nfp_net_xsk_setup_pool()`, and AF_XDP wakeups call `nfp_net_xsk_wakeup()`.

## State and Persistence Behavior

The header owns no storage but encodes ring occupancy calculations using host read/write pointers and datapath XDP/pool pointers. The batch constant affects XSK TX scheduling granularity in implementation code.

## Dependencies and Integration Points

It includes `net/xdp_sock_drv.h` and is consumed by `nfp_net_dp.c`, `nfp_net_xsk.c`, and datapath implementations. It integrates with Linux AF_XDP pool setup and NFP ring structs from `nfp_net.h`.

## Risks and Edge Cases

Ring-space helpers assume monotonic ring pointers and one reserved slot. `nfp_net_has_xsk_pool_slow()` requires both an XDP program and a pool; changing XSK support must preserve that invariant. Queue IDs must be validated before indexing `xsk_pools`.

## Test Signals

Compile with and without AF_XDP support, run XSK bind/unbind per queue, verify ring-space calculations near wraparound, and exercise normal RX fallback when XDP program or pool is absent.
