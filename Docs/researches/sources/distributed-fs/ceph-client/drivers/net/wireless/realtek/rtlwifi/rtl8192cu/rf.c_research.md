
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.c

Purpose: Implements RTL8192CU RF6052 transmit-power programming, bandwidth RF-register adjustment, and RF table configuration.

Important APIs/functions: `rtl92cu_phy_rf6052_set_bandwidth()` toggles RF channel/bandwidth bits for 20 or 20/40 MHz. `rtl92cu_phy_rf6052_set_cck_txpower()` computes CCK AGC values from channel power levels, dynamic tx-high-power state, external PA, and regulatory offsets, then writes CCK TXAGC BB registers. `rtl92c_phy_get_power_base()` builds OFDM/MCS base power from EEPROM channel power and HT/legacy diffs. `_rtl92c_get_txpower_writeval_by_regulatory()` applies regulatory modes 0-3 and customer limits. `_rtl92c_write_ofdm_power_reg()` clamps per-rate bytes and writes OFDM/MCS TXAGC registers. `rtl92cu_phy_rf6052_set_ofdm_txpower()` iterates six register groups. `rtl92cu_phy_rf6052_config()` and `_rtl92c_phy_rf6052_config_parafile()` configure one or two RF paths from table arrays.

Control flow: Channel/power changes compute bases, regulatory write values, clamp to `RF6052_MAX_TX_PWR`, and write BB registers. RF init determines `num_total_rfpath` from `rtlphy->rf_type`, enables RF interface bits, replays RF path tables, then restores RF environment bits.

State and persistence: Uses EEPROM-derived tx-power arrays, `rtlphy->mcs_offset`, `rtlphy->current_chan_bw`, `rtlphy->rfreg_chnlval`, `rtlphy->num_total_rfpath`, `rtlpriv->dm.dynamic_txhighpower_lvl`, and `rtlefuse->external_pa/eeprom_regulatory`. Writes persistent RF/BB TX power registers.

Dependencies/integration: Called through HAL ops in `sw.c` and common PHY code. Depends on CU table arrays, `rtl_set_bbreg()`, `rtl_set_rfreg()`, and EEPROM parsing in `hw.c`.

Risks: Regulatory and tx-power calculations are safety-sensitive. Underflow can occur in the BT1 adjustment (`writeval - 0x06060606`) if values are low before unsigned subtraction. External PA clipping only occurs in the scanning CCK branch. Incorrect table selection for 1T/2T/high-PA devices can misprogram RF paths.

Test signals: Per-channel tx-power verification, regulatory mode fixtures, dynamic tx-power transitions, external PA scan behavior, RF path count tests, 20/40 MHz bandwidth changes, and spectrum/regulatory compliance measurements.
