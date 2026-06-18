# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.c

## Purpose

`peer.c` manages firmware and datapath peer lifecycle for ath12k stations and vdevs. It coordinates WMI peer create/delete commands, waits for DP peer map/unmap events, updates per-radio peer counts, fills MLO peer metadata, deletes all link peers for MLO stations, and maintains a reverse-address hash table for link station lookup.

## Important APIs And Functions

- `ath12k_peer_create()` validates peer capacity and duplicate pdev/address state, sends WMI peer create, waits for DP map, fills `ath12k_dp_link_peer` fields, updates STA/MLO metadata, increments `ar->num_peers`, and assigns the peer to DP hardware.
- `ath12k_peer_delete()` unassigns DP mapping, sends WMI delete, waits for DP unmap and `peer_delete_done`, then decrements peer count.
- `ath12k_peer_cleanup()` removes stale DP peers for a vdev under `dp_lock`.
- `ath12k_peer_mlo_link_peers_delete()` sends delete for all MLO link peers before waiting for all responses, matching firmware expectations.
- `ath12k_peer_ml_alloc()` allocates an MLO peer ID from a bitmap.
- `ath12k_link_sta_rhash_*()` initializes, inserts, deletes, destroys, and looks up `ath12k_link_sta` by MAC address.

## Control Flow

Map/unmap waits use `ath12k_wait_for_dp_link_peer_common()`, which sleeps on `ab->peer_mapping_wq` while checking the DP peer list under `dp_lock`, and exits early if crash flush is set. Create sends WMI first, waits for map, then rechecks the DP peer object; if missing after a successful wait, it attempts cleanup by sending delete and waiting for delete completion. Delete reinitializes completion before sending WMI and waits for both DP and firmware completion signals.

## State And Persistence

Persistent driver state is in memory: DP peer list, peer fields (`pdev_idx`, `sta`, link ID, ML ID, ML address, primary-link flag, MLO flag), `ar->num_peers`, `ah->free_ml_peer_id_map`, and `ab->rhead_sta_addr`. There is no disk persistence. Peer state is synchronized by wiphy lock, `dp_lock`, and `base_lock` depending on operation.

## Dependencies And Integration

The file depends on ath12k core, DP peer helpers, WMI peer commands, debugfs, rhashtable, completions, and mac80211 STA/VIF objects. MAC station-state code calls peer create/delete, DP event handling wakes waits, and MLO link management depends on all-link delete ordering.

## Risks And Test Signals

Risks include timeouts when firmware/DP map events are lost, peer count imbalance on partial create/delete failures, MLO delete ordering regressions, duplicate-peer races if locks are not held, and stale rhashtable entries. Test signals include association/disassociation loops, AP and STA peer churn, MLO association/deletion across multiple links, firmware crash during peer operations, peer table exhaustion, lockdep, and rhashtable duplicate/remove fault cases.
