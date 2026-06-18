# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/phy.c

Purpose: Implements RTL8192DU PHY/BB/RF programming for the USB dual-MAC chipset: BB register access, MAC/BB/RF table loading, bandwidth and channel switching, IQK/LCK calibration, RF power states, band-specific BB/RF reconfiguration, and PA-bias setup.

Important APIs/functions: `rtl92du_phy_query_bb_reg()` / `rtl92du_phy_set_bb_reg()` wrap masked BB access and route accesses to the peer PHY during dual-MAC initialization. `rtl92du_phy_mac_config()`, `rtl92du_phy_bb_config()`, `rtl92du_phy_rf_config()`, and `rtl92du_phy_config_rf_with_headerfile()` load arrays from `table.c`. `rtl92du_phy_set_bw_mode()` programs 20/40 MHz MAC, BB, and RF bandwidth state. `rtl92du_phy_sw_chnl()` switches channel/band, updates TX power and RF channel registers, reloads IMR/RF settings, and applies IQK. `rtl92du_phy_iq_calibrate()` and `rtl92du_phy_lc_calibrate()` perform hardware calibrations and cache/reload results. `rtl92du_phy_set_rf_power_state()`, `rtl92du_phy_set_poweron()`, and `rtl92du_phy_check_poweroff()` handle RF/NIC power transitions. `rtl92du_update_bbrf_configuration()` applies band/topology/antenna/PA settings. `rtl92du_phy_init_pa_bias()` runs EFUSE-gated PA-bias sequences.

Control flow: HAL init calls MAC, BB, and RF setup through `sw.c`. BB setup enables device functions, loads PHY registers, optionally stores power-index offsets, loads AGC, and applies crystal-cap calibration. RF setup delegates to `rf.c`, which calls back for RF table programming. Runtime channel switching waits for LCK, handles single-MAC dual-band band changes, validates band/channel consistency, updates RF `RF_CHNLBW`, reloads IMR/RF synthesizer parameters, and reloads or executes IQK.

State and persistence: Live state is in `rtl_phy`, `rtl_hal`, `rtl_efuse`, and `rtl_ps_ctl`, including current channel/bandwidth, RF channel values, IQK matrix cache, curve indexes, dual-MAC routing flags, and RF power timestamps. No disk persistence exists.

Dependencies/integration: Depends on rtlwifi I/O helpers, rtl8192d common `reg.h`, `def.h`, `phy_common.h`, `rf_common.h`, USB speed, EFUSE, power-save helpers, `rf.c`, and table arrays from `table.c`. HAL ops in `sw.c` expose these functions.

Risks: Register sequences are timing-sensitive and magic-constant heavy. Dual-MAC routing flags can direct writes to the wrong PHY. IQK/LCK save/restore paths must be complete. Channel/band mismatches return after warnings. RF power transitions depend on shared mutexes and peer MAC bits.

Test signals: Probe with firmware, both USB interface probe orders, 2.4/5 GHz association, 20/40 MHz switching, scan while connected, suspend/resume, IPS/LPS transitions, IQK/LCK debug success, and no band/channel or MAC power-off warnings.
