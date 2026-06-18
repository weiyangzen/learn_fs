# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/event.h

## Purpose
Defines WiLink 8 mailbox event bits, radar type ids, the packed event mailbox ABI, and event function prototypes.

## Important APIs, types, and functions
- Event bit macros cover scan completion, DFS/radar, channel switch, BSS loss, TX failure, inactive STA, periodic scan, BA constraints, ROC, DFS config, Smart Config, RSSI/SNR, firmware logging, time sync, and RX BA window-size change.
- `enum wl18xx_radar_types` differentiates regular, chirp, and no-radar types.
- `struct wl18xx_event_mailbox` carries vector, counters, bitmaps, TSF parts, Smart Config payloads, channel/band fields, and radar data.
- Prototypes expose `wl18xx_wait_for_event()` and `wl18xx_process_mailbox_events()`.

## Control flow
No executable flow. `event.c` interprets this mailbox layout after firmware writes it.

## State and persistence behavior
The mailbox is volatile firmware-to-host state. It is read during event handling and not persisted.

## Dependencies and integration points
Includes wlcore core definitions. The mailbox size is passed to `wlcore_alloc_hw()` in wl18xx probe, and event masks are set during boot in `wl18xx/main.c`.

## Risks and test signals
ABI drift in the mailbox layout or event bit values can misroute events. Test signals are correct handling of each event type, especially little-endian bitmaps and Smart Config variable-length arrays.
