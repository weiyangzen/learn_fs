# sources/distributed-fs/ceph-client/net/mac802154/scan.c

Purpose: implements IEEE 802.15.4 scanning, beacon transmission, association, association response handling, and disassociation management.

Important APIs and functions: `mac802154_trigger_scan_locked()`, `mac802154_abort_scan_locked()`, and `mac802154_scan_worker()` manage active/passive scans. `mac802154_process_beacon()` reports scan events. `mac802154_send_beacons_locked()`/`mac802154_stop_beacons_locked()` and `mac802154_beacon_worker()` handle coordinator beaconing. Association functions include `mac802154_perform_association()`, `mac802154_process_association_resp()`, `mac802154_process_association_req()`, `mac802154_send_disassociation_notif()`, and `mac802154_process_disassociation_notif()`.

Control flow and state: scans store an RCU `scan_req`, set `IEEE802154_IS_SCANNING`, hold/sync the TX queue, switch channels with receiver stopped, optionally transmit beacon requests, wait per-channel duration, then cleanup restores channel, filtering, driver state, and queue. Beaconing stores an RCU `beacon_req`, builds a beacon template, sends once or periodically depending on interval. Association blocks on `assoc_done`, uses `local->assoc_dev/status/addr`, and mutates `wpan_dev->parent`/children under `association_lock`.

Dependencies and integration: driven by cfg802154 ops, RX beacon/MAC-command workers in `rx.c`, MLME TX helpers in `tx.c`, driver channel/start/stop hooks, nl802154 notifications, and cfg802154 address allocation/relationship helpers.

Risks and test signals: scan cleanup interleaves delayed work cancellation, RCU pointer replacement, driver restart, and queue release; abort/completion races are important. Association code contains a likely bug pattern: after an unsuccessful association response, it sets `ret = 0` unconditionally before returning, which can mask PAN-at-capacity/access-denied errors. Tests should cover scan abort during channel switch, active scan beacon request failures, beacon request response behavior, association timeout/negative status, retransmitted association requests, and disassociation of parent vs child.
