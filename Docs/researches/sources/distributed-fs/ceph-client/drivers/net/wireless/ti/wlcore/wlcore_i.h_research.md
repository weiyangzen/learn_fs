# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore_i.h

## Purpose
`wlcore_i.h` contains internal wlcore definitions used across common driver modules: firmware state enums, platform data, link/vif/station private structures, power-save and queue constants, RX filter structures, iterator macros, and declarations for internal helpers. It is the shared private model behind `wlcore.h` and the TX path.

## Important APIs, Types, And Fields
- `enum wlcore_state`, `enum wl12xx_fw_type`, `struct wl1271_chip`, and `struct wl_fw_status` describe driver/FW status and counters read from firmware.
- `struct wl1271_if_operations` abstracts the bus child operations: read, write, reset, init, power, and block-size setup.
- `struct wlcore_platdev_data` carries bus ops, family data, clock configuration, and suspend-power policy from platform glue.
- `enum wl12xx_flags` and `enum wl12xx_vif_flags` define global and per-vif flag bits for power, TX pending/busy, IRQ, suspend, recovery, vif changes, association/AP state, RX streaming, channel switch, beacon state, and more.
- `struct wl1271_link` owns per-HLID TX queues for each AC, allocated/freed packet accounting, PN tracking, address, BA bitmap, last firmware rate, owning vif, and total freed packets.
- `struct wl1271_station` is mac80211 station private data with HLID, firmware-added state, in-connection state, and freed-packet PN tracking.
- `struct wl12xx_vif` is mac80211 vif private data. It stores role IDs, STA/AP-specific HLIDs and rate indexes, AP station maps and recorded keys, last TX HLID, per-AC TX queue counts, link map, SSID/channel/rate state, templates, default key, power/RSSI, encryption/IP data, BA/WMM/radar flags, RX streaming work/timer, channel switch/loss work, pending-auth ROC state, rate-control update state, total freed packet counter, and a persistent tail.

## Control Flow And Integration
`wl12xx_vif_to_data()` and `wl12xx_wlvif_to_vif()` convert between mac80211 objects and wlcore private structures. Iterator macros traverse all vifs or filter by STA/AP BSS type. TX enqueue/dequeue uses `wl1271_link.tx_queue[]`, `wl12xx_vif.tx_queue_count[]`, `wl12xx_vif.links_map`, `wl12xx_vif.last_tx_hlid`, and global flags such as `WL1271_FLAG_FW_TX_BUSY` and `WL1271_FLAG_DUMMY_PACKET_PENDING`. Firmware status conversion populates `struct wl_fw_status`, which then drives TX block release, link PS maps, rate feedback, RX counters, and event handling elsewhere.

## State And Persistence Behavior
This header defines state containers but does not allocate them. Per-station and per-vif counters such as `total_freed_pkts` are intentionally retained across recovery/reconfiguration to preserve encryption PN continuity. The `persistent[0]` tail marks the boundary for vif data that must survive reconfig flows.

## Dependencies
The file includes kernel synchronization/list/bit operations and mac80211, plus wlcore `conf.h` and `ini.h`. It relies on constants from cfg80211/mac80211 and kernel networking headers through included dependencies.

## Risks And Test Signals
Risks include incorrect assumptions about max roles/links/rate policies, stale flags after recovery, mismatch between `links_map` and actual link ownership, per-link queue leaks, PN tracking regressions across recovery, and persistent-tail misuse when adding fields. Tests should exercise STA/AP/P2P roles, multi-vif queueing, station add/remove, AP power-save transitions, recovery with encrypted traffic, RX filter allocation/free/flatten helpers, and platform bus operation failure paths.
