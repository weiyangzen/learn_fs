# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.h

## Purpose

`sta.h` is the station-management contract for the MVM driver. It documents the station table model, DQA queue policy, internal station roles, AP power-save behavior, firmware restart assumptions, and exposes the data structures and APIs implemented by `sta.c` and newer MLD station code.

## Important APIs and types

The main types are `enum iwl_mvm_agg_state`, `struct iwl_mvm_tid_data`, `struct iwl_mvm_key_pn`, `struct iwl_mvm_rxq_dup_data`, `struct iwl_mvm_link_sta`, `struct iwl_mvm_sta`, `struct iwl_mvm_int_sta`, and `struct iwl_mvm_sta_state_ops`. `struct iwl_mvm_sta` is embedded in mac80211 station private data and stores per-station queue masks, firmware IDs, aggregation state, key PN state, duplicate detection, power-save state, TX disable state, rate-scaling link data, and MLO link station pointers. `struct iwl_mvm_int_sta` is the reduced representation for firmware-only stations.

Public prototypes cover station add/update/remove, queue restoration, key install/remove/update, RX/TX aggregation, internal station management, broadcast/multicast station setup, AP power-save controls, disable-TX handling, CSA cancellation, and MLD-specific station and queue APIs.

## Control flow and state model

The header describes station creation through mac80211 `sta_state`, firmware publication through `ADD_STA`, and RCU lookup through `fw_id_to_mac_id`. It establishes the locking split: `mvm->mutex` serializes station table writers, RCU protects fast readers, and `mvm_sta->lock` protects per-station sequence and BA/TID state reachable from softirq and response paths.

DQA documentation records the queue allocation policy: some queues remain static, dynamic queues are allocated on demand by RA/TID, management traffic is treated as TID 8, new stations reserve a data queue, and exhausted pools can force per-station shared queues. Restart documentation states that embedded mac80211 private station data survives firmware reset and must be reinitialized or reused carefully.

## Dependencies and integration points

The header depends on Linux spinlocks, wait queues, mac80211 station/vif/key types, `iwl-trans.h` for TID count, firmware station limits from `fw-api.h`, and rate-scaling types from `rs.h`. It is included by station implementation, TX/RX paths, MAC state handlers, TDLS, thermal/disable-TX users, and MLD station code.

## Risks

Because this header defines shared state layout, changes can break assumptions in interrupt/softirq paths, firmware restart, MLD link handling, and station private data sizing. The documented locking rules are essential; bypassing them can corrupt sequence counters, BA state, key PN pointers, or RCU station lookups. Non-MLO and MLO link fields coexist, so callers must use the correct `deflink` or link-indexed pointer.

## Test signals

Compile coverage across MLD and non-MLD builds is the first signal. Behavioral tests should cover station lifecycle, queue allocation, restart reconfiguration, AP power-save, aggregation transitions, key install/remove, and internal station setup. Static analysis should verify RCU annotations and spinlock-protected fields are used consistently.
