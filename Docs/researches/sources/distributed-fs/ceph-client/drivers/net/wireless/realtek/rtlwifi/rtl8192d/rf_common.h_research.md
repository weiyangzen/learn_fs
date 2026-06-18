# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/rf_common.h

Purpose: Declares shared RF6052 bandwidth and TX-power programming entry points.

Important APIs/types: Exposes `rtl92d_phy_rf6052_set_bandwidth()`, `rtl92d_phy_rf6052_set_cck_txpower()`, and `rtl92d_phy_rf6052_set_ofdm_txpower()`.

Control flow: No runtime flow; callers use these functions after EEPROM power tables, RF paths, current channel, and current bandwidth are initialized.

State and persistence: Functions declared here mutate RF/BB registers and `rtlphy->rfreg_chnlval[]`; the header owns no state.

Dependencies and integration: Included by PHY common and RF implementation. Requires `ieee80211_hw` and kernel integer types.

Risks: API accepts raw power-level byte arrays; callers must provide at least path A/B entries and a valid channel. Wrong call order can program invalid TX power.

Test signals: Compile coverage and TX-power/channel-change tests via `rtl92d_phy_set_txpower_level()`.
