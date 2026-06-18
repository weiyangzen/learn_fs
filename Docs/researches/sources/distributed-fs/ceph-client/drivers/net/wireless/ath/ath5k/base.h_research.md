# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.h

## Purpose
`base.h` is the public local header for the mac80211-facing ath5k base layer. It declares lightweight structures used by `base.c` and other ath5k files, plus lifecycle, beacon, channel, buffer, TX queue, and chip-name entry points.

## Important APIs and types
- `enum ath5k_srev_type` and `struct ath5k_srev_name`: classify and name MAC/radio silicon revisions.
- `struct ath5k_buf`: software wrapper for one DMA descriptor, descriptor bus address, optional SKB, SKB DMA address, and up to four rate stages.
- `struct ath5k_vif`: per-vif driver private state, association state, opmode, beacon slot, and beacon buffer.
- `struct ath5k_vif_iter_data`: aggregation state used while iterating active mac80211 interfaces to compute BSSID masks, active MAC, opmode, and association presence.
- Prototypes for start/stop, beacon update/config/filtering, BSSID/opmode updates, channel set, buffer free helpers, TX enqueue, chip name, attach, and detach.
- Hardware feature macros `ath5k_hw_hasbssidmask` and `ath5k_hw_hasveol`.

## Control flow and integration
mac80211 callbacks and bus probe/remove paths use the functions declared here. `ath5k_init_ah` and `ath5k_deinit_ah` are the high-level attach/detach API used after bus code has allocated `ieee80211_hw` and mapped device resources. `ath5k_start` and `ath5k_stop` are hardware lifecycle callbacks. Beacon functions are used by interface configuration and software beacon alerts. `ath5k_tx_queue` is the local bridge from mac80211 TX to a selected ath5k hardware queue.

## State and persistence behavior
The structures declared here describe runtime-only state. `ath5k_buf` entries persist for the lifetime of the device allocation and are recycled between free lists and active queues. `ath5k_vif` persists for the lifetime of a mac80211 virtual interface. No persistent storage is created; hardware capabilities and EEPROM-derived settings are stored in the larger `ath5k_hw` defined in `ath5k.h`.

## Dependencies
This header forward-declares kernel/mac80211 and ath5k structures to avoid heavy includes. It depends conceptually on Linux list/DMA/SKB/mac80211 types through included users, and it is paired with `base.c`, `ath5k.h`, and the bus-specific probe files.

## Risks and edge cases
- `ath5k_buf` couples software list ownership, DMA mapping, descriptor ownership, and SKB lifetime. Callers must use the correct free helper for TX vs RX mappings.
- `ath5k_vif_iter_data` fields are filled across atomic interface iteration, so users must initialize every field before iteration.
- The `ath5k_hw_hasbssidmask` and `ath5k_hw_hasveol` macros use `ah` instead of their `_ah` parameter, which can compile only in scopes where `ah` exists and can surprise future callers.
- Queue mapping assumes the order chosen in `base.c` matches mac80211 queue numbering.

## Test signals
Compile coverage catches prototype drift. Runtime signals include correct interface add/remove behavior, accurate BSSID masks for multiple vifs, beacon slot assignment, safe buffer recycling, and no DMA unmap warnings during stop/reset/deinit.
