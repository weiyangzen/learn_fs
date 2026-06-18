# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/datapath.h

Purpose: Defines datapath-group command IDs and payloads for MU-MIMO groups, timing measurements, channel estimation, datapath monitor notifications, thermal dual-chain requests, RLC/SAD, RX BAID sessions, scheduler queue config, and security key commands.

Important APIs and types: `enum iwl_data_path_subcmd_ids` names datapath commands/notifications. Structures include `iwl_mu_group_mgmt_cmd/notif`, `iwl_time_sync_cfg_cmd`, `iwl_synced_time_cmd/rsp`, `iwl_time_msmt_notify`, `iwl_time_msmt_cfm_notify`, `iwl_channel_estimation_cfg`, `iwl_datapath_monitor_notif`, `iwl_thermal_dual_chain_request`, `iwl_rlc_config_cmd`, `iwl_rx_baid_cfg_cmd/rsp`, `iwl_scd_queue_cfg_cmd`, and `iwl_sec_key_cmd`.

Control flow: No executable flow. Runtime code sends datapath commands to configure receive/transmit behavior and parses notifications for timing, monitor, thermal, BA, and power-management events.

State and persistence: Firmware stores MU group membership, RLC/SAD settings, BAID sessions, scheduler queues, and security keys until modified or reset. Driver mirrors relevant session/key state outside this header.

Dependencies and integration points: Used by MVM/MLD datapath, station security, block-ack setup, queue allocation, timing measurement userspace reporting, channel estimation collection, and command group routing.

Risks: Union fields in BAID, SCD queue, and security key commands must match the selected action/operation. Security key flags combine cipher, TX suppression, key size, MFP, multicast, and SPP A-MSDU semantics in one byte. Timing notifications contain large vendor-specific variable data. BAID limits differ old/current. Scheduler queue DMA addresses must be valid IOVAs.

Test signals: MU group update/notification, TM/FTM and PTM timestamp commands, channel-estimation filters by timer/count/rate/frame type, RLC/SAD configurations, thermal dual-chain SMPS requests, BAID add/modify/remove including old remove layout, scheduler queue add/modify/remove, and security key add/modify/remove for WEP/CCMP/TKIP/GCMP/MFP/multicast.
