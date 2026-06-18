# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/ethtool.c

## Purpose
Implements ALX ethtool operations for link settings, pause parameters, message level, and hardware statistics exposure.

## Important APIs, Types, and Functions
Exports `const struct ethtool_ops alx_ethtool_ops`. `alx_get_link_ksettings()` reports supported/advertised modes from `alx_hw`; `alx_set_link_ksettings()` validates and applies autoneg or forced speed via `alx_setup_speed_duplex()`. `alx_get_pauseparam()` and `alx_set_pauseparam()` map ethtool pause state to `ALX_FC_*` flags and MAC/PHY reconfiguration. `alx_get_ethtool_stats()` updates hardware stats and copies `struct alx_hw_stats` in the same order as `alx_gstrings_stats`.

## Control Flow and State
Most operations lock `alx->mtx` when reading or mutating link configuration. Stats use `alx->stats_lock` because hardware counters are clear-on-read and accumulated in `hw->stats`. Pause changes may restart PHY autoneg and may immediately update MAC flow-control bits.

## Dependencies and Integration Points
Depends on ethtool legacy link-mode conversion helpers, MDIO advertisement bit definitions, `alx_hw` helpers from `hw.c`, and stats layout in `hw.h`. Netdev installs this table during PCI probe.

## Risks and Test Signals
The order of `alx_gstrings_stats` must exactly match `struct alx_hw_stats`; the `BUILD_BUG_ON` protects size but not semantic order. Link-setting validation should be tested for 10/100 forced modes, disallowed forced 1000, Fast Ethernet chip support, and pause autoneg transitions. Stats tests should verify monotonic accumulation despite clear-on-read MIB registers.
