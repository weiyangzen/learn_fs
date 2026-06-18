# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk.c

## Purpose

`rtw8852c_rfk.c` implements RTL8852C RF calibration and RF channel programming for the `rtw89` driver. It covers DACK/DRCK, RCK, IQK, RX DCK, DPK, TSSI setup and scan handling, RF channel/bandwidth switching, LCK thermal tracking, and MCC channel-context RFK bookkeeping. The public functions declared in `rtw8852c_rfk.h` are called from `rtw8852c.c` through `rtw8852c_chip_ops` and channel-context listeners.

The file is hardware-sequencing heavy. Most code is structured as private one-shot helper stages that save register state, notify Bluetooth coexistence, stop TX when needed, run calibration firmware/NCTL commands or RFK table parsers, store results in `rtwdev` calibration substructures, and restore normal RX/TX state.

## Important APIs, types, and data

- `struct rxck_def` and `_ck480M`, `_ck960M`, `_ck1920M` describe ADC clock programming used by forced RX clock setup.
- TSSI DE address arrays such as `_tssi_de_cck_long`, `_tssi_de_mcs_20m`, and `_tssi_de_mcs_80m_80m` map RF path to BB registers used for efuse-derived digital error offsets.
- Backup arrays `rtw8852c_backup_bb_regs` and `rtw8852c_backup_rf_regs` define registers saved around IQK and DPK.
- RXK/TXK group arrays define band-specific gain and attenuation presets for narrowband and wideband IQK group selection.
- DPK constants and enums (`RTW8852C_DPK_VER`, `enum rtw8852c_dpk_id`, `enum dpk_agc_step`, `enum dpk_pas_result`) encode KIP/NCTL command IDs and AGC state-machine steps.
- `_kpath()` selects RF path mask based on DBCC state and PHY index. This is a central helper used by IQK, RX DCK, DPK, RF channel, and bandwidth programming.
- Public RFK APIs include `rtw8852c_rck()`, `rtw8852c_dack()`, `rtw8852c_iqk()`, `rtw8852c_rx_dck()`, `rtw8852c_rx_dck_track()`, `rtw8852c_dpk_init()`, `rtw8852c_dpk()`, `rtw8852c_dpk_track()`, `rtw8852c_tssi()`, `rtw8852c_tssi_scan()`, `rtw8852c_tssi_cont_en_phyidx()`, `rtw8852c_wifi_scan_notify()`, `rtw8852c_set_channel_rf()`, `rtw8852c_lck_init()`, `rtw8852c_lck_track()`, `rtw8852c_mcc_get_ch_info()`, and `rtw8852c_rfk_chanctx_cb()`.

## Control flow

RCK is the simplest flow. `rtw8852c_rck()` loops over both RF paths and `_rck()` temporarily resets RF, places the path into RX, triggers RCK through RF registers, polls for completion, writes the result back, and restores the saved RF register.

DACK starts at `rtw8852c_dack()`, which sends BTC start/stop notifications around `_dac_cal()`. `_dac_cal()` clears `dack_done`, saves RF modes, runs DRCK, forces RF into calibration mode, runs ADDCK and DACK with BTC one-shot notifications, backs up measured ADC/DAC/bias/MSBK data into `rtwdev->dack`, reloads it into BB registers, restores RF modes, marks `dack_done`, and increments `dack_cnt`. Timeout bits are recorded in `addck_timeout[]` and `msbk_timeout[]`.

IQK starts at `rtw8852c_iqk()`. It notifies BTC, stops scheduler TX, waits for selected paths to leave TX mode, initializes IQK state once, and calls `_iqk()`. `_iqk()` dispatches path A, path B, or both based on `_kpath()`. `_doiqk()` saves BB/RF registers, captures channel info, applies MAC/BB calibration settings, presets IQK coefficient table selection, runs LOK/TXK/RXK through `_iqk_by_path()`, restores coefficients and AFE/BB state, restores saved registers, and closes BTC notification. IQK stores failure flags, coefficient values, version, count, and channel metadata in `rtwdev->iqk`.

RX DCK starts at `rtw8852c_rx_dck()` or the thermal tracker. `_rx_dck()` selects paths, pauses TSSI tracking if active, forces RF RX mode, toggles RX DCK, checks base/current offsets, optionally rewrites outlier offsets from baseline values, records thermal reference values into `rtwdev->rx_dck`, and restores RF state. `rtw8852c_rx_dck_track()` skips 2 GHz and active scans, compares current thermal readings against saved RX DCK thermals, temporarily moves RF to an alternate target channel for recalibration when the threshold is exceeded, runs a deeper retry loop, and restores the original channel.

DPK starts at `rtw8852c_dpk()` with BTC notification, scheduler stop, and RX-mode wait. `_dpk()` checks bypass conditions for specific chip cuts or external PA configurations, otherwise calls `_dpk_cal_select()`. The calibration path optionally reloads existing per-band/channel DPK coefficients, backs up KIP and RF registers, records channel metadata in `rtwdev->dpk.bp`, pauses TSSI if active, disables RX AGC, sets BB/AFE and RF, runs KIP preset, AGC, sync, gain-loss, MDPD/IDL/MPA, parameter query, and DPK enable, then restores KIP/RF/AFE and resumes TSSI. `_dpk_track()` later compares thermal and TXAGC deltas against stored DPK parameters and updates power-scaling state for supported chip cuts.

TSSI setup starts at `rtw8852c_tssi()`. It chooses path range according to DBCC/PHY, disables current TSSI, then for each path applies TSSI system tables, TX power control tables, DCK tables, BB gain split, thermal meter table, slope/alignment defaults, and slope run. `_tssi_enable()` enables tracking and records base thermal; `_tssi_set_efuse_to_de()` maps current channel to CCK/MCS and trim groups, interpolates "extra group" values when needed, and writes digital error offsets to per-path BB registers. `rtw8852c_tssi_scan()` performs a lighter retune path for scan/band changes when TSSI mode is already active. `rtw8852c_tssi_cont_en_phyidx()` gates continuous TSSI around channel changes.

RF channel programming for the RF front end is exposed as `rtw8852c_set_channel_rf()`. It calls `rtw8852c_ctrl_bw_ch()`, which validates and writes RF channel/band selection for DAV and non-DAV register views, writes RF bandwidth fields, updates RXBB/TIA bandwidth, and handles a CAV path-B mirror workaround when DBCC is disabled.

LCK is initialized by `rtw8852c_lck_init()` storing current thermal values. `rtw8852c_lck_track()` periodically compares current EWMA thermal values to stored values and reruns `_lck()` when the delta exceeds `RTW8852C_LCK_TH`.

MCC support uses `rtw8852c_mcc_get_ch_info()` to select the active channel context, look up or allocate an RFK table index, and store channel/band metadata. `rtw8852c_rfk_chanctx_cb()` disables DPK during MCC start, reenables it on MCC stop, and reruns DPK for channel context 0.

## State and persistence behavior

All calibration state persists in `struct rtw89_dev` substructures for the device lifetime:

- `rtwdev->dack` stores ADDCK, DADCK, bias, MSBK arrays, timeout flags, `dack_done`, and `dack_cnt`.
- `rtwdev->iqk` stores initialization state, IQK mode flags, version, run count, channel/band/bandwidth per path, fail flags, LOK IDAC/VBUF, narrowband TX/RX CFIR coefficients, backup results, and MCC table indices.
- `rtwdev->rx_dck` stores per-path thermal references used by the RX DCK tracker.
- `rtwdev->dpk` stores enable/reload flags, current backup index per path, per-path/per-index band/channel/bandwidth, MDPD enable bits, path-ok state, calibration thermal, TXAGC, gain normalization, correlation/DC readings, and current K-set.
- `rtwdev->tssi` stores efuse TSSI groups, trim groups, thermal values, base thermal, and default TXAGC offsets saved around scans.
- `rtwdev->lck.thermal[]` stores thermal references for LCK retrigger decisions.
- `rtwdev->rfk_mcc.data` stores MCC channel/band descriptors and the active RFK table index.
- `rtwdev->is_tssi_mode[]`, `rtwdev->dbcc_en`, `rtwdev->scanning`, `rtwdev->hal.cv`, and FEM flags drive path selection and calibration bypass behavior.

The file writes no filesystem state. Hardware persistence is through BB/RF/MAC registers and coefficient memories loaded by RFK parser tables. Reload behavior for DPK is in-memory: `_dpk_reload_check()` matches current band/channel to cached `dpk->bp[path][idx]` entries and selects the coefficient index if available.

## Dependencies and integration points

This file includes `chan.h`, `coex.h`, `debug.h`, `fw.h`, `phy.h`, `reg.h`, `rtw8852c.h`, `rtw8852c_rfk.h`, `rtw8852c_rfk_table.h`, and `rtw8852c_table.h`. It depends on common register accessors (`rtw89_phy_write32_mask`, `rtw89_read_rf`, `rtw89_write_rf`), RFK table parsers (`rtw89_rfk_parser`, `rtw89_rfk_parser_by_cond`), channel helpers (`rtw89_chan_get`, `rtw89_get_entity_mode`, `rtw89_rfk_chan_lookup`), scheduler controls, BTC RFK notifications, and EWMA thermal readings.

The direct integration point is `rtw8852c_rfk.h`, consumed by `rtw8852c.c`. `rtw8852c.c` invokes these routines during chip initialization, channel changes, RFK channel events, scan notifications, RFK tracking, and channel-context callbacks.

The RFK code also coordinates with Bluetooth coexistence firmware via `rtw89_btc_ntfy_wl_rfk()`, `rtw89_btc_phymap()`, and connection-RFK notifications in the caller. During calibration it often stops Wi-Fi scheduler TX to prevent traffic from corrupting RF measurements.

## Risks and edge cases

- Path selection under DBCC is central. A mistake in `_kpath()` use or path loop bounds can calibrate the wrong RF path or leave a path uncalibrated.
- Calibration flows rely on exact save/restore ordering. Missed RF/BB restore after timeout can leave the device stuck in calibration, forced clock, disabled RXAGC, or TSSI-paused state.
- Polling timeouts in DACK, IQK, RX DCK, and DPK are logged but many flows continue with fallback or fail bits. Hardware may appear operational with degraded RF quality.
- TSSI group mapping is large and channel-specific for 2/5/6 GHz. Off-by-one errors can use the wrong efuse offset or trim group, especially extra/interpolated groups.
- DPK bypass is tied to chip cut and external PA flags. Wrong FEM metadata can either skip needed DPK or run unsafe DPK with external PA paths.
- `rtw8852c_rx_dck_track()` temporarily changes RF channel for recalibration. Failures before restoration would be high impact, though the current code restores after `_rx_dck()`.
- MCC handling disables DPK while MCC is active and reruns it afterward. Interactions with reload indices and channel context 1 require hardware testing.
- Several helper loops assume two RF paths and use raw `path << 8` or `path << 13` register offsets; future path-count changes would require broader changes than the path macros alone.

## Test signals

- Compile with RFK debug enabled and check for no format/type warnings around bitfields, sign extension, and enum path conversions.
- Probe logs should show initial RCK, DACK, LCK init, DPK init, and RX DCK without repeated timeout messages.
- Association on 2.4 GHz, 5 GHz, and 6 GHz should run RX DCK, IQK, TSSI, and DPK once per RFK channel event, with BTC start/stop notifications bracketing calibrations.
- DBCC/MCC scenarios should show path-specific calibration and `rtw8852c_mcc_get_ch_info()` table index changes without DPK remaining disabled after MCC stop.
- Thermal chamber or synthetic thermal-change testing should trigger LCK at delta >= 8 and RX DCK at delta >= 12 outside 2 GHz and outside scans.
- TSSI scan testing should preserve and restore default TXAGC offsets and update TSSI DE registers for the scanned channel.
- DPK reload testing should revisit a previous band/channel and observe coefficient reload rather than unnecessary recalibration when reload is enabled.
- Bluetooth coexistence testing should verify BTC RFK notifications and preserved BT time around TSSI/DPK calibration windows.
