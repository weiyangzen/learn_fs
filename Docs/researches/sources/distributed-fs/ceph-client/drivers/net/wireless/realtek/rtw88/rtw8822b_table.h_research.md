# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b_table.h

## Purpose

`rtw8822b_table.h` is a small declaration header for RTL8822B PHY/MAC/RF initialization and regulatory power-limit tables. It does not contain table data itself; it exposes `extern const struct rtw_table` objects generated/defined in the matching RTL8822B table implementation so `rtw8822b.c` and chip-spec setup can bind the right initialization tables into `struct rtw_chip_info` and RFE definitions.

## Important APIs and Types

- Include guard `__RTW8822B_TABLE_H__` prevents duplicate declarations.
- Declares MAC, AGC, BB, BB power-by-rate, RF path A/B, and transmit power limit tables:
  - `rtw8822b_mac_tbl`, `rtw8822b_agc_tbl`, `rtw8822b_bb_tbl`
  - `rtw8822b_bb_pg_type2_tbl`, `rtw8822b_bb_pg_type3_tbl`, `rtw8822b_bb_pg_type5_tbl`
  - `rtw8822b_rf_a_tbl`, `rtw8822b_rf_b_tbl`
  - `rtw8822b_txpwr_lmt_type0_tbl`, `rtw8822b_txpwr_lmt_type2_tbl`, `rtw8822b_txpwr_lmt_type5_tbl`
- Depends on `struct rtw_table` being declared before inclusion, normally through chip or PHY headers in the surrounding `rtw88` driver.

## Control Flow and Integration

There is no executable control flow in this header. Its role is link-time integration: other RTL8822B code includes it and assigns table addresses to chip/RFE descriptors. During device bring-up, the core `rtw_phy_load_tables()` path consumes the selected `struct rtw_table` entries and calls their parse callbacks to write register sequences into MAC/BB/RF hardware blocks.

## State and Persistence

The declarations reference immutable, static table data. Persistent behavior comes from the hardware state programmed from those tables, not from this header. The declared transmit-power limit tables are especially important because they feed regulatory/rate/channel power decisions after efuse and RFE selection.

## Dependencies

This header depends on the rtw88 table abstraction and matching table definitions. It is coupled to RTL8822B chip data in `rtw8822b.c`, RFE macros in `main.h`, and table parser helpers in `phy.c`/table declaration macros.

## Risks

- Missing or mismatched table symbols cause link failures for RTL8822B modules.
- Picking the wrong power-limit or BB power-group table for an RFE type can produce incorrect transmit power, regulatory failures, or poor RF performance.
- Because the header only declares `struct rtw_table`, include order must provide the type definition; using it in a new compilation unit without proper rtw88 headers will fail.

## Test Signals

- Build coverage for RTL8822B variants should catch unresolved externs.
- Runtime signals are indirect: successful PHY table loading, correct channel/rate TX power, and absence of RF initialization errors in `RTW_DBG_PHY`/`RTW_DBG_RFK` logs.
- Regulatory and RF regression testing should exercise all RFE table types referenced here.
