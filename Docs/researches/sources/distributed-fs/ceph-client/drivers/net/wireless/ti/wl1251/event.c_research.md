# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.c

Purpose: Handles wl1251 firmware event mailboxes, translates event bits into mac80211 notifications and power-save actions, and ACKs processed event buffers.

Important APIs, types, and functions: Public APIs are `wl1251_event_wait()`, `wl1251_event_unmask()`, `wl1251_event_mbox_config()`, and `wl1251_event_handle()`. Internal handlers process scan completion, power-save reports, BSS loss/regain, synchronization timeout, and RSSI threshold events.

Control flow: Boot configures mailbox pointers and unmask bits. On event interrupt, `wl1251_event_handle()` validates mailbox number, reads the selected `event_mailbox`, calls `wl1251_event_process()`, frees the buffer, and triggers `INTR_TRIG_EVENT_ACK`. Processing masks off firmware-disabled events, completes scans, retries or abandons PS entry, forces active mode on BSS loss, reports beacon loss to mac80211, restores requested PS on BSS regain, and sends CQM RSSI notifications.

State and persistence: Updates `wl->scanning`, `wl->station_mode` via PS commands, `wl->psm_entry_retry`, mailbox pointer array, and uses `wl->event_mask`. No persistent storage.

Dependencies and integration points: Depends on ACX event mask configuration, register/memory IO, PS mode helper, mac80211 scan/beacon/CQM notification APIs, and event bit definitions from `event.h`.

Risks: Event processing is bitmask-based and ignores many defined events. PS entry retry can issue nested PS commands from event context. `wl1251_event_wait()` polls both mailbox event fields and may race with normal interrupt-driven processing if used incorrectly.

Test signals: Scan completion clears `wl->scanning`; BSS loss triggers `ieee80211_beacon_loss`; low/regained RSSI triggers CQM notifications; PS entry fail retries exactly three times; invalid mailbox returns `-EINVAL`.
