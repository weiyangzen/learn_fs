# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/event.h

Purpose: Defines the wl1251 firmware event mailbox ABI, event bit IDs, mailbox layout, power-save status values, and event API prototypes.

Important APIs, types, and functions: Event ID bits cover scan complete, calibration, low/regained RSSI/SNR, PS report, sync timeout, health/debug/MAC status, join/channel switch, BSS lose/regain, BT PTA, and PLT calibration. `struct event_mailbox` contains event vectors/masks plus RSSI, PS status, health, debug, FCS, and SNR fields. `wl1251_event_unmask`, `wl1251_event_mbox_config`, `wl1251_event_handle`, and `wl1251_event_wait` are exported.

Control flow: Firmware alternates between two fixed event buffers; host reads one, processes bits, and ACKs to free it.

State and persistence: Defines transient mailbox contents and status codes. No host persistence.

Dependencies and integration points: Depends on `wl1251.h`, event handling in `event.c`, boot-time event mask setup, and mac80211 notification paths.

Risks: Packed mailbox layout must match firmware exactly. Event masks are inverted by ACX configuration (`~wl->event_mask`), so misunderstanding mask semantics can suppress needed events.

Test signals: Validate mailbox pointer spacing, event ACK behavior, mask/unmask semantics, and PS status handling for all defined status values.
