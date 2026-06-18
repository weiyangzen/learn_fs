# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.h

## Purpose
`testmode.h` declares the wlcore cfg80211 testmode command entry point.

## Important APIs
The only declaration is `wl1271_tm_cmd(struct ieee80211_hw *hw, struct ieee80211_vif *vif, void *data, int len)`. It includes `<net/mac80211.h>` for the mac80211 types required by the callback signature.

## Control Flow, State, and Integration
No state or logic exists in the header. `main.c` includes it to register `wl1271_tm_cmd` in `wl1271_ops` through `CFG80211_TESTMODE_CMD()`, while `testmode.c` provides the implementation.

## Risks and Test Signals
Risks are limited to callback signature drift relative to cfg80211/mac80211 testmode expectations. Compile coverage and a cfg80211 testmode command smoke test validate this header.
