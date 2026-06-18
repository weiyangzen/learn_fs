
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/phy.c

Purpose: Implements RTL8192CU PHY and RF-register access wrappers, MAC/BB/RF table replay, bandwidth switching, BB enable, LC calibration, and RF power-state transitions.

Important APIs/functions: `rtl92cu_phy_query_rf_reg()` and `rtl92cu_phy_set_rf_reg()` choose direct 3-wire or firmware-mediated RF serial access based on `rtlphy->rf_mode` and apply bit masks. `rtl92cu_phy_mac_config()` replays MAC tables. `rtl92cu_phy_bb_config()` enables BB/RF clocks and delegates baseband config to common code. `_rtl92cu_phy_config_bb_with_headerfile()` and `_rtl92cu_phy_config_bb_with_pgheaderfile()` replay PHY/AGC/power-group tables selected for 1T/2T/high-PA boards. `rtl92cu_phy_config_rf_with_headerfile()` replays RF path A/B tables. `rtl92cu_phy_set_bw_mode_callback()` updates MAC/BB/RF bandwidth registers. `_rtl92cu_phy_lc_calibrate()` performs LC calibration with TX paused or RF mode saved/restored. `rtl92cu_phy_set_rf_power_state()` wraps ERFON/ERFOFF/ERFSLEEP transitions.

Control flow: Init-time flow configures BB register definitions, enables clocks/resets, applies table arrays, configures RF paths, then later channel/bandwidth changes call the bandwidth callback. RF power-state transitions may call NIC enable/disable, CE RF-on/sleep helpers, LED updates, and queue drain waits.

State and persistence: Updates RF registers, BB registers, `rtlphy->set_bwmode_inprogress`, `rtlphy->rfreg_chnlval`, `rtlphy->pwrgroup_cnt`, `ppsc->rfpwr_state`, and sleep/awake jiffies. Table replay persists hardware calibration state.

Dependencies/integration: Depends on 8192C common PHY/DM/FW helpers, CU RF/table data, CE PHY declarations, rtlwifi PS/core APIs, and mac80211 channel width state.

Risks: `rtl92cu_phy_set_rf_power_state()` references PCI private TX rings (`rtl_pcipriv`, `rtl8192_tx_ring`) in a CU file, which is a transport-coupling risk and could be unsafe for USB-only contexts if executed. Bandwidth and LC calibration sequences are register-order-sensitive. Table lengths must match arrays. RF path C/D are logged or ignored.

Test signals: RF register read/write mask tests, 1T/2T and high-PA table replay traces, 20/40 MHz bandwidth switching with sideband changes, LC calibration under active and idle TX, IPS/LPS RF on/off transitions, and build/runtime checks for USB devices invoking RF power-state paths.
