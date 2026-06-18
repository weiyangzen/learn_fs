# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.c

Purpose: `rf.c` implements RF6052-specific RF bandwidth setup, CCK/OFDM transmit-power programming, regulatory power-offset application, and RF path configuration for RTL8723AE.

Important APIs/functions: exported functions are `rtl8723e_phy_rf6052_set_bandwidth`, `rtl8723e_phy_rf6052_set_cck_txpower`, `rtl8723e_phy_rf6052_set_ofdm_txpower`, and `rtl8723e_phy_rf6052_config`. Internal helpers compute OFDM/MCS power bases, calculate per-register write values under regulatory mode, clamp and write OFDM power registers, and load RF table data via `_rtl8723e_phy_rf6052_config_parafile`.

Control flow: bandwidth setup updates cached `rtlphy->rfreg_chnlval[0]` and writes RF `RF_CHNLBW`. CCK power expands per-path power indexes into per-rate AGC words, handles scan mode and regulatory mode, adds original offsets for regulatory mode 0, clamps to `RF6052_MAX_TX_PWR`, and writes CCK AGC registers. OFDM power computes legacy and MCS bases, applies one of four regulatory modes plus dynamic BT high-power reductions, then writes six OFDM/MCS register groups per path. RF config sets total RF path count from RF type, toggles RF environment bits on BB interfaces, applies the RF header table for each active path, and restores RF environment bits.

State and persistence: uses `rtlphy->rfreg_chnlval`, `rtlphy->current_chan_bw`, `rtlphy->rf_type`, `rtlphy->num_total_rfpath`, `rtlphy->mcs_txpwrlevel_origoffset`, `rtlefuse` tx-power/regulatory/group arrays, and `rtlpriv->dm.dynamic_txhighpower_lvl`. Hardware persistence is BB TX AGC registers and RF path registers.

Dependencies/integration: called by `phy.c` during RF config, bandwidth switching, and tx-power updates. Uses `reg.h` register/mask definitions, `def.h` RF path/rate constants, and `table.c` RF arrays through `rtl8723e_phy_config_rf_with_headerfile`.

Risks: tx-power arithmetic subtracts BT dynamic reductions from unsigned values before final clamping, so underflow must be considered when changing logic. Regulatory modes are magic-number driven. Path B calculations exist even for 1T1R, but actual active path count is limited during config. Power table offsets must be initialized by PHY PG-table parsing before runtime power updates.

Test signals: tx-power register dumps for channels 1, 6, 11/13, 20 and 40 MHz, scan vs non-scan mode, regulatory modes 0-3, BT high-power levels, RF_1T1R config, and bandwidth changes. Confirm no power values exceed `0x3f` after writes.
