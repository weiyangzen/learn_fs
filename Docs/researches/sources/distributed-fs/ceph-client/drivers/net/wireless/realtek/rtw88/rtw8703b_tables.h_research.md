# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.h

## Purpose
This header declares the RTL8703B table exports generated in `rtw8703b_tables.c`. It gives the chip implementation a stable list of table objects to attach to `struct rtw_chip_info`.

## Important APIs, Types, And Functions
The declarations are `rtw8703b_bb_pg_tbl`, `rtw8703b_txpwr_lmt_tbl`, `rtw8703b_mac_tbl`, `rtw8703b_agc_tbl`, `rtw8703b_bb_tbl`, and `rtw8703b_rf_a_tbl`, all as `const struct rtw_table`.

## Control Flow
No control flow is implemented. The header enables `rtw8703b.c` to reference table objects that are later traversed by generic rtw88 PHY and power-limit loaders.

## State And Persistence
The header owns no state. The declared tables are read-only data; when loaded, they program persistent hardware register state and provide power-limit policy data.

## Dependencies And Integration Points
It depends on the including code having `struct rtw_table` visible, normally through rtw88 core headers. It is included by `rtw8703b.c` and `rtw8703b_tables.c`.

## Risks
Mismatched declarations and definitions would break builds or bind the chip descriptor to the wrong table. Adding new table objects in the C file without updating this header prevents the chip implementation from using them.

## Test Signals
Build/link success and successful PHY table loading through `rtw8703b_hw_spec` are the main signals. Runtime proof comes from stable 8703B initialization and correct TX power-limit behavior.
