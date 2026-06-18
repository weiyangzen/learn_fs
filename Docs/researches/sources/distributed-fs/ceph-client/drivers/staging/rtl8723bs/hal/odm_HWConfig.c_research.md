# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.c

## Purpose

`odm_HWConfig.c` parses receive PHY status reports into signal/RSSI/EVM/CFO metrics, updates per-station smoothed RSSI for dynamic management, and dispatches table-driven RF/BB configuration header readers for RTL8723B. The source was read as a complete 446-line file.

## Important APIs, Types, and Functions

Important functions include `odm_signal_scale_mapping`, `odm_phy_status_query`, `ODM_ConfigRFWithHeaderFile`, `ODM_ConfigRFWithTxPwrTrackHeaderFile`, and `ODM_ConfigBBWithHeaderFile`. Internal helpers include `odm_query_rx_pwr_percentage`, `odm_evm_db_to_percentage`, `odm_cck_rssi`, `odm_rx_phy_status_parsing`, and `odm_Process_RSSIForDM`. It uses `struct phy_status_rpt_8192cd_t`, `struct odm_phy_info`, `struct odm_packet_info`, and station RSSI statistics.

## Control Flow

`odm_phy_status_query` first parses raw PHY status. CCK packets derive RSSI from LNA/VGA AGC report and signal quality from CCK SQ; OFDM packets derive per-path RSSI/SNR, all-path PWDB, EVM, and CFO tail. It then updates driver RSSI state unless RSSI test mode is active. RSSI smoothing tracks CCK and OFDM averages separately, maintains a packet map to weight mixed CCK/OFDM history, updates per-station undecorated smoothed RSSI, and counts beacon PHY queries. Configuration APIs select generated Realtek header-table readers according to RF/BB config type and SDIO interface.

## State and Persistence Behavior

The function mutates caller-supplied `odm_phy_info`, `dm_odm_t->PhyDbgInfo`, `RSSI_A`, `RSSI_B`, `RxRate`, CFO tracking state, and `sta_info->rssi_stat` smoothed fields. These values persist across packets and feed the ODM watchdog, rate adaptation, DIG, and firmware RSSI reports.

## Dependencies and Integration Points

It depends on raw PHY report layout from `odm_HWConfig.h`, descriptor rate constants, station pointer hooks in `dm_odm_t`, CFO parsing, generated hardware image functions such as `ODM_ReadAndConfig_MP_8723B_PHY_REG`, and register configuration wrappers.

## Risks and Edge Cases

`station_id == 0xFF`, invalid station pointers, or BSSID mismatch suppress RSSI updates. CCK RSSI conversion supports only specific LNA indices. The packet-map smoothing uses 64-bit history and must avoid stale initial values. The signal-scale mapping is SDIO-specific and returns zero for unsupported interfaces. CFO parsing only occurs on OFDM paths.

## Test Signals

Tests should cover CCK LNA/VGA conversions, OFDM per-path RSSI/SNR/EVM conversion, signal scaling boundaries, station RSSI smoothing for CCK-only/OFDM-only/mixed packet histories, beacon count increments, BSSID mismatch suppression, CFO parsing calls, and config dispatcher selection for RF radio, TX power limit, TX power tracking, PHY register, AGC, and PHY register page tables.
