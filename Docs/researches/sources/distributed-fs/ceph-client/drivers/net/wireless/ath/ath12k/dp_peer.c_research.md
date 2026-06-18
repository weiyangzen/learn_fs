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
