# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.c

Purpose: Implements shared RTL8192D PHY/RF helpers for RF serial access, BB/RF register definitions, TX-power index application, IQK/LCK calibration support, scan-time DIG pause/resume, MAC/PHY mode configuration, and channel-group mapping.

Important APIs/functions: `rtl92d_phy_query_rf_reg()` and `rtl92d_phy_set_rf_reg()` perform masked RF reads/writes. `rtl92d_phy_init_bb_rf_register_definition()` initializes path-specific register addresses. `rtl92d_store_pwrindex_diffrate_offset()` stores PHY_REG_PG power offsets. `rtl92d_phy_set_txpower_level()` calculates channel-adjusted CCK/OFDM power and calls RF6052 writers. `rtl92d_phy_enable_rf_env()`/`restore_rf_env()`, register save helpers, ADDA/MAC calibration setup, `rtl92d_phy_calc_curvindex()`, `rtl92d_phy_reset_iqk_result()`, `rtl92d_phy_set_io_cmd()`, and MAC/PHY mode helpers are exported to bus-specific PHY code.

Control flow: RF access serializes through `rtl92d_pci_lock()` for PCI, reads HSSI parameter/readback registers or writes LSSI address/data fields. TX-power flow converts the requested channel through `channel_all`, pulls EEPROM power indexes from `rtl_efuse`, optionally stores current CCX indexes, writes CCK power on 2.4 GHz, and always writes OFDM power. IO commands pause scan-time DM by backing up IGI and forcing a high/USB-specific IGI, or resume by restoring IGI and TX power. MAC/PHY mode flow writes `REG_MAC_PHY_CTRL_NORMAL` and derives RF type/band/current band by single/dual MAC mode and interface index.

State and persistence: Initializes `rtlphy->phyreg_def[]`, `mcs_offset`, `pwrgroup_cnt`, default initial gains, frame sync defaults, current TX power indexes, IQK matrix defaults, `current_io_type`, `set_io_inprogress`, `rf_type`, and `rtlhal` band/version fields. Writes BB/RF registers but no disk state.

Dependencies and integration: Depends on `dm_common` for DIG writes, `rf_common` for RF6052 TX-power programming, `reg.h` BB/RF register constants, channel5g data from shared definitions, and rtlwifi BB/RF access helpers. Called during hardware init, table loading, channel changes, IQK/LCK, scan handling, and EEPROM parsing.

Risks: Channel-to-index helpers assume valid inputs and use `channel_all` indices rather than raw channel numbers in several places. RF register accesses are timing-sensitive and rely on correct path definitions. `rtl92d_phy_get_chnlgroup_bypg()` is not exported unlike most helpers but is used within RF common. IO pause/resume changes DIG immediately and can affect scan sensitivity. The header includes duplicate sparse-only declarations around inline lock helpers.

Test signals: RF register read/write sanity, BB/RF table loading, channel switch over 2.4/5 GHz, TX power per channel and bandwidth, scan performance, IQK matrix reset/reload, sparse lock-context checks, and dual-MAC MAC/PHY mode validation.
