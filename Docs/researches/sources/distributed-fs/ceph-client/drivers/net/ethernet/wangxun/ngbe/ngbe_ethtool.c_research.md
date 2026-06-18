# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.c

## Purpose
`ngbe_ethtool.c` installs ethtool operations for the GbE PF driver and implements the `ngbe`-specific ring-size setter that safely reconfigures rings while preserving shared `wx` ethtool behavior.

## Important APIs, Types, and Functions
The main public function is `ngbe_set_ethtool_ops()`. The local `ngbe_set_ringparam()` clamps and aligns TX/RX descriptor counts, handles running and stopped devices, and uses `ngbe_down()`, `wx_set_ring()`, `wx_configure()`, and `ngbe_up()` to apply changes. `ngbe_ethtool_ops` delegates most operations to shared `wx_ethtool` helpers for link settings, WOL, stats, pause, coalesce, channels, RSS, message level, and PTP stats.

## Control Flow
During probe `ngbe_set_ethtool_ops()` assigns `netdev->ethtool_ops`. Ring changes acquire `wx->reset_lock`, set `WX_STATE_RESETTING`, update counts directly if the netdev is down, or allocate temporary rings, bring the device down, swap ring counts through `wx_set_ring()`, reconfigure, and bring it back up. The reset flag and mutex are cleared at exit.

## State and Persistence Behavior
Descriptor counts are persisted only in driver runtime fields `wx->tx_ring_count`, `wx->rx_ring_count`, and per-ring `count` until module unload/reset. Ettool WOL and other settings go through shared helpers and hardware registers.

## Dependencies and Integration Points
The file depends on shared `wx_ethtool`, `wx_lib`, and `wx_hw` helpers plus `ngbe_down()`/`ngbe_up()` from `ngbe_main.c`. It integrates with the kernel ethtool netlink/ioctl surface.

## Risks and Edge Cases
Temporary ring allocation failure leaves old rings active. Running ring changes are disruptive and depend on `ngbe_down()`/`ngbe_up()` fully restoring link, interrupts, and phylink. The file uses shared `WX_MIN/MAX_TXD/RXD` constants rather than `NGBE_*` min/max names, so those shared constants must remain compatible.

## Test Signals
Run `ethtool -g/-G` with min, max, unaligned, unchanged, and allocation-failure cases; repeat while interface is up/down and with traffic. Verify queue counts, interrupts, and phylink recover after ring changes.
