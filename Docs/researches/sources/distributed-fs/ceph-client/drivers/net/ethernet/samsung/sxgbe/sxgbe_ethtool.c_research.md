# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_ethtool.c

Purpose: exposes SXGBE driver state and controls through ethtool: driver info, message level, extended stats, channel counts, RX interrupt coalescing, RSS hash field selection, register dump, EEE, and PHY link settings.

Important APIs: `sxgbe_set_ethtool_ops()` assigns a static `ethtool_ops`. `sxgbe_gstrings_stats[]` maps `sxgbe_extra_stats` fields to ethtool string names and offsets. `sxgbe_get_eee()`/`sxgbe_set_eee()` bridge MAC EEE state with PHY EEE helpers. `sxgbe_get_coalesce()`/`sxgbe_set_coalesce()` convert RX watchdog ticks to/from usecs using the SXGBE clock. `sxgbe_get_rxfh_fields()`/`sxgbe_set_rxfh_fields()` report and configure RSS hash field support. `sxgbe_get_regs()` copies MAC, MTL, and DMA register ranges into a fixed register dump buffer.

Control flow: ethtool requests read `sxgbe_priv_data` via `netdev_priv()`. Stats optionally refresh EEE wake error count from PHY and then copy fields by offset. Coalesce rejects zero or out-of-range RX usecs and requires `priv->use_riwt` before programming DMA watchdog. RSS setters validate flow type and requested fields before OR-ing control bits into `SXGBE_CORE_RSS_CTL_REG`. EEE set disables MAC EEE or re-runs `sxgbe_eee_init()` before updating `tx_lpi_timer` and calling PHY set.

State and persistence: modifies `priv->msg_enable`, `priv->eee_enabled`, `priv->tx_lpi_timer`, `priv->rx_riwt`, hardware RSS and watchdog registers, and PHY EEE settings. Stats expose volatile counters.

Dependencies and integration: depends on netdevice ethtool APIs, PHY ethtool helpers, clocks, PTP headers, DMA ops, core register definitions, and `sxgbe_common.h` private state.

Risks: stats extraction treats non-u64 fields as u32 even though the struct uses `unsigned long`, which can truncate on 64-bit if `sizeof(unsigned long) != sizeof(u32)` and not equal u64 in assumptions. RSS setter ORs new mode bits with existing register contents and does not clear old flow-type bits. Register dump uses a fixed `REG_SPACE_SIZE` and `BUG_ON` if ranges exceed it. EEE set changes `priv->eee_enabled` before PHY set, so PHY failure may leave partial state.

Test signals: `ethtool -S`, stats string/count matching, EEE enable/disable with PHY support absent/present, coalesce boundary values and clock rate zero, RSS hash field validation per flow type, register dump length and contents, and PHY link ksettings passthrough.
