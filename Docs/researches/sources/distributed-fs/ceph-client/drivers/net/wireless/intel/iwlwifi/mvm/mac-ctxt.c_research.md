# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mac-ctxt.c

## Purpose

`mac-ctxt.c` manages legacy firmware MAC contexts and shared MAC-level helpers for iwlwifi MVM. It allocates MAC/TSF IDs, builds `MAC_CONTEXT_CMD` payloads for station, AP/GO, monitor, P2P device, and IBSS interfaces, prepares beacon templates, handles beacon/missed-beacon/stored-beacon/probe-response notifications, and coordinates channel-switch state with mac80211.

## Important APIs, Types, And Functions

- `iwl_mvm_ac_to_tx_fifo[]`, `iwl_mvm_ac_to_gen2_tx_fifo[]`, and `iwl_mvm_ac_to_bz_tx_fifo[]` map ACs to firmware TX FIFOs.
- `iwl_mvm_mac_ctxt_init()` allocates MAC and TSF IDs and initializes default link/time-event state.
- `iwl_mvm_mac_ctxt_add()`, `iwl_mvm_mac_ctxt_changed()`, and `iwl_mvm_mac_ctxt_remove()` are the public MAC context lifecycle entry points.
- `iwl_mvm_mac_ctxt_cmd_common()` fills shared MAC command fields: ID/color, type, TSF, addresses, basic rates, short preamble/slot, QoS, and protection flags.
- Per-type builders include `iwl_mvm_mac_ctxt_cmd_sta()`, `_listener()`, `_ibss()`, `_p2p_device()`, `_ap()`, and `_go()`.
- Shared helpers `iwl_mvm_set_fw_basic_rates()`, `iwl_mvm_set_fw_protection_flags()`, and `iwl_mvm_set_fw_qos_params()` are also used by link-context code.
- Beacon helpers include `iwl_mvm_mac_ctxt_beacon_changed()`, `iwl_mvm_mac_ctxt_send_beacon_v6()`, `_v7()`, `_v9()`, `iwl_mvm_mac_ctxt_set_tim()`, and rate/flag helpers.
- Notification handlers include `iwl_mvm_rx_beacon_notif()`, `iwl_mvm_rx_missed_beacons_notif()`, `iwl_mvm_rx_missed_beacons_notif_legacy()`, `iwl_mvm_rx_stored_beacon_notif()`, `iwl_mvm_probe_resp_data_notif()`, `iwl_mvm_channel_switch_start_notif()`, and `iwl_mvm_channel_switch_error_notif()`.

## Control Flow

MAC context initialization iterates active interfaces to reserve unused MAC IDs and compatible TSF IDs. TSF sharing is preferred between station and AP/GO interfaces when beacon intervals are divisor/multiple compatible, avoiding drift between related TBTT schedules. During resume/recovery, existing IDs are preserved if the iterator finds the vif already active.

Lifecycle commands route through `iwl_mvm_mac_ctx_send()` based on vif type. Station contexts set multicast acceptance, association timing, DTIM/TBTT values, listen interval, AID, P2P CT window, probe-request filters, HE filter, and TWT policy. AP/GO contexts set multicast FIFO, probe/beacon filters, beacon interval, DTIM interval, multicast queue, and stable beacon time; GO additionally sends CT window and opportunistic power-save state. Monitor mode enables promiscuous/control/beacon/probe/FCS filters and allocates a sniffer internal station. P2P device mode restricts receive filtering to probe requests and can enable extended discovery when another GO is active.

Beacon template updates get a beacon skb from mac80211 and choose firmware template version by capability/API. Older formats include TX command data and TIM/CSA offsets. Newer formats send rate flags, byte count, template/link ID, TIM, CSA/ECSA, optional broadcast TWT offset, and FILS discovery hints for APs on PSC or wide 6 GHz channels. Notifications update CSA countdowns, AP beacon GP2 time, IBSS manager state, missed-beacon loss decisions, stored beacon forwarding to mac80211 RX, P2P NoA/probe-response state, and channel-switch completion or disconnect.

## State And Persistence

The file mutates per-vif `struct iwl_mvm_vif` state: MAC ID, TSF ID, color, uploaded flag, AP/IBSS active fields, time-event data, AP beacon time, CSA countdown state, default link queues/stations, probe response RCU pointer, and counters. Global MVM state touched includes `csa_vif`, `csa_tx_blocked_vif`, `ap_last_beacon_gp2`, `ibss_manager`, sniffer station, hardware flags, and debug triggers. Firmware holds MAC contexts and beacon templates after commands; software state is runtime-only.

## Dependencies And Integration Points

This file sits between mac80211 vif/bss callbacks and firmware MAC commands. It depends on cfg80211/mac80211 interface types, rates, beacon generation, CSA helpers, RCU vif lookup, iwlwifi firmware context/filter/beacon/offload APIs, station allocation, Bluetooth coexistence TX priority, time-event CSA scheduling, debug triggers, and link-context helper reuse. `link.c` calls its rate/protection/QoS helpers for MLD link commands.

## Risks And Edge Cases

- MAC/TSF ID allocation is global across active interfaces; recovery/resume must preserve IDs to avoid firmware/mac80211 mismatches.
- Beacon template version gating is complex and tied to `IWL_UCODE_TLV_CAPA_CSA_AND_TBTT_OFFLOAD`, `IWL_UCODE_TLV_API_NEW_BEACON_TEMPLATE`, and command versions.
- `iwl_mvm_mac_ctxt_set_tim()` manually parses beacon IEs and warns if TIM is absent; malformed beacon templates can break power-save delivery.
- AP beacon scheduling intentionally offsets from an associated station TBTT using randomness; changes can affect multi-interface coexistence.
- Missed-beacon handling distinguishes consecutive misses with and without RX; wrong thresholds or notification version IDs can cause false disconnects or missed loss events.
- Probe-response NoA data uses RCU replacement; old data must be freed with `kfree_rcu()` to avoid use-after-free.
- CSA handling spans beacon TX notifications, delayed work, station TX blocking, and firmware error notifications, so partial failures can leave TX blocked or channel switch incomplete.

## Test Signals

Good coverage includes station association and reassociation, AP/GO/IBSS bring-up, monitor mode with FCS flag changes, P2P device discovery, multi-interface TSF sharing, beacon template updates across firmware versions, TIM and CSA/ECSA offset correctness, FILS beacon flags on 6 GHz/PSC channels, missed-beacon disconnect thresholds, stored beacon delivery into mac80211 RX, P2P NoA probe-response updates, and CSA start/error notifications for AP and station modes.
