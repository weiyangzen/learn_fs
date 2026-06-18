# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.h

`rf.h` is the public RTL8188EE RF6052 interface. It defines `RF6052_MAX_TX_PWR` as `0x3f` and declares the RF functions implemented in `rf.c`: bandwidth setting, CCK TX power programming, OFDM TX power programming, and RF path configuration.

The header has no control flow or persistent state. Its interface assumes callers provide `struct ieee80211_hw` and correctly sized RF path power arrays after PHY/eFuse state has been initialized.

It integrates chip-specific RF behavior with PHY/channel code and the HAL callbacks registered from `sw.c`. Risks are mostly API misuse, especially calling power functions before channel/eFuse state is valid or passing arrays not indexed for path A/B. Test signals are compile coverage, successful RF initialization, and working channel and TX power transitions.
