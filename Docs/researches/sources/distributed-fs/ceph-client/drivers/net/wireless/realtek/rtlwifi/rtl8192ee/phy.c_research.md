# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.c

## Purpose
`phy.c` owns RTL8192EE baseband and RF programming: BB/RF register access, MAC/BB/RF table loading, transmit-power derivation, channel and bandwidth switching, scan-time DIG/CCA adjustments, IQ calibration, LC calibration, antenna path switching, and RF power-state transitions.

## Important APIs, Types, And Functions
Public functions include BB/RF query/set helpers, `rtl92ee_phy_mac_config`, `rtl92ee_phy_bb_config`, `rtl92ee_phy_rf_config`, `rtl92ee_phy_config_rf_with_headerfile`, original-value capture, tx-power get/set, scan backup/restore, bandwidth and channel switching, IQ/LC calibration, RF path switch, IO command dispatch, and RF power-state control. Important internal helpers are `_rtl92ee_phy_rf_serial_read/write`, `_check_condition`, register-table loaders, tx-power-by-rate conversion, `_rtl92ee_phy_sw_chnl_step_by_step`, IQK path routines, IQK matrix fill/save/restore helpers, and `_rtl92ee_phy_set_rf_power_state`.

## Control Flow
BB config initializes `phyreg_def`, enables BB/RF functional blocks, loads PHY register and AGC tables from `table.h`, optionally loads PG tx-power data, converts absolute dBm table values into relative offsets, and applies crystal-cap settings. RF config delegates to RF6052 setup. Register tables support conditional sections marked by magic values and matched against board type, interface, and platform. Channel switching builds pre/RF/post command arrays, sets tx power first, then writes `RF_CHNLBW` channel bits for every active RF path. Bandwidth switching updates MAC `REG_BWOPMODE`, response sideband fields, BB modulation mode, CCK/OFDM sideband controls, and RF6052 bandwidth bits.

## State And Persistence Behavior
State is cached in `rtlpriv->phy`: RF path register definitions, RF channel values, tx-power by-rate offsets and bases, current channel/bandwidth, in-progress flags, backup RF register values, default initial gain, framesync, calibration backups, IQK matrix per channel, and current IO command. EFUSE tx-power tables and regulatory mode feed power index calculations. RF power state is persisted in `ppsc->rfpwr_state`, with last-awake/sleep timestamps.

## Dependencies And Integration Points
This file depends on `reg.h` constants, `table.h` generated register arrays, local `rf.c` for RF6052 configuration, `dm.c` for DIG/CCA writes, PCI rings for RF-off queue draining, power-save helpers for NIC disable/enable, and `hw.c` for `HW_VAR_IO_CMD` and RF/LPS interaction. It is timing-sensitive and relies on `udelay`/`mdelay` around serial RF and calibration sequences.

## Risks
The code is register-table and magic-value heavy; incorrect table parsing or condition matching can silently misprogram hardware. Several loops time out but continue, so failures may appear later as weak RF performance. `_rtl92ee_phy_init_tx_power_by_rate` uses nested loops without resetting inner loop counters per outer iteration, so only part of the intended matrix may be zeroed. Channel switching warns on channels above 14 even though helper tables include 5 GHz channel places, suggesting this variant is effectively 2.4 GHz focused or incomplete for 5 GHz. RF-off waits can delay while queues drain and may still proceed after busy timeout.

## Test Signals
Signals include correct BB/RF table load logs, stable RF serial readback, channel changes updating RF channel bits, tx-power registers matching EFUSE-derived expectations across CCK/OFDM/MCS rates, bandwidth changes working in 20 and 40 MHz, scan pause/restore lowering/restoring DIG and CCA thresholds, IQK success logs with stored matrix, LC calibration completion outside active scan, RF on/off/sleep LED and queue-drain behavior, and throughput/RSSI sanity after initialization.
