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
