# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.h

## Purpose
`rtw8812a_table.h` declares the static RTL8812A hardware data exported by `rtw8812a_table.c`. It is the table interface used by `rtw8812a.c` to populate `rtw_chip_info` and to run channel-specific AGC updates.

## Important APIs and declarations
- Table declarations for `rtw8812a_mac_tbl`, `rtw8812a_agc_tbl`, `rtw8812a_agc_diff_lb_tbl`, `rtw8812a_agc_diff_hb_tbl`, `rtw8812a_bb_tbl`, `rtw8812a_bb_pg_tbl`, `rtw8812a_bb_pg_rfe3_tbl`, `rtw8812a_rf_a_tbl`, `rtw8812a_rf_b_tbl`, and `rtw8812a_txpwr_lmt_tbl`.
- Power sequence flow declarations: `card_enable_flow_8812a`, `enter_lps_flow_8812a`, and `card_disable_flow_8812a`.
- Power tracking table declarations: `rtw8812a_rtw_pwr_track_tbl` and `rtw8812a_rtw_pwr_track_rfe3_tbl`.

## Control flow and state behavior
The header has no executable flow. It exposes immutable table objects whose interpretation is handled by rtw88 core table loaders, power sequence engines, and power tracking code. Runtime mutable state is held by the caller (`rtw_dev`, `rtw_hal`, `rtw_dm_info`) and hardware registers after the tables are applied.

## Dependencies and integration points
The declarations depend on rtw88 core types `struct rtw_table`, `struct rtw_pwr_seq_cmd`, and `struct rtw_pwr_track_tbl`. `rtw8812a.c` includes this header for chip registration and calibration, and the table implementation includes it to verify matching extern declarations.

## Risks and edge cases
- Missing or mismatched extern declarations cause link or type errors when `rtw8812a.c` references table objects.
- Because the header exposes both default and RFE3 tables, callers must choose the table matching EFUSE-derived RFE definitions.
- The power sequence pointer arrays are null-terminated; consumers rely on that convention from the implementation.

## Test signals
Build/link coverage is the primary signal. Runtime table-use signals include `rtw8812a_hw_spec` referencing all expected table objects, channel calibration being able to load low/high-band AGC diff tables, and power on/off flows resolving their declared sequence arrays.
