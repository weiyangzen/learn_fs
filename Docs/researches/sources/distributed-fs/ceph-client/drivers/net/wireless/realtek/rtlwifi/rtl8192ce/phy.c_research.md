# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.c

## Purpose
This CE-specific PHY file adapts shared RTL8192C PHY logic to the RTL8192CE PCI device. It implements RF register locking, MAC/BB/RF table application, bandwidth callback programming, LC calibration, and RF power-state transitions.

## Important APIs, Types, And Functions
Key functions include `rtl92c_phy_query_rf_reg()`, `rtl92c_phy_mac_config()`, `rtl92c_phy_bb_config()`, `rtl92ce_phy_set_rf_reg()`, `_rtl92ce_phy_config_bb_with_headerfile()`, `_rtl92ce_phy_config_bb_with_pgheaderfile()`, `rtl92c_phy_config_rf_with_headerfile()`, `rtl92ce_phy_set_bw_mode_callback()`, `_rtl92ce_phy_lc_calibrate()`, `_rtl92ce_phy_set_rf_power_state()`, and `rtl92c_phy_set_rf_power_state()`.

## Control Flow
MAC configuration writes `RTL8192CEMAC_2T_ARRAY` byte pairs and applies a 92C/88C register tweak. BB configuration enables BB/RF clocks, powers PLL/RF blocks, sets LEDCFG, initializes common path register definitions, and delegates PHY/AGC table loading to common code. RF register access is serialized by `rf_lock` and chooses direct or deprecated firmware RF serial access based on `rtlphy->rf_mode`. Bandwidth callback programs MAC BW operation, RRSR sideband, BB RF mode, CCK/OFDM sideband registers, RF6052 bandwidth, and clears the in-progress flag. RF power transitions call IPS NIC enable/disable, RF on/sleep helpers, LED updates, and TX-ring drain waits.

## State And Persistence
State is runtime-only in `rtlphy`, `rtlpriv->locks.rf_lock`, `rtl_ps_ctl`, `rtl_mac`, and PCI TX rings. Hardware register state includes BB/RF clocks, MAC table registers, PHY/AGC tables, RF path register values, bandwidth mode, LC calibration bit, and RF on/off/sleep state.

## Dependencies And Integration Points
It depends on `table.c` arrays, `reg.h` masks, common `phy_common.c`, `rf.c` RF6052 helpers, rtlwifi PCI power-save helpers, and HAL ops from `sw.c`. It is called during `hw.c` initialization, channel-width changes, RF power changes, and calibration.

## Risks And Edge Cases
RF register access depends on correct `rf_mode`; firmware-mode helpers are stubs. `rtl92c_phy_bb_config()` has hard-coded power/clock sequencing. RF sleep waits for non-beacon TX queues but can stop after `MAX_DOZE_WAITING_TIMES_9x` even if queues remain busy. LC calibration pauses TX or modifies RF modes based on a status register and must restore state exactly.

## Test Signals
Successful BB/MAC/RF table programming, stable RF register read/write under lock, correct 20/40 MHz operation, LC calibration without stuck TX, IPS enable/disable recovery, RF sleep/on LED behavior, and no queue-drain warnings validate this file.
