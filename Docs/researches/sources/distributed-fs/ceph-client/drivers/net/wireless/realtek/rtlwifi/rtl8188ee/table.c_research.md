# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.c

`table.c` is data-only hardware initialization content for RTL8188EE. It defines PHY register/value pairs, PHY power-group triples, RF path A register/value pairs, MAC byte register/value pairs, and AGC table entries used by PHY/RF initialization.

Important arrays are `RTL8188EEPHY_REG_1TARRAY`, `RTL8188EEPHY_REG_ARRAY_PG`, `RTL8188EE_RADIOA_1TARRAY`, `RTL8188EEMAC_1T_ARRAY`, and `RTL8188EEAGCTAB_1TARRAY`. The arrays program FPGA/baseband, CCK/OFDM, IQK, TX gain, power offsets, RF path A, MAC defaults, EDCA/SIFS/filter settings, and AGC values.

There is no code flow in this file. PHY loader code walks these arrays using lengths from `table.h`, interprets pairs or triples, handles delay sentinel entries, and writes values into MAC, BB, AGC, and RF hardware state.

The file is tightly coupled to `table.h`, PHY config-with-headerfile routines, and register definitions from `reg.h`. Risks are positional format errors, length mismatches, and accidental table edits that affect radio bring-up or sensitivity. Test signals include successful PHY/MAC/RF init, association, TX power behavior, AGC/RSSI quality, and comparison with vendor reference tables.
