# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals.h

Purpose: this header contains the `mt76x0_bbp_switch_tab` table used to program BBP/AGC/RXFE settings according to RF band and bandwidth.

Important data: `mt76x0_bbp_switch_tab` is an array of `struct mt76x0_bbp_switch_item` values. Each row combines band/bandwidth masks such as `RF_G_BAND`, `RF_A_BAND`, `RF_BW_20`, `RF_BW_40`, and `RF_BW_80` with a BBP register/value pair. The table covers AGC registers 4, 6, 8, 12, 13, 14, 26, 27, 28, 31, 32, 33, 35, 39, 43, 51, 53, 55, 58, RXO 28, and RXFE 0.

Control flow and integration: `init.c` applies the subset matching G-band 20 MHz during initial BBP setup. `phy.c` applies the matching rows on every channel/bandwidth change through `mt76x0_phy_set_chan_bbp_params`, with special adjustment for `MT_BBP(AGC, 8)` based on EEPROM-derived LNA gain.

State and persistence behavior: this file has no executable state; it supplies constant calibration values written into BBP hardware registers at runtime. No values are persisted back to hardware storage.

Dependencies: it includes `phy.h` for the switch item type and RF mask constants. Register macros come indirectly from the mt76x02 headers included by users.

Risks: values are hardware-calibration constants. Incorrect masks can apply 2 GHz gain tables to 5 GHz channels or wrong bandwidth behavior. Since AGC 8 is dynamically adjusted, table shape must remain compatible with that special case.

Test signals: channel changes across 2 GHz/5 GHz and 20/40/80 MHz should maintain receive sensitivity, false CCA rates, and stable AGC. DFS/radar channels are particularly useful for observing gain behavior.
