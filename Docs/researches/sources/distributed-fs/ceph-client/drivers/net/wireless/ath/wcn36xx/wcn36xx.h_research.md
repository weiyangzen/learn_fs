# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/wcn36xx.h

## Purpose
`wcn36xx.h` is the central private header for the WCN36xx mac80211 driver. It defines debug masks/macros, RF identifiers, channel helper macros, byte-order conversion helper, and the main per-driver, per-VIF, and per-STA private structures shared by SMD, DXE, TX/RX, PMC, debugfs, and mac80211 glue.

## Important APIs, Types, and Functions
- Debug macros (`wcn36xx_err`, `wcn36xx_warn`, `wcn36xx_info`, `wcn36xx_dbg`, `wcn36xx_dbg_dump`) gate logging by `wcn36xx_dbg_mask`.
- `enum wcn36xx_ampdu_state` tracks per-TID aggregation lifecycle.
- Channel macros derive hardware channel, band, frequency, listen interval, flags, and power from `wcn->hw->conf`.
- `buff_to_be()` converts an array of 32-bit words in place to big-endian representation used by firmware descriptors.
- `struct wcn36xx_vif` stores BSS type, encryption, firmware BSS/self station indices, power state, IPv6/GTK WoWLAN data, and per-VIF STA list.
- `struct wcn36xx_sta` stores association ID, TID, firmware STA/DPU indices, encryption state, rates, and AMPDU state.
- `struct wcn36xx` stores mac80211 device pointers, firmware/NV data, rpmsg endpoint, SMEM state bits, HAL synchronization, scan state, DXE channels, memory pools, TX ACK state, A-MSDU queue, RF ID, survey data, and optional debugfs state.
- Inline container helpers map between mac80211 objects and private structures.

## Control Flow
The header provides helpers rather than active workflows. Its structures are the shared state that `smd.c` mutates during firmware control operations, `txrx.c` consumes during frame processing, and higher mac80211 callbacks use to bind Linux wireless objects to firmware indices.

## State and Persistence Behavior
Most driver persistence is declared here: firmware version/capability state, NV firmware pointer, rpmsg/SMEM transport handles, locks/completions/workqueues, scan status, DXE rings and pools, TX ACK timer/skb, A-MSDU queue, RF module identity, and channel survey cache. VIF and STA structures persist for the lifetime of their mac80211 objects.

## Dependencies and Integration Points
It pulls in mac80211, Linux completion/spinlock/IPv6 definitions, and local headers `hal.h`, `smd.h`, `txrx.h`, `dxe.h`, `pmc.h`, and `debug.h`. This creates the central include hub for the WCN36xx driver.

## Risks and Test Signals
Risks include circular include fragility, shared-state locking errors, stale firmware indices after failed teardown, and helper misuse when mac80211 object lifetimes change. Test signals are build coverage across IPv6/debugfs options, interface add/remove, suspend/resume, scan cancellation, aggregation, and debug logging without use-after-free reports.
