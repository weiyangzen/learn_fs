# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.c

## Purpose
This is the RTL8192C-family shared PHY implementation used by RTL8192CE and related rtlwifi drivers. It provides baseband register access, RF 3-wire serial access, BB/RF initialization helpers, transmit-power indexing, channel switching, bandwidth dispatch, IQ/LC/AP calibration entry points, RF path switching, scan-time dynamic-initial-gain pause/resume, and RF on/sleep programming.

## Important APIs, Types, And Functions
Exported entry points include `rtl92c_phy_query_bb_reg()`, `rtl92c_phy_set_bb_reg()`, `_rtl92c_phy_rf_serial_read()`, `_rtl92c_phy_rf_serial_write()`, `rtl92c_phy_rf_config()`, `_rtl92c_phy_bb8192c_config_parafile()`, `_rtl92c_store_pwrindex_diffrate_offset()`, `_rtl92c_phy_init_bb_rf_register_definition()`, `rtl92c_phy_set_txpower_level()`, `rtl92c_phy_update_txpower_dbm()`, `rtl92c_phy_set_bw_mode()`, `rtl92c_phy_sw_chnl()`, `rtl92c_phy_iq_calibrate()`, `rtl92c_phy_lc_calibrate()`, `rtl92c_phy_set_io_cmd()`, `rtl92c_phy_set_io()`, `rtl92ce_phy_set_rf_on()`, and `_rtl92c_phy_set_rf_sleep()`. Internal helpers implement 1T BB adjustments, channel command arrays, RF-channel writes, IQK candidate comparison, ADDA/MAC save and restore, and per-path IQK matrix writes.

## Control Flow
Initialization first maps path-specific BB register definitions, loads chip-specific BB/AGC/PG tables through `rtlpriv->cfg->ops`, optionally adjusts 1T devices, and caches default gain/frame-sync values. RF access goes through `rtl_get_bbreg()`/`rtl_set_bbreg()` and either direct 3-wire LSSI sequences or deprecated firmware RF access stubs. Channel switching builds pre/RF/post command arrays, sets TX power, writes `RF_CHNLBW` for every active RF path, applies a UMC-B-cut channel-6 workaround, and advances stage/step state until complete. IQ calibration performs up to three trials, compares trial similarity, programs path A/B TX/RX imbalance matrices, and saves calibration registers for later recovery.

## State And Persistence
All state is runtime state in `struct rtl_phy`, `struct rtl_efuse`, `struct rtl_priv`, and hardware registers. The file updates `mcs_txpwrlevel_origoffset`, `pwrgroup_cnt`, `default_initialgain`, `framesync`, `phyreg_def[]`, current TX power indices, `rfreg_chnlval[]`, channel/bandwidth in-progress flags, IQK backup arrays, IQK result registers, RFPI mode state, and DIG backup values. EFUSE-derived power arrays are overwritten by `rtl92c_phy_update_txpower_dbm()` for runtime power changes, but this does not write back to EEPROM/EFUSE.

## Dependencies And Integration Points
The code depends on rtlwifi core register helpers, `rtl8192ce/reg.h` register definitions, `rtl8192ce/def.h` chip enums, common DM/FW helpers, and per-device HAL ops for BB table loading, RF6052 configuration, TX-power programming, bandwidth callbacks, and LC calibration. It integrates with mac80211 scan/channel changes, PCI power management through the HAL, dynamic management through `rtl92c_dm_write_dig()`, and firmware H2C power workflows from CE-specific code.

## Risks And Edge Cases
Register sequences are timing-sensitive and use `mdelay()`/`udelay()` around RF read/write edges. The firmware RF serial helpers are deprecated stubs that warn and return zero, so setting `rf_mode` to firmware RF operation would silently lose useful RF access. Channel switching only accepts 2.4 GHz channels 1-14. IQK result selection has several fallback paths and partially populated results can still program TX-only matrices. `RT_CANNOT_IO(hw)` is defined false, so callers rely on higher-level stop/unload checks.

## Test Signals
Useful signals include successful BB/AGC/RF table load during probe, stable RF readback through both RF paths, correct channel and 20/40 MHz switching, TX power updates following channel changes and dbm requests, IQK recovery after power cycle, LC calibration completion, scan entry/exit restoring DIG and TX power, RF on/sleep transitions without stuck TX queues, and absence of WARN_ONCE for illegal channels or deprecated firmware RF paths.
