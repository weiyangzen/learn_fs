# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.h

`rfkill.h` declares the b43 rfkill interface used by core registration and radio-state code.

It forward-declares `struct ieee80211_hw` and `struct b43_wldev`, then declares `b43_rfkill_poll(struct ieee80211_hw *hw)` and `b43_is_hw_radio_enabled(struct b43_wldev *dev)`. The implementation reads hardware radio-enable state and synchronizes mac80211 rfkill state.

The header has no control flow, mutable state, or persistence. It is integrated by the b43 main hw ops, where `b43_rfkill_poll()` is registered as the rfkill poll callback, and by code needing direct hardware radio-enable checks.

Risks are interface-lifetime assumptions: callers must pass valid b43 contexts and rely on the implementation for locking and power management. Test signals include successful b43 builds and runtime rfkill polling on devices with hardware radio switches.
