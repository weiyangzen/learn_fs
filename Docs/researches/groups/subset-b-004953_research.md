# subset-b-004953 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c.c

## Purpose

`rtw8852c.c` is the main RTL8852C chip integration file for the Linux `rtw89` wireless driver. It binds the generic `rtw89` core to RTL8852C-specific MAC, BB, RF, efuse, channel, transmit-power, Bluetooth coexistence, WoWLAN, and firmware properties. Its final exported object, `rtw8852c_chip_info`, is the module-level descriptor consumed by bus-specific front ends and by the shared `rtw89` core.

The file does not implement a network stack by itself. It provides the hardware callback table and chip constants that let common driver code power the device, load parameters and firmware, configure channels, run RF calibrations, set transmit power, parse RX PPDU reports, and coordinate Wi-Fi/Bluetooth coexistence.

## Important APIs, types, and data

- `RTW8852C_FW_FORMAT_MAX`, `RTW8852C_FW_BASENAME`, and `RTW8852C_MODULE_FIRMWARE` define firmware naming and the maximum format version advertised through `MODULE_FIRMWARE`.
- Host flow-control and DLE memory data are split by HCI: `rtw8852c_hfc_param_ini_pcie`, `rtw8852c_hfc_param_ini_usb`, `rtw8852c_dle_mem_pcie`, `rtw8852c_dle_mem_usb2`, and `rtw8852c_dle_mem_usb3`.
- Register descriptor blocks such as `rtw8852c_page_regs`, `rtw8852c_imr_info`, `rtw8852c_rrsr_cfgs`, `rtw8852c_rfkill_regs`, `rtw8852c_dig_regs`, and `rtw8852c_edcca_regs` adapt shared MAC/PHY helpers to RTL8852C register addresses and masks.
- `rtw8852c_pwr_on_func()` and `rtw8852c_pwr_off_func()` implement the low-level power sequencing registered in `rtw8852c_chip_ops`.
- `rtw8852c_read_efuse()` parses logical efuse into `rtwdev->efuse`, `rtwdev->tssi`, and `rtwdev->efuse_gain`. It selects MAC address layout differently for PCIe and USB.
- `rtw8852c_read_phycap()` parses phycap TSSI trim, thermal trim, and PA bias trim into `rtwdev->tssi` and `rtwdev->pwr_trim`.
- Channel programming is split across `rtw8852c_set_channel_mac()`, `rtw8852c_set_channel_bb()`, and `rtw8852c_set_channel_rf()` from `rtw8852c_rfk.c`, with `rtw8852c_set_channel()` coordinating the full sequence.
- RF calibration callbacks in this file are wrappers around the RFK implementation: `rtw8852c_rfk_init()`, `rtw8852c_rfk_channel()`, `rtw8852c_rfk_band_changed()`, `rtw8852c_rfk_scan()`, and `rtw8852c_rfk_track()`.
- Transmit power entry points include `rtw8852c_set_txpwr()`, `rtw8852c_set_txpwr_ctrl()`, `rtw8852c_init_txpwr_unit()`, and exported-through-ops `rtw8852c_set_txpwr_ul_tb_offset()`.
- Bluetooth coexistence entry points include `rtw8852c_btc_set_rfe()`, `rtw8852c_btc_init_cfg()`, `rtw8852c_btc_set_wl_pri()`, `rtw8852c_btc_set_wl_txpwr_ctrl()`, `rtw8852c_btc_get_bt_rssi()`, `rtw8852c_btc_wl_s1_standby()`, and `rtw8852c_btc_set_wl_rx_gain()`.
- `rtw8852c_chip_ops` maps all RTL8852C-specific callbacks into the generic `struct rtw89_chip_ops` contract.
- `rtw8852c_chip_info` declares chip identity, firmware, table references, efuse geometry, RF path count, NSS, bands, bandwidths, coexistence thresholds, CAM capacities, H2C/C2H registers, power modes, and capability flags.

## Control flow

Device bring-up starts through the core calling `chip->ops->pwr_on_func`. `rtw8852c_pwr_on_func()` checks the HCI selection, adjusts regulator and suspend gating, waits for `B_AX_RDY_SYSPWR`, toggles platform enable, opens analog and RF-related XTAL SI controls, removes isolation, enables DMAC/CMAC blocks, and selects a BT log pinmux. Shutdown reverses the analog/RF gates, disables BB reset/function bits, requests OFFMAC, and then chooses PCIe or USB low-power behavior.

Efuse and phycap loading are separate early initialization flows. `rtw8852c_read_efuse()` casts the logical efuse map to `struct rtw8852c_efuse`, stores regulatory country, TSSI offsets, gain offsets, MAC address, RFE type, and XTAL cap. `rtw8852c_read_phycap()` parses trim bytes and later `rtw8852c_power_trim()` applies thermal and PA bias trim to RF registers when programming is available.

Channel changes follow a staged stop/configure/resume pattern. `rtw8852c_set_channel_help(enter=true)` stops scheduler TX, disables PPDU status, DFS, continuous TSSI, ADC, and BB activity. `rtw8852c_set_channel()` then writes MAC bandwidth/subcarrier state, updates BB channel and bandwidth state, spur notches, CCK/SCO coefficients, 5 MHz mask, BTG sharing, TX path, and RF channel/bandwidth registers. `rtw8852c_set_channel_help(enter=false)` restores PPDU status, ADC, DFS, continuous TSSI, BB reset state, and scheduler TX.

RFK channel calibration after association runs through `rtw8852c_rfk_channel()`: MCC channel info is captured, BTC is notified that connection RFK is active, RX DCK, IQK, TSSI, and DPK are run with BT-preservation windows, BTC is released, and firmware is notified about MCC RF state. Periodic tracking calls DPK, LCK, and RX DCK thermal trackers.

Transmit power programming is layered. `rtw8852c_set_txpwr()` writes by-rate power, offsets, TX-shape, limits, RU limits, antenna-gain power reference differences, and SAR-per-antenna limits. `rtw8852c_set_tx_shape()` chooses 2 GHz CCK DFIR shape from RFE/regulatory data and configures OFDM band-edge TSSI behavior. UL TB offset programming validates the signed offset range and writes 1TX/2TX MAC power offsets.

Bluetooth coexistence initialization programs PTA mode, priority masks, RF grant debug, RF TRX mask tables, BT break table, and BT counters. Runtime BTC callbacks adjust shared antenna metadata, priority bits, WL TX power under BT grants, RF standby, non-BTG BT TX coexistence BB/RF gain, and WL RX gain policy.

## State and persistence behavior

Most durable state is stored in the shared `struct rtw89_dev` rather than in file-static mutable variables. Efuse parsing writes `rtwdev->efuse`, `rtwdev->tssi`, and `rtwdev->efuse_gain`. Phycap parsing writes `rtwdev->pwr_trim` and additional TSSI trim arrays. `rtw8852c_bb_sethw()` samples BB gain offset base registers into `rtwdev->efuse_gain.offset_base[]` after BB parameter tables have been loaded.

Runtime channel and calibration state is shared with `rtw8852c_rfk.c` through `rtwdev->rfk_mcc`, `rtwdev->is_tssi_mode[]`, and the RFK substructures maintained there. `rtw8852c_rfk_init()` resets TSSI mode flags and MCC RFK state, initializes LCK/DPK, and runs initial RCK/DACK/RX-DCK.

The file maintains no persistent on-disk state. Firmware identity and module metadata are static. Hardware state persists only in registers, RF tables, and `rtwdev` fields for the lifetime of the device instance.

## Dependencies and integration points

This file depends heavily on common `rtw89` headers: `chan.h`, `coex.h`, `debug.h`, `fw.h`, `mac.h`, `phy.h`, `reg.h`, `sar.h`, and `util.h`. It also depends on chip-specific headers and generated tables: `rtw8852c.h`, `rtw8852c_rfk.h`, and `rtw8852c_table.h`.

The integration point to the rest of the kernel driver is `EXPORT_SYMBOL(rtw8852c_chip_info)`. Bus modules can bind this chip descriptor, while common code calls through `rtw8852c_chip_ops`. The file uses `read_poll_timeout()` for hardware readiness, `rtw89_mac_write_xtal_si()` for analog SI writes, `rtw89_phy_write32*()` and `rtw89_write_rf()` for BB/RF programming, `rtw89_btc_*()` for coexistence notifications, and `rtw89_fw_*()` for firmware H2C/C2H integration.

WoWLAN support is conditionally exposed under `CONFIG_PM` with a stub capability structure supporting magic packet, disconnect, and net-detect wake conditions.

## Risks and edge cases

- Power sequencing is register-order-sensitive. Reordering XTAL SI, isolation, platform-enable, or DMAC/CMAC enable writes can cause boot or suspend/resume failures.
- HCI-specific branches affect efuse MAC address offsets, flow control, DLE memory, power-off behavior, and PCIe calibration disable. USB and PCIe must both be validated.
- Channel code handles DBCC specially; incorrect path selection can program path B through PHY0 or miss path B under PHY1.
- Spur elimination uses hard-coded channel/spur mappings for 2 GHz, 5 GHz, and 6 GHz. New regulatory channel support or 160 MHz corner cases can require updates.
- TSSI, gain, thermal, and PA bias parsing treats `0xff` as unprogrammed data. Bad efuse maps can silently disable trim behavior or write default-like values.
- `rtw8852c_btc_set_rfe()` has version-specific layout handling for BTC module info. BTC firmware interface version changes are a compatibility risk.
- SAR and antenna-gain power offsets only program SAR by antenna for PHY0; DBCC and future multi-link behavior would need careful review.
- Many helpers write raw numeric registers and masks. Static compile coverage catches syntax and type errors, but semantic regressions usually require hardware or register-trace validation.

## Test signals

- Build with `CONFIG_RTW89_8852C`, `CONFIG_RTW89_PCI`, and USB support where applicable; warnings around enum conversions, packed efuse layout, and unused callbacks are useful signals.
- Boot/probe logs should show firmware request for `rtw89/rtw8852c_fw-*`, successful power-on, efuse parse, BB/RF table loading, and no MAC/BB/RF enable timeout.
- Exercise PCIe and USB variants because HFC, DLE, efuse address layout, and power-off paths differ.
- Validate association and channel changes on 2.4 GHz, 5 GHz, and 6 GHz, including 20/40/80/160 MHz. Watch for CCK enable only on 2 GHz, correct center/primary channel handling, and no spur-notching warnings.
- Run scan while connected to cover TSSI scan notification and TXAGC save/restore.
- Check RFK debug categories for DACK/IQK/TSSI/DPK/LCK completion and BTC RFK notifications around calibration windows.
- Verify Bluetooth coexistence with shared and dedicated antenna RFE types, including WL priority bits, BT RSSI conversion, and WL RX gain policies.
- Suspend/resume and WoWLAN wake tests should validate the power-off path, wake reason registers, and low-power HCI mode capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c.h

## Purpose

`rtw8852c.h` is the public chip header for the RTL8852C main integration unit. It defines the RTL8852C RF/BB path counts, the packed logical efuse layout interpreted by `rtw8852c.c`, and the external `rtw8852c_chip_info` symbol used by bus glue and common `rtw89` code.

## Important APIs, types, and data

- `RF_PATH_NUM_8852C` and `BB_PATH_NUM_8852C` both define a two-path device and are used by main and RFK code to size arrays and path loops.
- `struct rtw8852c_u_efuse` describes the USB-oriented efuse tail where the MAC address appears after `0x88` reserved bytes.
- `struct rtw8852c_e_efuse` describes the PCIe-style efuse tail with MAC address at the start of that union view.
- `struct rtw8852c_tssi_offset` defines per-path TSSI offset groups: CCK, 2 GHz MCS/BW40, reserved bytes, and 5 GHz one-stream BW40 offsets.
- `struct rtw8852c_efuse` defines the packed RTL8852C logical efuse map, including TSSI offsets for paths A/B, country/channel plan fields, XTAL, IQK/LCK controls, RFE and coexistence module fields, thermal bytes, RX gain offsets for 2/5/6 GHz subbands, 6 GHz TSSI groups, and a union of USB/PCIe MAC-address sublayouts.
- `extern const struct rtw89_chip_info rtw8852c_chip_info;` exposes the chip descriptor defined in `rtw8852c.c`.

## Control flow

This header has no executable control flow. It shapes runtime behavior through structure layout. `rtw8852c_read_efuse()` casts a logical efuse byte buffer to `struct rtw8852c_efuse` and then reads fields directly. HCI type selects either `map->e.mac_addr` for PCIe or `map->u.mac_addr` for USB, relying on the union at the end of the packed structure.

## State and persistence behavior

The structures in this header model persistent device-programmed efuse content. At runtime the driver copies this persistent hardware/OTP data into mutable `rtwdev` state: country code, MAC address, RFE type, XTAL cap, TSSI offsets, thermal baselines, and gain offsets. The header itself contains no mutable state.

Because `struct rtw8852c_efuse` is `__packed`, its offsets are an ABI-like contract with the hardware logical efuse map. Padding changes would be a functional regression.

## Dependencies and integration points

The header includes `core.h` for kernel integer types, `ETH_ALEN`, `struct rtw89_chip_info`, and TSSI group constants. It is included by `rtw8852c.c` and `rtw8852c_rfk.c`; the former consumes the efuse layout and exports the chip descriptor, while the latter uses path-count constants for calibration loops and static arrays.

The external symbol is consumed by driver modules that instantiate RTL8852C support. This makes the header the boundary between bus-specific code and the chip-specific implementation.

## Risks and edge cases

- Any change to reserved array sizes or field ordering changes efuse offsets. That can corrupt MAC address, country code, gain offset, RFE type, or TSSI interpretation.
- The USB/PCIe union is selected by runtime HCI type. If a new HCI layout is added, `rtw8852c_read_efuse()` must be updated with a corresponding sublayout.
- TSSI and gain offset fields use raw `u8` values that are later sign-decoded or treated as `0xff` invalid markers; type changes can alter sign behavior.
- The path-count macros must remain aligned with `rtw8852c_chip_info.rf_path_num`, `.tx_nss`, `.rx_nss`, and RFK table dimensions.

## Test signals

- Compile-time validation should catch missing constants from `core.h` and mismatched references from `rtw8852c.c`.
- Efuse parse logs should show expected MAC address, country code, RFE type, TSSI values, and gain offsets on both PCIe and USB devices.
- Hardware bring-up on cards with 6 GHz support is a useful signal because the layout includes 6 GHz TSSI and RX gain fields late in the structure.
- Static review should confirm `sizeof(struct rtw8852c_efuse)` remains compatible with `rtw8852c_chip_info.logical_efuse_size` and expected logical map offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk.h

## Purpose

`rtw8852c_rfk.h` declares the RTL8852C RF calibration and RF channel-control interface implemented by `rtw8852c_rfk.c`. It is the narrow boundary used by `rtw8852c.c` to register RFK callbacks in `rtw8852c_chip_ops` and to coordinate scan, channel-context, and channel-change behavior.

## Important APIs, types, and data

The header declares:

- `rtw8852c_mcc_get_ch_info()` for MCC/channel-context RFK table selection.
- One-shot calibration entry points: `rtw8852c_rck()`, `rtw8852c_dack()`, `rtw8852c_iqk()`, `rtw8852c_rx_dck()`, `rtw8852c_dpk()`, and `rtw8852c_tssi()`.
- Tracking and initialization entry points: `rtw8852c_rx_dck_track()`, `rtw8852c_dpk_init()`, `rtw8852c_dpk_track()`, `rtw8852c_lck_init()`, and `rtw8852c_lck_track()`.
- Scan/channel support: `rtw8852c_tssi_scan()`, `rtw8852c_tssi_cont_en_phyidx()`, `rtw8852c_wifi_scan_notify()`, `rtw8852c_set_channel_rf()`, and `rtw8852c_rfk_chanctx_cb()`.

All functions operate on `struct rtw89_dev *` plus PHY, channel, channel-context, or scan-state parameters. There are no exported types or mutable globals in the header.

## Control flow

The header itself has no executable logic. It defines the callable RFK flow surface:

- Initialization code in `rtw8852c.c` calls LCK/DPK init and initial RCK/DACK/RX-DCK through these declarations.
- Channel RFK code calls MCC info capture, RX DCK, IQK, TSSI, and DPK.
- Channel switching calls `rtw8852c_set_channel_rf()` after MAC and BB channel programming, and gates continuous TSSI with `rtw8852c_tssi_cont_en_phyidx()`.
- Periodic tracking calls DPK, LCK, and RX DCK trackers.
- Scan and channel-context code calls scan notification and RFK channel-context callback hooks.

## State and persistence behavior

The API is stateful through `struct rtw89_dev`. Callers do not pass calibration result buffers; implementations store and reuse calibration state inside `rtwdev->dack`, `rtwdev->iqk`, `rtwdev->rx_dck`, `rtwdev->dpk`, `rtwdev->tssi`, `rtwdev->lck`, and `rtwdev->rfk_mcc`. This means call order matters: init routines establish baselines and flags used by later channel and tracking routines.

## Dependencies and integration points

The header includes `core.h` for `struct rtw89_dev`, `struct rtw89_chan`, `enum rtw89_phy_idx`, and `enum rtw89_chanctx_idx`. It is included by `rtw8852c.c` and implemented by `rtw8852c_rfk.c`.

Its functions are integrated into the chip ops and channel-context listener rather than exported as standalone kernel symbols. The dependency direction is intentionally one-way: the main chip file knows the RFK public API, while the RFK implementation can use chip constants from `rtw8852c.h` and generated RFK tables.

## Risks and edge cases

- Prototype drift between this header and `rtw8852c_rfk.c` would break chip ops wiring at compile time.
- Callers must pass the correct PHY and channel-context index under DBCC/MCC. Incorrect inputs can select the wrong RF path or calibration cache.
- Several functions assume RFK state has been initialized. Calling trackers before `rtw8852c_lck_init()` or `rtw8852c_dpk_init()` can produce weak baselines or disabled calibration behavior.
- `rtw8852c_tssi_cont_en_phyidx()` requires a valid current channel pointer because enabling continuous TSSI rewrites efuse-derived DE values for that channel.

## Test signals

- A normal build should validate every declaration against its implementation and the `rtw8852c_chip_ops` assignments.
- Runtime RFK debug should show the declared entry points being reached in the expected order: init RFK, channel RFK, scan notifications, and track callbacks.
- DBCC/MCC tests should explicitly cover non-default PHY/channel-context parameters because most APIs carry those selectors.
- Channel-change tests should confirm `rtw8852c_set_channel_rf()` is paired with MAC/BB programming and that TSSI continuous enable/disable is restored around the change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk.h -->
