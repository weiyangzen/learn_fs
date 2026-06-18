# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.h

`rtw8821a_table.h` declares the static RTL8821A table and power-flow symbols defined in `rtw8821a_table.c`. `rtw8821a.c` consumes these declarations when building `rtw8821a_hw_spec`.

The exported data includes MAC, AGC, BB, BB power-group, RF-A, and TX power-limit `struct rtw_table` objects; `card_enable_flow_8821a[]`, `enter_lps_flow_8821a[]`, and `card_disable_flow_8821a[]`; and `rtw8821a_rtw_pwr_track_tbl`. There is no runtime code in the header.

The declarations integrate table loading, power sequencing, regulatory/power-by-rate behavior, and thermal tracking. Risks are unresolved symbols or table/profile drift. Test signals are build/link success, all declared tables referenced by `rtw8821a_hw_spec`, successful LPS/card disable flows, and thermal tracking access to the power-track table.
