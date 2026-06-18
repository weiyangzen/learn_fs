# Research: subset-b-004934

This grouped report covers the Realtek rtw89 regulatory logic and RTL8851B chip/RF calibration files under `sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/regd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/regd.c

## Purpose

`regd.c` is the rtw89 regulatory-domain policy bridge between cfg80211/mac80211, Realtek firmware regulatory tables, efuse country programming, ACPI platform policy, and chip transmit-power programming. It maps alpha2 country codes to Realtek regulatory power domains for 2.4, 5, and 6 GHz; applies platform blocks for UNII-4 and 6 GHz operating classes; installs the wiphy regulatory notifier; and recalculates 6 GHz power/TPE limits when links become active or inactive.

The file is not a generic regulatory database. It owns Realtek-specific state in `rtwdev->regulatory`, then pushes consequences into `wiphy->bands[*]`, `wiphy->regulatory_flags`, TAS/antenna-gain block flags, and finally `rtw89_core_set_chip_txpwr()`.

## Important APIs, Types, And Data

- `COUNTRY_REGD()` builds `struct rtw89_regd` entries with alpha2, per-band `txpwr_regd[]`, and a `func_bitmap`.
- `rtw89_ww_regd` is the fallback worldwide domain. `rtw89_regd_is_ww()` relies on pointer identity with this object.
- `rtw89_regd_map[]` is the built-in country map. Firmware can override it through `rtwdev->fw.elm_info.regd`.
- `rtw89_alpha2_list_eu` expands the pseudo-country `EU` ACPI policy to individual ETSI/EU alpha2 entries.
- Public entry points are `rtw89_regd_get_string()`, `rtw89_regd_setup()`, `rtw89_regd_init_hint()`, and `rtw89_reg_6ghz_recalc()`.
- The installed cfg80211 callback is `rtw89_regd_notifier()`.

## Control Flow

Setup starts in `rtw89_regd_setup()`. It selects the regulatory map source from firmware ELM data or the built-in map, initializes `reg_6ghz_power` to default, applies ACPI regulatory-rule overrides, validates `wiphy`, then configures UNII-4 and 6 GHz policy before assigning `wiphy->reg_notifier`.

Initial country selection happens in `rtw89_regd_init_hint()`. If efuse contains a known non-worldwide country, the driver stores that `regd`, marks it programmed, sets `REGULATORY_COUNTRY_IE_IGNORE` and `REGULATORY_STRICT_REG`, and calls `regulatory_hint()`. If efuse is worldwide/unknown, it leaves country choice to the stack.

Runtime cfg80211 updates enter `rtw89_regd_notifier()`. The function takes the wiphy lock, exits power-save mode, applies the requested alpha2 unless efuse country is programmed, applies UNII-4, 6 GHz, TAS, and dynamic antenna gain policies, then recomputes chip transmit power.

6 GHz recalculation is split by dependency order. `rtw89_reg_6ghz_recalc()` first calls `rtw89_reg_6ghz_power_recalc()` to update each link's AP power type and the aggregate `regulatory->reg_6ghz_power`; only then it calls `rtw89_reg_6ghz_tpe_recalc()` because TPE constraints are meaningful only for standard-power links.

## State And Persistence

State is in memory under `rtwdev->regulatory`: selected `regd`, control map pointer/count, `programmed`, bitmaps for blocked UNII-4/6 GHz/SP/VLP countries, UK rule behavior, aggregate 6 GHz power type, and aggregate TPE constraint. Per-link state lives in `rtwvif_link->reg_6ghz_power` and `rtwvif_link->reg_6ghz_tpe`.

There is no file persistence. Persistent input comes from efuse country code, firmware ELM regulatory data, and ACPI DSM policy results. The file can permanently remove the 6 GHz supported band for the lifetime of the wiphy by freeing `wiphy->bands[NL80211_BAND_6GHZ]` when ACPI disables 6 GHz.

## Dependencies And Integration Points

The file depends on cfg80211 regulatory requests, mac80211 `wiphy`, Realtek ACPI DSM helpers from `acpi.h`, power-save exit via `rtw89_leave_ps_mode()`, and transmit-power refresh through `rtw89_core_set_chip_txpwr()`. It also touches TAS (`rtwdev->tas`) and antenna-gain (`rtwdev->ant_gain`) feature gating.

ACPI function dependencies include UNII-4 support, global 6 GHz disable, country block/allow policy, standard-power policy, very-low-power policy, and UK-vs-ETSI regulatory rule behavior. The code frees ACPI-allocated policy blobs with `kfree()`.

## Risks

- Country-map pointer identity is significant for worldwide fallback. Replacing map storage must preserve `rtw89_ww_regd` handling.
- `rtw89_regd_get_index()` subtracts the selected `regd` pointer from `regd_ctrl->map`; it is valid only for entries inside the active map and separately handles worldwide fallback.
- 6 GHz band removal frees `iftype_data` and the band object. Any later code must tolerate `wiphy->bands[6GHZ] == NULL`.
- Regulatory policy ordering matters: transmit power must be refreshed after policy changes, and 6 GHz TPE recalculation must follow power-type recalculation.
- `tpe_get_constraint()` encodes fixed hardware, antenna, and array gain offsets. Any regulatory interpretation change affects compliance.

## Test Signals

Useful signals are `RTW89_DBG_REGD` logs for ACPI policy decisions, country mapping, 6 GHz blocks, TPE recalculation, and power-type recalculation. Functional tests should cover efuse country vs worldwide behavior, cfg80211 user vs country-IE initiators, ACPI block/allow lists including `EU`, UNII-4 channel disabling, 6 GHz SP/VLP rejection, invalid TPE lower than `RTW89_MIN_VALID_POWER_CONSTRAINT`, and that `rtw89_core_set_chip_txpwr()` is called when aggregate regulatory state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/regd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b.c

## Purpose

`rtw8851b.c` is the RTL8851B chip descriptor and chip-operation implementation for the rtw89 driver. It provides hardware queue/memory geometry, firmware naming, interrupt/register layouts, efuse/phycap parsing, power sequencing, channel programming, baseband reset/setup, transmit-power setup, Bluetooth coexistence hooks, PPDU reporting, and the exported `rtw8851b_chip_info`.

Most helpers are `static`, but many are reachable through `rtw8851b_chip_ops`, which is referenced by `rtw8851b_chip_info.ops`. Bus-specific rtw89 PCIe/USB modules bind to this descriptor to operate the chip.

## Important APIs, Types, And Data

- Firmware: `RTW8851B_FW_BASENAME`, `RTW8851B_FW_FORMAT_MAX`, `MODULE_FIRMWARE()`.
- Queue/memory tables: `rtw8851b_hfc_param_ini_{pcie,usb}` and `rtw8851b_dle_mem_{pcie,usb2,usb3}`.
- Register-layout descriptors: page registers, IMR info, XTAL info, RRSR config, RF-kill GPIO, DIG registers, EDCCA registers.
- Efuse parsing entry: `rtw8851b_read_efuse()`, using `struct rtw8851b_efuse` from `rtw8851b.h`.
- Phycap parsing entry: `rtw8851b_read_phycap()`.
- Chip ops: `rtw8851b_chip_ops`.
- Exported descriptor: `const struct rtw89_chip_info rtw8851b_chip_info`.

## Control Flow

Power-on `rtw8851b_pwr_on_func()` clears suspend/LPS gates, waits for system power readiness, toggles platform enable, configures XTAL SI paths, releases isolation, reads chip version from efuse when needed, enables DMAC/CMAC blocks, and sets pinmux state. Power-off performs the reverse XTAL/RF isolation sequence, polls off-MAC completion, and diverges by HCI type for PCIe vs USB low-power handling.

Efuse parsing copies country code, MAC address selected by HCI type, RFE type, XTAL trim, TSSI offsets, thermal value, and RX gain offsets into `rtwdev`. Phycap parsing fills TSSI trim, thermal trim, PA bias trim, gain compensation, and ADC timing data.

Channel programming is layered: `rtw8851b_set_channel()` calls MAC, BB, then RF setup. MAC setup writes bandwidth/subcarrier/rate-check state. BB setup sets CCK SCO thresholds, band selection, bandwidth registers, CCK enable, NBI/CSI spur mitigation, BT share path fields, encoded channel index, 5 MHz mask, CFR shape, and a BB reset. RF setup is delegated to `rtw8851b_set_channel_rf()` in `rtw8851b_rfk.c`.

RF calibration orchestration is also layered. `rtw8851b_rfk_init()` initializes LCK/DPK/AACK/RCK/DACK/RX-DCK. Per-channel RFK (`rtw8851b_rfk_channel()`) notifies BTC, runs RX-DCK, IQK, TSSI, and DPK with BT time preservation, then clears the BTC notification. Periodic tracking runs DPK and LCK tracking.

Transmit-power setup calls common PHY helpers for by-rate, offset, limit, and RU limit, plus RTL8851B-specific TX shape and TX power reference initialization. UL TB power offset validates a signed range and writes one- and two-stream fields, even though this chip is one-stream.

## State And Persistence

The file populates persistent runtime state in `rtwdev->efuse`, `rtwdev->tssi`, `rtwdev->efuse_gain`, `rtwdev->pwr_trim`, `rtwdev->hal`, `rtwdev->btc`, `rtwdev->is_tssi_mode`, and baseband gain caches. It reads one-time-programmed efuse/phycap data but does not write persistent storage.

Hardware state is persistent until reset or power-cycle through direct MMIO, MAC TX-power, PHY, and RF writes. Important examples are DLE/HFC geometry, DMAC/CMAC enables, pinmux/RFE GPIO settings, BB gain offsets, notch/CSI spur filters, TSSI tracking toggles, and BTC coexistence LUTs.

## Dependencies And Integration Points

`rtw8851b.c` integrates with common rtw89 core, MAC, PHY, firmware, efuse, txrx, and coexistence code. It consumes RFK routines declared in `rtw8851b_rfk.h` and register tables in `rtw8851b_table.h`/`rtw8851b_rfk_table.h`. The Linux module exports `rtw8851b_chip_info` for bus-specific drivers and firmware loading.

BTC integration is broad: RFE metadata is translated to BTC module info, PTA is initialized, WL priority masks are configured, RF grant masks are written, WL TX power/RX gain can be controlled by coexistence policy, and PPDU reporting fills mac80211 RX status signal/frequency fields.

## Risks

- Power sequence polling and XTAL SI writes are order-sensitive; failures return early and can leave partial hardware state.
- Efuse layout is HCI-dependent for MAC address location. Wrong HCI type returns `-EOPNOTSUPP`.
- Several helpers assume one RF/BB path (`RF_PATH_NUM_8851B == 1`). Extending to a derived multi-path chip would require careful loops/table changes.
- Channel changes stop scheduling, disable PPDU status, TSSI, ADC, and BB reset around retune. Missing restore paths would break traffic.
- Spur mitigation has hard-coded channel cases and arithmetic. Off-by-one frequency/channel data would program invalid NBI/CSI tones.
- BTC RFE interpretation depends on versioned `fcxinit` structures and `rfe_type % 3` semantics.

## Test Signals

Test with probe/power-cycle logs, firmware load path, efuse/phycap dumps, successful MAC address and country code population, channel switch across 2G/5G/20/40/80 MHz, TX power table programming, WoWLAN stub exposure under `CONFIG_PM`, BTC initialization for shared and dedicated antenna RFE types, PPDU signal/frequency reporting, RFK sequence logs, and suspend/resume or USB/PCIe power-off paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b.h

## Purpose

`rtw8851b.h` declares the RTL8851B chip-facing efuse layout and exports the chip descriptor symbol. It is the shared contract between the chip implementation, bus modules, and code that casts the logical efuse map to RTL8851B-specific structures.

## Important APIs, Types, And Data

- `RF_PATH_NUM_8851B` and `BB_PATH_NUM_8851B` define this chip as one RF path and one baseband path.
- `struct rtw8851bu_efuse` and `struct rtw8851be_efuse` model USB and PCIe MAC-address placement.
- `struct rtw8851b_tssi_offset` stores CCK and MCS TSSI efuse offsets.
- `struct rtw8851b_efuse` is the packed logical efuse map consumed by `rtw8851b_read_efuse()`.
- `extern const struct rtw89_chip_info rtw8851b_chip_info` is the module-level exported chip descriptor.

## Control Flow

This header has no executable control flow. Runtime control flows through `rtw8851b_read_efuse()`, which casts a logical efuse buffer to `struct rtw8851b_efuse`, then copies fields into generic rtw89 state.

## State And Persistence

The structures describe persistent OTP/efuse data: country code, XTAL trim, IQK/LCK flags, customer and EEPROM metadata, RFE type, thermal trim, RX gain offsets, per-rate power indices, TSSI offsets, and bus-specific MAC address. The `__packed` annotations are essential because offsets must match hardware/firmware efuse layout rather than compiler alignment.

## Dependencies And Integration Points

The file includes `core.h` for rtw89 core types and constants such as `TSSI_*`, `ETH_ALEN`, and `struct rtw89_chip_info`. The layout is consumed by `rtw8851b.c` and indirectly by efuse loading code.

## Risks

- Any field insertion, removal, or alignment change can corrupt efuse parsing.
- The union at the end makes bus type part of the interpretation contract. Reading the wrong branch gives the wrong MAC address.
- Bitfields for power index differences depend on compiler layout assumptions within a packed hardware-format structure, matching the kernel driver's existing convention.

## Test Signals

Validate by comparing parsed MAC address for PCIe and USB variants, country code, RFE type, XTAL trim, thermal/TSSI values, and RX gain offsets against known efuse dumps. Compile-time coverage should catch missing constants or chip-info declaration mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.c

## Purpose

`rtw8851b_rfk.c` implements RTL8851B RF calibration and RF channel programming. It handles DACK, RX-DCK, IQK, DPK, RCK, AACK/LCK, TSSI setup/tracking, scan-time TSSI handling, thermal-triggered LCK tracking, and final RF bandwidth/channel writes. These routines are called by `rtw8851b.c` through chip ops and RFK wrappers.

The file is heavily register-sequence oriented. Its main job is to temporarily take ownership of RF/BB/KIP state, run calibration one-shots, store calibration results in `rtwdev`, restore normal state, and notify Bluetooth coexistence when Wi-Fi RF calibration is active.

## Important APIs, Types, And Data

- Public wrappers: `rtw8851b_aack()`, `rtw8851b_lck_init()`, `rtw8851b_lck_track()`, `rtw8851b_rck()`, `rtw8851b_dack()`, `rtw8851b_iqk()`, `rtw8851b_rx_dck()`, `rtw8851b_dpk_init()`, `rtw8851b_dpk()`, `rtw8851b_dpk_track()`, `rtw8851b_tssi()`, `rtw8851b_tssi_scan()`, `rtw8851b_wifi_scan_notify()`, and `rtw8851b_set_channel_rf()`.
- Calibration IDs and state machines are encoded in `enum dpk_id`, `enum dpk_agc_step`, and `enum rtw8851b_iqk_type`.
- Clock and mode enums (`rf_mode`, `adc_ck`, `dac_ck`) drive RF/ADC/DAC setup for calibration.
- Static TSSI DE register arrays map path A CCK/MCS bandwidth classes to register addresses.
- Backup register arrays preserve BB/RF/KIP state across IQK and DPK.

## Control Flow

DACK starts at `rtw8851b_dack()` -> `_dac_cal()`. It runs DRCK, disables manual DACK, manipulates RF mode, performs ADDCK, backs up and reloads ADDCK, runs DACK S0, runs new DADCK, dumps results, and marks `rtwdev->dack.dack_done`.

RX-DCK starts at `rtw8851b_rx_dck()`. It notifies BTC, stops scheduler TX, waits for RX mode, calls `_rx_dck()`, then resumes TX and notifies BTC completion. `_rx_dck()` saves RF state, optionally pauses TSSI tracking, forces RF RX mode, triggers RX DCK, swaps RXBB offsets into RF LUT, then restores state.

IQK starts at `rtw8851b_iqk()`. It notifies BTC, stops TX, initializes IQK state once, backs up BB/RF registers, forces calibration clocks, presets KIP/NCTL, runs LOK/TXK/RXK by band and wideband/narrowband mode, restores KIP/AFE/BB/RF state, resumes TX, and clears BTC notifications. Failure bits are stored in `rtwdev->iqk`.

DPK starts at `rtw8851b_dpk()`. It enables DPK state, backs up KIP/RF registers, records channel metadata, pauses TSSI if active, disables RXAGC and TSSI slope calibration, sets BB/AFE, runs `_dpk_main()` with KIP preset, TXAGC, TPG, AGC loop, IDL/MPA, parameter query, DPD enable, then restores KIP/RF/AFE/RXAGC/TSSI state. DPK tracking periodically reads thermal/TXAGC/TSSI offsets and updates DPD boundary power scale.

TSSI starts at `rtw8851b_tssi()` or scan-specific `rtw8851b_tssi_scan()`. It disables TSSI, programs system/TX power/DCK/thermal meter/DAC gain/slope/alignment tables from efuse and channel data, enables TSSI tracking, and writes efuse-derived DE values for CCK and MCS groups. Scan completion calls `_tssi_alimentk_done()` through `rtw8851b_wifi_scan_notify()`.

RF channel programming ends at `rtw8851b_set_channel_rf()`, which writes RF channel, bandwidth, and RXBB bandwidth through `_ctrl_ch()`, `_ctrl_bw()`, and `_rxbb_bw()`. `_set_ch()` includes LCK lock checks and recovery sequences if SYN lock is lost.

## State And Persistence

Persistent runtime state is stored in `rtwdev->dack`, `rtwdev->iqk`, `rtwdev->dpk`, `rtwdev->tssi`, `rtwdev->lck`, and `rtwdev->is_tssi_mode[]`. Calibration writes also persist directly in hardware RF/BB/KIP registers until reset/channel change/recalibration.

The file deliberately saves and restores many RF/BB registers around calibration to avoid leaking temporary calibration modes into normal operation. DPK stores per-path/current-index channel, bandwidth, thermal, TXAGC, gain, correlation, DC, and path-ok metadata for later tracking.

## Dependencies And Integration Points

The file depends on Realtek common RF/PHY/MAC helpers, `read_poll_timeout_atomic()`, RFK parser tables from `rtw8851b_rfk_table.h`, tracking tables from `rtw8851b_table.h`, BTC notifications from `coex.h`, channel context lookup through `rtw89_chan_get()`, and scheduler control through chip ops.

It is integrated into `rtw8851b.c`: `rtw8851b_rfk_init()`, per-channel RFK, scan notification, periodic RFK tracking, and RF channel programming all call these exported wrappers.

## Risks

- Calibration one-shots are timeout-sensitive. Several timeouts only log debug/warn and continue with fallback state.
- Many routines assume one RF path and hard-code `RF_PATH_A`; extending this logic would require table and loop changes.
- Backup/restore coverage is critical. Missing a register in backup arrays can leave KIP/RF in calibration mode.
- DPK AGC has bounded loops but many thresholds are magic hardware constants; changing them affects PA linearization.
- TSSI group interpolation and channel grouping must match efuse layout and regulatory/channel tables.
- Scan-time TSSI handling changes TXAGC offset on scan end; wrong ordering could affect transmit power after scans.

## Test Signals

Use `RTW89_DBG_RFK`, `RTW89_DBG_RFK_TRACK`, and `RTW89_DBG_TSSI` logs. Hardware validation should observe successful DACK/RX-DCK/IQK/DPK one-shot completion, no SYN lock failures after channel changes, sane TSSI thermal tables and DE writes from efuse, DPK path-ok and tracking updates, restored traffic after scheduler stop/resume, and stable RSSI/TX EVM across 2G/5G and 20/40/80 MHz channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.h

## Purpose

`rtw8851b_rfk.h` declares the RTL8851B RF calibration interface used by `rtw8851b.c`. It exposes calibration, tracking, scan-notification, TSSI, and RF channel setup routines while hiding the large register-sequence implementation in `rtw8851b_rfk.c`.

## Important APIs, Types, And Data

The header exports AACK/LCK/RCK/DACK, IQK, RX-DCK, DPK init/calibration/tracking, TSSI normal and scan setup, Wi-Fi scan notification, and RF channel programming. Function signatures use `struct rtw89_dev`, `enum rtw89_phy_idx`, `enum rtw89_chanctx_idx`, and `struct rtw89_chan`, keeping the interface aligned with rtw89 multi-PHY/channel-context abstractions even though RTL8851B is one-path.

## Control Flow

There is no implementation in the header. The control-flow contract is that chip setup calls init routines during hardware initialization, per-channel code calls IQK/RX-DCK/TSSI/DPK when channel context changes, periodic tracking calls DPK/LCK tracking, scan code calls `rtw8851b_wifi_scan_notify()`, and RF channel setup calls `rtw8851b_set_channel_rf()`.

## State And Persistence

The declared functions mutate `rtwdev` calibration state and hardware registers. The header itself stores no state, but its API passes enough context to bind calibration state to the active PHY and channel context.

## Dependencies And Integration Points

It includes `core.h` for rtw89 type definitions. It is included by `rtw8851b.c` and implemented by `rtw8851b_rfk.c`; table definitions remain private to the implementation.

## Risks

- Prototype changes require synchronized updates in `rtw8851b.c` chip-op glue and `rtw8851b_rfk.c`.
- The interface exposes no return values, so failure is observable mostly through logs and resulting hardware behavior.
- Callers must already handle scheduler stop/resume or rely on wrappers that do it internally; mixing low-level and high-level calibration entry points would be risky.

## Test Signals

Compile tests catch prototype drift. Runtime validation should confirm each chip-op path reaches the expected wrapper and that RFK logs appear during init, channel changes, scans, and periodic tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.h -->
