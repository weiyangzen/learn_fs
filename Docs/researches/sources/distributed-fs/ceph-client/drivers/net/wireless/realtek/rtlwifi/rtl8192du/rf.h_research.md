# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.h

Purpose: Declares RTL8192DU RF6052 configuration and peer-PHY power helpers.

Important APIs: `rtl92du_phy_rf6052_config()` is the RF initialization entry point. `rtl92du_phy_enable_anotherphy()` and `rtl92du_phy_powerdown_anotherphy()` are shared by RF and PHY band/channel code.

Control flow/integration: `phy.c` includes this for peer-PHY handling during RF switching; `sw.c` reaches RF setup through `rtl92du_phy_rf_config()`.

State and persistence: Header is stateless. Implementations mutate routing flags and peer MAC/PHY power bits in live driver state.

Dependencies: Requires `struct ieee80211_hw` and `bool` from rtlwifi/Linux includes.

Risks/test signals: Prototype drift and incorrect helper use are the main risks. Build rtl8192du and test RF initialization on dual-interface hardware.
