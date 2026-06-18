# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.c

Purpose: implements SXGBE DMA operation callbacks for system bus setup, per-channel descriptor ring programming, TX/RX start/stop, per-channel IRQ enable/disable, DMA interrupt status decoding, RX interrupt watchdog programming, and TSO enablement.

Important APIs: `sxgbe_get_dma_ops()` returns `sxgbe_dma_ops`. `sxgbe_dma_init()` programs AXI undefined burst and burst length map. `sxgbe_dma_channel_init()` writes per-channel control, PBL, TX/RX descriptor base addresses, tail pointers, ring lengths, and interrupt mask. `sxgbe_tx_dma_int_status()` and `sxgbe_rx_dma_int_status()` translate DMA status bits into `enum dma_irq_status` flags and extended stats.

Control flow: probe/open code initializes bus mode, then calls channel init for each active DMA channel. TX and RX start/stop iterate channel counts or target one queue. Interrupt handlers call status helpers, which read the channel status register, classify normal vs abnormal summary, update counters, build action bits such as `handle_tx`, `handle_rx`, `tx_hard_error`, `rx_hard_error`, `tx_bump_tc`, and `rx_bump_tc`, then clear served bits by writing back a mask.

State and persistence: persistent state is hardware DMA registers plus `sxgbe_extra_stats` counters. The file itself has no global mutable state.

Dependencies and integration: depends on `sxgbe_reg.h` for register offsets and bit masks, `sxgbe_desc.h` for descriptor size, `sxgbe_common.h` for stats and return flags, and Linux MMIO/delay/network includes.

Risks: `sxgbe_dma_channel_init()` computes an RX tail pointer but writes it to `SXGBE_DMA_CHA_RXDESC_LADD_REG(cha_num)` rather than a distinct RX tail pointer register, which looks like a functional bug or naming mismatch requiring hardware validation. It assumes upper 32 bits are constant for tail pointers. Status handling uses `if normal else if abnormal`, so simultaneous normal and abnormal bits process only the normal branch. Clearing FBE subcause bits must match hardware write-one-clear semantics.

Test signals: DMA ring base/tail/ring length register programming, TX/RX traffic on all channels, interrupt status paths for normal and abnormal bits, bus error subcause counters, RX watchdog conversion from ethtool coalesce settings, TSO enable per channel, and hardware register traces around RX tail programming.
