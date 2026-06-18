# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.h

## Purpose
`util.h` defines small shared utility types and inline helpers used by mwifiex data paths and diagnostics. Its main role is to structure the `skb->cb` private area so RX/TX metadata and DMA mapping information can be stored consistently across bus and core code.

## Important APIs, Types, and Functions
Key types are `struct mwifiex_dma_mapping`, holding a DMA address and length, `struct mwifiex_cb`, which overlays DMA mapping plus either `struct mwifiex_rxinfo` or `struct mwifiex_txinfo`, and `struct mwifiex_debug_data`, the debug descriptor used by `util.c`. Important inline APIs are `MWIFIEX_SKB_RXCB`, `MWIFIEX_SKB_TXCB`, `mwifiex_store_mapping`, `mwifiex_get_mapping`, `MWIFIEX_SKB_DMA_ADDR`, and `le16_unaligned_add_cpu`. The header also exposes `mwifiex_debug_info_to_buffer`.

## Control Flow and Integration
TX/RX code calls `MWIFIEX_SKB_TXCB` or `MWIFIEX_SKB_RXCB` to interpret `skb->cb` as mwifiex metadata. Bus-specific DMA paths can store mappings with `mwifiex_store_mapping` and later recover only the DMA address with `MWIFIEX_SKB_DMA_ADDR`. `BUILD_BUG_ON` in the RX accessor ensures the combined control block fits in Linux `skb->cb`.

## State and Persistence Behavior
The header does not own persistent state, but its layout controls transient per-SKB state used throughout the driver. Because RX and TX metadata share a union, callers must not expect both to be valid simultaneously. DMA mapping state persists only for the lifetime of the SKB and must match bus unmap/completion ownership.

## Dependencies and Risks
Dependencies include Linux SKB layout, DMA address types, unaligned little-endian helpers, and mwifiex RX/TX info structs declared elsewhere. Risks are control-block size growth, accidental reuse of the union as both RX and TX metadata, stale DMA mapping after SKB cloning/reuse, and assuming natural alignment for little-endian updates where only the helper is safe.

## Test Signals
Build-time failure from `BUILD_BUG_ON` is the primary guard. Runtime signals include correct BSS metadata propagation in `txrx.c`, DMA unmap correctness in bus drivers, no metadata corruption through SKB copies/aggregation, and successful debug formatting through `mwifiex_debug_info_to_buffer`.
