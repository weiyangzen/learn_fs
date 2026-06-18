# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/rf.h

## Purpose
`rf.h` exposes the RF6052 helper surface for RTL8192EE and defines the maximum RF transmit-power index constant used by RF-related code.

## Important APIs, Types, And Functions
It defines `RF6052_MAX_TX_PWR` as `0x3F` and declares `rtl92ee_phy_rf6052_set_bandwidth` and `rtl92ee_phy_rf6052_config`.

## Control Flow
No control flow is implemented. Callers invoke config during PHY/RF initialization and bandwidth programming during channel-width changes.

## State And Persistence Behavior
No state is stored here. RF state is in `rtlpriv->phy` and hardware RF registers.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw` and is consumed by `phy.c` and `rf.c`. It is part of the local contract between generic PHY initialization and RF6052-specific behavior.

## Risks
The interface is narrow. The main risk is semantic: callers must use supported bandwidth values and call config before bandwidth changes so cached RF channel values are valid.

## Test Signals
Build coverage plus RF init and bandwidth-switch runtime tests cover this header.
