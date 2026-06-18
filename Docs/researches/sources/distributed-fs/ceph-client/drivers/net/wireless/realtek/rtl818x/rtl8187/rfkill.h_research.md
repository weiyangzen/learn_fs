# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.h

## Purpose
This header declares the RTL8187 rfkill integration functions used by `dev.c`.

## Important APIs, Types, And Functions
It declares `rtl8187_rfkill_init()`, `rtl8187_rfkill_poll()`, and `rtl8187_rfkill_exit()`.

## Control Flow
No runtime control flow is present. The declarations support probe, mac80211 polling, and disconnect paths.

## State And Persistence
No state is defined here. State lives in `struct rtl8187_priv` and wiphy rfkill core state.

## Dependencies And Integration Points
The declarations take `struct ieee80211_hw *`, matching mac80211 hardware objects. `dev.c` includes this header to wire rfkill into `ieee80211_ops` and probe/disconnect.

## Risks
The header is intentionally small; the main risk is missing include coverage for `struct ieee80211_hw` if include order changes.

## Test Signals
Compile-time use by `dev.c` and runtime rfkill polling covered by `rfkill.c`.
