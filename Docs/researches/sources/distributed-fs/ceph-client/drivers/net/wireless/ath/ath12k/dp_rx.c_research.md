# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_rx.c

## Purpose

`dp_rx.c` implements ath12k receive datapath setup and RX helper logic. It allocates and replenishes RXDMA buffers, sets up REO destination and monitor rings, manages RX reorder queues for AMPDU/TID state, configures PN replay offload, reconstructs 802.11 frames from hardware decap formats, delivers RX skbs to mac80211, handles fragmented RX frame state, and initializes/frees RX datapath resources.

## Important APIs, Types, and Functions

Buffer/ring lifecycle APIs include `ath12k_dp_rx_bufs_replenish()`, `ath12k_dp_rx_alloc()`, `ath12k_dp_rx_free()`, `ath12k_dp_rx_pdev_alloc()`, `ath12k_dp_rx_pdev_free()`, `ath12k_dp_rx_pdev_reo_setup()`, `ath12k_dp_rx_pdev_reo_cleanup()`, `ath12k_dp_rx_htt_setup()`, and `ath12k_dp_rx_pdev_mon_attach()`.

REO/TID APIs include `ath12k_dp_init_rx_tid_rxq()`, `ath12k_dp_rx_reo_cmd_list_cleanup()`, `ath12k_dp_reo_cmd_free()`, `ath12k_dp_rx_process_reo_cmd_update_rx_queue_list()`, `ath12k_dp_rx_tid_del_func()`, `ath12k_dp_mark_tid_as_inactive()`, `ath12k_dp_rx_peer_tid_setup()`, `ath12k_dp_rx_peer_tid_cleanup()`, `ath12k_dp_rx_ampdu_start()`, `ath12k_dp_rx_ampdu_stop()`, and `ath12k_dp_rx_peer_pn_replay_config()`.

Packet conversion/delivery APIs include `ath12k_dp_rx_get_msdu_last_buf()`, `ath12k_dp_rx_crypto_mic_len()`, `ath12k_dp_rx_h_undecap()`, `ath12k_dp_rx_h_find_link_peer()`, `ath12k_dp_rx_h_ppdu()`, `ath12k_dp_rx_deliver_msdu()`, `ath12k_dp_rx_check_nwifi_hdr_len_valid()`, `ath12k_dp_rx_peer_frag_setup()`, `ath12k_dp_rx_h_undecap_frag()`, `ath12k_dp_rx_h_sort_frags()`, and `ath12k_dp_rx_h_get_pn()`.

Important local helpers include descriptor free-list slicing, RXDMA monitor/status ring buffer setup/free, crypto header/ICV/MIC length mapping, native Wi-Fi/raw/Ethernet undecap helpers, PPDU rate conversion, and fragment timeout cleanup.

## Control Flow

RX allocation starts by initializing monitor IDRs, setting up refill, optional MAC buffer, error destination, monitor buffer/status rings, and then replenishing RXDMA buffers. `ath12k_dp_rx_htt_setup()` advertises relevant ring IDs to firmware through HTT setup messages and calls the hardware `rxdma_ring_sel_config()` op. Per-pdev monitor allocation sets up RXDMA monitor destination rings on `rxdma1_enable` hardware and configures those rings through HTT.

RX buffer replenish locks the HAL source ring, syncs hardware tail state, optionally cuts descriptor nodes from `dp->rx_desc_free_list`, allocates aligned skbs, maps them for `DMA_FROM_DEVICE`, attaches the descriptor cookie, writes buffer address info through HAL ops, and returns unused descriptors to the free list on exit.

AMPDU start flows through mac80211 params to `ath12k_dp_rx_peer_tid_setup()`. That finds the link peer, checks primary-link and REO LUT prerequisites, updates an already-active TID if present, or allocates/assigns a new REO queue buffer. It marks the TID active, preallocates an update element used during delete, and either writes the REO queue LUT or sends a WMI reorder queue setup command. AMPDU stop sends an arch REO update that disables the queue and later delete callbacks free or cache-flush the queue descriptor.

RX undecap converts hardware decap formats back to mac80211-compatible skb data. Native Wi-Fi rebuilds QoS and crypto headers around the stripped header. Raw decap trims FCS and crypto trailers based on RX flags. Ethernet2 DIX normally keeps 802.3 fast-path format but reconstructs 802.11 for EAPOL or decrypted multicast/broadcast so mac80211 can do authorization/PN handling.

Delivery expects RCU protection for peer-ID lookup, fills `IEEE80211_SKB_RXCB`, sets MLO link status from `dp_peer->hw_links`, marks 802.3 fast path when safe, and calls `ieee80211_rx_napi()`.

Fragment setup initializes per-TID fragment queues and timers for the primary link. Fragment timeout cleans incomplete fragments under `dp_lock`; fragment undecap trims crypto headers/trailers; sorting inserts fragments by 802.11 fragment number.

## State and Persistence Behavior

Persistent state includes RX descriptor free/used lists, RXDMA and monitor SRNGs, monitor IDRs, `ath12k_dp_rx_tid` reorder queue DMA buffers, REO command/update/cache-flush lists, per-peer `rx_tid_active_bitmask`, fragment queues/timers, `dp_peer->dp_setup_done`, and hardware/firmware ring configuration.

DMA state is explicit: RX skbs are mapped before posting and must be unmapped by completion/free paths. REO queue buffers are DMA-mapped bidirectionally and cleaned by `ath12k_dp_rx_tid_cleanup()` after delete/cache flush. Locks include `srng->lock`, `rx_desc_lock`, `dp_lock`, `reo_rxq_flush_lock`, and `reo_cmd_lock`.

## Dependencies and Integration Points

This file depends on HAL SRNG and descriptor ops, architecture-specific datapath hooks such as `ath12k_dp_arch_rx_assign_reoq()`, `ath12k_dp_arch_peer_rx_tid_reo_update()`, `ath12k_dp_arch_reo_cmd_send()`, `ath12k_dp_arch_rx_frags_cleanup()`, and `ath12k_dp_arch_peer_rx_tid_qref_setup()`, WMI reorder queue setup, HTT SRNG setup via TX datapath, peer lookup from `dp_peer.c`, mac80211 RX/AMPDU APIs, Linux DMA/SKB/timer APIs, and FIPS policy for fragment support.

## Risks and Edge Cases

- `ath12k_dp_rx_peer_pn_replay_config()` appears immediately before an `EXPORT_SYMBOL(ath12k_dp_rx_get_msdu_last_buf)` line; the symbol export is for the following function, but its placement is unusual and worth verifying during cleanup.
- RX buffer replenish returns partial counts and recycles unused descriptors; callers must not assume full ring refill.
- Several REO cleanup flows rely on preallocated update elements to avoid leaks during delete. Failure in `ath12k_dp_prepare_reo_update_elem()` correctly frees the new queue buffer, but this path needs fault-injection coverage.
- Primary-link-only hardware parameters skip reorder/fragment setup for non-primary links; MLO correctness depends on peer `primary_link` initialization.
- `ath12k_dp_rx_h_undecap_raw()` warns and returns unless the skb is both first and last MSDU. Raw fragmented/A-MSDU paths must be handled elsewhere or rejected before this helper.
- Header reconstruction uses skb push/pull and crypto length tables; unsupported encryption types warn and return zero lengths, which may mask malformed frame handling.
- Fragment support is disabled under FIPS by returning `-ENOENT`; callers must treat that as an expected policy failure.

## Test Signals

Useful validation includes RX throughput and leak tests, ring setup/teardown across hardware variants with/without `rxdma1_enable`, AMPDU start/stop/restart on all TIDs, PN replay offload key add/remove, EAPOL and multicast decrypted RX paths, MLO link RX delivery, fragment timeout and reorder tests, FIPS-enabled behavior, DMA mapping fault injection, and lockdep/KASAN around peer deletion during RX.
