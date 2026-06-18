# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tx.h

## Purpose
Defines firmware TX command, TX response, block-ack notification, beacon template, TX flush, and scheduler queue configuration ABI for iwlwifi. It spans older v6 TX commands, newer v9/v10+ TX command formats, status decoding, aggregation feedback, compressed BA notifications, beacon offload, and queue flushing.

## Important APIs, Types, And Functions
Key enums include `iwl_tx_flags`, `iwl_tx_cmd_flags`, `iwl_tx_pm_timeouts`, `iwl_tx_cmd_sec_ctrl`, `iwl_tx_offload_assist_flags_pos`, `iwl_tx_status`, `iwl_tx_agg_status`, `iwl_mvm_ba_resp_flags`, `iwl_dump_control`, and `iwl_scd_cfg_actions`. Core structures include `iwl_tx_cmd_v6_params`, `iwl_tx_cmd_v6`, `iwl_dram_sec_info`, `iwl_tx_cmd_v9`, `iwl_tx_cmd`, `iwl_tx_resp_v3`, `iwl_tx_resp`, `iwl_mvm_ba_notif`, `iwl_compressed_ba_notif`, `iwl_mac_beacon_cmd_v6/v7`, `iwl_mac_beacon_cmd`, `iwl_extended_beacon_notif`, `iwl_tx_path_flush_cmd`, and `iwl_scd_txq_cfg_cmd`.

## Control Flow
TX callers build command parameters, append the 802.11 header and payload, select rate/security/offload/lifetime/retry behavior, and submit through transport queues. Firmware returns per-frame or aggregated TX responses, later BA or compressed BA notifications advance aggregation queues. AP/IBSS paths install beacon templates and receive beacon TX notifications. Flush commands remove queued frames by queue bitmap or station/TID, and SCD config commands enable, disable, or retarget scheduler queues.

## State And Persistence
Persistent firmware-visible state includes TX queue configuration, station/TID ownership, beacon templates, security DRAM info, sequence control behavior, and aggregation progress. Per-command state includes lifetime, retry limits, offload flags, key selection, rate, and header/payload bytes. Flexible arrays in TX commands, responses, compressed BA notifications, and beacon templates require exact command sizing.

## Dependencies And Integration Points
Includes Linux 802.11 header definitions and integrates with mac80211 TX, iwlwifi transport/TFD queues, rate control/TLC, security offload, BT coexistence, AP beaconing, aggregation state machines, station table configuration, and TXQ scheduling.

## Risks
TX ABI version changes alter command layout and flag semantics. Incorrect length accounting around MAC header padding, IV/MIC/ICV/FCS exclusions, or A-MSDU offload can corrupt transmitted frames. Aggregation status is not equivalent to BA success; callers must combine TX responses with BA notifications. Queue flush and SCD retargeting can race with station teardown if IDs or colors are stale.

## Test Signals
Exercise unicast, multicast, management, EAPOL/high-priority, encrypted, A-MSDU, and aggregated TX across firmware API versions. Verify BA/compressed BA accounting, retry/failure statuses, beacon template updates with CSA/ECSA/BTWT, queue flush responses, and scheduler queue enable/disable flows. Air captures and mac80211 TX status propagation are key validation signals.
