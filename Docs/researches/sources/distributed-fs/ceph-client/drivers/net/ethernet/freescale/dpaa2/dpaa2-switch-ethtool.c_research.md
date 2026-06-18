# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-ethtool.c

## Purpose
`dpaa2-switch-ethtool.c` implements ethtool support for DPAA2 Ethernet switch port netdevs. It reports driver and firmware identity, link settings, DPSW per-port counters, and optional DPMAC statistics for switch ports.

## Important APIs and functions
`dpaa2_switch_port_ethtool_ops` is the exported ethtool operation table. `dpaa2_switch_get_drvinfo()` reads the DPSW API version and bus name. `dpaa2_switch_get_link_ksettings()` delegates to phylink for PHY/backplane ports, otherwise reads DPSW link state with `dpsw_if_get_link_state()`. `dpaa2_switch_set_link_ksettings()` similarly delegates to phylink for PHY-backed ports, or disables the switch interface, applies a `dpsw_link_cfg`, and re-enables the interface for fixed/non-phylink ports. Stats functions expose `dpaa2_switch_ethtool_counters` plus MAC-library counters and standard MAC stats.

## Control flow
Etntool stats requests copy counter names, then `dpaa2_switch_ethtool_get_stats()` iterates DPSW counter IDs and calls `dpsw_if_get_counter()` for the target port. After hardware switch counters, it takes `port_priv->mac_lock` and appends DPMAC stats if the port has a MAC. Link settings take the same MAC lock to decide whether phylink owns the port.

## State and persistence behavior
This file does not own long-lived state. It reads `struct ethsw_port_priv` and `struct ethsw_core` created by switch core code. Link setting changes are written to DPSW MC state and may require the interface to be temporarily disabled. Stats are read from hardware.

## Dependencies and integration points
The file depends on `dpaa2-switch.h`, DPSW MC APIs, phylink ethtool helpers, and the shared MAC stats library from `dpaa2-mac.c`. It is separate from DPNI Ethernet ethtool support and operates on switch-port private data.

## Risks and edge cases
If re-enabling a port after a fixed-link setting change fails, the function returns that error and the port may remain disabled. `get_drvinfo()` reports `"N/A"` firmware version if API version read fails. MAC stats are conditional on a connected MAC and protected by `mac_lock`. The file does not expose pause stats unlike the DPNI ethtool path.

## Test signals
Use `ethtool -i`, `ethtool -S`, and link settings on switch ports with and without PHY-backed DPMAC endpoints. Validate interface disable/re-enable around fixed-port setting changes, firmware-version failure handling, and MAC stat string/count alignment.
