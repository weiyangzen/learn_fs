# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.h

## Purpose
Declares the RTL8821AE RF6052 interface used by the PHY/HAL code to configure RF paths, set channel bandwidth, and program transmit power for CCK and OFDM/MCS rates.

## Important APIs, Types, And Functions
Defines `RF6052_MAX_TX_PWR` as `0x3F` and declares `rtl8821ae_phy_rf6052_set_bandwidth`, `rtl8821ae_phy_rf6052_set_cck_txpower`, `rtl8821ae_phy_rf6052_set_ofdm_txpower`, and `rtl8821ae_phy_rf6052_config`. All APIs operate on `struct ieee80211_hw *` and use rtlwifi-private state reached through that object.

## Control Flow
This header has no runtime control flow. It is included by RF/PHY implementation files so channel switch and initialization paths can call the RF6052 routines.

## State And Persistence
No state is stored here. The max TX power constant constrains register byte values in `rf.c`.

## Dependencies And Integration Points
Depends on the surrounding rtlwifi include order to provide `struct ieee80211_hw`, `u8`, and `bool`. It is part of the RTL8821AE chip-specific HAL boundary used by `phy.c`, `rf.c`, and driver initialization.

## Risks And Edge Cases
The header lacks direct includes for Linux integer and mac80211 types, so standalone inclusion depends on prior includes. Any signature change must be coordinated with `rtl8821ae/phy.c` and `rtl8821ae/rf.c`.

## Test Signals
Build coverage for the RTL8821AE module is the primary signal. RF bring-up and channel-switch tests indirectly validate that all declared functions match their implementations.
