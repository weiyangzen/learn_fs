# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.c

## Purpose

`phy.c` is the RTL8821AE/RTL8812AE physical-layer implementation for the PCIe `rtlwifi` driver. It owns baseband and RF register access, MAC/BB/RF table programming, channel and bandwidth switching, transmit-power derivation and programming, scan-time dynamic-management pauses, RF power-state transitions, antenna/RFE path switching, and RTL8821AE IQ calibration. It is the main bridge between common `rtlwifi` state and chip-specific register tables from `table.h` plus register definitions from `reg.h`.

The file serves both `HARDWARE_TYPE_RTL8821AE` and `HARDWARE_TYPE_RTL8812AE`. Many paths branch on hardware type, current band, RFE type, BT coexistence flags, efuse regulatory mode, and RF path count. RTL8812AE gets table selection and RFE handling, but its IQ calibration entry point is currently empty; RTL8821AE has the full path-A IQK routine.

## Important APIs, Types, and Functions

- `rtl8821ae_phy_query_bb_reg()` / `rtl8821ae_phy_set_bb_reg()` perform masked baseband register reads and writes.
- `rtl8821ae_phy_query_rf_reg()` / `rtl8821ae_phy_set_rf_reg()` serialize RF register access with `rtlpriv->locks.rf_lock` and private 3-wire serial helpers.
- `rtl8821ae_phy_mac_config()`, `rtl8821ae_phy_bb_config()`, and `rtl8821ae_phy_rf_config()` stage MAC, baseband, AGC, power-limit, PG, crystal-cap, and RF6052 initialization.
- `rtl8821ae_phy_switch_wirelessband()`, `rtl8821ae_phy_set_bw_mode()`, `rtl8821ae_phy_set_bw_mode_callback()`, `rtl8821ae_phy_sw_chnl()`, and `rtl8821ae_phy_sw_chnl_callback()` implement runtime band/channel/bandwidth changes.
- `rtl8821ae_phy_set_txpower_level()` and `rtl8821ae_phy_set_txpower_level_by_path()` calculate and program CCK, OFDM, HT, and VHT TX AGC values.
- `rtl8821ae_phy_iq_calibrate()`, `rtl8821ae_do_iqk()`, and `rtl8821ae_reset_iqk_result()` manage RTL8821AE IQ calibration state and results.
- `rtl8821ae_phy_set_io_cmd()` gates scan-related dynamic-management pause/resume commands into `rtl8821ae_phy_set_io()`.
- `rtl8821ae_phy_set_rf_power_state()` coordinates RF on/off, IPS NIC halt/resume, LED state, and TX queue draining.
- `rtl8812ae_phy_config_rf_with_headerfile()` and `rtl8821ae_phy_config_rf_with_headerfile()` are consumed by RF6052 configuration.

Key private helpers include `_rtl8821ae_phy_rf_serial_read()`, `_rtl8821ae_phy_rf_serial_write()`, `__rtl8821ae_phy_config_with_headerfile()`, `_rtl8821ae_check_positive()`, `_rtl8821ae_check_condition()`, the TX power table conversion helpers, `_rtl8812ae_phy_set_rfe_reg_24g()`, `_rtl8812ae_phy_set_rfe_reg_5g()`, and the `_rtl8821ae_iqk_*()` calibration helpers.

## Control Flow

Initialization proceeds through MAC, BB, and RF config callbacks. MAC config selects the RTL8821AE or RTL8812AE MAC table and interprets conditional table entries. BB config initializes RF register-definition offsets, enables function blocks, loads regulatory power limits when allowed by efuse policy, writes PHY and AGC tables, loads PG power-by-rate data, converts dBm table data into relative offsets, converts power limits into power indexes, writes crystal-cap fields in `REG_MAC_PHY_CTRL`, and stores `cck_high_power`.

Runtime channel setup is layered. `rtl8821ae_phy_sw_chnl()` rejects concurrent channel/bandwidth operations, waits for calibration to finish, switches between 2.4 GHz and 5 GHz if needed, marks `sw_chnl_inprogress`, calls `rtl8821ae_phy_sw_chnl_callback()`, clears TX power tracking, and reprograms TX power. The callback writes RFC area channel-group values, RF `RF_CHNLBW` channel/band fields for each RF path, and RTL8821AE-specific `RF_APK` values on 5 GHz.

Bandwidth setup uses `rtl8821ae_phy_set_bw_mode()` as the guard and `rtl8821ae_phy_set_bw_mode_callback()` for actual programming. The callback updates MAC protocol bandwidth bits, secondary-channel encoding at `0x0483`, BB RF mode fields, CCK sideband state, L1 peak thresholds, spur workarounds, and RF6052 bandwidth state.

TX power programming combines efuse channel bases, OFDM/HT/VHT diffs, packed PG power-by-rate offsets, regulatory limit tables, DM remnant swing values, and `MAX_POWER_INDEX` clamping. `_rtl8821ae_phy_set_txpower_index()` maps descriptor rates to the correct TX AGC byte lanes.

RTL8821AE IQ calibration is serialized by `rtlpriv->locks.iqk_lock` and `rtlphy->lck_inprogress`. The implementation backs up MAC/BB/AFE/RF registers, configures calibration mode, runs repeated path-A LOK/TXK/RXK attempts, chooses stable TX/RX X/Y pairs, writes IQC correction registers, and restores state. RTL8812AE IQK and LC calibration are no-ops in this file.

RF power-state changes resume the NIC from IPS halt or write RF-on registers for `ERFON`; for `ERFOFF`, the code waits for non-beacon TX rings to drain and either halts the NIC or updates LED state.

## State and Persistence Behavior

The file persists state in driver memory and hardware registers only. It mutates `struct rtl_phy` fields for register definitions, channel/bandwidth progress flags, initial-gain snapshots, TX power arrays, IQK matrices, calibration flags, scan I/O state, and CCK high-power state. It consumes efuse-derived calibration and regulatory state from `struct rtl_efuse`, hardware identity from `struct rtl_hal`, and dynamic-management swing state from `struct rtl_dm`.

Hardware writes are extensive and remain until reset or later driver writes. Sensitive registers include `REG_SYS_FUNC_EN`, `REG_RF_CTRL`, `REG_OPT_CTRL`, `REG_MAC_PHY_CTRL`, `REG_TRXPTCL_CTL`, `REG_TXPAUSE`, TX AGC pages, RF `RF_CHNLBW`, RF `RF_APK`, IQK pages, RFE pinmux, CCK/OFDM enable fields, and power/interrupt/wake control registers.

## Dependencies and Integration Points

`phy.c` depends on `wifi.h`, `pci.h`, `ps.h`, `efuse.h`, `btcoexist/halbt_precomp.h`, and local `reg.h`, `def.h`, `phy.h`, `rf.h`, `dm.h`, `table.h`, `trx.h`, and `hw.h`. It calls shared register helpers, efuse helpers, RF6052 functions, dynamic-management functions, hardware ops callbacks, beacon helpers, PCI TX ring state, and common power-management helpers.

Table loading depends on the exact encoding of `RTL8821AE_*` and `RTL8812AE_*` arrays. Channel, scan, TX power, and RF power flows integrate with mac80211 through the surrounding `rtlwifi` ops.

## Risks and Edge Cases

- Register programming is order-sensitive and hardware-literal heavy.
- RF serial access depends on `phyreg_def` being initialized before use.
- Calibration code contains suspicious bitwise-negation checks on single-bit values, for example `~iqk_ready` and `~tx_fail`, which may not behave like logical-not checks.
- `_rtl8812ae_phy_get_txpower_limit()` has a suspicious 5 GHz non-worldwide indexing expression that appears to use channel where bandwidth is expected.
- RTL8821AE IQK only handles path A, while RTL8812AE IQK is empty.
- TX power conversion mixes signed limits, unsigned indexes, regulatory overrides, and VHT MCS8/9 special handling.
- `RT_CANNOT_IO(hw)` is defined as `false`, so apparent I/O guard checks do not currently block MMIO/RF access.
- Scan pause/resume must restore DIG and CCK CCA thresholds or sensitivity and IBSS behavior can regress.

## Test Signals

Build the RTL8821AE driver with warnings enabled. On hardware, test probe, MAC/BB/RF config, 2.4 GHz and 5 GHz association, scan, channel switching across channel 14, HT20/HT40/VHT80 bandwidth changes, TX throughput, suspend/resume, IPS RF off/on, and module reload. Use dynamic debug for `COMP_RF`, `COMP_INIT`, `COMP_SCAN`, `COMP_POWER`, `COMP_POWER_TRACKING`, and `COMP_IQK`. Validate programmed TX AGC indexes against efuse and regulatory tables for representative CCK, OFDM, HT, and VHT rates.
