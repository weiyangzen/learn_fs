# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_ethtool.c

## Purpose
`atl1c_ethtool.c` exposes driver diagnostics and policy controls through ethtool. It reports link capabilities, driver identity, MMIO/PHY register snapshots, EEPROM contents, message level, WoL state, and supports changing advertised speed/duplex settings.

## Important APIs, types, and functions
`atl1c_set_ethtool_ops()` installs `atl1c_ethtool_ops` on the netdev. `atl1c_get_link_ksettings()` maps `adapter->link_speed`, `adapter->link_duplex`, `hw->autoneg_advertised`, and `ATL1C_LINK_CAP_1000M` to the modern `ethtool_link_ksettings` interface. `atl1c_set_link_ksettings()` serializes on `__AT_RESETTING`, translates requested speed/duplex into legacy advertised bits, rejects invalid 1000 half-duplex, and calls `atl1c_restart_autoneg()`.

Diagnostic entry points are `atl1c_get_regs_len()`, `atl1c_get_regs()`, `atl1c_get_eeprom_len()`, `atl1c_get_eeprom()`, and `atl1c_get_drvinfo()`. WoL is handled by `atl1c_get_wol()` and `atl1c_set_wol()`, though the setter only accepts magic packet and PHY/link wake despite reporting conversion code for other `AT_WUFC_*` bits on read. `atl1c_nway_reset()` reinitializes the adapter if the netdev is running.

## Control flow and state behavior
Most functions are synchronous ethtool callbacks. Link setting changes mutate `hw->autoneg_advertised` and restart PHY negotiation without a full netdev down/up. WoL settings mutate `adapter->wol` and call `device_set_wakeup_enable()`, which later affects suspend behavior in `atl1c_main.c`. Register and EEPROM reads snapshot hardware state through MMIO and PHY/EEPROM helpers.

## Dependencies and integration points
This file depends on netdev private data, PCI identity, `atl1c_hw.c` helpers (`atl1c_restart_autoneg`, `atl1c_read_eeprom`, `atl1c_check_eeprom_exist`, `atl1c_read_phy_reg`), and register constants from `atl1c_hw.h`. It is registered by `atl1c_init_netdev()` in the probe path.

## Risks
`atl1c_get_eeprom()` computes `last_dword` inclusively but loops with `i < last_dword`, which skips the last dword for many ranges and leaves part of the allocated buffer unfilled before `memcpy()`. The function also has an unreachable second `return 0` after `return ret_val`. `atl1c_set_link_ksettings()` forces autoneg enabled in reported settings but accepts forced non-autoneg paths by converting speed and duplex into advertised bits, so userspace semantics are somewhat mixed. WoL read code recognizes unicast/multicast/broadcast flags that the setter refuses, so externally visible state can only be a subset unless other code sets those bits.

## Test signals
Use `ethtool <dev>`, `ethtool -s`, `ethtool -d`, `ethtool -e`, and `ethtool -s wol` coverage. Good signals are correct rejection of 1000 half-duplex, successful autoneg restart, register dumps with PHY BMCR/BMSR at the tail, EEPROM reads that include the requested final bytes, and suspend wake behavior matching magic/link settings.
