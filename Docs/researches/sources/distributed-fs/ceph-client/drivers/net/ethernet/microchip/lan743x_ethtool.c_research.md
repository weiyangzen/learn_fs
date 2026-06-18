# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.c

## Purpose
This file implements ethtool support for the LAN743x PCIe Ethernet driver: EEPROM/OTP access, driver info, message levels, statistics, private flags, RSS hash configuration, hardware timestamp capability reporting, EEE, link settings, WOL, pause parameters, and register dumps.

## Important APIs, Types, and Functions
The exported object is `const struct ethtool_ops lan743x_ethtool_ops`. EEPROM/OTP helpers include legacy `lan743x_otp_*`/`lan743x_eeprom_*` paths and high-speed PCI11x1x `lan743x_hs_otp_*`/`lan743x_hs_eeprom_*` paths. `lan743x_hs_syslock_acquire` and `lan743x_hs_syslock_release` are exported through `lan743x_main.h` and protect shared Hearthstone system registers with a hardware lock plus local spinlock/refcount.

Stats support is table-driven through string arrays and register-address arrays. RSS support reads/writes `RFE_INDX` and `RFE_HASH_KEY`. Timestamp, EEE, link settings, WOL, and pause operations mostly delegate to PTP state or phylink.

## Control Flow
`get_eeprom_len`, `get_eeprom`, and `set_eeprom` choose EEPROM versus OTP based on `LAN743X_ADAPTER_FLAG_OTP`, and choose legacy versus high-speed register blocks using `adapter->is_pci11x1x`. Writes require magic values: `LAN743X_EEPROM_MAGIC` or `LAN743X_OTP_MAGIC`. High-speed EEPROM/OTP operations acquire/release the hardware syslock around setup and per-byte commands; command completion is polled with `readx_poll_timeout`.

Stats flow copies string names to ethtool buffers and reads hardware counters plus per-queue software frame counts. RSS flow maps the 128-entry indirection table as 32 dwords and the 40-byte Toeplitz key as 10 dwords. Register dump flow writes common CSR values and, when SGMII is enabled, reads a curated set of SGMII MMD registers using `lan743x_sgmii_read`.

## State and Persistence
Ettool can mutate adapter state: `msg_enable`, `adapter->flags` for OTP access selection, RSS registers, EEPROM/OTP contents, WOL option fields and SecureOn password, wakeup enablement, EEE settings through phylink, and pause settings. EEPROM/OTP writes persist on device media; OTP writes are one-time programming and irreversible.

## Dependencies and Integration Points
This file depends on `lan743x_main.h` register definitions and CSR accessors, phylink ethtool helpers, PTP clock state, PCI naming, netdev ethtool APIs, and PM support for WOL. `lan743x_main.c` installs `lan743x_ethtool_ops` during probe.

## Risks
`set_priv_flags` accepts arbitrary flags without masking to known private flags. EEPROM and OTP access are byte-at-a-time and can be slow; OTP writes are dangerous by nature. Some high-speed OTP error paths return while holding no obvious cleanup for prior state, so lock/power sequencing needs careful review on failures. WOL split between PHY and MAC is subtle, especially for `WAKE_MAGICSECURE`. Register dumps read SGMII registers that may fail; failures are represented as `0xFFFF`.

## Test Signals
Useful tests include `ethtool -i`, `ethtool -d`, `ethtool -S`, RSS get/set round trips, private flag toggling for OTP access, EEPROM read/write with correct and incorrect magic, WOL option validation, EEE get/set through phylink, pause parameter changes, and SGMII register dump on PCI11x1x SGMII devices.
