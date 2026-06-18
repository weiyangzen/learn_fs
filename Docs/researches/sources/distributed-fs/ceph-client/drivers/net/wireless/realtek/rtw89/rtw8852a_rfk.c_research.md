# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.c

## Purpose
This file implements RTL8852A RF calibration for RTW89. It covers RCK, DACK, IQK, RX DCK, DPK, TSSI setup/tracking, and scan-related TSSI handling. It is invoked by `rtw8852a.c` chip callbacks during hardware initialization, channel changes, periodic tracking, and scan transitions.

## Important APIs, Types, and Data
- Public functions declared in `rtw8852a_rfk.h`: `rtw8852a_rck`, `rtw8852a_dack`, `rtw8852a_iqk`, `rtw8852a_rx_dck`, `rtw8852a_dpk`, `rtw8852a_dpk_track`, `rtw8852a_tssi`, `rtw8852a_tssi_scan`, `rtw8852a_tssi_track`, and `rtw8852a_wifi_scan_notify`.
- `_kpath()` maps DBCC and PHY index to RF path mask (`RF_A`, `RF_B`, or `RF_AB`).
- Backup/restore helpers save BB and RF registers around calibration sequences.
- DACK helpers calibrate ADC/DAC DC offsets, save MSBK/BIAS/DADCK/ADDCK values into `rtwdev->dack`, and reload them into path-specific registers.
- IQK helpers execute LOK, TXK, RXK, narrowband/wideband calibration, coefficient reads, and result recording into `rtwdev->iqk`.
- RX DCK helpers run AFE/RFC RX DC calibration while pausing TSSI when required.
- DPK helpers implement KIP setup, loopback RXIQK, AGC search, gain-loss/PAS checks, result fill, reload/bypass logic, and thermal tracking with results in `rtwdev->dpk`.
- TSSI helpers program RF/BB TSSI tables, EFUSE-derived DE offsets, thermal meter tables, slope/gap/PAK settings, high-power tracking decisions, PMAC pre-TX, and scan average/default TXAGC behavior.

## Control Flow
Initialization from `rtw8852a_rfk_init()` in the chip file runs RCK on both paths, then DACK and RX DCK. Per-channel RFK from `rtw8852a_rfk_channel()` runs RX DCK, IQK, TSSI, and DPK in sequence with coexistence notifications around the overall operation and BT time preservation around longer TSSI/DPK stages.

Each public calibration function stops scheduled TX where needed, waits for the selected RF paths to leave TX mode using `_wait_rx_mode()`, sends BTC RFK start/stop notifications, runs the internal calibration routine, and resumes TX.

DACK flow uses `_afe_init()`, ADDCK reset/trigger/backup/reload, DACK S0/S1 trigger/poll/backup/reload, and updates `dack_done`, timeout flags, and count. IQK flow initializes IQK state once, captures channel/bandwidth info, backs up BB/RF registers, sets MAC/BB calibration tables, presets coefficient selection, runs LOK/TXK/RXK per path, restores KIP/AFE/BB/RF state, and records fail bits. RX DCK flow iterates selected paths, optionally pauses TSSI, toggles RF DCK registers, waits, and restores path state.

DPK flow checks whether external PA FEM configuration should bypass DPK. Otherwise it optionally reloads a previous channel result, backs up state, pauses TSSI, configures BB/AFE/KIP, runs RF setup, RX DCK, AGC/sync/gain-loss loops, fills DPD coefficients and power-scale factors, enables or disables DPK per path, restores state, and later adjusts PWSF in `_dpk_track()` based on thermal delta and TSSI offsets.

TSSI flow disables TSSI, programs RF and BB TSSI tables per path and band, writes thermal-meter and EFUSE-derived CCK/MCS DE values, enables TSSI, decides high-power tracking, and runs a short PMAC packet TX to capture default TXAGC offsets. Scan notifications temporarily alter TSSI averaging and save/restore default TXAGC offsets.

## State and Persistence
Calibration results persist in `rtw89_dev`:
- `rtwdev->dack` stores ADDCK, DADCK, BIAS, MSBK arrays, timeout flags, `dack_done`, and `dack_cnt`.
- `rtwdev->iqk` stores initialization flags, channel/bandwidth/path metadata, LOK/TX/RX fail flags, coefficient backups, IQK table indexes, fail count, and diagnostic enable flags.
- `rtwdev->dpk` stores current backup index per path, per-path/channel DPK records including band/channel/bandwidth, thermal-at-DPK, TXAGC, PWSF, gain scaling, path_ok, and tracking correlation/DC values.
- `rtwdev->tssi` stores EFUSE/trim data read by `rtw8852a.c`, base thermal, default TXAGC offset, extra thermal offset, and tracking-check flags.
- `rtwdev->is_tssi_mode[]` gates thermal reads, RX DCK pause/resume, DPK pause/resume, and TSSI tracking.

Most operations also leave calibrated coefficients in BB/RF registers. The DPK reload path can reuse stored per-channel DPK entries instead of recalibrating if reload is enabled and channel matches, although the public `rtw8852a_dpk()` currently sets reload disabled before `_dpk()`.

## Dependencies and Integration Points
- Includes `coex.h`, `debug.h`, `mac.h`, `phy.h`, `reg.h`, `rtw8852a.h`, `rtw8852a_rfk.h`, `rtw8852a_rfk_table.h`, and `rtw8852a_table.h`.
- Heavy use of generated RFK table parsers such as `rtw89_rfk_parser()` and `rtw89_rfk_parser_by_cond()`.
- Uses RTW89 MAC helpers to stop/resume scheduled TX and PHY/RF helpers to read/write registers.
- Uses BTC notifications (`rtw89_btc_ntfy_wl_rfk`, `rtw89_btc_phymap`, `rtw89_btc_path_phymap`) so Bluetooth coexistence can reserve or account for calibration time.
- TSSI uses PMAC helpers from `rtw8852a.c` and TX power limit helpers from generic PHY code.

## Risks
- Calibration code is register-order-sensitive; missing restore paths can leave MAC/BB/RF in calibration mode and break normal traffic.
- Timeout handling mostly records debug flags and continues, so hardware failures can degrade RF performance without failing probe.
- DBCC path selection and path-specific offsets are easy to regress because many registers are computed as `base + (path << 8)` or `base + (path << 13)`.
- TSSI and DPK interact through `is_tssi_mode`, default TXAGC offsets, and extra thermal offsets; incorrect scan or tracking transitions can skew transmit power.
- EFUSE-derived TSSI/trim values from `rtw8852a.c` are trusted here; invalid values can propagate into DE tables and power tracking.

## Test Signals
- RFK debug logs should show RCK, DACK, IQK, RX DCK, DPK, and TSSI start/finish messages without repeated timeout reports.
- Association and throughput across 2.4 GHz/5 GHz and 20/40/80 MHz validate IQK/TSSI/DPK programming.
- Thermal drift tests should show DPK/TSSI tracking updating PWSF and offsets without power instability.
- Scan tests should exercise `rtw8852a_wifi_scan_notify()` and verify TSSI average/default TXAGC restoration after scan end.
- Bluetooth coexistence tests during RFK should verify BTC notifications prevent severe BT/Wi-Fi disruption.
