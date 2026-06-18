# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.h

## Purpose
This header declares the RTL8723D generated table objects used by the chip implementation.

## Important APIs, Types, And Functions
It declares `rtw8723d_mac_tbl`, `rtw8723d_agc_tbl`, `rtw8723d_bb_tbl`, `rtw8723d_bb_pg_tbl`, `rtw8723d_rf_a_tbl`, and `rtw8723d_txpwr_lmt_tbl` as `const struct rtw_table`.

## Control Flow
No control flow is implemented. The declarations allow `rtw8723d.c` to bind table objects into `rtw8723d_hw_spec`, after which generic rtw88 table loaders handle traversal and programming.

## State And Persistence
The header stores no state. The declared objects are read-only table data; their application programs persistent hardware registers and provides TX power-limit policy.

## Dependencies And Integration Points
The header depends on `struct rtw_table` being visible to includers. It is included by `rtw8723d.c` and `rtw8723d_table.c`.

## Risks
The risk is interface drift between table definitions and declarations. Missing declarations prevent the chip descriptor from referencing required tables, while wrong names/types fail the build.

## Test Signals
Build/link success and successful RTL8723D PHY initialization are the primary signals. Runtime behavior should show table-driven MAC/BB/RF setup and power-limit selection working through `rtw8723d_hw_spec`.
