# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.h

## Purpose

`peer.h` declares ath12k peer lifecycle and link-station lookup APIs used by MAC, DP, and MLO code. It is the compact interface to the implementation in `peer.c`.

## Important APIs

- `ath12k_peer_create()`, `ath12k_peer_delete()`, and `ath12k_peer_cleanup()` manage firmware and DP peer objects for one vdev.
- `ath12k_wait_for_peer_delete_done()` exposes the wait path when callers send deletes separately.
- `ath12k_peer_mlo_link_peers_delete()` deletes all link peers belonging to an MLO station.
- `ath12k_peer_ml_alloc()` allocates a multi-link peer ID.
- `ath12k_link_sta_rhash_tbl_init()`, `destroy()`, `add()`, `delete()`, and `find_by_addr()` manage the address-indexed `ath12k_link_sta` table.
- `ath12k_peer_ml_find()` is declared for multi-link peer lookup by address.

## Control Flow, State, And Integration

Callers are expected to hold the appropriate mac80211 wiphy or base lock depending on operation. The implementation mutates DP peer lists, per-radio peer counters, MLO peer ID bitmaps, and rhashtable state. MAC station-state transitions and MLO link changes are primary consumers.

## Risks And Test Signals

The header's risks are contract drift: changing prototypes affects peer lifecycle across MAC/DP. Locking expectations are not encoded in types, so implementation lockdep assertions are the main guard. Test signals include build coverage, station create/delete, MLO link peer deletion, and address lookup under concurrent association churn.
