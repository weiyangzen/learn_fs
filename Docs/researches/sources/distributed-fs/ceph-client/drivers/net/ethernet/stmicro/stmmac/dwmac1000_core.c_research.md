<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_core.c

## Purpose
Implements MAC-core operations for DWMAC1000/GMAC 3.x hardware: initialization, interrupts, filtering, flow control, PMT/WOL, EEE, PCS integration, debug counters, loopback, setup, and auxiliary PTP timestamp support.

## Important APIs, Types, And Functions
Exports `dwmac1000_ops`, `dwmac1000_setup`, `dwmac1000_get_ptptime`, `dwmac1000_timestamp_interrupt`, and `dwmac1000_ptp_enable`. Key internals include `dwmac1000_core_init`, `dwmac1000_set_filter`, `dwmac1000_irq_status`, EEE helpers, `dwmac1000_debug`, and PCS init/control functions.

## Control Flow
Setup fills `mac_device_info` with register base, filter counts, link bit masks, MII register layout, and capabilities. Core init applies jumbo/2K frame bits from MTU, writes `GMAC_CORE_INIT`, masks interrupts, and optionally configures VLAN tag detection. Runtime STMMAC callbacks then program MAC enable, checksum offload, filters, flow control, PMT, EEE, PCS, and loopback. PTP enable toggles auxiliary snapshot bits under `aux_ts_lock`, polls FIFO clear, and enables/disables timestamp interrupts.

## State And Persistence
State resides in GMAC registers, `mac_device_info`, `priv->dma_cap`, stats counters, `priv->plat->flags` for external snapshots, and PTP locks/clock event delivery. No disk state is used.

## Dependencies And Integration Points
Uses STMMAC core structures, `stmmac_pcs`, `stmmac_ptp`, ethtool stats, netdev address lists, CRC32 multicast hashing, and Linux PTP clock events.

## Risks
`dwmac1000_irq_status` uses GMAC interrupt mask semantics where disabled bits are discarded; incorrect mask writes can hide events. Multicast hash width depends on hardware configuration. External timestamp handling assumes valid PTP clock and can emit multiple events from snapshot count. Jumbo enable depends only on MTU thresholds.

## Test Signals
MAC setup, MTU >1500/>2000 behavior, unicast overflow to promiscuous, multicast hash bins 64/128/256, PMT wake, EEE LPI IRQ counters, PCS link/ANE IRQ, debug stat increments, loopback, and PTP external timestamp enable/interrupt are core tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac1000_core.c -->
