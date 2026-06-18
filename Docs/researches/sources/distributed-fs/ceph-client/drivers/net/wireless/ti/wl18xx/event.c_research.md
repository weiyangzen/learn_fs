# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.c

## Purpose
Processes WiLink 8 firmware mailbox events and maps them to common wlcore/mac80211/cfg80211 behavior. Also implements wait-for-event mapping for a small set of wlcore wait events.

## Important APIs, types, and functions
- `wl18xx_wait_for_event()` maps wlcore wait events to local firmware event bits and calls `wlcore_cmd_wait_for_event_or_timeout()`.
- `wl18xx_process_mailbox_events()` decodes `wl18xx_event_mailbox.events_vector` and dispatches scan, DFS, RSSI, BA, beacon-loss, channel-switch, ROC, Smart Config, firmware logger, and RX BA window-size events.
- `wlcore_smart_config_sync_event()` and `wlcore_smart_config_decode_event()` emit cfg80211 vendor events.
- `wlcore_event_time_sync()` logs firmware TSF time-sync values.

## Control flow
On each mailbox interrupt, the common core points `wl->mbox` at a `struct wl18xx_event_mailbox`; this file reads the little-endian event vector and checks each bit. Some events call common wlcore handlers directly, scan-complete calls `wl18xx_scan_completed()` on `wl->scan_wlvif`, and radar events call `ieee80211_radar_detected()` unless debug mode is active. RX BA window change finds the affected station and stops RX BA sessions after updating `max_rx_aggregation_subframes`.

## State and persistence behavior
The event path mutates transient driver/mac80211 state: scan completion work, RSSI trigger events, BA constraints, channel switch completion, link aggregation window size, and radar state in mac80211. No persistent storage is written.

## Dependencies and integration points
Depends on cfg80211 vendor events, mac80211 radar/BA APIs, common wlcore event handlers, wl18xx scan/event structures, wlcore vendor command attribute ids, and `wl->links[]` link metadata. Wired into `wl18xx_ops.process_mailbox_events` and `wait_for_event`.

## Risks and test signals
Risks include missing event bits in masks, wrong endian conversion on bitmaps, NULL link/vif assumptions for RX BA window changes, vendor event allocation failures, and radar debug suppressing real DFS notifications. Test scan completion, periodic scan reports/completion, DFS radar detection, beacon loss, max TX failure in AP mode, ROC completion, Smart Config sync/decode vendor events, firmware logger indication, and RX BA window change with active station.
