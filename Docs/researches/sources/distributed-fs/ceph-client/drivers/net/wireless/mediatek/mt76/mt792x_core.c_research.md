# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_core.c

## Purpose
This file provides shared MT792x mac80211/core behavior: TX routing with PM gating, stop and interface removal, TSF and channel context helpers, ethtool/station statistics, wiphy capability initialization, firmware feature probing, PM ownership wrappers, firmware loading, WCID initialization, and MAC address list generation.

## Important APIs, Types, And Functions
Exports include `mt792x_tx()`, `mt792x_stop()`, `mt792x_remove_interface()`, `mt792x_conf_tx()`, `mt792x_get_stats()`, `mt792x_get_tsf()`, `mt792x_set_tsf()`, `mt792x_tx_worker()`, timers, `mt792x_flush()`, channel context assign/unassign, wakeup, ethtool string/count/stats callbacks, `mt792x_sta_statistics()`, `mt792x_set_coverage_class()`, `mt792x_init_wiphy()`, `mt792x_get_mac80211_ops()`, `mt792x_init_wcid()`, PM ownership wrappers, `mt792x_load_firmware()`, and `mt792x_config_mac_addr_list()`.

## Control Flow
TX selects a WCID from station link state or vif pseudo-station, rewrites MLO addresses for MLD data frames, and either sends immediately under a PM reference or queues the SKB for wake. Stop cancels MAC/PM/reset work, frees pending PM SKBs, optionally disables the MAC in firmware, and clears running state. Interface removal calls the shared BSS cleanup routine under the MT792x mutex. Wiphy init advertises interface combinations based on CNM firmware capability and sets scan, ROC, offload, PS, ACK-signal, channel-switch, and aggregation features. Firmware feature probing reads the firmware trailer release-info tags to decide whether channel context/ROC ops remain native or are replaced by mac80211 emulation. Firmware load restarts MCU, loads patch/RAM images, waits for N9 ready, and enables WoWLAN support under PM.

## State And Persistence
The file mutates PM queues and stats, `mphy` running/PM state, `dev->mt76.wcid[]`, global WCID, vif/omac masks, per-vif queue params, mib/aggr stats, station TX rate/stat state, wiphy capabilities, firmware feature bits, MAC address list, and PM awake/doze counters. Firmware state is persistent after load but reset/replay is handled elsewhere.

## Dependencies And Integration Points
It is tightly integrated with mac80211/cfg80211, mt76 TX/WCID/firmware helpers, connac PM, firmware image format, page-pool/ethtool stats, MLO link APIs, and bus-specific HIF ops.

## Risks
PM gating can reorder or defer TX; failure to wake or unref can stall queues. MLO address rewriting dereferences RCU link objects and assumes valid link IDs. Firmware feature parsing is offset-sensitive and can disable native ROC/channel context if trailer parsing fails. Wiphy flags must match firmware/driver capabilities or mac80211 will call unsupported flows.

## Test Signals
TX under awake/sleep states, MLO station traffic, interface add/remove, TSF read/write, CNM and non-CNM firmware, ethtool stats, station statistics, firmware load failures, WoWLAN exposure, and PM ownership errors validate this shared core.
