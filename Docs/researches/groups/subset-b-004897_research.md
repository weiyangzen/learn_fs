# subset-b-004897 research

Work item: `subset-b-004897`

This grouped report covers the RTL8821AE/RTL8812AE PHY, register, and power-sequence files in source-tree order. Each file section is wrapped for reconciliation into the required per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.c

## Purpose

`phy.c` is the RTL8821AE/RTL8812AE physical-layer implementation for the PCIe `rtlwifi` driver. It owns baseband and RF register access, MAC/BB/RF table programming, channel and bandwidth switching, transmit-power derivation and programming, scan-time dynamic-management pauses, RF power-state transitions, antenna/RFE path switching, and RTL8821AE IQ calibration. It is the main bridge between the common `rtlwifi` core state (`struct rtl_priv`, `struct rtl_phy`, `struct rtl_hal`, efuse and DM state) and the chip-specific register tables declared in `table.h` plus register definitions in `reg.h`.

The file serves both `HARDWARE_TYPE_RTL8821AE` and `HARDWARE_TYPE_RTL8812AE`. Many code paths branch on `rtlhal->hw_type`, current band, RFE type, BT coexistence flags, efuse regulatory mode, and RF path count. RTL8812AE gets table selection and RFE handling, but its IQ calibration entry point is currently empty, while RTL8821AE has a large path-A IQK routine.

## Important APIs, Types, and Functions

Public APIs declared in `phy.h` and implemented here include:

- `rtl8821ae_phy_query_bb_reg()` and `rtl8821ae_phy_set_bb_reg()` read and update masked baseband registers through `rtl_read_dword()` and `rtl_write_dword()`.
- `rtl8821ae_phy_query_rf_reg()` and `rtl8821ae_phy_set_rf_reg()` serialize RF access under `rtlpriv->locks.rf_lock` and call the private 3-wire serial helpers.
- `rtl8821ae_phy_mac_config()`, `rtl8821ae_phy_bb_config()`, and `rtl8821ae_phy_rf_config()` perform staged MAC, baseband, AGC, power-limit, PG, crystal-cap, and RF6052 setup.
- `rtl8821ae_phy_switch_wirelessband()`, `rtl8821ae_phy_set_bw_mode()`, `rtl8821ae_phy_set_bw_mode_callback()`, `rtl8821ae_phy_sw_chnl()`, and `rtl8821ae_phy_sw_chnl_callback()` implement runtime band/channel/bandwidth changes.
- `rtl8821ae_phy_set_txpower_level()` and `rtl8821ae_phy_set_txpower_level_by_path()` calculate per-rate power indexes and program CCK, OFDM, HT, and VHT TX AGC registers.
- `rtl8821ae_phy_iq_calibrate()`, `rtl8821ae_do_iqk()`, and `rtl8821ae_reset_iqk_result()` manage RTL8821AE IQ calibration state and results.
- `rtl8821ae_phy_set_io_cmd()` gates scan-related dynamic-management pause/resume commands into `rtl8821ae_phy_set_io()`.
- `rtl8821ae_phy_set_rf_power_state()` transitions RF on/off and coordinates IPS NIC halt/resume, LED state, and TX queue draining.
- `rtl8812ae_phy_config_rf_with_headerfile()` and `rtl8821ae_phy_config_rf_with_headerfile()` are RF table loaders used by the RF6052 layer.
- `phy_get_tx_swing_8812A()` reads efuse or fallback swing settings and returns BB swing scaling for path A/B.

Key private helpers include:

- `_rtl8821ae_phy_rf_serial_read()` and `_rtl8821ae_phy_rf_serial_write()` implement RF register access through BB LSSI/PI/SI registers such as `RHSSIREAD_8821AE`, `RA_LSSIWRITE_8821A`, and `RB_LSSIWRITE_8821A`.
- `__rtl8821ae_phy_config_with_headerfile()` interprets Realtek header-array condition records and writes table entries only when board/cut/interface/package/RFE conditions match.
- `_rtl8821ae_check_positive()` and `_rtl8821ae_check_condition()` match conditional table entries against `rtlhal` and efuse board state.
- `_rtl8821ae_phy_init_tx_power_by_rate()`, `_rtl8821ae_phy_config_bb_with_pgheaderfile()`, `_rtl8821ae_phy_txpower_by_rate_configuration()`, `_rtl8812ae_phy_convert_txpower_limit_to_power_index()`, `_rtl8821ae_get_txpower_index()`, and `_rtl8821ae_phy_set_txpower_index()` form the TX power pipeline.
- `_rtl8812ae_phy_set_rfe_reg_24g()` and `_rtl8812ae_phy_set_rfe_reg_5g()` program external front-end pinmux/inversion by RFE type and BT coexistence.
- `_rtl8821ae_iqk_*()` helpers save MAC/BB/AFE/RF state, run repeated path-A LOK/TXK/RXK attempts, select stable calibration values, fill IQC registers, and restore state.

The file depends on common types and helpers from `wifi.h`, `pci.h`, `ps.h`, `efuse.h`, `btcoexist/halbt_precomp.h`, and the local `def.h`, `phy.h`, `rf.h`, `dm.h`, `table.h`, `trx.h`, `hw.h`, and `reg.h`.

## Control Flow

Initialization normally enters through the hardware ops table in the surrounding driver:

1. `rtl8821ae_phy_mac_config()` chooses the RTL8821AE or RTL8812AE MAC table and feeds it to `__rtl8821ae_phy_config_with_headerfile()`.
2. `rtl8821ae_phy_bb_config()` initializes BB/RF register-definition offsets, enables PCIe/BB/RF function blocks in `REG_SYS_FUNC_EN`, `REG_RF_CTRL`, and `REG_OPT_CTRL`, calls `_rtl8821ae_phy_bb8821a_config_parafile()`, programs crystal-cap bits in `REG_MAC_PHY_CTRL`, and snapshots register `0x837`.
3. `_rtl8821ae_phy_bb8821a_config_parafile()` initializes TX power-limit tables to `MAX_POWER_INDEX`, optionally loads regulatory power-limit strings, writes PHY register arrays, initializes and stores power-by-rate offsets from PG arrays, converts dBm offsets to relative values, converts power limits to power indexes, writes AGC tables, and records `cck_high_power`.
4. `rtl8821ae_phy_rf_config()` delegates to `rtl8821ae_phy_rf6052_config()`, which uses the exported RF header-file configuration functions in this file.

Runtime channel setup is layered:

1. `rtl8821ae_phy_sw_chnl()` rejects concurrent bandwidth/channel changes, waits for `lck_inprogress` to clear, switches 2.4 GHz/5 GHz band when the requested channel crosses channel 14, marks `sw_chnl_inprogress`, and calls `rtl8821ae_phy_sw_chnl_callback()`.
2. `rtl8821ae_phy_switch_wirelessband()` updates `rtlhal->current_bandtype`, enables/disables CCK behavior, writes RFE pinmux and AGC selection, waits for TX packet empty bits before 5 GHz changes, adjusts BB swing through `phy_get_tx_swing_8812A()`, and clears TX power tracking state.
3. `rtl8821ae_phy_sw_chnl_callback()` writes RFC area channel-group values, RF `RF_CHNLBW` channel/band fields for each RF path, and RTL8821AE-specific `RF_APK` values on 5 GHz.
4. `rtl8821ae_phy_sw_chnl()` then clears TX power tracking and reprograms TX power for the current channel.

Bandwidth setup similarly uses `rtl8821ae_phy_set_bw_mode()` to guard against concurrent changes and `rtl8821ae_phy_set_bw_mode_callback()` to write MAC protocol bandwidth bits, secondary-channel encoding at `0x0483`, BB RF mode fields, CCK sideband flags, L1 peak thresholds, spur workarounds, and RF6052 bandwidth state.

TX power programming starts from efuse bases and table offsets. The PG table loader stores packed dBm values by band/RF path/TX count/rate section. The conversion path stores section bases, converts packed table bytes to relative offsets, loads min regulatory limits per band/bandwidth/rate/channel, converts those limits relative to the section base, then `_rtl8821ae_get_txpower_index()` combines efuse channel bases, OFDM/HT/VHT diffs, regulatory per-rate deltas, DM remnant swing values, and `MAX_POWER_INDEX` clamping. `_rtl8821ae_phy_set_txpower_index()` maps each descriptor rate to the correct TX AGC byte lane.

IQ calibration for RTL8821AE is intentionally serialized. `rtl8821ae_phy_iq_calibrate()` checks `rtlphy->lck_inprogress`, sets it under `iqk_lock`, runs `_rtl8821ae_phy_iq_calibrate()`, and clears the flag. The calibration routine backs up MAC/BB/AFE/RF registers, configures MAC/CCA for calibration, runs path-A LOK/TXK/RXK up to `cal_num` attempts, chooses matching TX/RX X/Y pairs, writes IQC correction registers, restores RF/AFE/MACBB state, and leaves path B untouched. `rtl8812ae_phy_iq_calibrate()` is an empty stub, although `rtl8812ae_do_iqk()` still updates `thermalvalue_iqk` and calls it.

RF power state changes are handled by `rtl8821ae_phy_set_rf_power_state()`. It short-circuits when the requested state equals `ppsc->rfpwr_state`; otherwise `_rtl8821ae_phy_set_rf_power_state()` resumes the NIC from IPS halt, writes RF-on registers, updates awake/sleep timestamps and LED state, or waits for non-beacon TX rings to drain before RF off. If configured for halt-NIC IPS, it calls `rtl_ps_disable_nic()` and sets `RT_RF_OFF_LEVL_HALT_NIC`.

## State and Persistence Behavior

This file persists state in driver memory and hardware registers only; it does not write filesystem state.

- `struct rtl_phy` is the main mutable store. This file writes register definitions, current channel/bandwidth progress flags, default initial gain/frame-sync snapshots, CCK high-power state, TX power-by-rate offset arrays, TX power-base arrays, TX power-limit arrays, current TX power indexes, IQK matrices, `lck_inprogress`, `set_io_inprogress`, `current_io_type`, and scan-time initial-gain backups.
- `struct rtl_hal` contributes hardware type, version, interface, package, board/RFE details, and current band. Band-switching mutates `current_bandtype`.
- `struct rtl_efuse` supplies persistent hardware calibration and regulatory inputs read elsewhere from efuse. This file consumes `crystalcap`, `autoload_failflag`, `eeprom_regulatory`, per-channel TX power levels, 2.4/5 GHz diffs, board type, and other RF option fields.
- `struct rtl_dm` receives BB swing deltas and thermal IQK values and provides remnant swing indexes for final TX power.
- Hardware register writes are extensive and persist until later driver writes, power transitions, or device reset. Sensitive areas include `REG_SYS_FUNC_EN`, `REG_RF_CTRL`, `REG_OPT_CTRL`, `REG_MAC_PHY_CTRL`, `REG_TRXPTCL_CTL`, `REG_TXPAUSE`, TX AGC pages, RF `RF_CHNLBW`, RF `RF_APK`, IQK pages, RFE pinmux, CCK/OFDM enable fields, and interrupt/wake/power control registers.
- RF and IQK access is synchronized with `rf_lock` and `iqk_lock`, while channel and bandwidth changes use boolean in-progress flags rather than a full state machine.

## Dependencies and Integration Points

- Integrates with mac80211 through the surrounding `rtlwifi` PCI driver ops and common channel, scan, power-management, LED, and TX/RX paths.
- Calls shared register helpers (`rtl_read_*`, `rtl_write_*`, `rtl_get_bbreg`, `rtl_set_bbreg`, `rtl_get_rfreg`, `rtl_set_rfreg`) and shared bit helpers such as `calculate_bit_shift()`.
- Depends on local register constants from `reg.h`, PHY declarations and efuse-layout constants from `phy.h`, RF6052 functions from `rf.h`, dynamic-management functions from `dm.h`, chip tables from `table.h`, and beacon helpers from `hw.h`.
- Uses `efuse_shadow_read()` for TX swing values and consumed efuse state populated by the efuse reader/parser.
- Uses `rtlpriv->cfg->ops->set_hw_reg()` and `rtlpriv->cfg->ops->led_control()` to integrate with common ops.
- Uses PCI-private TX ring state (`struct rtl_pci_priv`, `struct rtl8192_tx_ring`) when powering RF off, so PHY power transitions depend on TX queue state.
- The table interpreter must match the exact format of `RTL8821AE_*` and `RTL8812AE_*` arrays. Changes in table encoding or condition marker semantics directly affect initialization.

## Risks and Edge Cases

- Register programming is highly order-sensitive and filled with hardware literals. Reordering or simplifying sequences can break RF bring-up, regulatory power, scan behavior, 5 GHz operation, or coexistence.
- `_rtl8821ae_phy_rf_serial_read()` and `_rtl8821ae_phy_rf_serial_write()` depend on correct `phyreg_def` initialization and RF path selection. Missing initialization before RF access would target the wrong 3-wire registers.
- Several readiness checks use bitwise negation on single-bit values, for example `if ((~iqk_ready) || ...)` and `if (~tx_fail)`. This appears inherited but is risky because bitwise `~0` and `~1` are both nonzero in C; behavior may not match logical-not intent.
- `_rtl8812ae_phy_get_txpower_limit()` has a suspicious 5 GHz non-worldwide indexing expression using `[regu][chnl][sec][chnl][rf_path]` rather than `[regu][bdwidth][sec][chnl][rf_path]`. The worldwide path is usually used (`TXPWR_LMT_WW`), but direct regulation lookups would be fragile.
- Some functions support path B for TX power and RF table loading, while RTL8821AE IQK only calibrates path A and RTL8812AE IQK is empty. Changes that assume symmetric path support can regress 2T parts.
- TX power conversion mixes signed limits with unsigned indexes, applies special handling for VHT MCS8/9, and clamps only the final index. Off-by-one or sign mistakes can create regulatory or throughput regressions.
- `rtl8821ae_phy_sw_chnl()` waits up to roughly one second for `lck_inprogress`; calibration hangs or missed flag clearing can delay channel changes.
- Bandwidth secondary-channel mapping logs errors for invalid primary-offset combinations but still returns a combined subchannel value, potentially programming invalid state after caller mistakes.
- `RT_CANNOT_IO(hw)` is defined as `false` in `phy.h`, so power/sleep protection in this file is effectively disabled unless the macro is changed.
- Empty `rtl8812ae_phy_iq_calibrate()` and `rtl8821ae_phy_lc_calibrate()` functions are intentional no-ops or incomplete ports; callers should not assume calibration actually ran for those cases.
- Scan pause/resume changes DIG and CCK CCA thresholds and stops/resumes ad-hoc beacons. Failure to restore after scan would affect sensitivity and IBSS behavior.

## Test Signals

- Build with the `rtlwifi` RTL8821AE PCI driver enabled and treat warnings in `phy.c`, `phy.h`, `reg.h`, `pwrseq.*`, `rf.h`, `dm.h`, and `table.h` as meaningful.
- Probe RTL8821AE and RTL8812AE PCIe devices and verify MAC/BB/RF configuration succeeds without "Write BB Reg Fail", "BB_PG Reg Fail", "AGC Table Fail", invalid RF path, or invalid rate warnings.
- Exercise 2.4 GHz and 5 GHz association, scan, channel switching across channel 14, HT20/HT40/VHT80 bandwidth changes, and TX throughput while watching dynamic debug for channel, band, TX power, and IQK logs.
- Validate regulatory TX power behavior by comparing programmed TX AGC indexes against efuse and power-limit tables for representative CCK, OFDM, HT, and VHT rates.
- Test suspend/resume, IPS power save, RF kill/off/on, and repeated module unload/reload to catch RF power-state and TX queue-drain regressions.
- For RTL8821AE, run thermal-triggered IQK and inspect calibration success/fallback logs and RF performance before/after; for RTL8812AE, confirm the no-op IQK behavior is acceptable for the target hardware.
- Use dynamic debug around `COMP_RF`, `COMP_INIT`, `COMP_SCAN`, `COMP_POWER`, `COMP_POWER_TRACKING`, and `COMP_IQK` to confirm table conditions, RFE type branches, and RF register writes match expected hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.h

## Purpose

`phy.h` declares the RTL8821AE/RTL8812AE PHY programming interface and local data structures used by `phy.c`, RF code, dynamic-management code, and the hardware ops layer. It defines efuse offsets, TX power layout structures, calibration constants, RF/path limits, channel-switch command structures, antenna-selection bitfields, and exported PHY function prototypes.

The header is the contract for all chip-specific PHY behavior in this directory. It exposes functions for BB/RF register access, MAC/BB/RF configuration, band/channel/bandwidth changes, TX power programming, calibration, RF path switching, scan I/O commands, and RF power-state changes.

## Important APIs, Types, and Constants

- `MAX_TX_COUNT`, `TX_1S` through `TX_4S`, `MAX_POWER_INDEX`, `RTL8821AE_MAX_PATH_NUM`, and `RF6052_MAX_PATH` define dimensions used by efuse and TX power tables.
- `CT_OFFSET_*` constants describe the compact efuse content offsets for MAC address, CCK/HT40/HT20/OFDM power indexes and diffs, channel plan, thermal meter, RF options, version, and customer ID.
- `struct swchnlcmd` and `enum swchnlcmd_id` preserve an older command-script representation for channel switching, though current `phy.c` primarily performs direct callback logic rather than building these scripts.
- `enum hw90_block_e` and `enum baseband_config_type` identify hardware table classes, with `BASEBAND_CONFIG_PHY_REG` and `BASEBAND_CONFIG_AGC_TAB` used by the BB table loader.
- `enum ra_offset_area` groups rate-adaptive offset sections.
- `enum antenna_path`, `struct r_antenna_select_ofdm`, and `struct r_antenna_select_cck` define antenna selection encodings for OFDM/CCK register fields.
- `struct efuse_contents` models the parsed efuse payload used by this chip family: MAC address, power indexes, power diffs, max offsets, channel plan, thermal meter, RF options, version, OEM ID, and regulatory byte.
- `struct tx_power_struct` stores per-path per-channel CCK/HT power tables, group power arrays, legacy/HT diffs, group count, and original MCS offsets.
- `enum _ANT_DIV_TYPE` names antenna-diversity modes, including fixed, hardware, smart, and software diversity options.
- `RT_CANNOT_IO(hw)` is currently defined as `false`, so guard checks in `phy.c` do not block I/O in sleep/unload paths.

Exported prototypes include register access (`rtl8821ae_phy_query_bb_reg()`, `rtl8821ae_phy_set_bb_reg()`, `rtl8821ae_phy_query_rf_reg()`, `rtl8821ae_phy_set_rf_reg()`), configuration (`rtl8821ae_phy_mac_config()`, `rtl8821ae_phy_bb_config()`, `rtl8821ae_phy_rf_config()`), runtime channel and bandwidth control, calibration (`rtl8821ae_phy_iq_calibrate()`, `rtl8812ae_phy_iq_calibrate()`, `rtl8821ae_phy_lc_calibrate()`, `rtl8812ae_do_iqk()`, `rtl8821ae_do_iqk()`), RF path/power state control, RF table loading, and TX swing lookup.

## Control Flow

This header does not execute control flow directly. Its declarations shape the chip operations used by the driver:

1. The hardware initialization path calls MAC, BB, and RF config functions declared here.
2. Runtime mac80211 channel changes flow into `rtl8821ae_phy_sw_chnl()`, `rtl8821ae_phy_set_bw_mode()`, and `rtl8821ae_phy_switch_wirelessband()`.
3. Rate/power management code uses TX power functions and IQK entry points declared here.
4. Power-management code uses `rtl8821ae_phy_set_rf_power_state()` and `rtl8821ae_phy_set_io_cmd()`.
5. RF6052 setup uses the RF-header table loaders for RTL8812AE and RTL8821AE.

## State and Persistence Behavior

`phy.h` defines in-memory structure layouts and constants only. It does not create persistent state, but its structures mirror data read from hardware efuse and stored in `struct rtl_efuse`/`struct rtl_phy` by implementation files. Changing array dimensions or efuse offsets can corrupt how persistent device calibration data is interpreted.

The `RT_CANNOT_IO(hw)` macro is an important behavioral knob despite being defined as a constant false value. Any future change to it would alter many I/O guard paths in `phy.c`.

## Dependencies and Integration Points

- Depends on kernel and `rtlwifi` types included before or through local headers, especially `struct ieee80211_hw`, `enum radio_path`, `enum nl80211_channel_type`, `enum rf_pwrstate`, `enum io_type`, `ETH_ALEN`, and `CHANNEL_MAX_NUMBER`.
- Includes no other local header directly in this file, but its declarations assume `wifi.h`, `def.h`, and related headers are available in translation units.
- Its efuse offset constants must stay aligned with the parser and efuse reader in the RTL8821AE hardware code.
- Function prototypes are implemented mostly in `phy.c`, while some are used by `rf.c`, `dm.c`, and hardware ops files.

## Risks and Edge Cases

- `IQK_ADDA_REG_NUM` is defined twice with the same value. This is harmless as written but fragile if one copy changes.
- `RT_CANNOT_IO(hw)` being hardcoded to `false` means code that looks protected from unsafe MMIO/RF access is not actually gated.
- `MAX_TX_COUNT` has a comment warning that it must remain `4` or efuse table sequence parsing breaks.
- `struct efuse_contents` and `struct tx_power_struct` have fixed array dimensions. Any change must be coordinated with efuse parsing and channel constants.
- The header exposes both RTL8812AE and RTL8821AE IQK functions even though the RTL8812AE implementation is currently empty in `phy.c`.
- Several constants and enums retain older naming or misspellings (`CMDID_SET_TXPOWEROWER_LEVEL`, `_ANT_DIV_TYPE`), so mechanical cleanup could break external references.

## Test Signals

- Compile all translation units in `rtl8821ae` after any prototype, enum, or structure change.
- Confirm efuse parsing still produces expected MAC, channel plan, thermal meter, and TX power arrays on real hardware.
- Verify channel switching, RF power state changes, and IQK callers still link and execute after signature changes.
- Review any change to `MAX_TX_COUNT`, efuse offsets, or path counts against the vendor efuse map and `phy.c` table loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.c

## Purpose

`pwrseq.c` materializes RTL8812 and RTL8821A power transition flows as `struct wlan_pwr_cfg` arrays. The common power-sequence executor parses these arrays and performs the corresponding register writes, polling operations, delays, and end markers defined by `pwrseq.h` macros.

The file contains no algorithmic logic beyond array definitions. It is the concrete data provider for power on/off, card enable/disable, suspend/resume, hardware power-down, and firmware low-power-state entry/leave flows.

## Important APIs and Data

Exported arrays for RTL8812:

- `rtl8812_power_on_flow`
- `rtl8812_radio_off_flow`
- `rtl8812_card_disable_flow`
- `rtl8812_card_enable_flow`
- `rtl8812_suspend_flow`
- `rtl8812_resume_flow`
- `rtl8812_hwpdn_flow`
- `rtl8812_enter_lps_flow`
- `rtl8812_leave_lps_flow`

Exported arrays for RTL8821A:

- `rtl8821A_power_on_flow`
- `rtl8821A_radio_off_flow`
- `rtl8821A_card_disable_flow`
- `rtl8821A_card_enable_flow`
- `rtl8821A_suspend_flow`
- `rtl8821A_resume_flow`
- `rtl8821A_hwpdn_flow`
- `rtl8821A_enter_lps_flow`
- `rtl8821A_leave_lps_flow`

Each array is sized from the corresponding `*_STEPS` constants plus `*_TRANS_END_STEPS`, and its initializer is the concatenation of transition macros such as `RTL8812_TRANS_CARDEMU_TO_ACT` and `RTL8812_TRANS_END`.

## Control Flow

Power control code elsewhere selects one of these arrays through aliases in `pwrseq.h`, then iterates until it sees a `PWR_CMD_END` entry. Typical flows are:

1. NIC power-on uses card-emulation-to-active plus an end marker.
2. Radio-off uses active-to-card-emulation plus an end marker.
3. Card disable uses active-to-card-emulation, then card-emulation-to-card-disable, then end.
4. Card enable uses card-disable-to-card-emulation, then card-emulation-to-active, then end.
5. Suspend and resume combine active/card-emulation/suspend transitions in opposite directions.
6. Hardware power down moves active to card emulation and then power-down.
7. LPS entry pauses TX and shuts down selected MAC/BB/RF blocks; LPS leave wakes the firmware/host power mechanism and reenables WMAC/BB.

## State and Persistence Behavior

The arrays are static driver data compiled into the module. Runtime state changes occur only when the power-sequence interpreter executes their entries against hardware. Those changes affect MAC, SDIO/USB/PCIe local registers, GPIO wake controls, analog isolation, LDO sleep, WL suspend, firmware/8051 reset, DMA, TX pause, BB/RF clocks, and WMAC TRX state.

The arrays themselves are mutable C globals rather than `const`, but this file never modifies them. Treating them as immutable transition tables is required for correctness.

## Dependencies and Integration Points

- Includes `../pwrseqcmd.h` for `struct wlan_pwr_cfg`, command IDs, masks, base-address identifiers, interface masks, and delay constants.
- Includes local `pwrseq.h`, where all transition macros, step counts, extern declarations, and alias names are defined.
- Consumed by RTL8821AE hardware/power code through aliases such as `RTL8812_NIC_PWR_ON_FLOW` and `RTL8821A_NIC_PWR_ON_FLOW`.
- The array sizes must match the number of entries emitted by the macros. Extra capacity is tolerated by C initialization, but undersizing would be a build error and wrong step counts can mislead readers or validators.

## Risks and Edge Cases

- The transition macros contain interface-specific entries for PCIe, USB, and SDIO even though this driver directory is PCIe-focused. The interpreter masks entries by interface, so mask correctness is critical.
- `rtl8812_card_enable_flow` is sized with `RTL8812_TRANS_CARDEMU_TO_PDN_STEPS` even though it initializes `RTL8812_TRANS_CARDDIS_TO_CARDEMU` plus `RTL8812_TRANS_CARDEMU_TO_ACT`; this matches current compile-time sizing but is a maintenance hazard.
- `rtl8821A_card_enable_flow` uses `RTL8821A_TRANS_ACT_TO_CARDEMU_STEPS` in its size expression where the logical first transition is card-disable-to-card-emulation. Current step counts are both 15, but renumbering could silently create confusion or size mismatches.
- Because this file is pure data, functional regressions from a macro change may not be caught except by hardware power-cycle, suspend/resume, and LPS testing.

## Test Signals

- Compile the module after changing any `*_STEPS` constant or transition macro; array initializer warnings/errors are useful signals.
- Probe hardware and verify NIC power-on reaches active mode without power-ready polling timeouts.
- Exercise radio off/on, card disable/enable, suspend/resume, runtime power save, and IPS/LPS entry/leave.
- Use dynamic debug in the common power-sequence executor to confirm the selected flow reaches `PWR_CMD_END` and masks entries by the expected interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.h

## Purpose

`pwrseq.h` defines the RTL8812 and RTL8821A hardware power-state transition scripts used by the common `rtlwifi` power-sequence executor. It describes sequences for moving among card emulation, active, suspend, card-disable, power-down, and low-power states, then declares the concrete arrays in `pwrseq.c` and provides chip-specific alias names for callers.

The file is a register-script specification, not imperative C control logic. Each macro expands to a list of `struct wlan_pwr_cfg` initializers containing register offset, cut mask, fabrication mask, interface mask, base address, command, mask, and value.

## Important APIs, Data, and Macros

- Step-count constants such as `RTL8812_TRANS_CARDEMU_TO_ACT_STEPS`, `RTL8812_TRANS_ACT_TO_LPS_STEPS`, `RTL8821A_TRANS_CARDEMU_TO_ACT_STEPS`, and `RTL8821A_TRANS_END_STEPS` size the arrays in `pwrseq.c`.
- RTL8812 transition macros include `RTL8812_TRANS_CARDEMU_TO_ACT`, `RTL8812_TRANS_ACT_TO_CARDEMU`, `RTL8812_TRANS_CARDEMU_TO_SUS`, `RTL8812_TRANS_SUS_TO_CARDEMU`, `RTL8812_TRANS_CARDEMU_TO_CARDDIS`, `RTL8812_TRANS_CARDDIS_TO_CARDEMU`, `RTL8812_TRANS_CARDEMU_TO_PDN`, `RTL8812_TRANS_PDN_TO_CARDEMU`, `RTL8812_TRANS_ACT_TO_LPS`, `RTL8812_TRANS_LPS_TO_ACT`, and `RTL8812_TRANS_END`.
- RTL8821A transition macros mirror the same state graph with additional RTL8821A-specific LDO, analog isolation, GPIO9 wake, BT/GPS pin, DPDT/PAPE/LNA, and XTAL trim steps.
- Extern declarations expose all `rtl8812_*_flow` and `rtl8821A_*_flow` arrays.
- Alias macros such as `RTL8812_NIC_PWR_ON_FLOW`, `RTL8812_NIC_DISABLE_FLOW`, `RTL8821A_NIC_RESUME_FLOW`, and `RTL8821A_NIC_LPS_LEAVE_FLOW` provide the names used by hardware code.

## Control Flow

The intended state graph is documented for RTL8821A as:

- `POFF`
- `PDN`
- `CARDEMU`
- `ACT`
- `LPS`
- `SUS`

The common executor walks arrays built from these macros:

1. For each entry, it checks cut/fab/interface masks against the current hardware.
2. It applies the command to the selected base address: write, poll, delay, or end.
3. Polling entries wait for hardware bits such as power-ready, MAC-off completion, TX-empty, TSF clock, SDIO suspend state, or LPS state transitions.
4. `PWR_CMD_END` terminates interpretation.

RTL8812 and RTL8821A use broadly similar flows, but RTL8821A has a longer card-emulation-to-active transition with LDOA12 enable, BT/GPS pin selection, analog isolation release, GPIO9 wake interrupt setup, BT start for test chips, XTAL trim, and cut-specific writes.

## State and Persistence Behavior

This header defines hardware side effects that become real when executed:

- Active transitions enable power rails, release WLON reset, disable hardware/software power-down and suspend, switch antenna/control pins to WLAN BB, enable interrupts, and prepare BT/coexistence-related pins.
- Active-to-card-emulation transitions turn off RF, switch DPDT selection back to registers, request MAC hardware power-down, isolate analog from digital for USB/SDIO, and disable selected LDO blocks.
- Suspend and card-disable transitions set WL suspend bits, configure GPIO direction and output, enable GPIO9 external wake for USB, enter LDO sleep, set SDIO local suspend, or reset the 8051.
- LPS entry pauses TX, polls TX queues empty, gates CCK/OFDM/RF/BB/MAC blocks, resets MAC TRX, and asks the scheduler to respond TxOK.
- LPS leave writes RPWM values for SDIO/USB/PCIe, delays for firmware wake, switches TSF to 40 MHz, reenables BB clocks, WMAC TRX, BB macro, and clears TX pause.

The script definitions are compiled into the module through `pwrseq.c`; they are not persisted outside the driver.

## Dependencies and Integration Points

- Includes `../pwrseqcmd.h` for `struct wlan_pwr_cfg` fields, `PWR_CMD_WRITE`, `PWR_CMD_POLLING`, `PWR_CMD_DELAY`, `PWR_CMD_END`, `PWRSEQ_DELAY_US/MS`, cut/fab/interface masks, base addresses, and bit macros.
- Includes `../btcoexist/halbt_precomp.h`, reflecting that some power transitions interact with BT/GPS/coexistence pins and BT low-power behavior.
- Consumed by `pwrseq.c`, which expands these macros into concrete arrays.
- Consumed indirectly by hardware power-management code using the `RTL8812_NIC_*` and `RTL8821A_NIC_*` alias macros.

## Risks and Edge Cases

- The macros are dense register scripts. A one-bit change can affect boot, suspend/resume, wake, LPS, or coexistence on real hardware.
- Comments and masks sometimes mention USB/SDIO behavior inside a PCIe driver subtree. This is expected from shared vendor sequences, but interface masks must remain accurate.
- Step-count constants must stay large enough for the number of macro entries. Some current array sizes use logically mismatched but numerically equal step constants, which could become wrong if counts diverge.
- Polling commands can hang or time out in the executor if the mask/value pair does not match hardware behavior for a cut/interface.
- GPIO9 wake, WL suspend, analog isolation, and LDO sleep entries have platform power-management implications; regressions may only appear under suspend, WoWLAN, or runtime PM.
- `RTL8821A_TRANS_CARDEMU_TO_ACT` contains a `PWR_CUT_TESTCHIP_MSK` BT start write and a `PWR_CUT_A_MSK` write; cut masks need validation against supported silicon revisions.

## Test Signals

- Build-test after any macro or step-count edit to catch initializer or declaration mismatches.
- Run cold probe, warm reboot, module reload, RF off/on, suspend/resume, hardware power-down, and LPS entry/leave on RTL8812AE and RTL8821AE hardware.
- Enable executor-level logging to verify masked entries are skipped or executed as expected per PCIe/USB/SDIO interface and chip cut.
- Check for power-ready polling failures, TX-empty polling failures, failure to wake from LPS, missing GPIO wake events, or BT coexistence regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/reg.h

## Purpose

`reg.h` is the RTL8821AE/RTL8812AE register and bitfield map. It defines MAC, DMA, PCIe, USB/SIE, beacon, EDCA, security, WoWLAN, power, efuse, BB, OFDM, CCK, RF, TX AGC, IQK, RFE, ODM, and aggregation constants used throughout the local driver. It contains no executable code, but it is the naming layer that makes the heavy register programming in `phy.c`, `hw.c`, `rf.c`, `dm.c`, `trx.c`, and power sequencing readable and maintainable.

## Important Register Groups and Constants

Major MAC register regions:

- System and power: `REG_SYS_ISO_CTRL`, `REG_SYS_FUNC_EN`, `REG_APS_FSMCO`, `REG_SYS_CLKR`, `REG_RF_CTRL`, `REG_MAC_PHY_CTRL`, `REG_MCUFWDL`, `REG_SYS_CFG`, `REG_ROM_VERSION`.
- Interrupts: `REG_HIMR`, `REG_HISR`, `REG_HIMRE`, `REG_HISRE`, `REG_FSIMR`, `REG_FSISR`, `REG_HSIMR`, `REG_HSISR`, plus `IMR_*` and `HSIMR/HSISR_*` bits.
- DMA and queues: `REG_CR`, `REG_PBP`, `REG_TRXDMA_CTRL`, `REG_RQPN`, `REG_RXDMA_CONTROL`, PCIe descriptor registers, queue information registers, TX packet empty status, and TX/RX packet buffer controls.
- Protocol and rate control: `REG_RRSR`, `REG_ARFR*`, `REG_RETRY_LIMIT` fields, `RATR_*`, `RATE_*`, EDCA registers, SIFS registers, beacon/TSF registers, AMPDU controls, and retry/aggregation bitfields.
- Receive filtering and security: `REG_RCR`, `RCR_*`, CAM registers and bits, `REG_SECCFG`, `SCR_*`.
- Efuse/EEPROM: `REG_EFUSE_CTRL`, `REG_EFUSE_ACCESS`, `RTL_EEPROM_ID`, `EFUSE_REAL_CONTENT_LEN`, `EEPROM_*` offsets/defaults, RF options, MAC address, IDs, channel plans, and customer IDs.
- USB/SIE aliases: `REG_USB_INFO`, `REG_USB_SPECIAL_OPTION`, `REG_USB_AGG_*`, normal/test SIE VID/PID/endpoint/PHY/MAC/string fields.

PHY/BB/RF regions:

- BB/RF access and pages: `RA_LSSIWRITE_8821A`, `RB_LSSIWRITE_8821A`, `RHSSIREAD_8821AE`, `RA_PIREAD_8821A`, `RA_SIREAD_8821A`, and `RFREG_OFFSET_MASK`.
- OFDM/CCK control: `RFPGA0_RFMOD`, `ROFDMCCKEN`, `RRFMOD`, `RADC_BUF_CLK`, `RCCK_SYSTEM`, `RCCK_RX`, CCK/OFDM false-alarm and report registers.
- TX AGC: `RTXAGC_A_*` and `RTXAGC_B_*` define per-rate byte lanes for CCK, OFDM, HT MCS0-15, and VHT NSS indexes.
- IQK and calibration: `RFPGA0_IQK`, `RTX_IQK_*`, `RRX_IQK_*`, `RIQK_*`, `RTX_POWER_*`, `RRX_POWER_*`, and many IQ imbalance masks.
- RF path registers: `RF_CHNLBW`, `RF_APK`, `RF_T_METER_8812A`, `RF_WE_LUT`, and many legacy RF register names.
- RFE controls: `RA_RFE_PINMUX`, `RB_RFE_PINMUX`, `RA_RFE_INV`, `RB_RFE_INV`, `RA_TXSCALE`, `RB_TXSCALE`, and `BMASKRFEINV`.
- ODM helper constants: `ODM_REG_*` and `ODM_BIT_*` map dynamic-management code to BB false-alarm, CCA, IGI, and RX path registers.

Power and system bitfields include `FEN_*`, `APFM_*`, `AFSM_*`, `RDY_MACON`, `MCUFWDL_*`, `XCLK_VLD`/`ACLK_VLD`, `TRP_BT_EN`, `BD_HCI_SEL`, `HCI_TXDMA_EN`, `PROTOCOL_EN`, `SCHEDULE_EN`, `MACTXEN`, `MACRXEN`, and many page-buffer and LLT helpers.

## Control Flow

`reg.h` does not define control flow. Its constants are consumed by control flows in implementation files:

1. Initialization code writes system, MAC, BB, RF, and AGC registers by these names.
2. Power-sequence scripts use raw offsets that correspond to many registers named here.
3. Channel and bandwidth logic writes `REG_TRXPTCL_CTL`, `REG_TXPKT_EMPTY`, `REG_CCK_CHECK`, `RRFMOD`, `RADC_BUF_CLK`, `RCCAONSEC`, `RF_CHNLBW`, and TX AGC registers.
4. TX/RX descriptor and queue code uses queue, DMA, interrupt, retry, aggregation, and receive-filter fields.
5. Efuse parsing uses `EEPROM_*` offsets and defaults to load hardware identity, regulatory, MAC, and calibration state.

## State and Persistence Behavior

This header defines symbolic names for state stored elsewhere:

- Hardware register state persists in the device until overwritten, reset, powered down, or reinitialized.
- Efuse/EEPROM offsets describe nonvolatile device data; changing them changes how persistent hardware calibration and identity data is interpreted.
- Bit masks determine partial-register updates. Incorrect masks can corrupt unrelated neighboring fields.
- Several names alias the same offsets, for example normal/test SIE registers and generic MAC aliases. This is intentional but requires context-aware use.

The header itself stores no runtime state and performs no I/O.

## Dependencies and Integration Points

- Depends on Linux bit macros (`BIT`, `BIT16` in existing code context) supplied by included kernel headers before use.
- Included by `phy.c` and other local RTL8821AE source files for all register programming.
- Must remain aligned with vendor tables in `table.h`; table addresses and bit masks need to match these definitions.
- Interacts with `pwrseq.h` because many power-sequence raw offsets map to registers and bit meanings defined here.
- Provides constants shared with common `rtlwifi` abstractions, including CAM/security, receive filters, interrupts, queue control, and rate bitmaps.

## Risks and Edge Cases

- Duplicate definitions exist for some names (`REG_USB_INFO` family, `MAX_MSS_DENSITY_*`, `XCLK_VLD`/`ACLK_VLD`, `VENDOR_ID`, and `EEPROM_DEFAULT_LEGACYHTTXPOWERDIFF`). They currently resolve to the same values but are maintenance hazards.
- Many constants are copied from older chip families and comments mention 8723/8188E or 8192-era behavior. Reuse may be intentional, but updates must verify RTL8821AE/RTL8812AE applicability.
- Register aliases such as `REG_DBI_CTRL` and `REG_DBI_ADDR` sharing an offset are context-dependent.
- Bitfield helper macros do not validate input range beyond masking. Callers can silently truncate values.
- Efuse defaults and offsets are safety-critical for MAC address, regulatory domain, thermal meter, crystal cap, board type, and TX power. Incorrect changes can break identity, compliance, or RF performance.
- TX AGC and IQK register maps are tightly coupled to `phy.c` switch statements and calibration code. Renaming or remapping one side without the other is likely to produce subtle hardware failures.
- Some macros contain spelling errors preserved from vendor code (`CAM_POLLINIG`, `REG_BB_ACCEESS_CTRL`, `RRX_POER_*`, `REG_UN_used_register`). Correcting names can break users unless all references are updated.

## Test Signals

- Build all RTL8821AE objects after changes; undefined macro or duplicate-definition warnings are important.
- Run static searches for every changed register name or mask to validate all call sites were updated.
- On hardware, test probe, firmware download, efuse read, interrupt enable/clear, DMA queue operation, scan/association, encryption, WoWLAN/suspend, channel switching, and TX power programming.
- For bit-mask changes, compare register readback before/after writes to confirm only intended bits changed.
- For efuse offset/default changes, dump parsed efuse fields and compare against known-good hardware or vendor documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/reg.h -->
