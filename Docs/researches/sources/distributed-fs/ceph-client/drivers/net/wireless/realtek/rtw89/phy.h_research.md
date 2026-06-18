# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy.h

## Purpose
`phy.h` is the central PHY contract for the rtw89 driver. It defines register-table encodings, rate-adaptation masks, dynamic-mechanism thresholds, PHY status IDs, transmit-power table layouts, RF calibration command APIs, generation-specific PHY callbacks, and inline register helpers used by AX and BE chip implementations. It does not implement the large algorithms itself; instead it provides the type, constant, and dispatch surface that ties chip-specific PHY files, firmware C2H/H2C handling, dynamic gain, environment monitoring, rate adaptation, TX power, RFK calibration, and channel information together.

## Important APIs, types, and definitions
- PHY table condition macros such as `get_phy_headline()`, `get_phy_target()`, `get_phy_cond_*()`, `PHY_COND_BRANCH_*`, and `PHY_COND_CHECK` describe conditional register-table parsing keyed by RFE/CV/package fields.
- `RA_MASK_*` constants encode CCK, OFDM, HT, VHT, HE, and EHT rate bitmaps, including 1-4 spatial stream layouts and EHT MCS0-11 subsets.
- CFO, UL TB, antenna diversity, CCX, DIG, PD threshold, EDCCA, NHM, and PHY status constants provide shared thresholds for dynamic PHY mechanisms.
- C2H enums (`rtw89_phy_c2h_ra_func`, `rtw89_phy_c2h_rfk_log_func`, `rtw89_phy_c2h_rfk_report_func`, `rtw89_phy_c2h_dm_func`, `rtw89_phy_c2h_class`) define firmware-to-host PHY message classes and functions.
- PHY status enums (`rtw89_phy_status_ie_type`, `rtw89_phy_status_bitmap`) enumerate parsed PPDU status information elements and packet-status bits.
- TX power structures include `rtw89_txpwr_byrate_cfg`, `rtw89_txpwr_track_cfg`, `rtw89_txpwr_limit_ax`, `rtw89_txpwr_limit_be`, `rtw89_txpwr_limit_ru_ax`, and `rtw89_txpwr_limit_ru_be`, with page-size constants validated by implementation code.
- `struct rtw89_phy_gen_def` is the generation-specific dispatch table. It contains CR base, PHY-status register addresses, CCX/CFO/BB-wrap register sets, address-offset logic, BB gain parsing, preinit hooks, channel-info setup, and TX power programming callbacks.
- Inline helpers `rtw89_phy_write*()`, `rtw89_phy_read*()`, `rtw89_phy_write32_idx()`, generation dispatchers, and TX power unit converters hide CR-base and factor differences.
- RFK declarations (`rtw89_rfk_tbl`, `RTW89_DECLARE_RFK_TBL`, `RTW89_DECL_RFK_*`) encode RF writes, BB writes, set/clear operations, and delays for the RFK parser.
- Function declarations expose PHY initialization, RF read/write variants, rate adaptation, RFK wait operations, C2H handling, CFO tracking, stat/env monitor tracking, DIG, antenna diversity, BSS color, UL TB control, EDCCA, channel-index coding, and NHM control.

## Control flow and state behavior
The header's main runtime pattern is indirect dispatch through `rtwdev->chip->phy_def`. Generic code calls wrappers such as `rtw89_phy_set_txpwr_byrate()`, `rtw89_phy_preinit_rf_nctl()`, or `rtw89_phy_ch_info_init()`, and the active chip generation supplies the actual implementation. Register helpers add `phy_def->cr_base` before MMIO access so AX/BE register maps can share call sites while selecting different base offsets.

PHY-index access is split between simple CR-base helpers and indexed helper declarations implemented elsewhere. `rtw89_bbmcu_write32()` also adjusts addresses for PHY1 if the address is below `0x10000`, then writes through the BBMCU offset. Subband conversion helpers persist no state; they normalize channel subbands into OFDM gain-offset, legacy BB-gain-band, or BE gain-band enums. TX power conversion helpers translate between RF, BB, MAC, and dBm units using per-chip factor fields and clamp dBm-to-MAC output to the signed MAC field range.

Most persistent state described by this header lives in `struct rtw89_dev`: `rtwdev->bb_gain`, `rtwdev->efuse`, `rtwdev->hal`, per-station rate-adaptation state, dynamic-mechanism state, and firmware completion state. The header fixes the memory layout expected by implementation files for TX power pages and RFK descriptors, so changing structure fields or sizes changes how runtime tables are serialized to hardware.

## Dependencies and integration points
`phy.h` includes `core.h` and depends on Linux bitfield helpers, rtw89 core types, channel/rate enums, RF path enums, firmware command structures, and mac80211 types referenced in prototypes. It is included by chip generation files such as `phy_be.c`, broader PHY implementation files, power-save code for `rtw89_phy_dm_reinit()`, and chip-specific table loaders. The exported generation definitions `rtw89_phy_gen_ax`, `rtw89_phy_gen_be`, and `rtw89_phy_gen_be_v1` are selected from `struct rtw89_chip_info`, making this header a key ABI between chip descriptions and generic PHY control.

## Risks and edge cases
- TX power page structures must match hardware page sizes exactly; implementation files rely on `BUILD_BUG_ON()` for BE sizes, but semantic ordering still depends on this header.
- RA masks and PHY status bit positions are protocol/hardware ABI. A wrong bit range can silently disable rates or misclassify received packets.
- Generation callback pointers are mostly assumed present. Missing callbacks in a chip definition can become null calls through inline dispatch.
- The inline CR-base helpers assume `rtwdev->chip->phy_def` is initialized and valid before use.
- Subband-to-gain mappings default to 2 GHz for unknown values, which is safe for switch exhaustiveness but can hide invalid channel state.
- RFK table macros encode opaque command streams; malformed tables can write wrong RF/BB registers without type-system protection.

## Test signals
Good signals include build coverage for all rtw89 chip modules, successful selection of the right `phy_def` at probe, table loading without condition-parser warnings, correct TX power page size assertions, valid RA masks in firmware station updates, PHY C2H dispatch for RA/DM/RFK classes, stable CFO/DIG/EDCCA/NHM watchdog activity, and no null-pointer faults when generic code calls PHY generation dispatchers.
