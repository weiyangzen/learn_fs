# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.c

## Purpose
Regulatory-domain setup and notifier handling for rtlwifi. It maps efuse channel plans to Realtek country codes, selects static custom regdomains, applies radar/passive-scan/beaconing flags, stores alpha2, and updates channel flags on notifications.

## Important APIs, Types, And Functions
Public APIs are `rtl_regd_init()` and `rtl_reg_notifier()`. Internals include `all_countries`, static regdomains, `_rtl_is_radar_freq()`, `_rtl_reg_apply_beaconing_flags()`, `_rtl_reg_apply_active_scan_flags()`, `_rtl_reg_apply_radar_flags()`, `_rtl_regdomain_select()`, `_rtl_regd_init_wiphy()`, and `channel_plan_to_country_code()`.

## Control Flow
Init converts efuse channel plan, falls back to world-wide 13 if invalid, stores alpha2, installs notifier, applies custom regulatory domain, and applies radar/world flags. Notifier calls reapply DFS radar flags and relax beaconing/active-scan flags when country IE rules permit.

## State And Persistence
`rtlpriv->regd.country_code` and `alpha2` derive from efuse. Channel flags live in wiphy band/channel structures and change with regulatory events.

## Dependencies And Integration Points
Uses cfg80211 regulatory APIs, wiphy bands, efuse channel plan, and mac80211 channel flags.

## Risks
Static domains approximate channel plans. Only a small channel-plan set is mapped. DFS range is hard-coded. Active-scan relaxation must respect initiator/rule semantics.

## Test Signals
Plans 0x20/0x21/0x22/0x25/0x32/0x41/0x7f and invalid values, alpha2/regdomain selection, channel 12/13 flags, DFS flags, and notifier behavior.
