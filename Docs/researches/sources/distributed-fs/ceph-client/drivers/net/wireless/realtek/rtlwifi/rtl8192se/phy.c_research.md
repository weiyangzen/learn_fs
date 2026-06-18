# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.c

## Purpose
This file implements RTL8192SE PHY, baseband, RF, channel, bandwidth, RF-power, transmit-power, firmware-command, EPHY/ASPM, and beacon-timing control. It bridges table-driven BB/RF initialization, EFUSE-derived power data, dynamic-management firmware commands, and low-level RF serial register access.

## Important APIs, Types, And Functions
Public register APIs are `rtl92s_phy_query_bb_reg()`, `rtl92s_phy_set_bb_reg()`, `rtl92s_phy_query_rf_reg()`, and `rtl92s_phy_set_rf_reg()`. Configuration entry points are `rtl92s_phy_mac_config()`, `rtl92s_phy_bb_config()`, `rtl92s_phy_rf_config()`, `rtl92s_phy_config_rf()`, and `rtl92s_phy_get_hw_reg_originalvalue()`. Runtime control APIs include `rtl92s_phy_scan_operation_backup()`, `rtl92s_phy_set_bw_mode()`, `rtl92s_phy_sw_chnl()`, `rtl92s_phy_set_rf_power_state()`, `rtl92s_phy_set_txpower()`, `rtl92s_phy_set_fw_cmd()`, `rtl92s_phy_chk_fwcmd_iodone()`, `rtl92s_phy_switch_ephy_parameter()`, and `rtl92s_phy_set_beacon_hwreg()`.

Internal helpers implement RF 3-wire serial read/write, table command arrays for channel switching, RF sleep, PA bias current correction, power-group offset storage, register-definition initialization, BB/AGC/table programming, RF-path-specific tables, transmit-power index selection, and firmware command post-processing.

## Control Flow
During init, `rtl92s_phy_bb_config()` initializes register-definition mappings, programs PHY and AGC tables, applies RF-type-specific BB overrides, applies PG power tables when EFUSE autoload succeeded, reads path enable maps, and validates RF path count against RF type. `rtl92s_phy_rf_config()` sets total RF paths and delegates RF6052 configuration, while `rtl92s_phy_config_rf()` writes path A/B RF tables and adjusts PA bias for inferior ICs.

At runtime, bandwidth changes guard against concurrent channel/bandwidth work and stopped HAL state, update MAC/BB 20/40 MHz bits, set sideband fields, and call RF6052 bandwidth setup. Channel switching builds pre/RF/post command arrays, first reapplies transmit power, then writes RF channel bits for every active RF path. RF power state transitions bring the NIC out of halted IPS through `rtl_ps_enable_nic()`, wake from sleep by enabling TX/CCA, enter sleep after waiting for non-beacon TX queues to drain, or halt through PCI power-save helpers.

Firmware commands use `rtl92s_phy_set_fw_cmd()` to choose between newer command-map bits and older WFM5 post-processing depending on firmware version. `_rtl92s_phy_set_fwcmd_io()` handles legacy RA, IQK, scan pause/resume, high-power, LPS, A2 entry, and driver-controlled DM commands with completion polling.

## State And Persistence
State lives in `rtlphy` fields such as `phyreg_def[]`, `rf_pathmap`, `num_total_rfpath`, `rfreg_chnlval[]`, `current_channel`, `current_chan_bw`, channel/bandwidth in-progress flags, default initial gain, frame sync, MCS power offsets, current CCK/OFDM power indices, and CCK high-power flag. Power-save state lives in `ppsc`, including RF power state, halt level, sleep/awake jiffies, and RF-off reason. Firmware command state lives in `rtlhal->set_fwcmd_inprogress`, `current_fwcmd_io`, and command map/parameter registers.

## Dependencies And Integration Points
This file depends on Realtek register definitions, table arrays from `table.c`, RF6052 helpers in `rf.c`, firmware command macros from `fw.h`, dynamic-management state from `dm.h`, PCI queue state for RF sleep, power-save helpers in `../ps.h`, and hardware GPIO helpers from `hw.c`. It is called from `hw.c` during init and from rtlwifi HAL ops during scan, channel, bandwidth, RF power, and BB/RF register operations.

## Risks
RF serial access is protected by `rf_lock`, but BB writes are not similarly serialized; callers must avoid conflicting channel/bandwidth/DM operations. Channel switching validates channels 1-14 only with `WARN_ONCE` but still writes the provided channel bits, so invalid channel state can reach hardware. RF sleep waits on TX queues with a bounded loop and may sleep while frames remain. Firmware command paths have multiple version-dependent encodings; wrong firmware version assumptions can leave command bits uncleared or skip needed post-processing. Table programming uses raw vendor arrays and delays; ordering changes can break RF calibration. EPHY switching writes magic values for ASPM/backdoor clock-request behavior and is platform-sensitive.

## Test Signals
Test BB/RF read/write helpers, cold init table programming, RF type/path-map validation, channel 1-14 switching, 20/40 MHz changes with sideband selection, scan pause/restore, IPS/LPS enter/leave, RF kill, TX queue drain before sleep, firmware command completion, transmit-power updates across channels, and ASPM/EPHY behavior across suspend/resume. Hardware validation should include 1T1R, 1T2R, and 2T2R boards.
