# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/event.h

Purpose: Defines wl12xx firmware event bit IDs, mailbox layout, and event-processing prototypes.

Important APIs and types: Event bit enum includes scan, role stop, radar/channel switch, BSS loss/regain, max TX retry, dummy packet, Soft Gemini, inactive station, peer remove, periodic scan, BA constraint, and remain-on-channel. `struct wl12xx_event_mailbox` defines the firmware mailbox fields. Prototypes expose wait and processing functions.

Control flow: No executable control flow. The bit definitions drive event masks and mailbox processing.

State and persistence: Describes volatile firmware mailbox state. Fields carry scan status, RSSI metrics, HLID bitmaps, channel switch status, role IDs, and event status bytes.

Dependencies and integration points: Included by `event.c` and `main.c`; event masks in `wl12xx_boot()` use these constants.

Risks: Packed mailbox layout is firmware ABI. Bit positions overlap a 32-bit event vector and must remain correct. Any mismatch will route wrong events to wlcore.

Test signals: Correct handling of each event class, especially scheduled scan, channel switch, peer removal, and AP station aging/retry events.
