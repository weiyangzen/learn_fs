# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.c

## Purpose
`cfr.c` implements Channel Frequency Response capture support when firmware and hardware advertise CFR. It configures a direct-buffer ring, exposes debugfs controls, sends per-peer WMI capture commands, correlates DMA buffer release events with WMI TX capture events, and relays binary CFR records to userspace through relayfs.

## Important APIs, Types, And Functions
Main external functions are `ath11k_cfr_init()`, `ath11k_cfr_deinit()`, `ath11k_cfr_get_dbring()`, `ath11k_cfr_lut_update_paddr()`, `ath11k_process_cfr_capture_event()`, `ath11k_cfr_send_peer_cfr_capture_cmd()`, unassociated-peer pool helpers, and `ath11k_cfr_update_phymode()`. Internal helpers calculate tones from DMA headers, fill metadata headers, correlate events in `ath11k_cfr_correlate_and_relay()`, process DBR data in `ath11k_cfr_process_data()`, and manage debugfs/relayfs files.

## Control Flow
Initialization checks `WMI_TLV_SERVICE_CFR_CAPTURE_SUPPORT` and `hw_params.cfr_support`, then for each radio obtains DBR capabilities, initializes IDR and locks, allocates a LUT capped by `CFR_MAX_LUT_ENTRIES`, sets up the direct-buffer SRNG, fills buffers, sends WMI ring configuration, and creates `enable_cfr`, `cfr_unassoc`, and `cfr_capture` debugfs/relayfs files. Data flow has two asynchronous halves: DBR release processing stores DMA data, PPDU ID, metadata, buffer pointer, and timestamp in the LUT; WMI TX capture event processing looks up the same LUT entry by buffer address and fills peer/radio metadata. When both halves arrive and PPDU IDs match, the header, data, and end magic are written to relayfs and the buffer is replenished. Mismatches clear TX state and count DMA aborts.

## State And Persistence
`struct ath11k_cfr` stores runtime locks, LUT, relay/debugfs dentries, peer count, event counters, last success timestamp, phymode, and unassociated peer pool. Peer CFR settings are cached in `ath11k_sta::cfr_capture` and are not persistent. Relayfs output is transient; userspace must consume it live.

## Dependencies And Integration Points
CFR depends on WMI capture service, DBR infrastructure, debugfs, relayfs, mac80211 peer state, firmware TX status fields, and `ath11k_dbring_buffer_release_event()`. The feature is compiled out through `CONFIG_ATH11K_CFR` stubs in the header.

## Risks And Test Signals
Race and lifetime risks center on LUT locking, held buffers, peer count accounting, and deinit while events are in flight. Buffer data length is inferred from DMA header tone and chain fields; malformed firmware data can reject the capture. Useful tests include enabling/disabling CFR via debugfs, per-peer and unassociated peer commands, CFR capture under peer powersave/failure statuses, DBR-before-TX and TX-before-DBR ordering, PPDU mismatch/abort counters, relayfs output validation, and deinit/reinit during traffic.
