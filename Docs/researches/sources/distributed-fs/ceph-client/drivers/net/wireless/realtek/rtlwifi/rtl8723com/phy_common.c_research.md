<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.c

## Purpose
Implements shared RTL8723 PHY helpers for BB register access, RF serial access, TX power conversion, RF register definition initialization, channel-switch command construction, IQ calibration matrix application, register backup/restore, ADDA path control, calibration MAC settings, path standby, and PI mode switching.

## Important APIs, Types, And Functions
- Register access: `rtl8723_phy_query_bb_reg`, `rtl8723_phy_set_bb_reg`, `rtl8723_phy_rf_serial_read`, and `rtl8723_phy_rf_serial_write`.
- Utility/setup: `rtl8723_phy_txpwr_idx_to_dbm`, `rtl8723_phy_init_bb_rf_reg_def`, and `rtl8723_phy_set_sw_chnl_cmdarray`.
- Calibration: `rtl8723_phy_path_a_fill_iqk_matrix`, `rtl8723_save_adda_registers`, `rtl8723_phy_save_mac_registers`, `rtl8723_phy_reload_adda_registers`, `rtl8723_phy_reload_mac_registers`, `rtl8723_phy_path_adda_on`, `rtl8723_phy_mac_setting_calibration`, `rtl8723_phy_path_a_standby`, and `rtl8723_phy_pi_mode_switch`.
- Uses `struct rtl_priv`, `struct rtl_phy`, `struct bb_reg_def`, `struct swchnlcmd`, `enum radio_path`, `enum wireless_mode`, and many BB/RF register constants.

## Control Flow
BB access helpers read/modify/write selected bit fields using `calculate_bit_shift`. RF serial read programs the LSSI read address and edge, waits 120 microseconds, selects PI or non-PI readback register, and returns RF data. RF serial write packs 8-bit offset plus 20-bit data into the three-wire register. RF register definition initialization fills the `rtlphy->phyreg_def[]` table for paths A through D. Channel command setup bounds-checks the command table before writing one entry. IQK matrix fill applies signed calibration results to TX/RX IQ imbalance registers unless no final candidate exists or TX-only mode is requested. Backup/restore helpers snapshot and restore ADDA/MAC registers. ADDA setup differs for RTL8723AE and RTL8723BE hardware type.

## State And Persistence
The file mutates BB/RF hardware registers, RF definition tables in `rtlphy`, calibration backup arrays supplied by callers, and command-table entries. Calibration and RF serial writes persist in hardware until reset, reload, or channel/calibration changes.

## Dependencies And Integration Points
Used by both RTL8723AE and RTL8723BE PHY code. It depends on `phy_common.h`, rtlwifi BB/RF register accessors, RTL8723AE register constants for shared aliases, and chip-specific hardware type checks. Several functions are exported with `EXPORT_SYMBOL_GPL` for chip modules.

## Risks And Edge Cases
`RT_CANNOT_IO(hw)` is currently defined as false, so IO-suppression paths are dead unless that macro changes. RF serial timing and bit packing are hardware-sensitive. RF definition table initialization must match every path's register aliases before RF operations run. IQK math sign-extends 10-bit values manually; mistakes affect calibration quality. Channel command setup silently fails on out-of-bounds indexes.

## Test Signals
Signals include successful BB/RF reads and writes, RF initialization on both AE and BE, channel switching command execution, IQK calibration pass/fail behavior, restored register snapshots after calibration, stable RSSI/EVM after PI mode switches, and no warnings from null or oversized switch-command tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/phy_common.c -->
