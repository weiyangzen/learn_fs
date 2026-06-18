# Research: subset-b-004939

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk_table.c

## Purpose

`rtw8852a_rfk_table.c` is a data-only RF calibration table module for the Realtek rtw89 8852A wireless driver. It defines ordered register/RF-write sequences for TSSI setup and tracking, AFE initialization, DACK/ADDCK/DADC calibration, DPK preparation/restore, loopback RXIQK setup, PAS reads, and IQK set/restore flows. The file has no callable functions of its own; each static `struct rtw89_reg5_def` array is exported as a `const struct rtw89_rfk_tbl` through `RTW89_DECLARE_RFK_TBL()`.

The operational value of the file is sequencing. Consumers in `rtw8852a_rfk.c` call `rtw89_rfk_parser()` or `rtw89_rfk_parser_by_cond()` with these exported tables, and the generic parser in `phy.c` walks the entries in order, dispatching each entry by its `flag` to the proper hardware-write, RF-write, bit-set, bit-clear, or delay handler.

## Important APIs, Types, and Tables

The core type is `struct rtw89_reg5_def`, populated through macros from `phy.h`:

- `RTW89_DECL_RFK_WM(addr, mask, data)`: masked BB/register write.
- `RTW89_DECL_RFK_WS(addr, mask)`: set masked bits.
- `RTW89_DECL_RFK_WC(addr, mask)`: clear masked bits.
- `RTW89_DECL_RFK_WRF(path, addr, mask, data)`: RF-path register write.
- `RTW89_DECL_RFK_DELAY(data)`: calibration delay entry.
- `RTW89_DECLARE_RFK_TBL(name)`: publishes `name_tbl` with `.defs = name` and `.size = ARRAY_SIZE(name)`.

This source declares 74 exported RFK tables. Major groups are:

- TSSI system and TX power control: `rtw8852a_tssi_sys_defs_tbl`, 2G/5G overrides, path A/B TX power control BB tables, HE TB controls, DCK controls, DAC gain tables, slope calibration originals, RF gap tables, slope/track tables, TXAGC moving-average tables, per-subband PAK tables, enable/disable, and tracking tables.
- AFE and DACK support: `rtw8852a_rfk_afe_init_defs_tbl`, DACK reload tables for A/B, ADDC check tables, ADDCK reset/trigger/restore tables, DADC check enter/restore tables, and DACK front/middle/restore tables for both RF paths.
- DPK/IQK preparation: DPK BB/AFE setup and restore for path A, path B, and AB combined modes; DPK loopback RXIQK enter/restore; PAS read setup; IQK set/restore tables for non-DBCC path01 and DBCC path0/path1.

The table names intentionally map to the extern declarations in `rtw8852a_rfk_table.h`; any rename or new table needs a matching declaration for users outside this translation unit.

## Control Flow and Integration

The file contributes declarative control flow. The order of entries inside each array is the execution order on hardware. Important integration points in `rtw8852a_rfk.c` include:

- `_tssi_ini_sys()` applies `rtw8852a_tssi_sys_defs_tbl`, then selects 2G or 5G system overrides by channel band.
- `_tssi_ini_txpwr_ctrl_bb()` selects path A/B TX power control tables, then applies 2G/5G deltas.
- TSSI helpers select path-specific DAC gain, slope, RF gap, tracking, TXAGC offset, and PAK tables. PAK tables are further selected by subband: 2G, 5G band 1, 5G band 3, or 5G band 4.
- `_tssi_enable()` applies path-specific tracking and enable tables and flips `rtwdev->is_tssi_mode[path]` in driver state; `_tssi_disable()` applies the disable table and clears the mode state elsewhere.
- `_afe_init()` applies the AFE init table before later RFK flows.
- `_addck()`, `_check_addc()`, `_check_dadc()`, `_dack_s0()`, and `_dack_s1()` interleave procedural polling/backup code with this file's reset, trigger, restore, check, and reload tables.
- DPK and IQK routines use the path and DBCC/non-DBCC table variants to force the PHY into calibration topology, then restore it afterward.

The generic parser in `phy.c` performs no semantic validation beyond dispatching `_rfk_handler[p->flag]`; malformed flags, masks, addresses, or ordering mistakes become hardware behavior changes rather than C-level errors.

## State and Persistence Behavior

All arrays and published `rtw89_rfk_tbl` objects are `const` and persist for the lifetime of the loaded driver, usually in read-only data. They do not store runtime state. Runtime state is affected indirectly through hardware registers and through caller-owned structures in `rtw8852a_rfk.c`, such as `rtwdev->dack`, `rtwdev->tssi`, and `rtwdev->is_tssi_mode`.

Some tables intentionally produce persistent hardware state until later restore/disable tables or procedural code revert it. Examples include TSSI enable/disable, IQK/DPK set versus restore tables, ADDCK reset/trigger/restore triplets, and DACK front/middle/restore sequences. Table order is therefore part of the persistence contract.

## Dependencies

Direct dependency:

- `rtw8852a_rfk_table.h`, which includes `phy.h`.

Indirect dependencies and contracts:

- `phy.h` defines `struct rtw89_rfk_tbl`, `struct rtw89_reg5_def`, RFK declaration macros, and parser prototypes.
- `phy.c` implements `rtw89_rfk_parser()`, walking `.defs` through `.size` and dispatching through the RFK handler table.
- `rtw8852a_rfk.c` owns the calibration algorithms that choose which exported table to apply based on RF path, channel band, subband, DBCC state, and calibration phase.
- Register constants and masks are largely raw numeric addresses/masks in this table file, so the strongest dependency is on the 8852A register map and vendor calibration sequence.

## Risks and Edge Cases

- The file is almost entirely magic register data. C compilation can confirm names and object layout, but it cannot prove that a mask/data pair is correct for the silicon revision.
- Ordering is critical. Moving a delay, set/clear, trigger, or restore entry can change calibration timing or leave the PHY in a forced/debug state.
- Path A and path B tables are mostly offset mirrors. Asymmetries can be intentional hardware differences, but they need RF validation. One notable review signal is the path-B slope-calibration original table using `0x7878` where the path-A counterpart sequence uses `0x5858`; this may be deliberate but should be checked against the vendor register table before editing adjacent entries.
- Several masks are written more than once in sequence, such as repeated `0x581c`/`0x781c` fields and repeated `0x58f4`/`0x78f4` fields. These look like staged programming rather than simple duplicates, so deduplication would be risky.
- Band/subband selection is split between table data and procedural code. If a new band, channel group, or DBCC mode is added, both the caller selection logic and extern/table coverage must be updated together.
- The parser trusts `tbl->size`, generated by `ARRAY_SIZE()`. Hand-built tables should keep using `RTW89_DECLARE_RFK_TBL()` to avoid size drift.
- RFK table failures often surface as calibration timeouts or degraded RF performance, not immediate crashes. DACK/ADDCK polling and debug output in `rtw8852a_rfk.c` are important runtime evidence.

## Test Signals

- Build/link signal: the rtw89/8852A objects should compile with no undefined references between `rtw8852a_rfk_table.h`, `rtw8852a_rfk_table.c`, and `rtw8852a_rfk.c`.
- Static signal: count and compare `RTW89_DECLARE_RFK_TBL()` definitions against header externs; this source currently defines 74 exported tables.
- Runtime RFK signal: enable rtw89 RFK/TSSI debug and watch TSSI init, DACK, ADDCK, DADCK, IQK, and DPK traces for timeout messages and expected per-path progression.
- Hardware behavior signal: check association stability, transmit power tracking, thermal compensation, EVM, RX sensitivity, and regulatory power behavior across 2G and 5G subbands.
- Regression signal: exercise both RF paths, DBCC and non-DBCC modes, channel changes, scan-time TSSI handling, suspend/resume or firmware reload, and repeated calibration cycles.

## Research Notes

The full 1,607-line source was read in chunks. No source edits were made. This report treats the file as a calibration data contract rather than algorithmic code; the substantive behavior is the parser-visible ordering and table selection in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk_table.h

## Purpose

`rtw8852a_rfk_table.h` is the public declaration surface for the 8852A RF calibration tables implemented in `rtw8852a_rfk_table.c`. It lets procedural calibration code in `rtw8852a_rfk.c` reference named `const struct rtw89_rfk_tbl` objects without exposing the underlying static `struct rtw89_reg5_def` arrays.

The header is intentionally narrow: it has an include guard, includes `phy.h` for the `struct rtw89_rfk_tbl` definition, and declares the exported table objects.

## Important APIs and Types

The only exported type referenced directly is:

- `const struct rtw89_rfk_tbl`, defined in `phy.h` as a pointer to a `struct rtw89_reg5_def` array plus a table size.

The declarations are grouped by calibration domain:

- TSSI system, BB TX power control, DCK, DAC gain, slope, RF gap, PAK, enable/disable, and tracking tables.
- AFE initialization, DACK reload/check/reset/trigger/restore tables.
- DPK BB/AFE setup/restore, loopback RXIQK, and PAS read tables.
- IQK set/restore tables for non-DBCC and DBCC path-specific operation.

There are no function declarations and no inline logic in this header.

## Control Flow and Integration

The header does not execute control flow itself. Its integration role is link-time binding:

- `rtw8852a_rfk_table.c` defines each object through `RTW89_DECLARE_RFK_TBL(name)`, producing `name_tbl`.
- `rtw8852a_rfk.c` includes this header and passes selected table addresses to `rtw89_rfk_parser()` or `rtw89_rfk_parser_by_cond()`.
- `phy.c` parses the selected table and applies the encoded writes/delays to hardware.

Because the underlying arrays are `static` in the `.c` file, this header is the only supported way for other translation units to access the tables.

## State and Persistence Behavior

The header declares immutable table objects only. It owns no runtime state, performs no allocation, and has no persistence behavior beyond causing references to resolve to driver read-only data. Runtime state changes occur in the parser and the RFK callers that use these table references.

## Dependencies

Direct dependency:

- `phy.h`, required for `struct rtw89_rfk_tbl`.

Source-pair dependency:

- Every extern here must match an emitted `RTW89_DECLARE_RFK_TBL()` symbol in `rtw8852a_rfk_table.c`.
- Every consumer must include this header rather than guessing table names or layouts.

The include guard name, `__RTW89_8852A_RFK_TABLE_H__`, prevents duplicate declarations during normal kernel-style include graphs.

## Risks and Edge Cases

- Declaration/definition drift is the main risk. Adding a table in the `.c` file without an extern prevents external use; adding an extern without a matching definition creates a link failure when referenced.
- The header provides no semantic grouping type, so consumers can accidentally pass a table from the wrong calibration phase if names are misread.
- Because all symbols have external linkage, accidental duplicate table names in another object would be a build/link problem.
- Changes to `struct rtw89_rfk_tbl` in `phy.h` affect every declaration here, though the header itself has no direct control over layout.

## Test Signals

- Compile signal: all declarations resolve cleanly when `rtw8852a_rfk.c` references the tables.
- Definition coverage signal: each extern in the header has a matching `RTW89_DECLARE_RFK_TBL()` in the `.c` file, and the `.c` file's exported table count remains intentional.
- Consumer signal: RFK paths in `rtw8852a_rfk.c` continue to select the correct A/B, 2G/5G, subband, DBCC, and non-DBCC table names after any rename or table addition.

## Research Notes

The full 86-line header was read. No source edits were made. Its primary importance is maintaining a stable, source-tree-local ABI between declarative RFK table data and the procedural RFK implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk_table.h -->
