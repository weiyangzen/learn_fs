# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_ethtool.c

## Purpose
`atl1e_ethtool.c` provides ethtool integration for the ATL1E driver. It reports and changes advertised link modes, dumps selected registers, reads and nominally writes EEPROM/VPD data, reports driver identity, exposes WoL options, and triggers renegotiation/reset.

## Important APIs, types, and functions
`atl1e_set_ethtool_ops()` assigns `atl1e_ethtool_ops` to the netdev. Link reporting is in `atl1e_get_link_ksettings()`, which reports 10/100 support for all devices and 1000 full only for `athr_l1e`, using `adapter->link_speed`, `adapter->link_duplex`, and `hw->autoneg_advertised`. `atl1e_set_link_ksettings()` converts userspace advertising into legacy bits, rejects unsupported gigabit on non-L1E devices and all 1000 half-duplex, updates MII advertisement shadows, sets `hw->re_autoneg`, and restarts the device if needed.

Diagnostics include `atl1e_get_regs_len()`, `atl1e_get_regs()`, `atl1e_get_eeprom_len()`, `atl1e_get_eeprom()`, `atl1e_set_eeprom()`, and `atl1e_get_drvinfo()`. WoL callbacks map only magic and PHY wake to `adapter->wol`. `atl1e_nway_reset()` calls `atl1e_reinit_locked()` when the interface is running.

## Control flow and state behavior
Link setting changes are serialized by `__AT_RESETTING`. Unlike ATL1C, the setter brings the device down/up if running or calls `atl1e_reset_hw()` if stopped, so advertisement changes are applied through a broader reset path. EEPROM set performs read/modify/write handling for unaligned first/last dwords before calling `atl1e_write_eeprom()`.

## Dependencies and integration points
The file depends on `atl1e_hw.c` for EEPROM, reset, and low-level link behavior, and on main driver functions `atl1e_up()`, `atl1e_down()`, and `atl1e_reinit_locked()`. It integrates with userspace through ethtool and with device PM through `device_set_wakeup_enable()`.

## Risks
`atl1e_get_eeprom()` has the same inclusive-range issue as ATL1C: it computes `last_dword` but loops with `i < last_dword`, skipping the final dword. `atl1e_set_eeprom()` can report success even though `atl1e_write_eeprom()` in `atl1e_hw.c` is a stub that always returns true and writes nothing. `atl1e_get_msglevel()` ignores adapter state and returns a compile-time constant based on `DBG`, so ethtool cannot tune runtime logging here. The link setter only supports autoneg-enabled requests and returns `-EINVAL` for forced settings.

## Test signals
Run `ethtool`, `ethtool -s advertise`, `ethtool -d`, `ethtool -e`, `ethtool -E`, and WoL configuration tests. Key expected signals are correct rejection of unsupported 1000 modes, real re-autoneg after advertisement change, EEPROM reads including the last requested bytes, and confirmation that EEPROM writes either truly persist or are disabled to avoid false success.
