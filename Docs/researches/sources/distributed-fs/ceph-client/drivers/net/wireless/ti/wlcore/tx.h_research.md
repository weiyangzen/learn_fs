# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/tx.h

## Purpose
`tx.h` defines the wlcore transmit firmware ABI, TX result ABI, queue-stop reason enum, queue mapping helpers, and exported prototypes used by common wlcore code and chip-family drivers. It is the contract between the common TX implementation, firmware descriptors, and mac80211 queue management.

## Important APIs, Types, And Constants
- `TX_HW_ATTR_*` and `TX_HW_ATTR_OFST_*` define descriptor bitfields for retries, header padding, session counter, rate policy, last-word padding, completion request, dummy packet, host encryption, and EAPOL marking.
- `struct wl1271_tx_hw_descr` is the packed descriptor prepended to every firmware TX packet. It carries length, chip-family memory accounting union, host/device timing, lifetime, attributes, descriptor ID, TID, HLID, and wl18xx checksum metadata.
- `struct wl1271_tx_hw_res_descr` and `struct wl1271_tx_hw_res_if` define the 16-entry TX result ring read by `wlcore_tx_complete()`.
- `enum wl1271_tx_hw_res_status` enumerates firmware completion results such as success, retry exceeded, timeout, missing key, invalid peer, session mismatch, and invalid link.
- `enum wlcore_queue_stop_reason` provides independent queue-stop bits for watermark pressure, firmware restart, flush, and wl18xx spare-block limits.
- Inline helpers `wl1271_tx_get_queue()`, `wlcore_tx_get_mac80211_queue()`, and `wl1271_tx_total_queue_count()` translate mac80211 queue indexes to wlcore ACs and summarize pending work.

## Control Flow And Integration
The header is included by `tx.c`, `main.c`, and chip-family code. mac80211 queue mappings 0..3 are converted to wlcore AC constants in priority order VO, VI, BE, BK. Per-vif hardware queue bases are used to address mac80211 queues for stop/wake operations. The descriptor and result structs are filled/read only after chip ops have calculated block counts and chip-specific memory fields.

## State And Persistence Behavior
The header itself holds no storage, but its structs define persistent in-memory state exchanged with firmware in DMA/bus-visible buffers. Because descriptors are packed and use little-endian fields, layout drift would be an ABI break. Queue-stop reasons are stored in `wl->queue_stop_reasons[]`, one bitmap per mac80211 hardware queue.

## Dependencies
The file depends on wlcore configuration constants such as `CONF_TX_AC_*`, `NUM_TX_QUEUES`, `WLCORE_NUM_MAC_ADDRESSES`, and `struct wl1271`/`struct wl12xx_vif` declarations from wlcore headers. It also relies on Linux bit macros and endian types.

## Risks And Test Signals
Primary risks are packed-struct layout mismatch with firmware, incorrect AC mapping, off-by-one handling of the 16-entry result ring mask, and stop-reason bits being added without updating queue-state logic. Tests should validate TX descriptor sizes, successful TX completion parsing, mac80211 queue stop/wake behavior per vif, and all chip-family implementations of memory-block descriptor fields.
