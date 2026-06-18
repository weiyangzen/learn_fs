# sources/distributed-fs/ceph-client/net/mac80211/link.c

## Purpose
`link.c` implements multi-link operation (MLO) link object setup, teardown, valid-link changes, AP VLAN link mirroring, and active-link switching for station vifs. It manages the relationship between `struct ieee80211_sub_if_data`, per-link `struct ieee80211_link_data`, per-link `struct ieee80211_bss_conf`, driver `change_vif_links`/`change_sta_links` callbacks, channel contexts, keys, stations, and debugfs.

## Important APIs, Types, And Functions
Public functions include `ieee80211_apvlan_link_setup()`, `ieee80211_apvlan_link_clear()`, `ieee80211_link_setup()`, `ieee80211_link_init()`, `ieee80211_link_stop()`, `ieee80211_vif_set_links()`, `ieee80211_set_active_links()`, and `ieee80211_set_active_links_async()`. Static helpers include `ieee80211_update_apvlan_links()`, `ieee80211_tear_down_links()`, `ieee80211_free_links()`, `ieee80211_check_dup_link_addrs()`, `ieee80211_set_vif_links_bitmaps()`, `ieee80211_vif_update_links()`, and `_ieee80211_set_active_links()`.

## Control Flow
`ieee80211_vif_set_links()` calls `ieee80211_vif_update_links()`, which allocates new link containers, snapshots old link/conf pointers, removes pointers for deleted links, initializes added links, checks duplicate link addresses, tears down removed links and their keys, updates valid/dormant/active bitmaps, calls `drv_change_vif_links()` for non-AP-VLAN vifs, refreshes AP VLAN child links for APs, and handles rollback on errors. Link initialization fills `link_conf`, assigns addresses/BSSID for AP/AP_VLAN links, initializes work items for CSA/color/DFS, sets power defaults, installs RCU pointers, and adds debugfs for non-default links. Active-link switching is station-only: it validates usable links, optionally switches through an overlapping active link, changes driver vif links, releases channels for removed links, assigns channels for added links, recalculates station aggregates, changes station links, switches per-link key hardware offload, notifies link info for added links, and finally updates `vif.active_links`.

## State And Persistence
Persistent state includes `sdata->link[]`, `sdata->vif.link_conf[]`, `sdata->deflink`, allocated `link_container` objects, `vif.valid_links`, `vif.dormant_links`, `vif.active_links`, `sdata->desired_active_links`, AP VLAN `wdev.valid_links` and per-link addresses, per-link work items, channel contexts, and per-link keys. Removed links are detached with RCU pointer clearing, stopped, synchronized, and then freed after key lists are destroyed.

## Dependencies And Integration Points
The file depends on MLO definitions in `<net/mac80211.h>` and `ieee80211_i.h`, driver ops for vif/station link changes and link activation capability, key removal/switching from `key.c`, managed-mode link setup/stop and QoS helpers, TDLS teardown, channel-context assignment/release, CSA/color/DFS work callbacks, debugfs netdev link entries, AP VLAN state from `iface.c`, and station aggregation recalculation.

## Risks And Edge Cases
Rollback is only partial after some state changes: once keys are removed from deleted links, the code explicitly cannot undo that. Active-link switching contains warnings for driver failures that are hard to recover from after internal state is advanced. Channel assignment for newly active links is forced not to fail from mac80211's perspective, relying on driver recovery if hardware fails. AP links are always treated as active, station active links are limited initially, and duplicate per-link MAC addresses are rejected. Async active-link changes are ignored for stopped or non-station vifs and are skipped during reconfiguration.

## Test Signals
Tests should cover adding/removing valid links, dormant-link validation, AP VLAN link propagation with and without 4-address stations, duplicate link address rejection, driver `change_vif_links()` failure rollback, link teardown key movement/freeing, station active-link switch with overlapping and non-overlapping masks, TDLS/channel release on deactivation, key hardware offload switch on link activation, async active-link work cancellation on stop, and lockdep/RCU checks during concurrent station/link updates.
