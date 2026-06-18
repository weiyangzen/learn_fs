# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.c

## Purpose
This file implements dynamic management for the Realtek RTL8821AE/RTL8812AE PCI wireless driver. It is the runtime feedback loop that adjusts receiver initial gain, CCK packet detection, rate-adaptive masks, EDCA turbo parameters, CFO/crystal-cap tracking, thermal transmit-power tracking, and IQ/LCK calibration. It sits between mac80211 link state/statistics, rtlwifi shared state, chip-specific PHY helpers, firmware H2C commands, and direct MAC/BB/RF register programming.

The file also carries the swing and delta-swing lookup tables used to translate temperature/channel/rate conditions into BB swing or TxAGC compensation. It handles both the single-stream RTL8821AE path and the two-path RTL8812AE path, selecting behavior through `rtlhal->hw_type`, `rtlpriv->phy.rf_type`, and channel/rate state.

## Important APIs, Types, And Functions
Primary public entry points are `rtl8821ae_dm_init()`, `rtl8821ae_dm_watchdog()`, `rtl8821ae_dm_init_edca_turbo()`, `rtl8821ae_dm_init_rate_adaptive_mask()`, `rtl8821ae_dm_check_txpower_tracking_thermalmeter()`, `rtl8821ae_dm_initialize_txpower_tracking_thermalmeter()`, `rtl8821ae_dm_clear_txpower_tracking_state()`, `rtl8821ae_dm_txpower_track_adjust()`, `rtl8821ae_dm_update_init_rate()`, `rtl8821ae_hw_rate_to_mrate()`, `rtl8812ae_dm_txpower_tracking_callback_thermalmeter()`, `rtl8821ae_dm_txpower_tracking_callback_thermalmeter()`, and per-chip `*_dm_txpwr_track_set_pwr()` functions.

The central state is spread across `struct rtl_dm`, `struct dig_t`, `struct rate_adaptive`, `struct rtl_phy`, `struct rtl_hal`, `struct rtl_mac`, `struct rtl_efuse`, `struct false_alarm_statistics`, and `struct rtl_stats`. Important tables include `txscaling_tbl`, `rtl8821ae_txscaling_table`, EDCA per-peer tables, and per-band/per-path delta-swing tables for RTL8812AE and RTL8821AE.

Private control helpers include RSSI aggregation (`rtl8821ae_dm_find_minimum_rssi()`, `rtl8821ae_dm_check_rssi_monitor()`), false alarm sampling/reset (`rtl8821ae_dm_false_alarm_counter_statistics()`), DIG (`rtl8821ae_dm_dig()`), CCK threshold selection (`rtl8821ae_dm_cck_packet_detection_thresh()`), EDCA traffic selection (`rtl8821ae_dm_check_edca_turbo()`), CFO/ATC tracking (`rtl8821ae_dm_dynamic_atc_switch()`), and delta-swing table selection (`rtl8812ae_get_delta_swing_table()`, `rtl8821ae_get_delta_swing_table()`).

## Control Flow
Initialization runs through `rtl8821ae_dm_init()`: it clears LCK-in-progress under `iqk_lock`, initializes common RF-path information, initializes DIG from the current BB IGI register, enables driver-side RA mask control, clears EDCA turbo state, initializes thermal power tracking from efuse thermal meter values, and records the initial ATC/crystal-cap state.

The steady-state loop is `rtl8821ae_dm_watchdog()`. It first asks the hardware ops whether firmware power-save mode is active and whether firmware LPS RF is awake, suppressing dynamic work during P2P power save or RF transitions. Under `rf_ps_lock`, and only when RF is on and firmware is awake, it updates common info, samples false alarms, updates RSSI/FW RSSI reports, runs DIG, adjusts CCK detection thresholds, refreshes RA and basic rate masks, applies EDCA turbo, tracks CFO/ATC, triggers or completes thermal power tracking, and runs delayed IQ calibration after link establishment.

Transmit-power tracking is a two-stage loop. The check function alternates between triggering the RF thermal meter and calling the thermal callback. The callback averages recent thermal samples, computes deltas against previous, LCK, IQK, and efuse baseline values, may run LC/IQ calibration when thresholds are crossed, maps the thermal delta through per-band/per-rate swing tables, updates OFDM/CCK indices, then calls the per-chip set-power function in `MIX_MODE`. `MIX_MODE` clamps BB swing to rate-specific limits and pushes any excess or deficit into TxAGC by calling `rtl8821ae_phy_set_txpower_level_by_path()`.

DIG control samples OFDM/CCK false alarm counters, derives gain bounds from link state, RSSI, number of associated entries, and large-false-alarm recovery state, then writes IGI to path A and optionally path B. EDCA turbo compares interval TX/RX byte deltas and peer vendor to choose uplink or downlink BE parameters. CFO tracking uses `rtldm->cfo_tail[]` and `packet_count` to avoid stale samples, filters one large jump, updates crystal-cap registers when average CFO crosses dynamic thresholds, and restores efuse crystal cap when disconnected.

## State And Persistence
Persistent runtime state lives in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, `rtlpriv->falsealm_cnt`, `rtlpriv->stats`, `rtlpriv->phy`, and efuse-backed defaults. Notable fields include `txpower_track_control`, thermal history and indices, OFDM/CCK swing bases/current indices, remnant TxAGC offsets, `modify_txagc_flag_path_*`, `tm_trigger`, `tx_rate`, RSSI minima/maxima, `one_entry_only`, EDCA byte counters and turbo flags, CFO/crystal-cap history, and `linked_interval`.

State is not persistent across device reset except what is reloaded from efuse and driver structures during init. Hardware effects are direct register writes to BB/RF/MAC registers such as IGI, CCK CCA, EDCA BE, TXSCALE, RF thermal meter, crystal-cap fields, and rate/basic-rate controls through `cfg->ops`. The watchdog clears `num_qry_beacon_pkt` each tick after using it as a signal for weak beacon reception.

## Dependencies And Integration Points
The file depends on rtlwifi core headers (`wifi.h`, `base.h`, `pci.h`, `core.h`), chip headers (`reg.h`, `def.h`, `phy.h`, `dm.h`, `fw.h`, `trx.h`), and Bluetooth coexistence callbacks from `rtl_btc.h`. It calls firmware H2C reporting through `rtl8821ae_fill_h2c_cmd()` for RSSI, rate adaptation through `cfg->ops->update_rate_tbl()`, power/basic-rate hardware ops, PHY calibration and Tx-power helpers in `phy.c`, descriptor helpers for antenna selection, and mac80211 station lookup under RCU.

The watchdog is normally driven by rtlwifi periodic work. RX/TX paths feed it through `rtlpriv->stats`, `rtlpriv->dm.undec_sm_pwdb`, `rtldm->cfo_tail`, `rtldm->packet_count`, and beacon/non-BE debug counters. Firmware C2H rate reports call `rtl8821ae_dm_update_init_rate()`, which updates `rtldm->tx_rate` and immediately reapplies power tracking.

## Risks
Most risk is hardware-state drift: the code directly writes many chip registers and has separate one-path/two-path branches that can silently diverge. Thermal tracking has complex signed/unsigned index arithmetic and uses table sizes as bounds; wrong rate/channel classification can over- or under-compensate power. The RTL8821AE low-temperature branch calls the RTL8812AE set-power helper for one case, which is suspicious even if path A behavior overlaps.

DIG and CCK threshold tuning are sensitive to stale or noisy counters. RSSI monitoring uses static TX/RX byte baselines inside the function, so multiple devices would share those statics if the driver supports more than one instance. EDCA turbo relies on `is_any_nonbepkts` and interval byte deltas, so counter resets or missed watchdog ticks can temporarily program aggressive BE parameters. CFO/crystal-cap adjustment uses sampled packet counters and jump suppression; incorrect bounds or stale CFO tails can move oscillator compensation in the wrong direction.

Concurrency risk centers on `rf_ps_lock`, `iqk_lock`, RCU station lookup, and entry-list locking. Several helpers write hardware outside the narrower locks, so sequencing with power transitions and firmware LPS state is important. Test failures may manifest as reduced throughput, excessive false alarms, association instability, thermal drift, or poor coexistence rather than clean crashes.

## Test Signals
Useful signals include successful association/disassociation in station, AP, adhoc, and mesh modes; stable RSSI reports to firmware; RA mask transitions at high/mid/low RSSI; low and high false-alarm scenarios changing IGI as expected; CCK threshold transitions around 10/25 RSSI and high CCK false alarms; EDCA register changes only under BE-only traffic; thermal meter trigger/callback alternation; Tx power tracking under rising/falling temperature; LCK/IQK threshold behavior; CFO tracking with crystal-cap convergence; and no dynamic work while firmware LPS/RF-off/P2P PS is active.

Hardware-oriented regression tests should monitor BB/RF register traces, firmware H2C logs, throughput and PER, thermal-compensated EVM/power measurements, lockdep, KASAN, and multi-adapter behavior for the static counters in RSSI monitoring.
