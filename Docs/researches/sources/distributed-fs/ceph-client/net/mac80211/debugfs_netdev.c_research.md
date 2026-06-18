# sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.c

## Purpose

`debugfs_netdev.c` creates and manages debugfs directories for mac80211 virtual interfaces and MLO links. It exposes common rate-control masks, interface state, per-link tx power and SMPS, station/AP/IBSS/mesh-specific diagnostics, TSF controls, active-link controls, and hooks for driver-owned per-vif/per-link debugfs files.

## Important APIs, Types, And Functions

The lifecycle APIs are `ieee80211_debugfs_remove_netdev()`, `ieee80211_debugfs_rename_netdev()`, `ieee80211_debugfs_recreate_netdev()`, `ieee80211_link_debugfs_add()`, `ieee80211_link_debugfs_remove()`, `ieee80211_link_debugfs_drv_add()`, and `ieee80211_link_debugfs_drv_remove()`. Internal wrapper helpers `ieee80211_if_read_sdata()`, `ieee80211_if_write_sdata()`, `ieee80211_if_read_link()`, and `ieee80211_if_write_link()` route debugfs operations through `wiphy_locked_debugfs_read/write()`.

Macro families generate file operations for sdata and link fields: `IEEE80211_IF_FILE*` and `IEEE80211_IF_LINK_FILE*`. Notable writable handlers include `ieee80211_if_parse_smps()`, `ieee80211_if_parse_tkip_mic_test()`, `ieee80211_if_parse_beacon_loss()`, `ieee80211_if_parse_uapsd_queues()`, `ieee80211_if_parse_uapsd_max_sp_len()`, `ieee80211_if_parse_tdls_wider_bw()`, `ieee80211_if_parse_tsf()`, and `ieee80211_if_parse_active_links()`.

## Control Flow

`ieee80211_debugfs_add_netdev()` creates `netdev:<name>`, stores it in `sdata->vif.debugfs_dir`, aliases the default link directory to it, creates a `stations` subdirectory, adds interface-type-specific files, and adds default-link files for non-MLD vifs. `ieee80211_debugfs_recreate_netdev()` removes and recreates this tree, then re-invokes driver debugfs hooks if the vif is in the driver.

`add_files()` always adds `flags` and `state`, adds common rate/AQM files for non-monitor types, then dispatches by iftype: station files include BSSID/AID/beacon timeout, TKIP MIC test injection, beacon-loss trigger, U-APSD controls, TDLS wider bandwidth, valid/active links, and dormant links; AP files include PS/multicast counters, TKIP MIC test, and multicast-to-unicast; AP VLAN exposes multicast station count; IBSS/mesh expose TSF; mesh adds stats and configuration directories.

Link debugfs for MLO creates `link-<id>`, adds link address and tx-power files, and station SMPS controls where applicable. Driver link debugfs is added through `drv_link_add_debugfs()` and removed by deleting/recreating the link directory without driver data.

## State And Persistence

The file stores dentry pointers in `sdata->vif.debugfs_dir`, `sdata->deflink.debugfs_dir`, `sdata->debugfs.subdir_stations`, and `link->debugfs_dir`. Reads expose live `sdata`, `vif`, `bss_conf`, queue, mesh, TSF, and link-mask state. Writes can change SMPS requests, inject TKIP MIC failure frames, synthesize beacon loss, adjust U-APSD settings, prohibit/allow TDLS wider bandwidth, reset/set/offset TSF through driver ops, and call `ieee80211_set_active_links()`.

Most sdata/link file access uses wiphy-locked debugfs helpers. AQM reads take `local->fq.lock`. TSF operations call driver wrappers and recalculate DTIM.

## Dependencies And Integration Points

This file depends on debugfs, netdevice and cfg80211 types, mac80211 rate/driver ops, mesh Kconfig, active-link management, station debugfs directories, and driver debugfs callbacks. It is called by interface/link lifecycle paths and by `driver-ops.c` when adding/removing driver-side debugfs entries.

## Risks

The most concrete implementation risk is in `ieee80211_if_write_link_handler()`: it declares `struct ieee80211_if_write_sdata_data *d = data` even though `ieee80211_if_write_link()` passes `struct ieee80211_if_write_link_data`. Because both structures contain a function pointer followed by a pointer, this may compile but calls a link write parser through an incompatible function pointer type and passes the link pointer as if it were `sdata`; link write files such as `smps` should be tested carefully. Writable debugfs entries can trigger live protocol behavior, including MIC failure frames, beacon loss, TSF mutation, and active-link changes. Directory recreation can drop driver debugfs entries if lifecycle ordering is wrong.

## Test Signals

Coverage should create/remove/rename/recreate netdev debugfs for station, AP, AP VLAN, IBSS, mesh, monitor, NAN, MLD and non-MLD cases; add/remove MLO link directories; verify driver debugfs hooks are re-added after recreation; exercise `active_links`, `smps`, `tsf`, `tkip_mic_test`, `beacon_loss`, U-APSD, and mesh config files with valid/invalid input; and run KASAN/lockdep while writing link-level files to catch the handler type mismatch.
