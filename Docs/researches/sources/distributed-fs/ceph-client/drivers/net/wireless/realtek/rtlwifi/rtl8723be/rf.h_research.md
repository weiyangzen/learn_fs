<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.h

## Purpose
Declares the RTL8723BE RF6052 interface used by PHY and hardware initialization code, and defines the chip's maximum encoded TX power value.

## Important APIs, Types, And Functions
- `RF6052_MAX_TX_PWR` limits per-rate TX power bytes to `0x3f`.
- `rtl8723be_phy_rf6052_set_bandwidth(struct ieee80211_hw *hw, u8 bandwidth)` programs RF bandwidth bits.
- `rtl8723be_phy_rf6052_set_cck_txpower(struct ieee80211_hw *hw, u8 *ppowerlevel)` programs CCK TX AGC.
- `rtl8723be_phy_rf6052_set_ofdm_txpower(struct ieee80211_hw *hw, u8 *ppowerlevel_ofdm, u8 *ppowerlevel_bw20, u8 *ppowerlevel_bw40, u8 channel)` programs OFDM/HT TX AGC.
- `rtl8723be_phy_rf6052_config(struct ieee80211_hw *hw)` loads RF table configuration.

## Control Flow
The header has no control flow. It exposes the RF configuration hooks implemented in `rf.c` to the chip PHY code.

## State And Persistence
The declarations operate on `struct ieee80211_hw` and indirectly mutate persistent RF/BB registers, `rtl_priv` PHY state, and EFUSE-derived power behavior in the implementation.

## Dependencies And Integration Points
Included by `rf.c` and chip PHY/hardware code that needs RF bandwidth, power, or initialization hooks. It assumes `struct ieee80211_hw`, `u8`, and `bool` are available through the including rtlwifi headers.

## Risks And Edge Cases
Changing function signatures breaks the `rtl8723be` PHY integration. Changing `RF6052_MAX_TX_PWR` affects regulatory and thermal TX power clamping for every rate.

## Test Signals
Compile coverage of all includers, successful RF initialization, channel bandwidth switching, and TX power programming without register value overflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.h -->
