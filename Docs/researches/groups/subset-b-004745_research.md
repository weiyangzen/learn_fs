# Research: subset-b-004745

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_mon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_mon.c

## Purpose

`dp_mon.c` implements ath12k monitor-mode receive support and monitor-derived peer statistics. It allocates and replenishes monitor RXDMA/status buffers, parses monitor destination/status descriptors into skb chains, reconstructs monitor MPDUs for mac80211 delivery, adds radiotap HE/EHT metadata, and updates per-peer SU/MU RX counters from `hal_rx_mon_ppdu_info`.

This file is datapath-facing but not transport-specific. It depends on HAL descriptor callbacks and SRNG helpers for buffer rings, on `dp_rx.c` helpers for undecap/descriptor extraction, on peer lookup for station/link attribution, and on mac80211 for final monitor delivery.

## Important APIs, Types, and Functions

Exported monitor buffer APIs include `ath12k_dp_rx_alloc_mon_status_buf()`, `ath12k_dp_mon_buf_replenish()`, and `ath12k_dp_mon_status_bufs_replenish()`. They allocate aligned skbs, map them for DMA, store them in monitor ring IDRs, encode buffer IDs into RXDMA cookies, and write physical addresses into HAL source-ring descriptors.

Packet assembly and delivery are handled by `ath12k_dp_mon_parse_status_buf()`, `ath12k_dp_mon_rx_merg_msdus()`, `ath12k_dp_pkt_set_pktlen()`, `ath12k_dp_mon_update_radiotap()`, and `ath12k_dp_mon_rx_deliver_msdu()`. These functions remove consumed monitor buffers from IDR state, unmap DMA, chain MSDUs into `dp_mon_mpdu`, merge raw or native Wi-Fi decaps, fill `ieee80211_rx_status`, optionally push radiotap HE/EHT TLVs, map link IDs for MLO stations, and call `ieee80211_rx_napi()`.

Statistics helpers include `ath12k_dp_mon_rx_update_peer_su_stats()`, `ath12k_dp_mon_rx_process_ulofdma()`, `ath12k_dp_mon_rx_update_peer_mu_stats()`, and the local `ath12k_dp_mon_rx_update_user_stats()`. They update `ath12k_rx_peer_stats`, rate tables, RSS EWMA, RU allocation, AMPDU/non-AMPDU counts, MPDU FCS counts, TID counters, NSS/BW/GI/MCS histograms, and per-peer RX duration.

## Control Flow

Monitor buffer setup starts with a caller providing a `dp_rxdma_mon_ring`. The replenish path locks the backing HAL SRNG, calls `ath12k_hal_srng_access_begin()`, allocates and aligns skbs, maps them with `DMA_FROM_DEVICE`, assigns IDR buffer IDs under `idr_lock`, fetches a source-ring entry, stores the physical address and cookie, then ends SRNG access and unlocks. Failure paths remove IDR entries, unmap DMA, and free the skb before returning either `-ENOMEM` or the number of buffers actually posted.

Status parsing starts from a `dp_mon_packet_info` cookie. `ath12k_dp_mon_parse_status_buf()` decodes the buffer ID, removes the skb from the monitor buffer IDR, unmaps the original DMA mapping, adjusts packet length to `dma_length + ATH12K_MON_RX_DOT11_OFFSET`, chains the skb onto `pmon->mon_mpdu`, and replenishes one replacement buffer. Invalid cookies are warned and otherwise ignored.

MPDU merge and delivery split by decap format. Raw decap pulls descriptor/L3 padding from each skb, builds a fragment list under the head skb, and returns the head. Native Wi-Fi decap obtains the original payload header through HAL ops, handles QoS header restoration, appends FCS length to the tail, and returns the merged chain. Delivery extracts RX descriptor data, finds a link peer by peer ID or address under RCU plus `dp_lock`, propagates link information into `ieee80211_rx_status`, optionally marks 802.3 fast-path eligibility, and hands the skb to mac80211.

Radiotap flow is layered on top of RX status. `ath12k_dp_mon_update_radiotap()` derives signal from RSSI and noise floor unless firmware already reports dBm, sets AMPDU details, pushes EHT/EHT-USIG TLVs for 802.11be, HE-MU or HE radiotap structures for 802.11ax, and falls back to HT/VHT/legacy rate metadata.

## State and Persistence Behavior

Persistent state is primarily in datapath runtime objects: monitor ring `bufs_idr` tables, skb DMA addresses in `ATH12K_SKB_RXCB`, `ath12k_mon_data` MPDU chains/status queues, and per-link peer stats. The file also updates `ieee80211_rx_status` in skb control blocks immediately before mac80211 ownership transfer.

Locking is ring-specific and peer-specific. Monitor buffer IDRs use `idr_lock`; HAL ring pointer mutations require `srng->lock`; peer lookup during delivery uses RCU and `dp->dp_lock`. Peer stats are updated through peer pointers found from the datapath peer table and assume the caller is sequencing monitor status processing consistently with peer lifetime.

## Dependencies and Integration Points

Direct dependencies include `dp_mon.h` for monitor types, `dp_rx.h` for descriptor extraction and undecap support, `dp_tx.h` for datapath linkage, `peer.h`/`dp_peer.c` for link peer lookup and stats storage, HAL SRNG and descriptor ops, mac80211 RX/radiotap APIs, DMA mapping APIs, IDR allocation, and ath12k debug/logging.

The code integrates with `dp_rx.c` allocation/setup paths that initialize monitor rings and `ath12k_dp_rx_pdev_mon_attach()`, with hardware params such as `rxdma1_enable`, with WMI service feature bits for dBm conversion, and with extended debugfs RX stats through `peer->peer_stats.rx_stats`.

## Risks and Edge Cases

- `ath12k_dp_mon_rx_merg_msdus()` calls `ath12k_dp_mon_rx_msdus_set_payload(ab, head_msdu, tail_msdu)` inside the loop even while processing later `msdu` entries; this may be intentional due to shared head/tail state, but it is a fragile-looking area for chained skb length bugs.
- Monitor buffer IDR limits differ between allocation paths (`bufs_max` versus `bufs_max * 3`), so ring sizing changes should verify cookie space and cleanup coverage.
- `ath12k_dp_mon_status_bufs_replenish()` returns partial success on allocation/mapping/ring exhaustion rather than a hard error; callers must tolerate underfilled monitor rings.
- Radiotap EHT/HE data is pushed onto the skb head; malformed or undersized headroom would surface as skb manipulation failure or corruption, so monitor RX tests should cover EHT TLV paths.
- Peer stat update paths mutate `ppdu_info` fields for legacy/HT normalization. Callers must not rely on those fields remaining raw after stats updates.
- Multicast decrypted 802.3 monitor delivery deliberately avoids the fast path because PN validation stays in mac80211.

## Test Signals

Useful signals include monitor-mode captures across legacy/HT/VHT/HE/EHT frames, HE-MU and EHT-USIG radiotap validation with packet analyzers, RXDMA buffer leak checks across monitor start/stop, fault injection for skb allocation and DMA mapping failures, peer stats deltas under SU/MU/OFDMA traffic, MLO link ID validation in monitor delivery, and lockdep/KASAN coverage while peers are deleted during monitor traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_mon.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_mon.h

## Purpose

`dp_mon.h` declares ath12k monitor datapath interfaces and compact monitor-only data structures. It is the contract between generic RX setup/processing code, monitor status parsing, monitor MPDU reconstruction, radiotap generation, and peer statistic updates.

## Important APIs, Types, and Functions

Key constants include `ATH12K_MON_RX_DOT11_OFFSET`, `ATH12K_MON_RX_PKT_OFFSET`, and the `ATH12K_LE32_DEC_ENC`/`ATH12K_LE64_DEC_ENC` field-copy helpers used by monitor TLV handling.

Monitor mode and TX monitor parsing enumerations include `dp_monitor_mode`, `dp_mon_tx_ppdu_info_type`, `dp_mon_tx_tlv_status`, and `dp_mon_tx_medium_protection_type`.

Monitor frame and packet structures include `dp_mon_qosframe_addr4`, `dp_mon_frame_min_one`, `dp_mon_packet_info`, and `dp_mon_tx_ppdu_info`. `dp_mon_packet_info` carries cookie, DMA length, continuation, and truncation state for monitor buffer parsing. `dp_mon_tx_ppdu_info` stores PPDU ID, user count, an embedded `hal_rx_mon_ppdu_info`, and TX monitor MPDU list state.

Declared functions cover buffer replenishment, monitor status buffer allocation/parsing, PPDU ID comparison across wrap, radiotap update, monitor MSDU delivery, MPDU merge, UL OFDMA post-processing, and SU/MU peer stat updates.

## Control Flow and Integration

RX setup code uses `ath12k_dp_mon_buf_replenish()` and `ath12k_dp_mon_status_bufs_replenish()` when creating monitor rings. Monitor destination/status processing calls `ath12k_dp_mon_parse_status_buf()` to convert ring cookies into skb chains, then merge/deliver helpers to construct packets for mac80211. Peer statistics code calls the SU/MU update helpers after HAL monitor TLVs have populated `hal_rx_mon_ppdu_info`.

The header includes `core.h`, so declarations have access to `ath12k_base`, `ath12k_pdev_dp`, `dp_rxdma_mon_ring`, `ath12k_mon_data`, and mac80211-visible types indirectly.

## State and Persistence Behavior

The header owns no storage, but the declared functions mutate monitor ring IDRs, skb DMA metadata, monitor MPDU lists, peer statistics, and mac80211 RX status blocks. Callers should treat the APIs as stateful datapath operations with DMA and peer lifetime implications.

## Dependencies and Integration Points

This header depends on HAL monitor PPDU structures and core datapath structures. It is consumed by `dp_mon.c`, `dp_rx.c`, and other datapath files that need monitor buffer lifecycle and monitor delivery helpers.

## Risks and Contract Notes

- The declarations expose raw pointers to monitor ring and skb state; callers must hold the appropriate SRNG/IDR/peer locks required by implementation paths.
- `ath12k_dp_pkt_set_pktlen()` can reallocate skb head storage under `GFP_ATOMIC`; callers must handle `-ENOMEM`.
- `ath12k_dp_mon_comp_ppduid()` maintains caller-provided PPDU state and encodes wraparound behavior; incorrect state sharing can reorder monitor processing.
- The header declares TX monitor enums and structures even though this source subset primarily implements RX monitor helpers, so future TX monitor users should verify all states are consumed.

## Test Signals

Header-level validation is compile coverage with monitor support enabled, prototype consistency with `dp_mon.c`, and integration tests that include both `rxdma1_enable` and non-`rxdma1_enable` hardware parameter paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_mon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_peer.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_peer.c

## Purpose

`dp_peer.c` owns ath12k datapath peer bookkeeping. It manages firmware link-peer map/unmap events, host-created `ath12k_dp_peer` objects, MLO/non-MLO peer ID indexing, link-peer assignment to host peers, address rhashtable maintenance, RCU lookup tables used by RX/TX completion paths, and per-link rate/stat reset helpers.

## Important APIs, Types, and Functions

Link-peer lookup APIs include `ath12k_dp_link_peer_find_by_vdev_and_addr()`, `ath12k_dp_link_peer_find_by_pdev_and_addr()`, `ath12k_dp_link_peer_find_by_addr()`, `ath12k_dp_link_peer_exist_by_vdev_id()`, `ath12k_dp_link_peer_find_by_ast()`, and `ath12k_dp_link_peer_find_by_peerid()`. Most require `dp->dp_lock`; peer-ID lookups require RCU read-side protection.

Map/unmap event handlers are `ath12k_dp_link_peer_map_event()` and `ath12k_dp_link_peer_unmap_event()`. They create or free `ath12k_dp_link_peer`, initialize RSSI EWMA, optionally allocate extended RX stats, link into `dp->peers`, and wake `peer_mapping_wq`.

Rhashtable lifecycle and mutation are handled by `ath12k_dp_link_peer_rhash_tbl_init()`, `ath12k_dp_link_peer_rhash_tbl_destroy()`, `ath12k_dp_link_peer_rhash_add()`, and `ath12k_dp_link_peer_rhash_delete()`.

Host peer lifecycle and indexing use `ath12k_dp_peer_create()`, `ath12k_dp_peer_delete()`, `ath12k_dp_peer_find_by_addr()`, `ath12k_dp_peer_find_by_addr_and_sta()`, `ath12k_dp_peer_get_peerid_index()`, and `ath12k_dp_peer_find_by_peerid()`. MLO peer IDs are used directly; link peer IDs are combined with `dp->device_id << 10` to avoid conflicts between hardware-wide ML peers and device-local link peers.

Assignment helpers `ath12k_dp_link_peer_assign()` and `ath12k_dp_link_peer_unassign()` bind firmware link peers to host peers, update `dp_peer->hw_links[]`, publish `link_peers[]` and `dp_hw->dp_peers[]` through RCU, and update address rhashtable entries for split-PHY/roaming cases.

## Control Flow

Firmware map events first search `dp->peers` by vdev/address. Missing peers are allocated atomically, populated with vdev ID, peer ID, AST hash, hardware peer ID, MAC address, optional debugfs stats, and then added to the datapath peer list. Unmap events search by peer ID or ML ID, remove the peer from the list, free stats storage, and wake waiters.

Host peer creation is separate from firmware link-peer creation. `ath12k_dp_peer_create()` rejects duplicates under `dp_hw->peer_lock`, allocates `ath12k_dp_peer`, initializes security state as open, records station/MLO attributes, inserts into `dp_peers_list`, and immediately publishes MLO peers into the RCU peer table because their peer ID is host-assigned. Non-MLO host peers are published later when the firmware link peer is assigned.

`ath12k_dp_link_peer_assign()` takes `dp->dp_lock` then `dp_hw->peer_lock`, finds the firmware link peer and host peer, copies non-MLO peer ID into the host peer, records the hardware link ID and link ID mapping, publishes pointers with `rcu_assign_pointer()`, and refreshes the address rhashtable. Unassignment clears those pointers and calls `synchronize_rcu()` after dropping locks.

## State and Persistence Behavior

Persistent datapath peer state is stored in `dp->peers`, `dp->rhead_peer_addr`, `dp_hw->dp_peers_list`, `dp_hw->dp_peers[]`, `ath12k_dp_peer::link_peers[]`, `hw_links[]`, security fields, per-TID RX state, reorder queue buffers, peer stats, and RSSI EWMA.

Concurrency relies on three mechanisms: `dp->dp_lock` for link-peer list/rhashtable access, `dp_hw->peer_lock` for host peer list/table updates, and RCU for lockless peer-ID lookups from hot RX paths. Destructive changes call `synchronize_rcu()` after unpublishing pointers.

## Dependencies and Integration Points

The file integrates with `dp_rx.c` for RX peer/TID lookup and cleanup, `mac.c` station/link structures through `ath12k_dp_link_peer_to_link_sta()`, debugfs extended RX stats allocation, firmware HTT peer map/unmap events, and MLO station/link mappings. It includes `dp_peer.h`, `debug.h`, and `debugfs.h`.

## Risks and Edge Cases

- Lock ordering in assignment is `dp_lock` then `peer_lock`; future callers must avoid reverse ordering.
- `dp_peer->hw_links[peer->hw_link_id] = 0` on unassign uses zero as the cleared value, which is also a valid link index. Correctness depends on the corresponding RCU pointer being cleared and caller checks.
- Rhashtable updates in split-PHY roaming remove an old peer entry before adding the new one and best-effort restore on failure. A double failure can leave no address-table entry while list/RCU state still exists.
- `ath12k_dp_peer_find_by_peerid()` rejects `peer_id == 0`; this is correct only if firmware never uses zero for valid peers.
- `ath12k_dp_link_peer_unmap_event()` frees the link peer under `dp_lock`; RCU-published link-peer pointers must already have been unassigned or otherwise protected by teardown ordering.
- Extended RX stats are allocated only if debugfs setting is enabled at map time.

## Test Signals

Useful validation includes peer map/unmap stress under association churn, MLO station bring-up/teardown, split-PHY roaming with duplicate MAC addresses, lockdep coverage for assignment/unassignment, RCU/KASAN tests during RX while peers are deleted, debugfs RX stats allocation/reset, and tests that peer-ID lookup indexes do not collide across device IDs and ML peer IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_peer.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_peer.h

## Purpose

`dp_peer.h` defines datapath peer state and peer lookup/lifecycle contracts for ath12k. It bridges RX/TX datapath code, monitor statistics, mac80211 station objects, firmware peer map events, and MLO link-peer mapping.

## Important APIs, Types, and Functions

`ATH12K_DP_PEER_ID_INVALID` and `ATH12K_PEER_ML_ID_VALID` define peer ID sentinel and ML peer ID tagging.

`struct ppdu_user_delayba`, `ath12k_rx_peer_rate_stats`, `ath12k_rx_peer_stats`, `ath12k_wbm_tx_stats`, and `ath12k_dp_peer_stats` hold per-peer PPDU, RX, rate, and WBM TX completion statistics.

`struct ath12k_dp_link_peer` represents a firmware/device link peer. It stores vdev ID, MAC, peer IDs, AST hash, pdev/hw link IDs, MLO fields, primary-link flag, station pointer, rhashtable node, TID activity bitmask, rate/RSSI/duration fields, and optional per-peer stats.

`struct ath12k_dp_peer` represents the host peer across one or more links. It stores MLO status, security/key state, host station pointer, hardware link-to-link ID map, RCU link-peer pointers, per-TID reorder state, and REO queue buffers.

The header declares link-peer map/unmap event handlers, lookup helpers by vdev/address/AST/pdev/peer ID, rhashtable lifecycle, host peer create/delete, peer ID indexing, link-peer conversion to `ath12k_link_sta`, and link-peer free.

## Control Flow and Integration

Firmware map events create `ath12k_dp_link_peer` objects; mac80211/peer setup creates `ath12k_dp_peer` objects; assignment binds the two and publishes RCU lookups. RX hot paths use peer ID or address helpers to find peer state. Aggregation and fragmentation setup use the per-peer `rx_tid[]` and `reoq_bufs[]` arrays declared here.

## State and Persistence Behavior

The structures declared here persist for peer lifetime and are mutated by firmware events, station lifecycle code, RX reorder setup, key configuration, monitor statistics, and TX completion statistics. The `link_peers[]` table is RCU-protected; the list/rhashtable fields are protected by datapath locks in implementation.

## Dependencies and Integration Points

This header includes `dp_rx.h`, so it depends on RX TID and REO buffer definitions. It also references mac80211 station/key/rate types, HAL encryption and RX stat constants, WMI key index limits, and ath12k MLO constants.

## Risks and Contract Notes

- Hot-path lookup helpers have lock requirements not visible from type signatures; callers must follow implementation lockdep warnings.
- The header exposes both host peer and link peer objects. Mixing them up can break MLO mapping, because host peer IDs and link peer IDs have different index semantics.
- Statistics pointers are optional; update code must tolerate `NULL`.
- `primary_link` controls whether RX reorder/fragment operations run for a peer, so MLO setup must initialize it consistently.

## Test Signals

Compile coverage under MLO and non-MLO configurations, station association/teardown tests, peer stats debugfs tests, RX aggregation start/stop, and static analysis for lookup calls outside required lock/RCU sections are useful header-level signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_peer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_rx.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_rx.h

## Purpose

`dp_rx.h` declares ath12k RX datapath data structures and helper APIs. It defines RX reorder queue state, REO command state, fragment state, decap types, small inline HAL descriptor wrappers, and externally used RX setup/delivery functions.

## Important APIs, Types, and Functions

Core data structures include `ath12k_reoq_buf`, `ath12k_dp_rx_tid`, `ath12k_dp_rx_tid_rxq`, `ath12k_dp_rx_reo_cache_flush_elem`, `dp_reo_update_rx_queue_elem`, and `ath12k_dp_rx_reo_cmd`. These represent DMA-backed REO queue buffers, per-TID reorder/fragment state, inactive-update elements, delayed cache-flush elements, and REO commands with completion handlers.

Constants include `DP_MAX_NWIFI_HDR_LEN`, `ATH12K_DP_RX_FRAGMENT_TIMEOUT_MS`, `ATH12K_DP_RX_REO_DESC_FREE_THRES`, and `ATH12K_DP_RX_REO_DESC_FREE_TIMEOUT_MS`.

Inline helpers translate HE GI values, inspect 802.11 fragment fields after HAL descriptor offset, fetch L3 padding, copy descriptor end TLVs, set/get RX descriptor fields through `hal->ops`, clean skb lists, and extract descriptor data.

Declared APIs cover undecap/delivery, native Wi-Fi header validation, PN extraction and fragment sorting, AMPDU start/stop, PN replay configuration, TID setup/cleanup/delete, REO setup/cleanup, RX allocation/free, RX buffer replenish, monitor attach, peer fragment setup, PPDU status filling, crypto MIC length, and REO command callbacks.

## Control Flow and Integration

RX processing code includes this header to operate on per-peer TID state and to call HAL descriptor ops without knowing hardware-specific descriptor layouts. `dp_peer.h` includes this file because `ath12k_dp_peer` embeds `ath12k_dp_rx_tid` and `ath12k_reoq_buf`.

Typical runtime flow is: allocate RX rings, replenish buffers, parse completion descriptors into `hal_rx_desc_data`, undecap if required, fill PPDU/rate status, deliver to mac80211, and manage TID reorder state through AMPDU callbacks and REO command completions.

## State and Persistence Behavior

The structures declared here persist in peer objects and datapath command lists. They hold DMA addresses, fragment queues, timers, active flags, and command handlers. The inline helpers are thin wrappers over mutable HAL descriptor state and skb contents.

## Dependencies and Integration Points

The header includes `core.h` and `debug.h` and depends on HAL descriptor abstractions, Linux skb/timer/mac80211 types, REO command statuses, encryption types, and ath12k datapath/core structures.

## Risks and Contract Notes

- Several inline helpers assume `skb->data + hal_desc_sz` points to a valid 802.11 header; callers must only use them after descriptor/body layout validation.
- `ath12k_dp_clean_up_skb_list()` consumes the entire skb queue without locking; caller owns queue serialization.
- REO command handler callbacks carry `void *ctx`, so type discipline is by convention.
- Declarations expose many setup and teardown entry points that require `dp_lock` or wiphy lock in implementation; callers must follow surrounding mac80211/datapath sequencing.

## Test Signals

Compile coverage for all RX users, static checking of inline descriptor access, AMPDU/fragment tests for all TIDs, and build coverage across hardware descriptor ops variants are the main header-level signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.c

## Purpose

`dp_tx.c` provides shared ath12k TX datapath helpers for encapsulation selection, native Wi-Fi header adjustment, TID selection, encryption type mapping, TX descriptor allocation/release, metadata tail allocation, payload alignment, and TX skb cleanup after failed or completed descriptor ownership.

## Important APIs, Types, and Functions

`ath12k_dp_tx_get_encap_type()` maps device raw mode and mac80211 `IEEE80211_TX_CTL_HW_80211_ENCAP` into HAL TCL encapsulation types.

`ath12k_dp_tx_encap_nwifi()` strips QoS control from QoS data frames when converting to native Wi-Fi encapsulation and clears the QoS subtype bit.

`ath12k_dp_tx_get_tid()` derives the TCL/REO TID from skb priority, returning `HAL_DESC_REO_NON_QOS_TID` for non-QoS 802.11 frames.

`ath12k_dp_tx_get_encrypt_type()` maps Linux cipher suite constants to HAL encryption types.

`ath12k_dp_tx_assign_buffer()` and `ath12k_dp_tx_release_txbuf()` move `ath12k_tx_desc_info` objects between per-pool free and used lists under `tx_desc_lock`.

`ath12k_dp_metadata_align_skb()` makes skb data writable and appends zeroed metadata at the tail. `ath12k_dp_tx_align_payload()` shifts or reallocates skb payload so the data pointer satisfies `dp->hw_params->iova_mask`.

`ath12k_dp_tx_free_txbuf()` unmaps TX DMA, frees optional extension descriptors, frees the mac80211 TX skb, decrements `num_tx_pending`, and wakes `tx_empty_waitq` when the pdev drains.

## Control Flow

TX submission code calls the small helpers while constructing TCL descriptors: choose encap, possibly rewrite native Wi-Fi header, choose TID, allocate a descriptor, align payload or append metadata if hardware requires it, and map/send elsewhere. On rollback or completion, `ath12k_dp_tx_free_txbuf()` reverses DMA ownership and skb ownership and descriptor release is handled separately by `ath12k_dp_tx_release_txbuf()`.

## State and Persistence Behavior

Persistent state touched here includes per-pool TX descriptor free/used lists, `tx_desc->skb_ext_desc`, skb DMA addresses in `ATH12K_SKB_CB`, optional extension descriptor DMA addresses, and `dp_pdev->num_tx_pending`. The list operations are protected by per-pool spinlocks; TX skb free uses RCU to map MAC ID to pdev datapath.

## Dependencies and Integration Points

The file depends on mac80211 TX metadata, skb helpers, HAL TCL and encryption enums, ath12k hardware params, peer/mac headers for shared datapath context, and `ieee80211_free_txskb()` for final skb release. Other TX implementation files are expected to use these helpers while programming TCL rings.

## Risks and Edge Cases

- `ath12k_dp_tx_align_payload()` may replace `*pskb` with a reallocated skb and free the original. Callers must use the updated pointer after success.
- Payload movement uses memmove with skb push/pull/trim; off-by-one errors would corrupt TX frames, so hardware IOVA alignment changes need direct packet tests.
- Descriptor allocation warns and returns `NULL` on exhaustion; callers need backpressure/drop handling.
- `ath12k_dp_tx_free_txbuf()` assumes `desc_params->skb_ext_desc` is valid when `paddr_ext_desc` is set.
- Encryption mapping defaults unknown ciphers to open, which is safe only if unsupported ciphers are filtered earlier.

## Test Signals

Useful tests include raw/native/Ethernet encapsulation selection, QoS/non-QoS TID mapping, cipher mapping coverage, TX descriptor exhaustion, IOVA alignment with tight headroom/tailroom and realloc paths, DMA mapping fault cleanup, and TX drain waitqueue behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.h

## Purpose

`dp_tx.h` declares shared ath12k TX datapath helper APIs and a compact HTT WBM TX status structure. It is the interface used by TX descriptor-building code and cleanup code for encapsulation, TID selection, metadata alignment, descriptor pools, and TX buffer freeing.

## Important APIs, Types, and Functions

`struct ath12k_dp_htt_wbm_tx_status` carries completion acknowledgement state and ACK RSSI.

Declared APIs include `ath12k_dp_tx_put_bank_profile()`, `ath12k_dp_tx_get_encap_type()`, `ath12k_dp_tx_encap_nwifi()`, `ath12k_dp_tx_get_tid()`, `ath12k_dp_metadata_align_skb()`, `ath12k_dp_tx_align_payload()`, `ath12k_dp_tx_release_txbuf()`, `ath12k_dp_tx_assign_buffer()`, and `ath12k_dp_tx_free_txbuf()`.

## Control Flow and Integration

TX code uses these helpers around TCL descriptor construction: determine encapsulation, edit native Wi-Fi frames, select TID, allocate descriptor state, append metadata, align payload for device IOVA requirements, and free/unmap buffers on completion or failure.

## State and Persistence Behavior

The header has no storage, but its functions mutate skb contents/control blocks, TX descriptor lists, DMA mappings, and pdev pending counters.

## Dependencies and Integration Points

It includes `core.h` and depends on HAL TCL encap types, ath12k datapath rings, TX descriptor structures, and Linux skb/mac80211 APIs.

## Risks and Contract Notes

- Callers must treat `ath12k_dp_tx_align_payload()` as possibly replacing the skb pointer.
- Descriptor pool functions require a valid pool ID and initialized list/lock state.
- Header does not declare `ath12k_dp_tx_get_encrypt_type()` even though `dp_tx.c` exports it, so consumers may rely on another declaration; prototype drift should be checked.

## Test Signals

Compile checks for all TX users, symbol/prototype consistency, and TX-path tests covering encapsulation, descriptor exhaustion, and cleanup paths are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.c

## Purpose

`fw.c` parses ath12k API 2 firmware container files. It validates the firmware magic, walks typed information elements, records firmware feature bits, and maps embedded AMSS, M3, auxiliary microcode, and dual-MAC AMSS image spans into `ab->fw`. It also exposes firmware map/unmap and feature query helpers.

## Important APIs, Types, and Functions

The local `ath12k_fw_request_firmware_api_n()` requests `firmware-2.bin`, validates `ATH12K_FIRMWARE_MAGIC`, iterates `struct ath12k_fw_ie` records, and handles IE IDs for timestamp, features, AMSS image, M3 image, auxiliary microcode image, and dual-MAC AMSS image.

`ath12k_fw_map()` tries API 2 firmware and sets `ab->fw.api_version` to 2 on success or 1 on failure. `ath12k_fw_unmap()` releases the firmware and zeroes the firmware state. `ath12k_fw_feature_supported()` checks `fw_features_valid` and a bit in `ab->fw.fw_features`.

## Control Flow

Firmware map requests the API 2 file through `ath12k_core_firmware_request()`. On success, parsing starts with a magic string including its trailing NUL, aligns past padding, and loops over IE headers while enough bytes remain. Each IE length is bounds-checked before use, payloads are interpreted by ID, then the payload length is aligned to four bytes before advancing.

On parse errors, the requested firmware is released and `ab->fw.fw` is cleared. Unknown IE IDs are warned but skipped, so forward-compatible metadata does not fail loading.

## State and Persistence Behavior

State persists in `ab->fw`: the `struct firmware *`, API version, feature bitmap validity, image data pointers, and image lengths. Image pointers reference memory owned by the firmware blob and remain valid until `ath12k_fw_unmap()` releases it. Unmap clears the whole firmware state to prevent stale pointers.

## Dependencies and Integration Points

This file depends on core firmware request/release support, `fw.h` constants and enums, `hw.h` image naming conventions indirectly, debug logging, and later boot/QMI/MHI paths that consume `ab->fw.amss_data`, `m3_data`, `aux_uc_data`, or feature bits such as MLO and multi-QRTR support.

## Risks and Edge Cases

- API 2 parse failure silently falls back to API version 1 in `ath12k_fw_map()` without requesting legacy files here; legacy consumers must handle that path elsewhere.
- If aligned IE length exceeds remaining length, the loop breaks and returns success rather than failing. This tolerates trailing truncation/padding but can hide malformed final IEs.
- Feature bitmap parsing stops when `index == ie_len`; using `>=` would be more defensive if future edits alter loop bounds.
- Image data pointers are borrowed from the firmware blob; no consumer may outlive `ath12k_fw_unmap()`.

## Test Signals

Test with valid API 2 blobs, missing firmware, invalid magic, too-small files, truncated IE payloads, unknown IEs, feature bitmaps of varying length, and boot paths that require MLO or auxiliary microcode features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.h

## Purpose

`fw.h` defines ath12k firmware container constants, firmware IE IDs, firmware feature bits, and the public firmware map/unmap/feature-query API.

## Important APIs, Types, and Functions

Constants include `ATH12K_FW_API2_FILE` (`firmware-2.bin`) and `ATH12K_FIRMWARE_MAGIC`.

`enum ath12k_fw_ie_type` identifies timestamp, features, AMSS image, M3 image, dual-MAC AMSS image, and auxiliary microcode image records.

`enum ath12k_fw_features` currently exposes `ATH12K_FW_FEATURE_MULTI_QRTR_ID`, `ATH12K_FW_FEATURE_MLO`, and a count sentinel.

Declared functions are `ath12k_fw_map()`, `ath12k_fw_unmap()`, and `ath12k_fw_feature_supported()`.

## Control Flow and Integration

Boot code calls `ath12k_fw_map()` before image download and feature-dependent setup. Consumers check features through `ath12k_fw_feature_supported()`. Teardown calls `ath12k_fw_unmap()` after all users of borrowed firmware image pointers are done.

## State and Persistence Behavior

The header defines no storage, but its API fills and clears `ab->fw`, including borrowed pointers into the firmware blob and feature bitmap validity.

## Dependencies and Integration Points

The header depends on `struct ath12k_base` from core declarations and is consumed by firmware boot, QMI/transport setup, and feature gating code.

## Risks and Contract Notes

- Feature enum ordering is ABI-like for firmware bitmaps; new features must be appended before `ATH12K_FW_FEATURE_COUNT`.
- API 2 image IDs are container-specific and should stay synchronized with firmware tooling.
- Feature checks are false until `fw_features_valid` is set by a successfully parsed features IE.

## Test Signals

Compile checks, firmware parser unit/fault tests, and boot tests that assert feature gates for MLO and multi-QRTR are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.c

## Purpose

`hal.c` implements generic ath12k hardware abstraction helpers around SRNG rings, CE descriptors, REO/WBM setup hooks, buffer address encoding, shadow register configuration, and TLV header encode/decode. Hardware-specific behavior is delegated through `ab->hal.ops`; this file provides common state management and ring pointer mechanics.

## Important APIs, Types, and Functions

Thin ops wrappers cover CE descriptor size/setup, DSCP/TID maps, TCL bank configuration, REO queue LUT programming, REO hardware setup, idle link list setup, RX buffer address set/get, RX MSDU list extraction, REO entry buffer address extraction, current-channel config, and idle link RBM selection.

SRNG APIs include `ath12k_hal_srng_get_entrysize()`, `ath12k_hal_srng_get_max_entries()`, `ath12k_hal_srng_get_params()`, `ath12k_hal_srng_get_hp_addr()`, `ath12k_hal_srng_get_tp_addr()`, peek/get/reap helpers for source and destination rings, `ath12k_hal_srng_src_num_free()`, `ath12k_hal_srng_dst_num_free()`, `ath12k_hal_srng_access_begin()`, `ath12k_hal_srng_access_end()`, `ath12k_hal_srng_setup()`, `ath12k_hal_srng_init()`, and `ath12k_hal_srng_deinit()`.

Debug/config helpers include `ath12k_hal_srng_shadow_config()`, `ath12k_hal_srng_get_shadow_config()`, `ath12k_hal_srng_shadow_update_hp_tp()`, `ath12k_hal_dump_srng_stats()`, and TLV helpers `ath12k_hal_encode_tlv64_hdr()`, `ath12k_hal_encode_tlv32_hdr()`, `ath12k_hal_decode_tlv64_hdr()`, and `ath12k_hal_decode_tlv32_hdr()`.

## Control Flow

HAL initialization calls the hardware op to create the SRNG config table, stores the device pointer, allocates coherent remote-data-pointer (`rdp`) and write-pointer (`wrp`) arrays, and registers lockdep classes for every SRNG. Deinit unregisters lock keys, frees coherent pointer memory, and frees the config table.

SRNG setup resolves a ring ID from type/ring/mac ID, fills `hal->srng_list[ring_id]`, clears ring memory, initializes source or destination software pointers, assigns pointer addresses in `rdp`/`wrp` memory, flags LMAC rings when pointer updates go through firmware-shared memory, initializes UMAC hardware rings through ops, and applies CE destination setup for CE DST rings.

Ring access is bracketed. `ath12k_hal_srng_access_begin()` syncs cached tail/head pointers from hardware/shared memory and uses `dma_rmb()` before reading new destination descriptors. Callers then use src/dst get/peek helpers, which mutate software HP/TP offsets modulo `ring_size`. `ath12k_hal_srng_access_end()` writes updated HP/TP either to shared memory for LMAC rings or through `ath12k_hif_write32()` for UMAC/MMIO rings, with memory barriers before publishing descriptor ownership.

Shadow config walks non-CE, non-DMAC/PMAC ring types and asks hardware ops to configure shadow registers. Stats dump prints CE interrupt ages, external IRQ group ages, and current/cached/last ring pointers for initialized rings.

## State and Persistence Behavior

Persistent HAL state lives in `struct ath12k_hal`: SRNG list entries, SRNG config table, coherent RDP/WRP memory, device pointer, hardware ops, register table, HAL params, shadow register config, descriptor sizes, and TCL-to-WBM maps. Each `hal_srng` tracks ring identity, physical/virtual base, entry sizes, interrupt settings, MSI data, pointer addresses, cached pointers, last pointers, timestamp, and spinlock.

Ring pointer updates are shared state with hardware/firmware. The memory barriers in access begin/end are part of the ownership protocol and must be preserved when optimizing.

## Dependencies and Integration Points

The file depends on `hif.h` for MMIO writes, hardware-specific `hal_ops`, Linux DMA coherent allocation, lockdep, jiffies, ath12k CE state, external IRQ groups, and all datapath users that post/reap SRNG descriptors (`dp_rx.c`, TX datapath, CE transport, HTT/REO command paths).

## Risks and Edge Cases

- Source ring helpers keep one entry empty to distinguish full from empty; callers must use `ath12k_hal_srng_src_num_free()` rather than raw entry counts.
- Many helpers assume `srng->lock` is held and rely on lockdep assertions. Missing locks can corrupt HP/TP state.
- Modulo arithmetic is used for all rings because some descriptor sizes make ring size non-power-of-two; attempts to optimize must preserve non-power-of-two correctness.
- `ath12k_hal_srng_setup()` indexes LMAC pointer arrays by subtracting `HAL_SRNG_RING_ID_DMAC_CMN_ID_START`; invalid hardware ring IDs would corrupt pointer setup.
- `ath12k_hal_srng_shadow_update_hp_tp()` only updates source rings when non-empty; callers relying on shadow state for empty rings need to understand that behavior.
- TLV encode helpers use `HAL_TLV_HDR_*` masks for both 32-bit and 64-bit paths in `hal.c`; definitions exist separately in the header, so mask consistency matters.

## Test Signals

Useful validation includes ring setup for every `hal_ring_type`, CE send/receive, RX/TX data traffic, monitor rings, shadow register configuration, ring full/empty wraparound tests with non-power-of-two sizes, DMA barrier stress on weakly ordered architectures, lockdep coverage, and SRNG stats dumps during simulated interrupt stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.h

## Purpose

`hal.h` defines ath12k hardware abstraction constants, descriptor/ring enums, RX monitor status structures, SRNG state, REO command structures, hardware register maps, HAL ops, and public HAL helper prototypes. It is the central contract between generic datapath code and hardware-specific ath12k implementations.

## Important APIs, Types, and Functions

The header defines ring IDs in `enum hal_srng_ring_id`, ring types in `enum hal_ring_type`, ring direction and MAC type enums, SRNG flags, interrupt mitigation thresholds, and `struct hal_srng_config`, `hal_srng_params`, and `hal_srng`.

RX/monitor metadata types include `hal_rx_user_status`, `hal_rx_u_sig_info`, `hal_rx_tlv_aggr_info`, `hal_rx_eht_info`, `hal_rx_msdu_desc_info`, `hal_mon_buf_ring`, `hal_rx_mon_ppdu_info`, and `hal_rx_desc_data`. These carry PPDU IDs, rates, MCS/NSS/BW/GI, EHT/HE radiotap data, user stats, RSSI, addresses, crypto/decap state, and descriptor-derived RX status fields.

Buffer and descriptor types include `ath12k_buffer_addr`, `hal_wbm_link_desc`, `hal_wbm_idle_scatter_list`, `ath12k_hal_reo_cmd`, `hal_reo_status_header`, and CE descriptor forward declarations.

Hardware-level state is represented by `ath12k_hw_hal_params`, `ath12k_hw_regs`, `ath12k_hal`, `ath12k_hal_tcl_to_wbm_rbm_map`, and `ath12k_hw_version_map`.

`struct hal_ops` declares hardware-specific callbacks for SRNG config/ring ID/setup, RX descriptor parsing, CE descriptors, TX bank/DSCP configuration, REO queue LUT and hardware setup, buffer address encoding, current channel config, idle link RBM, MSDU list extraction, and TLV encode/decode variants.

Public prototypes expose the SRNG, CE, REO, RX buffer, shadow config, stats dump, and TLV helpers implemented by `hal.c`.

## Control Flow and Integration

Hardware-specific files populate `ath12k_hw_version_map` with `hal_ops`, descriptor sizes, register maps, RBM maps, and HAL params. Core initialization copies those into `ab->hal`, then `hal.c` creates SRNG config and initializes common ring state. Datapath code uses the public helpers and inline structures to post RX/TX buffers, parse completions, configure REO queues, and decode monitor TLVs without embedding chip-specific descriptor layouts.

## State and Persistence Behavior

Most structures here describe long-lived hardware/shared-memory state: ring pointers, coherent pointer memory, register offsets, buffer cookies, REO queue settings, and monitor PPDU status. Many fields are shared with firmware/hardware through DMA or MMIO, so layout, alignment, endianness, and bit masks are persistent interface contracts.

## Dependencies and Integration Points

`hal.h` includes `hw.h`, creating a close coupling between hardware parameter definitions and HAL definitions. It also references mac80211 radiotap/rate types, Linux DMA addresses, lockdep keys, HAL RX descriptor forward declarations, and ath12k core structures.

## Risks and Contract Notes

- The header includes `hw.h` while `hw.h` includes `hal.h`; include guards prevent recursion, but this circular relationship makes forward declaration hygiene important.
- Ring ID ranges and derived constants such as `HAL_SRNG_RING_ID_MAX` must match hardware-specific ops and register maps exactly.
- `struct hal_rx_mon_ppdu_info` is large and accumulates many optional TLV-derived fields; parsers must carefully reset it between PPDUs.
- `ath12k_he_ru_tones_to_nl80211_he_ru_alloc()` maps unsupported/default cases to 26-tone RU, which can hide unexpected RU values.
- Public structures use packed hardware layouts and little-endian fields; accidental host-endian access would corrupt descriptors.
- Many ops are mandatory in practice despite being function pointers; hardware map initialization must provide a complete ops table.

## Test Signals

Build all hardware variants, run sparse/endian checks on descriptor fields, validate ring ID/config tables against hardware docs, exercise RX/TX/CE/monitor/REO paths, run radiotap HE/EHT capture validation, and use lockdep/KASAN with SRNG wraparound traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hif.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hif.h

## Purpose

`hif.h` defines the ath12k host interface abstraction. It is the bus/transport-facing operations table used by common core, HAL, HTC, CE, power management, MSI, panic, and coredump code without hard-coding PCI or AHB behavior.

## Important APIs, Types, and Functions

`struct ath12k_hif_ops` contains callbacks for 32-bit register read/write, IRQ enable/disable, device start/stop, power up/down, suspend/resume, HTC service-to-pipe mapping, MSI vector/address lookup, CE IRQ control, CE MSI index lookup, panic handling, and coredump download.

Inline wrappers include `ath12k_hif_map_service_to_pipe()`, `ath12k_hif_get_user_msi_vector()`, `ath12k_hif_get_msi_address()`, `ath12k_hif_get_ce_msi_idx()`, CE/global IRQ enable/disable, suspend/resume, start/stop, read/write32, power up/down, panic handler, and coredump download.

## Control Flow and Integration

Bus drivers install `ab->hif.ops`. Core and HTC call `map_service_to_pipe()` to bind WMI/HTT/control endpoints to CE pipes. HAL calls `ath12k_hif_write32()` when publishing UMAC ring pointers through MMIO. Interrupt setup uses MSI helpers and IRQ wrappers. Power management and crash paths call suspend/resume, power, panic, and coredump wrappers if provided.

## State and Persistence Behavior

The header owns no storage; it dispatches to persistent bus-specific state behind `ab->hif.ops`. Some optional methods have fallback behavior: unsupported MSI vector lookup returns `-EOPNOTSUPP`, missing MSI address and CE IRQ methods are no-ops, missing CE MSI index maps CE ID directly, missing suspend/resume returns success, missing power-up returns `-EOPNOTSUPP`, and missing panic handler returns `NOTIFY_DONE`.

## Dependencies and Integration Points

It includes `core.h` and is consumed by HAL, HTC, CE, core boot/shutdown, PCI/AHB bus implementations, PM, and crash-dump code.

## Risks and Contract Notes

- Required callbacks such as read/write32, IRQ enable/disable, start, stop, and service-to-pipe mapping are called without null checks.
- Optional callback fallbacks can hide unsupported platform behavior if callers do not check return values.
- `ath12k_hif_power_down()` silently no-ops when unsupported, while `power_up()` reports unsupported; caller expectations must match bus behavior.
- `get_ce_msi_idx()` defaulting to CE ID is only valid for transports whose MSI data layout matches CE numbering.

## Test Signals

Build/test every bus implementation, verify HTC service-to-pipe maps, MSI vector assignment, IRQ enable/disable sequencing, suspend/resume on platforms with and without callbacks, panic notifier return behavior, and HAL MMIO ring pointer writes through the transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.c

## Purpose

`htc.c` implements the ath12k Host Target Communications layer. It frames outbound skbs with HTC headers, manages target transmit credits, parses inbound HTC headers/trailers, receives control messages on endpoint 0, connects services to HTC endpoints and HIF/CE pipes, waits for target readiness, starts HTC setup completion, and initializes endpoint state.

## Important APIs, Types, and Functions

Allocation and send helpers include `ath12k_htc_alloc_skb()`, local `ath12k_htc_build_tx_ctrl_skb()`, `ath12k_htc_prepare_tx_skb()`, and `ath12k_htc_send()`. They reserve HTC header space, enforce 4-byte alignment, push headers, consume credits, map TX DMA, and send through `ath12k_ce_send()`.

Receive/control helpers include `ath12k_htc_process_credit_report()`, `ath12k_htc_process_trailer()`, `ath12k_htc_suspend_complete()`, `ath12k_htc_wakeup_from_suspend()`, and `ath12k_htc_rx_completion_handler()`. They parse trailer records, add endpoint credits, complete control waits, handle suspend/wakeup events, dispatch endpoint RX callbacks, and poll CE TX completions for interrupt-disabled pipes.

Service setup uses `ath12k_htc_wait_target()`, `ath12k_htc_connect_service()`, `ath12k_htc_start()`, and `ath12k_htc_init()`. It parses target READY credit counts/sizes, divides credits among WMI endpoints, connects endpoint 0 as a pseudo control service, sends CONNECT_SERVICE messages for real services, maps service IDs to UL/DL pipes through HIF, and sends SETUP_COMPLETE_EX.

## Control Flow

Initialization sets up `tx_lock`, resets every endpoint to unused with credit flow enabled, derives `wmi_ep_count` from preferred hardware mode, connects the pseudo endpoint-0 control service locally, and initializes `ctl_resp`.

Target wait blocks on `ctl_resp` for the READY message. If it times out, it manually services every CE engine once and waits again. READY parsing validates message ID, credit count, and credit size, then stores credit state and computes WMI service credit allocations.

Service connection either handles the reserved control service locally or builds a control skb, sets connect flags, disables credit flow for non-WMI-control services, sends on endpoint 0, waits for a response, validates message/service status, records assigned endpoint and max message size, copies callbacks, maps the service to HIF pipes, and initializes endpoint credits.

Normal TX pushes an HTC header, checks and deducts endpoint credits if flow control is enabled, fills endpoint ID/payload length/sequence/control flags, DMA maps the skb, and submits to CE. DMA or CE send failures unmap and restore credits before pulling the header back off.

RX completion pulls the HTC header, validates endpoint and payload length, parses optional trailers and credit reports, handles endpoint-0 control messages by copying into `control_resp_buffer` and completing waiters, or dispatches non-control skbs to endpoint callbacks and transfers skb ownership.

## State and Persistence Behavior

Persistent HTC state includes endpoint table entries, endpoint callbacks, service IDs, CE pipe IDs, sequence numbers, per-endpoint TX credits, flow-control flags, `control_resp_buffer`, `control_resp_len`, completion `ctl_resp`, total target credits, service allocation table, target credit size, and WMI endpoint count. `tx_lock` serializes endpoint credit and sequence updates.

TX skbs carry DMA addresses in `ATH12K_SKB_CB`. On successful CE send, ownership moves to CE completion; on RX dispatch, ownership moves to the endpoint callback.

## Dependencies and Integration Points

HTC depends on CE transport (`ath12k_ce_send()`, CE service/poll helpers), HIF service-to-pipe mapping, mac80211/Linux skb/DMA/completion APIs, ath12k boot/debug flags, WMI preferred hardware mode, and endpoint users such as WMI, HTT, NMI, pktlog, and test services.

## Risks and Edge Cases

- `ath12k_htc_send()` checks `eid >= ATH12K_HTC_EP_COUNT` after computing `ep = &htc->endpoint[eid]`; invalid `eid` values could index before validation if ever supplied by a caller.
- Credit report validation warns "too long" when `record->hdr.len < sizeof(report)`; the message text is inverted, though the error behavior is correct.
- `ath12k_htc_wait_target()` ignores the return value from `ath12k_htc_setup_target_buffer_assignments()`, so invalid `wmi_ep_count` could leave no credit allocation but still return success.
- Endpoint 0 duplicate control message handling completes the same completion and drops the skb; unsolicited firmware behavior is treated as fatal/warn but not an immediate crash.
- Only WMI control services keep credit flow enabled; other services depend on CE/backpressure rather than target credits.
- Timeout paths after `ath12k_htc_send()` do not own the skb anymore, so service connect timeout cleanup relies on later CE completion.

## Test Signals

Useful tests include target READY timeout/poll fallback, invalid READY payloads, service connect success/failure/status codes, multi-WMI endpoint credit allocation for single/DBS/DBS-SBS modes, TX credit exhaustion and restoration on CE send failure, trailer credit report parsing, suspend ACK/NACK events, invalid endpoint RX frames, and DMA mapping fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.h

## Purpose

`htc.h` defines the ath12k HTC wire protocol structures, service IDs, endpoint IDs, credit/trailer formats, endpoint callback contracts, HTC state object, and public HTC APIs.

## Important APIs, Types, and Functions

Bit masks define HTC header fields, service message fields, READY fields, service response fields, and setup-complete fields.

Protocol enums include TX/RX flags, HTC message IDs, HTC versions, service connection threshold flags/statuses, trailer record IDs, service groups, service IDs, and endpoint IDs.

Wire structs include `ath12k_htc_hdr`, `ath12k_htc_ready`, `ath12k_htc_ready_extended`, `ath12k_htc_conn_svc`, `ath12k_htc_conn_svc_resp`, `ath12k_htc_setup_complete_extended`, `ath12k_htc_msg`, `ath12k_htc_record_hdr`, `ath12k_htc_credit_report`, and `ath12k_htc_record`.

Runtime structs include `ath12k_htc_ep_ops`, `ath12k_htc_svc_conn_req`, `ath12k_htc_svc_conn_resp`, `ath12k_htc_ep`, `ath12k_htc_svc_tx_credits`, and `ath12k_htc`.

Public APIs are `ath12k_htc_init()`, `ath12k_htc_wait_target()`, `ath12k_htc_start()`, `ath12k_htc_connect_service()`, `ath12k_htc_send()`, `ath12k_htc_alloc_skb()`, and `ath12k_htc_rx_completion_handler()`.

## Control Flow and Integration

Endpoint users construct `ath12k_htc_svc_conn_req` with callbacks, connect to a service, receive endpoint ID/max message length in the response, send skbs with `ath12k_htc_send()`, and receive inbound skbs through `ep_rx_complete`. Boot code initializes HTC, waits for target READY, connects WMI/HTT services, then calls `ath12k_htc_start()`.

## State and Persistence Behavior

`struct ath12k_htc` persists for device lifetime and stores endpoint table, TX lock, control response buffer/completion, credit allocation state, target credit size, and WMI endpoint count. Endpoint entries persist service IDs, callbacks, pipe IDs, credit state, flow-control status, and sequence number.

## Dependencies and Integration Points

The header depends on Linux kernel list/bug/skb/timer headers and `struct ath12k_base`. It is consumed by HTC implementation, WMI, HTT, CE completion paths, boot, suspend, and service clients.

## Risks and Contract Notes

- Packed/aligned wire structs are firmware ABI; field order and bit masks must remain synchronized with target firmware.
- `ATH12K_HTC_EP_UNUSED = -1` is in an enum also used for array indices; code must validate before indexing.
- Control buffer size is fixed at 256 bytes; future firmware control messages larger than this need explicit handling.
- Service IDs are generated from group/index values. New service IDs must not collide with firmware-defined IDs.

## Test Signals

Compile and sparse checks for packed wire structs, service connect tests for every service ID used by the driver, endpoint index validation, credit accounting tests, and boot/suspend event tests are useful header-level signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hw.h

## Purpose

`hw.h` defines ath12k target defaults, firmware/board filenames, bus identifiers, hardware capability/parameter structures, hardware operation callbacks, firmware/board IE layouts, and small helper mappings for pdev/mac/SRNG IDs. It is the central hardware-variant configuration contract used by core, HAL, WMI, datapath, firmware, and bus code.

## Important APIs, Types, and Functions

Target defaults cover vdev/station counts, peer keys, AST skid/offload limits, chain masks, RX timeouts, decap modes, scan/roam/offload limits, multicast tables, TX debug log size, RX batch mode, MSDU descriptors, fragment entries, beacon offload, WDS entries, DMA burst, and EMA max profile period.

Firmware and board constants include directory/name strings for board-2, board, caldata, AMSS, M3, auxiliary microcode, and regdb files, plus board magic and PCIe payload/userpd constants.

Enums define CCK/OFDM hardware rates, bus type, and M3 firmware loader type.

`struct ath12k_hw_ring_mask` maps datapath ring classes to external IRQ groups. `struct ath12k_hw_params` stores per-chip capabilities and configuration: firmware layout, radio count, QMI service ID, CE configs/maps, RXDMA shape, monitor support, power-management flags, REO LUT/shadow register support, MHI config, WMI init hook, QMI feature bitmap, rfkill, RDDM, MLO limits, ACPI, dynamic SMPS, IOVA mask, CE remap/address tables, board offset, and primary-link-only datapath behavior.

`struct ath12k_hw_ops` provides hardware-specific helpers for pdev/mac/SRNG ID translation, RXDMA ring selection, TX completion ring identification, skb ring selection, and frame link-agnostic checks.

Inline helpers `ath12k_hw_get_mac_from_pdev_id()`, `ath12k_hw_mac_id_to_pdev_id()`, and `ath12k_hw_mac_id_to_srng_id()` call hardware ops when present or default to zero.

Firmware/board IE definitions include `struct ath12k_fw_ie`, board/regdb IE enums, and `ath12k_bd_ie_type_str()`.

## Control Flow and Integration

Chip-specific tables populate `ath12k_hw_params` and `ath12k_hw_ops` during device matching. Core and boot code use these values to size WMI resources, request firmware/board files, configure CE/MHI/QMI, set datapath ring counts, select monitor/RXDMA behavior, and gate suspend/ASPM/current-channel/MLO behavior. HAL and datapath code repeatedly call the inline ID mapping helpers and hardware ops when setting up rings and peer RX/TX state.

## State and Persistence Behavior

The header defines mostly immutable configuration tables referenced through `ab->hw_params`. Those parameters control long-lived driver state allocation sizes, firmware resource requests, interrupt masks, RX/TX ring topology, and feature gates for the lifetime of the device.

## Dependencies and Integration Points

It includes MHI and UUID kernel headers plus `wmi.h` and `hal.h`. It references CE pipe/config structures, service-to-pipe maps, HAL descriptor types, WMI resource configuration, MHI controller configs, ACPI GUIDs, and mac80211 management/link-vif types.

## Risks and Contract Notes

- The mutual include relationship with `hal.h` is guarded but tight; adding new direct type dependencies can create incomplete-type issues.
- Default inline ID mapping helpers return zero when ops are absent. That is only correct for single-radio/simple hardware.
- Resource macros depend on `ab->profile_param`; callers must ensure profile parameters are initialized before using them.
- `ath12k_hw_params` is broad and feature-packed; adding a new hardware family requires careful audit of every boolean default, especially RXDMA, REO LUT, shadow regs, MLO, and primary-link-only behavior.
- Firmware/board filenames and IE IDs are external ABI with linux-firmware and board tooling.

## Test Signals

Useful validation includes booting every supported hardware table, WMI resource sizing tests for profile modes, firmware/board file lookup, CE/service map checks, ring mask interrupt routing, pdev/mac/SRNG ID translation tests, monitor support gating, suspend/ASPM feature tests, MLO peer limit tests, and static build coverage for PCI and AHB buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hw.h -->
