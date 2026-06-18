# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.c

## Purpose
Implements the RTL8192DE PCIe PHY layer: BB/MAC/RF table loading, BB register access, RF-path configuration, bandwidth changes, band/channel switching, IQK and LCK calibration, RF power-state transitions, and dual-MAC/dual-PHY coordination. This is the main hardware-tuning file for the 8192DE variant and is wired into the driver's `rtl_hal_ops` from `sw.c`.

## Important APIs, Types, And Functions
The exported entry points are `rtl92d_phy_query_bb_reg()`, `rtl92d_phy_set_bb_reg()`, `rtl92d_phy_mac_config()`, `rtl92d_phy_bb_config()`, `rtl92d_phy_rf_config()`, `rtl92d_phy_config_rf_with_headerfile()`, `rtl92d_phy_set_bw_mode()`, `rtl92d_phy_sw_chnl()`, `rtl92d_phy_set_rf_power_state()`, `rtl92d_phy_set_poweron()`, `rtl92d_phy_check_poweroff()`, `rtl92d_phy_lc_calibrate()`, `rtl92d_update_bbrf_configuration()`, `rtl92d_phy_iq_calibrate()`, and `rtl92d_phy_reload_iqk_setting()`. Internal helpers cover static RF parameter tables for C-cut 2.4G/5G paths, IMR reload, RF SYN channel programming, IQK path-A/path-B trial execution, IQK similarity selection, IQK matrix programming, LCK curve-index generation, and stepwise channel command execution.

## Control Flow
Initialization starts with `rtl92d_phy_bb_config()`, which initializes common register definitions, enables BB/RF clocks and reset bits, then calls `_rtl92d_phy_bb_config()` to load PHY register tables, optional power-index PG data, and AGC tables from `table.c`. `rtl92d_phy_rf_config()` delegates RF6052 setup to `rf.c`, while `rtl92d_phy_mac_config()` writes the MAC table and adjusts aggregation limits for single-PHY versus multi-PHY operation.

Channel changes enter `rtl92d_phy_sw_chnl()`. It waits for LCK to finish, switches wireless band when a single-PHY/both-band device crosses channel 14, validates band/channel consistency, then executes pre, RF-dependent, and post command arrays. The RF command writes `RF_CHNLBW`, reloads IMR, applies channel-specific RF SYN settings, and reloads IQK matrix data. Bandwidth changes enter `rtl92d_phy_set_bw_mode()`, update MAC bandwidth registers, CCK/OFDM sideband state, BB RF mode bits, and RF6052 bandwidth.

Calibration is multi-stage. `rtl92d_phy_iq_calibrate()` performs up to three IQK trials, compares results with `_rtl92d_phy_simularity_compare()`, stores the winning matrix per channel, and writes TX/RX IQ imbalance registers. LCK waits for scan quiescence, pauses TX, puts RF paths in standby, captures curve-count data, calculates 2G/5G curve indexes, restores queues and RF modes, then reloads the channel-specific LCK setting.

## State And Persistence
State is stored mostly in `rtlpriv->phy`, `rtlpriv->rtlhal`, `rtlpriv->efuse`, and `rtlpriv->psc`. Important persistent fields include `current_channel`, `current_chan_bw`, `rfreg_chnlval[]`, `reg_rf3c[]`, `iqk_matrix[]`, IQK backup registers, `need_iqk`, `lck_inprogress`, `sw_chnl_inprogress`, `set_bwmode_inprogress`, `rfpwr_state`, MAC/PHY mode, interface index, current band type, internal-PA flags, and dual-MAC DBI flags. The static `curveindex_2g[]` and `curveindex_5g[]` arrays cache LCK-derived channel synthesizer values after calibration.

## Dependencies And Integration Points
Depends on common rtlwifi PCI, power-save, register, RF, DM, and PHY helpers plus the 8192DE table arrays. It integrates with mac80211 through the `rtl_hal_ops` callbacks in `sw.c`, with RF6052 setup in `rf.c`, with firmware/hardware mode state from `hw.c`, and with global dual-MAC locks from `sw.h`. The DBI read/write paths are critical when one MAC programs the other PHY/radio in dual-MAC dual-PHY mode.

## Risks
This file is timing and ordering sensitive. Incorrect DBI direction, band/channel mismatch, wrong 2G/5G path selection, or stale `during_mac*init_*` flags can program the wrong PHY. IQK and LCK save/restore paths touch many BB/MAC/RF registers and can leave TX paused, RF disabled, or imbalance matrices corrupted if interrupted or partially failed. `rtl92d_phy_reload_iqk_setting()` contains a disabled redo branch (`if (0 && ...)`), so missing per-channel IQK data may silently fall back to previously stored/default values. RF sleep waits for PCI TX queues but has bounded retry behavior, so pending packets and power transitions can race under stress.

## Test Signals
Useful signals are successful probe and firmware bring-up on RTL8192DE, 2.4G and 5G association, channel changes across channel 14, 20/40 MHz transitions, dual-MAC dual-PHY startup order, suspend/resume and IPS/LPS RF state transitions, and stable throughput after IQK/LCK. Kernel logs should show no `WARN_ONCE` for band/channel mismatch, no power-off timeout, no RF switch timeout, and no repeated IQK/LCK failures. RF register readback, RSSI stability, EVM/throughput, and scan results are practical hardware validation points.
