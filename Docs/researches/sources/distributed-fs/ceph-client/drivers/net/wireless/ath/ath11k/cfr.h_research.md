# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.h

## Purpose
`cfr.h` defines the CFR feature contract: metadata formats, DMA header bitfields, correlation state, per-radio CFR state, public APIs, and no-op stubs when `CONFIG_ATH11K_CFR` is disabled.

## Important APIs, Types, And Functions
Important constants include `ATH11K_CFR_NUM_RESP_PER_EVENT`, `ATH11K_CFR_EVENT_TIMEOUT_MS`, `ATH11K_CFR_NUM_RING_ENTRIES`, `ATH11K_MAX_CFR_ENABLED_CLIENTS`, `CFR_MAX_LUT_ENTRIES`, magic values, vendor/platform identifiers, tone counts, and `CFIR_DMA_HDR_*` bitfields. Types include `ath11k_cfr_peer_tx_param`, packed `cfr_metadata`, packed `ath11k_csi_cfr_header`, `ath11k_cfr_dma_hdr`, `ath11k_look_up_table`, `cfr_unassoc_pool_entry`, and `ath11k_cfr`. APIs cover init/deinit, DBR lookup/update, peer count/pool updates, WMI command send, event processing, LUT release, and phymode update.

## Control Flow
The header enables `core.c` to initialize/deinitialize CFR, `dbring.c` to find the CFR DBR ring and update LUT physical addresses, WMI event handlers to pass TX capture parameters into CFR correlation, and MAC peer code to configure or clear per-peer CFR state. When CFR is disabled at build time, inline stubs make callers compile without runtime feature checks.

## State And Persistence
The declared state is runtime-only. `ath11k_cfr` contains the DBR ring, locks, LUT, debugfs/relayfs handles, counters, phymode, and unassociated pool. `ath11k_look_up_table` is the correlation record binding a DMA buffer address, DBR data, TX event data, timestamps, and relay header.

## Dependencies And Integration Points
The header includes `dbring.h` and `wmi.h`, and references `ath11k`, `ath11k_sta`, and `ath11k_per_peer_cfr_capture` from the core/MAC object model. Packed binary output structs are consumed by userspace relayfs readers, so their layout is an external ABI-like surface.

## Risks And Test Signals
Layout changes in packed metadata can break CFR consumers. Counter and pool fields require consistent locking in implementation. The disabled-feature stubs return success for some APIs, so call sites must not assume active CFR merely from a zero return. Test signals include compile coverage with and without `CONFIG_ATH11K_CFR`, struct size/layout checks for userspace tooling, and event correlation tests using all supported bandwidth/preamble combinations.
