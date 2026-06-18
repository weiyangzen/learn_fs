# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.c

Purpose: Allocates, initializes, flushes, cleans, and frees Sunplus TX/RX DMA descriptor rings and their SKB mapping side tables.

Important APIs/functions: `spl2sw_descs_init()` seeds ring counts, positions, and buffer size, allocates one coherent descriptor block, clears TX descriptors, then allocates/maps all RX SKBs. `spl2sw_descs_alloc()` lays out TX descriptors first, then RX high/low queues in the same coherent allocation. `spl2sw_rx_descs_init()` creates RX SKBs, maps them for DMA, writes buffer addresses/lengths/EOR, and sets `RXD_OWN`. `spl2sw_rx_descs_flush()` re-hands existing RX buffers to hardware after reset. `spl2sw_tx_descs_clean()`, `spl2sw_rx_descs_clean()`, `spl2sw_descs_clean()`, and `spl2sw_descs_free()` unwind mappings, SKBs, side tables, and coherent memory.

Control flow and state: Descriptor state lives in `struct spl2sw_common`: `desc_base/desc_dma/desc_size`, `tx_desc`, `rx_desc[]`, `rx_skb_info[]`, and ring indices. Hardware ownership ordering uses `wmb()` before setting `RXD_OWN`, and cleanup clears `cmd1` before zeroing other fields. RX descriptors are populated for fixed `MAC_RX_LEN_MAX` buffers and recycled by NAPI.

Dependencies and integration points: Called from probe, remove, MAC reset, and interrupt recovery paths. It depends on coherent DMA allocation, `dma_map_single()`, `dma_unmap_single()`, `netdev_alloc_skb()`, and Sunplus descriptor field definitions.

Risks and test signals: A DMA mapping failure after assigning `rx_skbinfo[j].skb` leaks the just-allocated SKB because the mapping is not stored and the local SKB is not freed before `spl2sw_rx_descs_clean()`. `spl2sw_tx_descs_init()` clears `TX_DESC_NUM + MAC_GUARD_DESC_NUM`, while TX cleanup iterates only real TX descriptors. Test probe failure unwinds, RX allocation pressure, reset flushing with live RX buffers, TX timeout cleanup, and DMA API debug for map/unmap symmetry.
