# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ethtool.c

## Purpose
`xgbe-ethtool.c` exposes the AMD XGBE driver's ethtool control plane. It reports driver identity, link modes, pause settings, MMC and extended statistics, RSS settings, timestamp capability, SFP module EEPROM information, descriptor ring sizes, channel counts, and offline self-tests. It is mostly a validation and dispatch layer: it translates ethtool requests into updates on `struct xgbe_prv_data`, then calls PHY or hardware function pointers to apply the change.

## Important APIs, Types, And Functions
- `struct xgbe_stats` plus `XGMAC_MMC_STAT` and `XGMAC_EXT_STAT` map ethtool statistic names to offsets in `struct xgbe_prv_data`.
- `xgbe_get_strings`, `xgbe_get_ethtool_stats`, and `xgbe_get_sset_count` implement the stats and self-test string sets.
- `xgbe_get_link_ksettings` and `xgbe_set_link_ksettings` expose and update `pdata->phy.lks`, validating PHY address, autonegotiation, speed, and duplex.
- `xgbe_get_pauseparam` and `xgbe_set_pauseparam` map pause autoneg/TX/RX settings to link-mode advertisement bits.
- `xgbe_get_coalesce` and `xgbe_set_coalesce` expose RX interrupt watchdog and TX timer coalescing, with range checks against descriptor counts, RIWT limits, and jiffy granularity.
- RSS operations use `get_rxfh*`/`set_rxfh` and delegate table/key writes to `hw_if->set_rss_lookup_table` and `hw_if->set_rss_hash_key`.
- `xgbe_get_ts_info` advertises PTP hardware timestamp support and reports `ptp_clock_index` when a PHC is registered.
- `xgbe_get_module_info` and `xgbe_get_module_eeprom` delegate to `phy_if` for SFP information.
- `xgbe_set_ringparam` and `xgbe_set_channels` change descriptor and queue/channel geometry and trigger `xgbe_restart_dev` or `xgbe_full_restart_dev`.
- `xgbe_get_ethtool_ops` returns the file-local `struct ethtool_ops`.

## Control Flow
The netdev setup path assigns `netdev->ethtool_ops = xgbe_get_ethtool_ops()`. ethtool calls enter one of the handlers, obtain `pdata` via `netdev_priv`, validate user-provided values, update cached driver state, and optionally reconfigure live hardware. Link and pause changes call `phy_if.phy_config_aneg` when the interface is running. Coalescing changes immediately call the hardware coalescing hooks. Ring count changes restart the device if rounded descriptor counts differ. Channel count changes stage `new_rx_ring_count`/`new_tx_ring_count` and request a full restart.

## State And Persistence
State is kept in `struct xgbe_prv_data`: `phy.lks`, `phy.autoneg`, `phy.speed`, pause flags, RSS key/table, coalescing fields, descriptor counts, ring/channel counts, and debug message level. These values are runtime configuration, not durable storage; they persist while the netdev instance exists and are re-applied through restart paths when needed.

## Dependencies And Integration Points
This file depends on Linux ethtool/netdev APIs, timestamping constants, link-mode bit helpers from `xgbe.h`, hardware callbacks in `pdata->hw_if`, PHY callbacks in `pdata->phy_if`, and self-test callbacks from `xgbe-selftest.c`. It also depends on `xgbe-main.c` for netdev registration and on the PHY implementation files for validating speeds and serving module EEPROM requests.

## Risks
User-triggered channel or ring changes can restart the device and disrupt traffic. Coalescing accepts TX usecs after rounding, returning a netlink extended-ack message rather than a hard failure for granularity adjustment. Statistics are read by offset and cast to `u64`; the table must remain aligned with actual stat field widths. Pause advertising changes are subtle because symmetric/asymmetric pause uses bit combinations. Module EEPROM calls depend on PHY implementation support and can fail for non-SFP ports or down interfaces.

## Test Signals
Useful tests include `ethtool -i`, `ethtool -S`, `ethtool -c/-C`, `ethtool -g/-G`, `ethtool -l/-L`, `ethtool -x/-X`, `ethtool --test offline`, and link-mode changes through `ethtool -s`. Kernel logs should be checked for validation messages and restart behavior after ring/channel changes.
