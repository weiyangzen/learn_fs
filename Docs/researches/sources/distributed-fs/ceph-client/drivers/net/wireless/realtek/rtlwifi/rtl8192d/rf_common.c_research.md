# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.c

Purpose: Implements shared RF6052 bandwidth and TX-power programming for RTL8192D.

Important APIs/functions: `rtl92d_phy_rf6052_set_bandwidth()` sets RF channel bandwidth bits. `rtl92d_phy_rf6052_set_cck_txpower()` computes and writes CCK TXAGC values. `rtl92d_phy_rf6052_set_ofdm_txpower()` computes OFDM/MCS write values by power base, regulatory mode, bandwidth, channel group, and RF path, then writes TXAGC registers.

Control flow: Bandwidth setting updates cached `rtlphy->rfreg_chnlval[]` and `RF_CHNLBW` bits for each active path. CCK power builds per-path replicated byte values from requested power levels, special-cases active scanning and regulatory mode, applies offset tables when allowed, clamps to `RF6052_MAX_TX_PWR`, then writes split CCK registers. OFDM power derives OFDM and MCS bases from EEPROM differences, selects regulatory write values for Realtek performance, Realtek regulatory groups, better regulatory zero offset, or customer limits, clamps each byte, writes A/B path TXAGC registers, and adjusts adjacent fallback bytes for the final MCS groups.

State and persistence: Consumes `rtl_efuse` regulatory and power-group tables, `rtl_phy->mcs_offset`, `pwrgroup_cnt`, current bandwidth, RF type, and scan state. Writes BB TXAGC and RF bandwidth registers.

Dependencies and integration: Called by `rtl92d_phy_set_txpower_level()` and bus-specific channel/bandwidth code. Uses register constants from `reg.h` and channel grouping from `phy_common.c`.

Risks: Regulatory branch behavior is subtle; changing offsets can violate power limits or reduce throughput. CCK scan behavior uses max power unless regulatory nonzero enables normal levels. OFDM path assumes two RF paths for write loops even when RF type limits active streams. Byte-level clamping and special fallback writes must match hardware expectations.

Test signals: Per-rate TX power register dumps across channels/bandwidths/regulatory modes, active scan behavior, RF bandwidth switch tests, and radiated power/regulatory validation.
