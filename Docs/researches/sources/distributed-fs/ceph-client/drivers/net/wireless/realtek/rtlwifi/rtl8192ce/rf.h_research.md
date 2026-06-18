# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.h

## Purpose
This header declares the RTL8192CE RF6052 radio helper interface and RF power/path limits.

## Important APIs, Types, And Functions
It defines `RF6052_MAX_TX_PWR` as `0x3f`, `RF6052_MAX_PATH` as `2`, and declares `rtl92ce_phy_rf6052_set_bandwidth()`, `rtl92ce_phy_rf6052_set_cck_txpower()`, `rtl92ce_phy_rf6052_set_ofdm_txpower()`, and `rtl92ce_phy_rf6052_config()`.

## Control Flow
The header is declarative. Common PHY code calls the declared functions through HAL ops while CE PHY initialization and RF configuration use them directly.

## State And Persistence
No storage is declared. Constants constrain runtime TXAGC writes and RF path iteration.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw` and is included by CE PHY, RF, SW, and HW-related files. It is part of the CE HAL RF contract.

## Risks And Edge Cases
The maximum TX power is a packed byte limit used by CCK and OFDM paths; changes would affect regulatory behavior. `RF6052_MAX_PATH` assumes at most two paths for this driver.

## Test Signals
Build coverage and runtime RF6052 configuration, TX-power, and bandwidth tests validate this header.
