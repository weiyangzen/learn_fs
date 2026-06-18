<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_star_emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_star_emac.c

## Purpose
`mtk_star_emac.c` is a standalone platform netdev driver for the MediaTek STAR Ethernet MAC used by SoCs such as MT8516, MT8518, MT8175, and MT8365. It handles MMIO/regmap setup, per-SoC MII/RMII interface configuration, clock management, DMA descriptor rings, NAPI RX/TX, MDIO bus access, PHY connection, multicast hash filtering, hardware counters, suspend/resume, and netdev registration.

## Important APIs, Types, And Functions
Descriptor state is modeled by `struct mtk_star_ring_desc`, `mtk_star_ring_desc_data`, and `mtk_star_ring`. `struct mtk_star_priv` stores the netdev, regmaps, clocks, coherent descriptor memory, TX/RX rings, MDIO bus, NAPI structures, PHY state, timing flags, compatibility data, spinlock, and accumulated stats. `struct mtk_star_compat` carries SoC-specific interface setup and MAC clock divisor.

Core ring helpers are `mtk_star_ring_init`, `mtk_star_ring_pop_tail`, `mtk_star_ring_push_head`, RX/TX push wrappers, and `mtk_star_tx_ring_avail`. DMA helpers map and unmap RX/TX SKBs. Hardware setup helpers include `mtk_star_dma_init`, `mtk_star_dma_start`, `mtk_star_dma_stop`, `mtk_star_dma_disable`, `mtk_star_set_mac_addr`, `mtk_star_reset_counters`, `mtk_star_update_stats`, `mtk_star_reset_hash_table`, `mtk_star_set_hashbit`, `mtk_star_phy_config`, `mtk_star_init_config`, and `mtk_star_set_timing`. Netdev callbacks implement open, stop, xmit, stats, multicast mode, ioctl, ethtool, and PM.

## Control Flow
Probe allocates an etherdev, maps registers through regmap, obtains PERICFG syscon and IRQ, enables three clocks, validates MII/RMII mode, parses PHY and timing properties, runs SoC-specific interface mode setup, programs timing, sets a 32-bit DMA mask, allocates coherent descriptor memory, initializes config and MDIO, assigns a MAC address, adds NAPI, enables PHY managed PM, and registers the netdev.

Open calls `mtk_star_enable`: it disables powerdown and interrupts, stops DMA, writes MAC/config registers, resets the hash table, initializes descriptor rings, fills RX descriptors with mapped SKBs, requests IRQ, enables NAPI and interrupts, connects the PHY, starts DMA/PHY, and starts the netdev queue. TX maps the SKB head, pushes a descriptor with first/last/interrupt flags, accounts bytes, stops the queue if descriptor availability is low, and resumes TX DMA. TX NAPI pops completed descriptors, unmaps and frees SKBs, completes netdev queue accounting, wakes the queue above threshold, and re-enables TX interrupts. RX NAPI pops owned descriptors, drops CRC/oversize frames, allocates and maps replacement SKBs before handing the current SKB to the stack, pushes a fresh RX descriptor, resumes RX DMA, and re-enables RX interrupts when complete.

Stop disables queue/NAPI/interrupts/DMA, acknowledges interrupts, stops/disconnects PHY, frees IRQ, and unmaps/frees RX and TX SKBs. Suspend disables the running device and clocks; resume re-enables clocks and the netdev if it was running.

## State And Persistence
Runtime state lives in `mtk_star_priv`; descriptor ownership is shared with hardware through the COWN bit in coherent DMA memory. Accumulated `rtnl_link_stats64` are updated from hardware counters, which are read to reset/clear thresholded counters. PHY link, speed, duplex, and pause are cached and used to reprogram `PHY_CTRL1`. Multicast filter state persists in the hardware hash table until reset or mode change.

## Dependencies And Integration Points
The driver integrates with platform device probing, OF match data, syscon PERICFG, clocks, DMA API, netdev/NAPI, PHY/MDIO, ethtool, and PM. It does not share the main `mtk_eth_soc.h` data path; it is a separate MAC driver in the same vendor directory. Device tree properties include `mediatek,pericfg`, `phy-handle`, `phy-mode`, `mediatek,rmii-rxc`, `mediatek,rxc-inverse`, and `mediatek,txc-inverse`.

## Risks
TX maps only the linear SKB head even though availability checks account for fragments, so scatter-gather assumptions should be verified against netdev feature flags and SKB layout. RX allocation failure reuses the current SKB and counts drops, preserving ring operation but potentially hiding pressure. Descriptor ownership needs barriers exactly where implemented; changing COWN writes can break DMA coherency. Hash table operations have short polling timeouts and can fail under hardware faults. The stop path assumes `priv->phydev` exists after successful open. Multicast hash addressing is simple and can collide heavily.

## Test Signals
Probe should succeed for each compatible with correct MII/RMII PERICFG values and clock divisors. Runtime tests should cover open/close cycles, PHY link changes and pause settings, TX queue stop/wake under load, RX error drops, multicast/allmulti/promisc transitions, MDIO reads/writes, suspend/resume while running and stopped, hardware counter threshold interrupts, and DMA mapping failure injection where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_star_emac.c -->
