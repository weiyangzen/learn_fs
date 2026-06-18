# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.c

## Purpose

`agg.c` implements MLD RX Block Ack aggregation support: firmware BAID allocation/removal, software reorder buffering per BAID/RX queue, release notifications, BAR-driven releases, BA session timeout handling, and station-mask updates when MLO station IDs change.

## Important APIs, Types, and Functions

Public functions are `iwl_mld_reorder()`, `iwl_mld_ampdu_rx_start()`, `iwl_mld_ampdu_rx_stop()`, `iwl_mld_handle_frame_release_notif()`, `iwl_mld_handle_bar_frame_release_notif()`, `iwl_mld_del_ba()`, and `iwl_mld_update_sta_baids()`. Local helpers release stored frames, process firmware release notifications, start/stop BA in firmware with `RX_BAID_ALLOCATION_CONFIG_CMD`, initialize/free reorder buffers, and expire inactive sessions through mac80211's BA timer callback.

## Control Flow

Starting an A-MPDU RX session allocates cacheline-aligned per-queue reorder entries, sends an ADD BAID command, records the firmware BAID in station TID state, initializes per-queue windows, starts an inactivity timer if requested, and publishes BAID data through RCU. Incoming MPDUs with valid BAIDs are verified against station mask and TID, duplicate/old frames are dropped, immediately releasable frames pass upward, and out-of-order frames are queued by sequence number. Firmware release or BAR notifications release buffered lists up to NSSN. Stopping a session removes it from firmware unless restarting, synchronizes RX queues with an internal DELBA notification, purges unexpected leftovers, clears the RCU pointer, and frees by `kfree_rcu()`.

## State and Persistence Behavior

Persistent state includes `mld->fw_id_to_ba[]`, `mld->num_rx_ba_sessions`, each station's `tid_to_baid[]`, BAID station masks, reorder windows, per-queue stored frame lists, inactivity timers, and last-RX timestamps. RCU protects RX-side lookups from teardown races.

## Dependencies and Integration Points

The file depends on mac80211 sequence arithmetic, skb queues, MLD station/link helpers, firmware RX BAID API structures, command sending in `hcmd.h`, RX queue sync, and packet delivery through `iwl_mld_pass_packet_to_mac80211()`.

## Risks and Edge Cases

Reorder correctness is sensitive to A-MSDU subframes: NSSN is ignored until the last subframe to avoid advancing past missing subframes. BAID/station-mask mismatch falls back to passing packets, which is safer than dropping but can hide firmware mapping bugs. Timer expiry may run during failed restart flows where station pointers are absent. Teardown relies on RX queue synchronization to release all stored skbs; leftover frames trigger WARN and purge.

## Test Signals

KUnit should cover `iwl_mld_reorder()` for in-order, holes, duplicates, old SN, A-MSDU first/last subframes, BAR release, and invalid BAID. Integration tests should verify ADDBA/DELBA firmware commands, BAID exhaustion, MLO station-mask update, restart stop path, timer expiry, and no skb leaks on teardown.
