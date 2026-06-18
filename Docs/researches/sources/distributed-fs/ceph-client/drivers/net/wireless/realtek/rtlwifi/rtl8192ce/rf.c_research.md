# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.c

## Purpose
This file implements RTL8192CE RF6052 radio configuration and TX-power programming. It handles RF bandwidth bits, CCK/OFDM TX AGC tables, EEPROM regulatory modes, dynamic high-power reductions, and RF table loading for one- and two-transmit-chain devices.

## Important APIs, Types, And Functions
Public functions are `rtl92ce_phy_rf6052_set_bandwidth()`, `rtl92ce_phy_rf6052_set_cck_txpower()`, `rtl92ce_phy_rf6052_set_ofdm_txpower()`, and `rtl92ce_phy_rf6052_config()`. Internal helpers include `rtl92c_phy_get_power_base()`, `_rtl92c_get_txpower_writeval_by_regulatory()`, `_rtl92c_write_ofdm_power_reg()`, and `_rtl92ce_phy_rf6052_config_parafile()`.

## Control Flow
Bandwidth changes update cached `rfreg_chnlval[0]` and write `RF_CHNLBW` for path A. CCK TX power builds four-byte AGC words per RF path, handles scan mode and regulatory mode 0 offsets, clamps each byte to `RF6052_MAX_TX_PWR`, then writes CCK TXAGC registers. OFDM TX power derives OFDM and MCS bases from EFUSE power, HT20/legacy differences, applies regulatory mode logic and customer limits, adjusts for BT dynamic high-power levels, clamps and writes six OFDM/MCS register groups for path A and B. RF config sets total RF paths and writes radio table arrays while toggling RFENV bits.

## State And Persistence
Runtime state includes `rtlphy->rfreg_chnlval`, `num_total_rfpath`, `current_chan_bw`, `mcs_offset`, `pwrgroup_cnt`, EFUSE power/regulatory arrays, and `rtlpriv->dm.dynamic_txhighpower_lvl`. Hardware state includes RF_CHNLBW, RFENV, radio registers, and TXAGC BB registers.

## Dependencies And Integration Points
It depends on `reg.h`, `def.h`, `phy.h`, `rf.h`, `dm.h`, and `table.c` RF arrays through `rtl92c_phy_config_rf_with_headerfile()`. Common PHY TX-power and channel paths call these functions through HAL ops.

## Risks And Edge Cases
Regulatory mode math is complex and byte-packed; signed differences are represented in small fields from EFUSE. Dynamic BT reductions subtract packed byte values and can underflow before clamp logic if not considered. Bandwidth programming only writes path A cached channel value. 1T devices use a dummy one-entry path-B array.

## Test Signals
Validate RF table load on 1T/2T devices, TX power per CCK/OFDM/MCS rate, regulatory modes 0-3, scan-mode power behavior, BT high-power reductions, 20/40 MHz bandwidth changes, and no TXAGC byte above `0x3f`.
