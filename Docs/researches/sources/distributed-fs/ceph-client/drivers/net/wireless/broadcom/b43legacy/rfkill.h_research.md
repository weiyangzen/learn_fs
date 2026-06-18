# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/rfkill.h

## Purpose
Declares the b43legacy rfkill polling and hardware-radio-state helpers.

## Important APIs, Types, and Functions
Forward declares `struct ieee80211_hw` and `struct b43legacy_wldev`, and exposes `b43legacy_rfkill_poll()` plus `b43legacy_is_hw_radio_enabled()`.

## Control Flow, State, and Persistence
No executable state. Runtime rfkill state is maintained by `rfkill.c`, wiphy rfkill, and `struct b43legacy_wldev`.

## Dependencies and Integration Points
Consumed by b43legacy main/mac80211 registration paths that provide the rfkill poll callback and by code that needs a hardware radio switch query.

## Risks and Test Signals
Risks are limited to prototype drift. Build coverage and rfkill polling tests validate this header.
