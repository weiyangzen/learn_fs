# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.c

## Purpose

`phy.c` implements RTL8188EE baseband and RF programming, RF register serialization, MAC/BB/RF parameter-table loading, TX-power computation and programming, bandwidth and channel switching, scan-related PHY IO commands, IQ calibration, LC calibration, RF path switching, and RF power-state transitions. It is the main physical-layer control file used by hardware initialization, dynamic management, and power management.

## Important APIs And Functions

Public register accessors are `rtl88e_phy_query_bb_reg()`, `rtl88e_phy_set_bb_reg()`, `rtl88e_phy_query_rf_reg()`, and `rtl88e_phy_set_rf_reg()`. RF accesses are serialized with `rtlpriv->locks.rf_lock` and implemented through `_rtl88e_phy_rf_serial_read()` and `_rtl88e_phy_rf_serial_write()`.

Configuration APIs are `rtl88e_phy_mac_config()`, `rtl88e_phy_bb_config()`, `rtl88e_phy_rf_config()`, and `rtl88e_phy_config_rf_with_headerfile()`. They load Realtek table arrays from `table.h`, apply conditional branches based on board/interface/platform, store TX-power original offsets from PG tables, initialize `rtlphy->phyreg_def`, and delegate RF6052 setup to `rf.c`.

Runtime APIs include `rtl88e_phy_set_txpower_level()`, `rtl88e_phy_get_txpower_level()`, `rtl88e_phy_set_bw_mode()`, `rtl88e_phy_sw_chnl()`, `rtl88e_phy_scan_operation_backup()`, `rtl88e_phy_iq_calibrate()`, `rtl88e_phy_lc_calibrate()`, `rtl88e_phy_set_rfpath_switch()`, `rtl88e_phy_set_io_cmd()`, and `rtl88e_phy_set_rf_power_state()`.

## Control Flow

During `rtl88ee_hw_init()`, `rtl88e_phy_mac_config()` writes MAC table bytes, `rtl88e_phy_bb_config()` enables BB/RF functions and loads PHY/PG/AGC tables, and `rtl88e_phy_rf_config()` invokes RF6052 configuration, which calls back into `rtl88e_phy_config_rf_with_headerfile()`. After table programming, initialization reads RF channel state, selects RF path, runs IQK/LCK, and starts DM.

Channel switching is staged by `_rtl88e_phy_sw_chnl_step_by_step()`: precommands set TX power for the target channel, RF-dependent commands write `RF_CHNLBW` with the channel number for each RF path, and postcommands finish immediately. `rtl88e_phy_sw_chnl()` guards against concurrent bandwidth/channel work and halts on invalid stopped/IO states. Bandwidth switching writes MAC bandwidth registers, RRSR sideband fields, BB RF mode bits, CCK/OFDM sideband bits, and then calls `rtl88e_phy_rf6052_set_bandwidth()`.

TX-power flow starts from EFUSE tables loaded in `hw.c`. `_rtl88e_get_txpower_index()` derives CCK, OFDM, HT20, and HT40 indexes for the current channel and RF path. `_rtl88e_ccxpower_index_check()` updates current power indexes in `rtlphy`, and `rtl88e_phy_rf6052_set_cck_txpower()` / `rtl88e_phy_rf6052_set_ofdm_txpower()` write the hardware values. `dm.c` calls this path for thermal tracking and dynamic TX power.

IQK flow runs up to three calibration attempts, saving ADDA/MAC/BB registers, switching PI mode as needed, testing path A TX/RX and optionally path B, comparing candidate results with tolerance, filling IQK matrices, and saving the chosen matrix for recovery. LC calibration waits briefly for scans to stop, pauses TX or changes RF mode, toggles RF channel calibration, waits 100 ms, and restores state.

RF power-state flow in `rtl88e_phy_set_rf_power_state()` delegates to `_rtl88ee_phy_set_rf_power_state()`. ERFON may re-enable the NIC through `rtl_ps_enable_nic()` if halted by IPS or directly turns RF on. ERFOFF and ERFSLEEP wait for TX queues to drain with bounded loops, then either disable NIC for IPS/halt or put RF to sleep and update LEDs.

## State And Persistence Behavior

The file updates persistent runtime fields in `rtlpriv->phy`: RF register definitions, RF path/channel values, current TX-power indexes, original MCS TX-power offsets, default initial gains, framesync values, channel/bandwidth in-progress flags, IQK backups/results, RFPI state, LCK flag, IO command state, and RF type/path information. It also updates `rtlpriv->psc.rfpwr_state` on successful RF power changes. Hardware side effects include BB/RF tables, RF channel/bandwidth registers, TXAGC power registers, IQK/LC calibration registers, antenna path switches, scan CCA/IGI settings, RF sleep/on register sequences, and PCI TX-queue-dependent power decisions.

## Dependencies And Integration Points

`phy.c` depends on `wifi.h`, `pci.h`, `ps.h`, device register definitions, `rf.h`, `dm.h`, and large table arrays from `table.h`. It integrates with `hw.c` for initialization and power-state operations, `dm.c` for thermal tracking, DIG scan pause/resume, and antenna path decisions, `rf.c` for RF6052-specific TX power and RF config, and shared rtlwifi power-save helpers for NIC enable/disable.

## Risks And Edge Cases

The table parsers use sentinel values (`0xcdcdcdcd`, `0xDEAD`, `0xCDEF`, `0xCDCD`) and manual index increments; malformed table lengths can skip or overrun intended entries despite boundary guards. RF register access requires correct `phyreg_def` initialization before use. Channel switching only warns for channels outside 1-14 and is 2.4 GHz specific, despite some generic 5 GHz structures elsewhere. Calibration code has many magic register values and sleeps; running during scan, RF changes, or power transitions can affect traffic. RF power-off waits for queues but proceeds after bounded retries. IO scan pause/resume changes DIG/CCA but the write-DIG call is commented out in resume, so state and hardware can diverge if not otherwise refreshed.

## Test Signals

Coverage should include MAC/BB/AGC/RF table loading, conditional table branches for board/interface/platform values, RF register read/write serialization, channel switch across channels 1/6/11/14, bandwidth 20 and 20/40 with both sidebands, EFUSE-derived TX-power programming and default fallback, scan backup/restore, IQK success/failure/recovery paths, LCK while scanning, RF path switch for main/aux and antenna-diversity modes, ERFON/ERFOFF/ERFSLEEP transitions with queued TX traffic, and integration with DM thermal tracking and hardware init.
