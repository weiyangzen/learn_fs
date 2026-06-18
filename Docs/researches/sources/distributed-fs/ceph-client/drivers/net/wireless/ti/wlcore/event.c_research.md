# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.c

## Purpose
`event.c` translates firmware mailbox events into driver state changes and mac80211/cfg80211 notifications. It handles firmware logger data, RSSI threshold notifications, SoftGemini state, scheduled-scan completion, block-ack constraints, channel switch completion, dummy-packet requests, AP station disconnect hints, remain-on-channel completion, beacon loss, event mask programming, and mailbox processing.

## Important APIs and functions
`wl1271_event_handle()` reads an event mailbox into `wl->mbox`, calls the chip-specific `process_mailbox_events()` callback, then ACKs the event through `wl->ops->ack_event()`. `wl1271_event_unmask()` programs the inverse event mask with `wl1271_acx_event_mbox_mask()`.

Exported handlers include `wlcore_event_fw_logger()`, `wlcore_event_rssi_trigger()`, `wlcore_event_soft_gemini_sense()`, `wlcore_event_sched_scan_completed()`, `wlcore_event_ba_rx_constraint()`, `wlcore_event_channel_switch()`, `wlcore_event_dummy_packet()`, `wlcore_event_max_tx_failure()`, `wlcore_event_inactive_sta()`, `wlcore_event_roc_complete()`, and `wlcore_event_beacon_loss()`.

## Control flow
The interrupt path chooses mailbox 0 or 1, reads the descriptor, lets chip-specific code decode event bits, and ACKs the mailbox. Individual decoded events walk active wlcore vifs/links, update flags, and call mac80211 APIs such as `ieee80211_cqm_rssi_notify()`, `ieee80211_sched_scan_stopped()`, `ieee80211_stop_rx_ba_session()`, `ieee80211_chswitch_done()`, `ieee80211_csa_finish()`, `ieee80211_report_low_ack()`, `ieee80211_ready_on_channel()`, `ieee80211_connection_loss()`, and `ieee80211_cqm_beacon_loss_notify()`.

## State and persistence behavior
The handlers update `wl->flags`, `wlvif->last_rssi_event`, `wlvif->ba_allowed`, channel-switch flags, `wl->sched_vif`, and deferred connection-loss work. Firmware logger handling copies ring-buffer data to the driver logger path and writes the updated read pointer back to device memory. Event mask state lives in `wl->event_mask`.

## Dependencies and integration points
This file depends on mailbox addresses initialized elsewhere, IO wrappers, ACX event-mask commands, PS/RX streaming recalculation, scan state, TX dummy packet support, mac80211 station/vif APIs, and chip-specific mailbox decoding. It is tightly coupled to `event.h` event IDs and wait-event names used by command paths.

## Risks
Mailbox ACK ordering is critical; missed ACKs can stall event delivery. Firmware logger pointer validation protects against out-of-bounds reads, but constants are wl18xx-specific. Event handlers assume locks and runtime context are provided by callers. Beacon-loss delayed work and channel-switch completion can race with interface teardown, so role IDs and flags are checked defensively.

## Test signals
Signals include event interrupt handling on both mailboxes, firmware logger output with ring wraparound, RSSI CQM notifications, scheduled-scan completion, BA session stop on constraints, CSA completion for STA/AP roles, dummy packet TX, low-ack station reports, ROC ready notification, beacon loss reporting, and successful command waits for role stop, peer removal, and DFS config completion.
