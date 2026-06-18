# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.c

Purpose: Translates wl12xx firmware mailbox events into wlcore/mac80211 actions and implements waiting for selected firmware events.

Important APIs and functions: `wl12xx_wait_for_event()` maps generic wlcore wait events to wl12xx event bits, and `wl12xx_process_mailbox_events()` consumes a `wl12xx_event_mailbox`.

Control flow: `wl12xx_wait_for_event()` supports role stop and peer remove completion by calling `wlcore_cmd_wait_for_event_or_timeout()`. Mailbox processing masks event bits by `events_mask`, logs the vector, completes scans, reports scheduled scan results/completion, handles soft Gemini sense, beacon loss, RSSI trigger, BA RX constraint, channel switch, dummy packet, max TX retry, inactive station, and remain-on-channel completion through wlcore event helpers.

State and persistence: Reads volatile mailbox data from `wl->mbox`. It may clear scan state indirectly through scan completion helpers and update cfg80211/mac80211 state through wlcore events.

Dependencies and integration points: Registered as `process_mailbox_events` and `wait_for_event` in `wl12xx_ops`. Depends on `scan.h`, `event.h`, wlcore command/debug/event helpers, and mac80211/cfg80211 upper layers through wlcore.

Risks: Unsupported wait events return success (`0`) without waiting, which is intentional for unimplemented events but can hide missing mappings if new wlcore waits are added. Event role IDs sometimes pass `0xff` rather than mailbox role fields, so multi-role handling depends on wlcore semantics.

Test signals: Scan completion, scheduled scan reports, beacon loss CQM, RSSI triggers, channel switch completion, ROC completion, inactive station cleanup, and AP max retry handling.
