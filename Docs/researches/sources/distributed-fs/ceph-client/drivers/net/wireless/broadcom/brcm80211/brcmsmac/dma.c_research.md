# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/dma.c

## Purpose
`dma.c` implements the software side of the Broadcom `brcmsmac` DMA engine. It allocates and initializes DMA64 descriptor rings, programs D11/BCMA DMA registers, maps and unmaps SKB payload buffers, tracks TX/RX ring indices, posts receive buffers, drains completed receive frames, queues transmit frames, batches AMPDU transmit frames, reclaims descriptors, and exposes runtime counters through `struct dma_pub`.

## Important APIs, Types, and Functions
- `struct dma64desc` is the hardware-read descriptor format with little-endian control and address words.
- `struct dma_info` is the private object behind `struct dma_pub`; it stores BCMA/DMA devices, TX/RX register bases, coherent rings, SKB pointer arrays, indices, address offsets, alignment state, RX sizing, counters, and `brcms_ampdu_session`.
- Ring helpers `txd()`, `rxd()`, `nexttxd()`, `prevtxd()`, `nextrxd()`, `ntxdactive()`, and `nrxdactive()` implement wrap arithmetic.
- Descriptor helpers `_dma_ctrlflags()`, `_dma_isaddrext()`, `_dma_descriptor_align()`, `dma_ringalloc()`, `dma64_alloc()`, `dma64_dd_upd()`, and `_dma_ddtable_init()` handle parity, address-extension, alignment, coherent allocation, and register programming.
- Lifecycle APIs include `dma_attach()`, `dma_detach()`, `dma_txinit()`, `dma_rxinit()`, `dma_txreset()`, `dma_rxreset()`, `dma_txsuspend()`, `dma_txresume()`, and `dma_txsuspended()`.
- RX APIs include `dma_rxfill()`, `dma_rx()`, `dma_rxreclaim()`, `_dma_getnextrxp()`, and `dma64_getnextrxp()`.
- TX APIs include `dma_txfast()`, `dma_txenq()`, `dma_kick_tx()`, `dma_getnexttxp()`, `dma_txreclaim()`, `dma_txpending()`, `prep_ampdu_frame()`, and `ampdu_finalize()`.
- Utility APIs include `dma_counterreset()`, `dma_getvar()`, and `dma_walk_packets()`.

## Control Flow
`dma_attach()` allocates `dma_info`, selects DMA64 mode, stores TX/RX register bases, computes PCI address offsets, probes address-extension and descriptor-alignment behavior, allocates TX/RX pointer arrays, allocates coherent descriptor rings, validates unsupported high addresses, and initializes the AMPDU session. `dma_txinit()` and `dma_rxinit()` reset indices, clear rings, program descriptor bases in the order required by alignment behavior, and enable the DMA engines.

The RX steady-state path is `dma_rxfill()` followed by `dma_rx()`. Refill allocates SKBs, reserves optional headroom, maps buffers for `DMA_FROM_DEVICE`, records them in `rxp[]`, writes descriptors, and updates the hardware RX pointer. `dma_rx()` retrieves completed buffers, reads the device-written frame length, trims SKBs, assembles multi-buffer frames when `DMA_CTRL_RXMULTI` is enabled, or drops oversized frames and increments `rxgiants`.

The TX path starts at `dma_txfast()`. Normal frames are mapped and posted by `dma_txenq()`, then the hardware pointer is kicked. AMPDU frames are first queued in `brcms_ampdu_session`; `ampdu_finalize()` finalizes headers through common AMPDU code, enqueues each SKB into DMA, writes the TX pointer, and resets session state. Reclaim uses hardware current/active descriptor pointers unless `DMA_RANGE_ALL` is requested.

Reset paths quiesce hardware: `dma_txreset()` requests suspend, waits for idle/stopped/disabled, disables TX, and waits again; `dma_rxreset()` disables RX and waits for disabled. `dma_detach()` frees rings and arrays but assumes outstanding SKBs have already been reclaimed.

## State and Persistence
State is runtime-only. Important mutable state includes `txin`, `txout`, `rxin`, `rxout`, `txavail`, `txp[]`, `rxp[]`, coherent descriptor contents, DMA physical addresses, address offsets, control flags, RX buffer sizing/headroom, `nrxpost`, `rxoffset`, and the AMPDU session. Hardware state is reflected through DMA64 control/status/base/pointer registers. No data is persisted to disk.

## Dependencies and Integration Points
- Linux DMA APIs: `dma_alloc_coherent()`, `dma_free_coherent()`, `dma_map_single()`, `dma_unmap_single()`, and `dma_mapping_error()`.
- BCMA register access and core metadata: `bcma_read32()`, `bcma_write32()`, `bcma_set32()`, `bcma_mask32()`, `bcma_maskset32()`, `core->dma_dev`, and host-type information.
- SKB helpers from `brcmu_utils`: `brcmu_pkt_buf_get_skb()` and `brcmu_pkt_buf_free_skb()`.
- mac80211 metadata via `IEEE80211_SKB_CB()` and `IEEE80211_TX_CTL_AMPDU`.
- Common brcmsmac AMPDU and hardware state through `struct brcms_c_info`, `brcms_c_ampdu_*()` helpers, debug logging, and `trace_brcms_ampdu_session()`.

## Risks and Edge Cases
- Ring sizes must be powers of two because wrapping uses bit masking.
- Descriptor alignment, pointer-base handling, and address-extension programming are hardware-specific and easy to break on PCI/high-address systems.
- `dma_rxfill()` can hit partial-progress paths on allocation or mapping failure; ring and pointer updates must remain consistent.
- `dma_txenq()` frees an SKB on mapping failure but cannot return that failure to `dma_txfast()`.
- `dma_detach()` does not free still-posted SKBs; callers must reclaim first.
- RX length is read from device-written packet data, and the BCM47XX workaround can busy-wait until hardware writes a length.
- `dma_walk_packets()` sees descriptor-ring SKBs but not queued AMPDU-session SKBs.
- Reset waits use fixed spin limits and report failure if hardware state does not converge.

## Test Signals
Build with `CONFIG_BRCMSMAC`, debug variants, and BCM47XX where possible. Exercise attach/init failure paths, descriptor alignment, PCI address extension, RX refill/drain/ring-wrap, multi-buffer RX, giant drops, TX descriptor exhaustion, TX reclaim ranges, DMA mapping failures, AMPDU batching/finalization/kick, suspend/resume bits, reset state transitions, exported counters, and DMA debug/trace output.
