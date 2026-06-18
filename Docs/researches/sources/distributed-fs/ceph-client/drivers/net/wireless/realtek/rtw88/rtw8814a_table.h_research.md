# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.h

`rtw8814a_table.h` is the declaration surface for the RTL8814A static hardware tables consumed by the rtw88 chip profile in `rtw8814a.c`. It exports `struct rtw_table` instances for MAC, AGC, BB, BB power-group, RF path A-D, and multiple RFE-specific TX power limit tables, plus `struct rtw_pwr_track_tbl` instances and card enable/disable power flows.

There is no runtime control flow. The header is link-time wiring: `rtw8814a.c` includes it, places selected symbols into RFE definitions and `rtw_chip_info`, and the shared PHY/power helpers later apply those tables. State is immutable data until applied; applying the tables writes MAC/BB/RF registers and power-sequence registers that persist until reset or reconfiguration.

Dependencies are common rtw88 definitions for `struct rtw_table`, `struct rtw_pwr_track_tbl`, and `struct rtw_pwr_seq_cmd`. Risks are declaration/data skew, wrong RFE table selection, unresolved symbols, or silent RF misconfiguration. Test signals include module build, probe, RF initialization across four paths, RFE option selection, regulatory power limits, thermal tracking table use, and suspend/resume power sequencing.
