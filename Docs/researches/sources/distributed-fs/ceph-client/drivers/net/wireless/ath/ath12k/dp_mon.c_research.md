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
