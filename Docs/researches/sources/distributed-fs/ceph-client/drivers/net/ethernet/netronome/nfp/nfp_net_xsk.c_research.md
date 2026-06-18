# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.c

## Purpose

`nfp_net_xsk.c` implements AF_XDP zero-copy pool support for compatible NFP datapaths. It manages XSK RX buffer ownership, fills RX freelists from an XSK pool, maps/unmaps pools for DMA, installs/removes pools through ring reconfiguration, drops XSK RX buffers, and wakes NAPI for XSK TX progress.

## Important APIs, Types, and Functions

Public functions are `nfp_net_xsk_rx_unstash()`, `nfp_net_xsk_rx_free()`, `nfp_net_xsk_rx_bufs_free()`, `nfp_net_xsk_rx_ring_fill_freelist()`, `nfp_net_xsk_rx_drop()`, `nfp_net_xsk_setup_pool()`, and `nfp_net_xsk_wakeup()`. Local helpers are `nfp_net_xsk_rx_bufs_stash()`, `nfp_net_xsk_pool_map()`, and `nfp_net_xsk_pool_unmap()`.

## Control Flow

Freelist fill loops while RX space is available, allocates `xdp_buff`s from the queue's pool, stashes buffer/DMA state, writes 48-bit DMA addresses into RX descriptors, advances host write pointer, then uses a write memory barrier before incrementing the queue-controller freelist write pointer. Pool setup rejects NFDK and older firmware lacking dynamic RX offset or chained metadata, DMA-maps the new pool, clones datapath state, swaps `dp->xsk_pools[queue_id]`, and calls `nfp_net_ring_reconfig()`. Wakeup schedules the queue's NAPI instance.

## State and Persistence Behavior

State includes per-RX descriptor `xsk_rxbufs`, XSK pool DMA mappings, `r_vec->xsk_pool`, datapath cloned pool pointers, ring write pointers, RX descriptor reserved/metadata fields, and drop counters under `rx_sync`. Uninstall unmaps the previous pool after successful reconfiguration.

## Dependencies and Integration Points

It depends on AF_XDP driver APIs, XDP buffer pools, NFP RX descriptor helpers, NFP ring reconfiguration, datapath version/capability state, NAPI scheduling, traceable XDP infrastructure, and DMA mapping APIs.

## Risks and Edge Cases

The feature is deliberately disabled for NFDK and old firmware so datapath code can assume dynamic metadata support. Reconfiguration failure must unmap any newly mapped pool and leave old pool state intact. The queue ID is trusted in wakeup because AF_XDP setup validates it, but out-of-band callers would need bounds checks. DMA address width uses 48-bit descriptor encoding for NFP3800 while still accepting 40-bit addresses.

## Test Signals

Run AF_XDP zero-copy bind/unbind, pool replacement, RX fill, RX drop, wakeup, interface up/down, and ring reconfig tests. Include rejection tests for NFDK, non-dynamic RX offset, missing chained metadata, DMA map failure, and allocation failure from `xsk_buff_alloc()`.
