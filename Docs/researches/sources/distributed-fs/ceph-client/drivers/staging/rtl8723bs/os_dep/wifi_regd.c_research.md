# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/wifi_regd.c

Purpose: supplies rtl8723bs cfg80211 regulatory-domain setup and channel flag application for 2.4 GHz operation.

Important APIs/types/functions: `rtw_regdom_rd` is a custom world-like regulatory domain with active channels 1-11 and passive channels 12-13. `_rtw_reg_apply_flags()` disables all wiphy channels then re-enables channels present in the driver's channel plan, setting `IEEE80211_CHAN_NO_IR` for passive scan. Public entry points are `rtw_regd_init()` and `rtw_reg_notifier()`.

Control flow: `rtw_wdev_alloc()` calls `rtw_regd_init()`, which stores the notifier, sets custom regulatory flags, applies `rtw_regdom_rd`, then hard-applies channel flags from `mlmeextpriv.channel_set`. Later regulatory notifications call `_rtw_reg_notifier_apply()`, which reapplies the same driver channel-plan flags.

State and persistence: regulatory state persists in `wiphy` flags, custom regdomain, channel flags, and the adapter `mlmeextpriv.channel_set/max_chan_nums` generated elsewhere from the registry/efuse channel plan.

Dependencies and integration: depends on cfg80211 regulatory APIs, `rtw_ieee80211_channel_to_frequency()` from cfg80211 glue, and adapter lookup via `wiphy_to_adapter()`.

Risks: the request contents are ignored, so country-specific updates do not alter the base domain beyond the driver's hard channel plan. Channel 14 is not in the custom regdomain even though frequency conversion supports it. All bands are disabled first, which is safe only because this chip exposes 2.4 GHz here.

Test signals: verify channels enabled for a representative channel plan, passive/no-IR behavior for channels 12-13, notifier reapplication after regulatory events, and absence of enabled channels not present in `channel_set`.
