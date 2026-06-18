# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.c

`rtw8821a_table.c` contains the RTL8821A static MAC, AGC, BB, RF-A, BB power-group, TX power limit, power-sequence, and thermal power-tracking data. The raw arrays are converted into exported rtw88 table objects with `RTW_DECL_TABLE_PHY_COND`, `RTW_DECL_TABLE_BB_PG`, `RTW_DECL_TABLE_RF_RADIO`, and `RTW_DECL_TABLE_TXPWR_LMT`.

There is no procedural logic beyond static initialization. Runtime control is external: PHY initialization walks the table objects and writes register/value pairs, power management walks `struct rtw_pwr_seq_cmd` arrays until `RTW_PWR_CMD_END`, and dynamic power tracking indexes `rtw8821a_rtw_pwr_track_tbl`. Public power flows compose card enable, LPS entry, and card disable from transition arrays.

State is constant data until applied. Applying it persistently changes MAC/BB/AGC/RF registers and interface-specific power state. Dependencies are `main.h`, `phy.h`, table macros, and `rtw8821a_table.h`; integration is through `rtw8821a_hw_spec`, RFE definitions, regulatory TX power code, and the power-sequence parser.

Risks include wrong conditional markers, wrong regulatory/channel limit entries, and power-sequence errors that leave enable/LPS/disable stuck. Test signals include successful probe table load, regulatory TX power checks, 2.4/5 GHz operation, thermal compensation, LPS entry, card disable/reenable, and USB plus future PCI/SDIO interface-mask coverage.
