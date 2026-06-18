# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk_table.h

## Purpose
Declares the exported RF calibration table descriptors implemented in `rtw8852c_rfk_table.c`. This header is the ABI between the RTL8852C RFK implementation and the static register-script catalog: `rtw8852c_rfk.c` includes it to select path-, band-, and calibration-stage-specific `struct rtw89_rfk_tbl` objects for `rtw89_rfk_parser()`.

## Important APIs, Types, and Functions
The sole public type used here is `struct rtw89_rfk_tbl` from `phy.h`. The header declares one `extern const struct rtw89_rfk_tbl` symbol per table. The declarations are grouped by calibration domain: DACK reload/reset/run and DRCK; IQK RXK configuration and AFE/BB restore; RX SRAM debug pre/post; DPK MDPD order and KIP power-clock scripts; and TSSI system, TX power control, DCK, BB gain split, slope, alignment, tracking, moving-average, enable, and disable scripts.

There are no functions or inline helpers. The important API contract is symbol naming: each declaration must match the `RTW89_DECLARE_RFK_TBL(<base>)` expansion in the `.c` file, which exports `<base>_tbl`.

## Control Flow
The header has no execution path. It enables callers to pass table addresses to `rtw89_rfk_parser()` or to `rtw89_rfk_parser_by_cond()`. Typical control flow in `rtw8852c_rfk.c` selects a table by RF path (`RF_PATH_A` versus `RF_PATH_B`), band (`RTW89_BAND_2G`, 5G fallback, or explicit 6G alignment defaults), bandwidth-derived setup, or DPK MDPD order, then lets the generic parser apply the ordered register definitions.

## State and Persistence Behavior
No runtime state is stored in the header. All declared tables are constant module data defined in the companion `.c` file. Persistent calibration effects are indirect: when a declared table is parsed, it can mutate hardware RF/BB state, while caller-owned software state such as DACK backups, DPK current indices, TSSI thermal baselines, and TSSI mode flags lives in `struct rtw89_dev`.

## Dependencies and Integration Points
The header includes `phy.h` for `struct rtw89_rfk_tbl` and is protected by `__RTW89_8852C_RFK_TABLE_H__`. Its main consumers are `rtw8852c_rfk.c` and any compilation unit that needs RTL8852C RFK table descriptors. It is coupled to the companion `.c` file for definitions and to the generic rtw89 RFK parser for semantics.

## Risks
Adding, removing, or renaming a declaration without making the matching `.c` change causes build or link failures. More subtle risk comes from exposing a correctly named but semantically wrong table to a caller: path A/B or 2G/5G/6G mixups compile cleanly but program the wrong hardware register windows. Because the header exports all table descriptors as plain `const` symbols, it does not encode which calibration phase, path, or band may legally consume each table.

## Test Signals
Primary signals are compile and link coverage for `rtw8852c_rfk.o` plus the table object, no undefined `_tbl` references, and successful module load on builds that include RTL8852C support. Functional signals mirror the caller paths: DACK/DRCK, IQK, DPK, RX SRAM debug, TSSI init/tracking, TSSI enable/disable, and band/path switching should all find their expected table symbols and run without RFK timeout or invalid-power behavior.
