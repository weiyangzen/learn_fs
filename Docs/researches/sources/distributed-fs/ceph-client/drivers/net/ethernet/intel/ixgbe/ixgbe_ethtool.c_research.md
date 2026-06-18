# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ethtool.c

## Purpose

`ixgbe_ethtool.c` implements the ixgbe driver's `struct ethtool_ops` surface. It translates userspace ethtool requests into ixgbe state reads, register dumps, EEPROM access, ring resizing, statistics, diagnostics, Wake-on-LAN, LED identification, interrupt moderation, Flow Director rules, RSS configuration, timestamp capability reporting, channel counts, module EEPROM reads, EEE control, and private flags. It also defines an E610-specific ethtool ops table that reuses most generic operations but swaps in E610 behavior for pause configuration, WoL handling, and physical-ID LED control.

## Important APIs, types, and functions

The file defines `struct ixgbe_stats` and stat/test/private-flag string tables. Public functions are `ixgbe_refresh_fw_version()` and `ixgbe_set_ethtool_ops()`. Major operation groups are link settings, pause parameters, register and EEPROM access, driver info, ring parameters, string/stat sets, diagnostics, WoL, physical ID, coalescing/RSC, Flow Director, RSS hash fields and RETA/key programming, timestamp info, channels, module EEPROM, firmware-PHY EEE, and private flags.

## Control flow

`ixgbe_set_ethtool_ops()` selects `ixgbe_ethtool_ops_e610` for `ixgbe_mac_e610`, otherwise `ixgbe_ethtool_ops`. Link reads ask `hw->mac.ops.get_link_capabilities()`, populate ethtool link modes by media/PHY/SFP type and advertised masks, report pause advertising from `hw->fc.requested_mode`, and report current speed from `adapter->link_speed` only when carrier is up. Link writes validate requested advertising, restrict forced modes, serialize against SFP init, call `hw->mac.ops.setup_link()`, and roll back the old advertised mask on failure.

Pause writes build a temporary `hw->fc` copy, validate hardware/DCB/autoneg constraints, map rx/tx booleans to ixgbe flow-control modes, then reset or reinitialize only when the configuration changes. E610 refuses disabled pause autoneg and requires autoneg-capable flow control.

Ring resizing clamps and aligns descriptor counts. If down, only counts are updated. If running, the code sets `__IXGBE_RESETTING`, allocates temp rings, takes the adapter down, allocates replacement TX/XDP/RX resources before freeing old resources, copies successful temp rings into adapter rings, brings the adapter up, and clears reset state.

Diagnostics split online and offline modes. Offline tests reject active VFs, close or reset the interface, run link/register/EEPROM/interrupt/MAC-loopback tests with resets between them, skip loopback under SR-IOV or VMDq, then restore state. Online tests only run link and mark offline-only tests as passed.

FDIR insertion validates perfect-filter support, maps ring cookies to queues or VF pools, enforces rule index range, converts ethtool flow specs to ATR flow types, enforces one input mask per port, computes a perfect hash, writes the hardware filter, and stores a sorted software rule under `fdir_perfect_lock`. RSS configuration validates supported hash fields, updates UDP RSS flags and MRQC/PFVFMRQC, validates RETA entries, and stores RETA/key.

Module EEPROM reads use PHY I2C callbacks and reject firmware-controlled PHYs. EEE reads for firmware PHYs call `ixgbe_fw_phy_activity()` and combine link-partner data with cached PHY EEE masks; writes only toggle whole EEE enablement and reject unsupported fine-grained changes.

## State and persistence behavior

The file reads and mutates `adapter->msg_enable`, `adapter->wol`, `hw->wol_enabled`, `hw->fc`, `hw->phy.autoneg_advertised`, ring descriptor counts, RSS key/indirection table, RSS UDP flags, FDIR software filter list/count/mask, coalescing settings, RSC enable flag, channel feature limits, EEE flags and advertised speeds, private `flags2`, and diagnostic state bits. Hardware side effects include EEPROM writes/checksum updates, WoL register programming, PCI wake enablement, link autoneg restarts, resets, interrupt moderation writes, MRQC/PFVFMRQC RSS field updates, FDIR hardware programming/erasure, and LED identification state.

## Dependencies and integration points

The file integrates Linux ethtool core with ixgbe core state, PCI, netdevice features, PTP clock indexing, module EEPROM standards, Flow Director ATR helpers, RSS storage helpers, DCB/FCoE ring-feature limits, and E610 helpers from `ixgbe_e610.h`. It relies on `ixgbe_main.c` and `ixgbe_lib.c` for reset/open/close, queue allocation, interrupt schemes, TX/RX resource setup, TC setup, stats update, and feature flags.

## Risks and edge cases

Many ethtool operations reset or stop/start the device, so locking and state-bit discipline are important. `ixgbe_set_eeprom()` assumes EEPROM write and checksum-update callbacks exist; that must be reviewed for operation tables that expose read-only EEPROM support such as E610. Register diagnostics write hardware registers and must stay offline-only. FDIR supports only one input mask per port. UDP RSS can reorder fragments. Module EEPROM returns `-ENXIO` for firmware PHYs, limiting legacy module reporting on E610. The fixed register dump layout can drift as MAC-specific registers evolve.

## Test signals

Useful tests include `ethtool -i`, stats, ring get/set, coalesce get/set, channels get/set, RSS get/set, RXNFC rule add/delete/list, EEE get/set, module EEPROM reads on supported PHYs, and online/offline diagnostics. E610-specific tests should cover ACI LED identification, pause autoneg refusal, E610 WoL ACPI paths, and firmware version refresh. Regression tests should verify ring-resize failure preserves old resources, FDIR single-mask enforcement, invalid RSS field rejection, SR-IOV channel limits, active-VF offline diagnostic rejection, and unavailable module I2C handling.
