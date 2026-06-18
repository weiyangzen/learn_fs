# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.c

## Purpose

`nfp_net_dp.c` provides datapath-neutral allocation, initialization, reset, hardware configuration, and small transmit helpers for NFP netdev rings. It sits below netdev lifecycle code and above the NFD3/NFDK datapath-specific implementations selected through `struct nfp_dp_ops`.

## Important APIs, Types, and Functions

Exported functions include `nfp_net_rx_alloc_one()`, `nfp_net_rx_ring_reset()`, `nfp_net_tx_rings_prepare()`, `nfp_net_tx_rings_free()`, `nfp_net_rx_rings_prepare()`, `nfp_net_rx_rings_free()`, `nfp_net_rx_ring_hw_cfg_write()`, `nfp_net_tx_ring_hw_cfg_write()`, `nfp_net_vec_clear_ring_data()`, `nfp_net_tx()`, `__nfp_ctrl_tx()`, `nfp_ctrl_tx()`, and `nfp_net_vlan_strip()`. Important local helpers allocate/free RX software buffers, initialize TX/RX ring queue-controller pointers, allocate coherent descriptor memory, register XDP RXQ memory models, and allocate optional TX ring write-back memory.

## Control Flow

Ring preparation allocates arrays of `struct nfp_net_tx_ring` or `struct nfp_net_rx_ring`, initializes each ring's index, vector pointer, queue-controller index, queue-controller BAR pointer, and stats sync, then allocates descriptor resources and per-buffer software state. TX resource allocation is delegated to datapath ops; RX descriptor rings are allocated here and then filled with either page fragments/pages or left for XSK pools. Hardware configuration writes ring DMA addresses, ring size encodings, MSI-X vector entries, and TX write-back DMA addresses to the CFG BAR.

## State and Persistence Behavior

Persistent runtime state includes `dp->tx_rings`, `dp->rx_rings`, optional `dp->txrwb`, ring DMA addresses, descriptor memory, software buffer arrays, XDP RXQ registrations, host read/write pointers, queue-controller BAR pointers, and CFG BAR ring configuration. `nfp_net_rx_ring_reset()` reestablishes the driver's expected freelist geometry after device disable by moving the empty entry to the end and zeroing descriptors.

## Dependencies and Integration Points

The file depends on `nfp_net.h` core structures, `nfp_net_dp.h` inline DMA helpers and ops wrappers, `nfp_net_xsk.h` XSK checks, Linux DMA mapping/coherent allocation, page-frag allocation, XDP RXQ registration, VLAN accel APIs, queue-controller pointer helpers, and NFP CFG BAR macros.

## Risks and Edge Cases

Error unwind paths must free partially allocated TX rings, RX descriptors, XDP RXQ registrations, coherent write-back memory, and software buffers in the right order. XDP mode changes allocation from page fragments to full pages and changes DMA direction/length assumptions through `dp`. XSK rings skip normal RX buffer allocation and use different buffer arrays. `nfp_net_vlan_strip()` must reconcile old descriptor VLAN flags with chained metadata and reject unknown TPIDs.

## Test Signals

Test ring preparation/failure injection for descriptor allocation, TX op allocation, buffer allocation, DMA map failure, XDP enabled, AF_XDP enabled, and TXRWB enabled. Runtime tests should reconfigure ring counts/sizes, open/close netdevs, run VLAN strip traffic, verify CFG BAR ring fields, and use KASAN/KMEMLEAK for ring lifecycle leaks.
