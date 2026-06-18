# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tdls.c

## Purpose

`tdls.c` manages Tunneled Direct Link Setup support for MVM, with emphasis on TDLS peer tracking, firmware TDLS configuration, TDLS discovery protection, and TDLS channel-switch state. It coordinates mac80211 TDLS operations with firmware commands and the MVM time-event/session-protection layer.

## Important APIs and functions

Peer lifecycle helpers are `iwl_mvm_teardown_tdls_peers()`, `iwl_mvm_tdls_sta_count()`, and `iwl_mvm_recalc_tdls_state()`. Channel-switch functions include `iwl_mvm_tdls_channel_switch()`, `iwl_mvm_tdls_cancel_channel_switch()`, `iwl_mvm_tdls_recv_channel_switch()`, `iwl_mvm_rx_tdls_notif()`, and delayed work `iwl_mvm_tdls_ch_switch_work()`. Internal helpers `iwl_mvm_tdls_check_action()`, `iwl_mvm_tdls_config_channel_switch()`, and `iwl_mvm_tdls_update_cs_state()` implement the channel-switch state machine.

## Control flow

TDLS peer teardown scans firmware station IDs under `mvm->mutex`, filters valid TDLS stations, and asks mac80211 to issue teardown operations. Recalculation counts peers for a VIF, updates power when the first peer is added or last peer removed, and sends `TDLS_CONFIG_CMD` when firmware advertises TDLS channel-switch capability.

TDLS discovery protection schedules session protection for two DTIM periods, using the newer session-protection command when available and legacy time events otherwise. Channel switch setup validates the requested action against current state and peer identity, finds the mac80211 station, chooses the requested peer channel or base channel, embeds the TDLS action frame and TX command metadata, sends `TDLS_CHANNEL_SWITCH_CMD`, and updates `mvm->tdls_cs` state. Firmware notifications move the state to active and schedule delayed retry/return work; cancellation clears the stored peer template and may wait a DTIM for PHY return to base channel.

## State and persistence

TDLS channel-switch state is stored in `mvm->tdls_cs`: current state, current firmware station ID, peer station ID, peer channel definition, initiator flag, operating class, copied template SKB, timing IE offset, and request timestamp. Only one switching peer is supported at a time. The state machine protects against stale responses, competing peers, duplicate requests, and invalid move-channel actions.

## Dependencies and integration points

The file depends on mac80211 TDLS APIs, firmware `TDLS_CONFIG_CMD` and `TDLS_CHANNEL_SWITCH_CMD`, MVM station lookup from `fw_id_to_mac_id`, channel formatting helpers, TX command setup helpers, and time-event/session-protection APIs. It integrates with station removal, power management, and delayed work on `system_percpu_wq`.

## Risks

The main risks are stale or conflicting TDLS action frames, single-peer assumptions, copied SKB lifetime, and races between cancellation, firmware notifications, station removal, and delayed retry work. Channel selection depends on valid chandef or base-channel RCU access. Incorrect state transitions can leave the PHY off-channel too long or repeatedly retry a failed peer.

## Test signals

Tests should cover peer count/power-update transitions, firmware config generation, discovery protection duration, outgoing and incoming channel-switch requests/responses, stale timestamp rejection, peer mismatch rejection, cancellation during active switch, station removal during TDLS work, and fallback between session-protection and legacy protection paths.
