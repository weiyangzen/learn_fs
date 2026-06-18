# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.h

## Purpose
`dpaa2-mac.h` declares the DPAA2 DPMAC helper interface and state structures shared between Ethernet and switch drivers. It provides the minimal abstraction for opening/closing MC DPMAC objects, connecting them to phylink, starting/stopping link management, and retrieving MAC statistics.

## Important APIs and types
`struct dpaa2_mac_stats` stores DMA memory and IOVA addresses for bundled counter index/value arrays. `struct dpaa2_mac` stores the MC device, DPMAC link state, netdev, MC portal, attributes, API version, feature bits, phylink config and instance, interface mode, link type, optional PCS, firmware node, optional SerDes PHY, and five stats bundles. `dpaa2_mac_is_type_phy()` returns true for PHY and backplane DPMAC link types and is used by DPNI and switch code to decide whether phylink owns link settings.

The header declares lifecycle calls `dpaa2_mac_open()`, `dpaa2_mac_close()`, `dpaa2_mac_connect()`, `dpaa2_mac_disconnect()`, `dpaa2_mac_start()`, and `dpaa2_mac_stop()`. It also declares ethtool string/count/stat helpers and standard RMON, pause, control, and MAC stat getters.

## Control flow and integration
Callers allocate `struct dpaa2_mac`, fill `mc_dev`, `mc_io`, and `net_dev`, call `dpaa2_mac_open()`, optionally call `dpaa2_mac_connect()` for PHY/backplane endpoints, then start/stop around netdev open/close and disconnect/close on teardown. Switch and DPNI ethtool code call the stat helpers under their own MAC locks.

## State and persistence behavior
The structures model runtime-only MC/phylink state and DMA buffers. They do not persist settings across driver reload. `fw_node` reference ownership is held by the `dpaa2_mac` instance after open and released during close.

## Dependencies
The header depends on OF, MDIO/OF net helpers, phylink, and DPMAC MC command headers. Users must also include locking discipline around their pointer to `struct dpaa2_mac`; this header does not provide synchronization primitives.

## Risks and edge cases
`dpaa2_mac_is_type_phy(NULL)` returns false, allowing callers to safely check absent endpoints. Any future expansion of `struct dpaa2_mac_stats` must preserve DMA sync/free expectations in `dpaa2-mac.c`. Start/stop require RTNL as enforced by the implementation, so callers must invoke them from netdev-open/stop contexts.

## Test signals
Build coverage across Ethernet and switch users is important. Runtime signals include successful phylink start/stop, no use-after-free when endpoint changes clear the MAC pointer, stable ethtool MAC stat counts/strings, and correct handling of ports without a DPMAC endpoint.
