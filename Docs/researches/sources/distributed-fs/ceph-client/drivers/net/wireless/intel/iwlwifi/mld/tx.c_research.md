# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.c

## Purpose

Implements the MLD transmit path for Intel iwlwifi: firmware TXQ allocation/removal, skb-to-`TX_CMD` construction, TSO/A-MSDU segmentation, TXQ draining, TX response and compressed BA reclaim, station queue flushing, lowest-rate conversion, and antenna fallback.

## Important APIs, Types, and Functions

Key entry points are `iwl_mld_add_txq_list()`, `iwl_mld_add_txqs_wk()`, `iwl_mld_ensure_queue()`, `iwl_mld_remove_txq()`, `iwl_mld_tx_from_txq()`, `iwl_mld_tx_skb()`, `iwl_mld_handle_tx_resp_notif()`, `iwl_mld_handle_compressed_ba_notif()`, `iwl_mld_flush_link_sta_txqs()`, `iwl_mld_update_sta_txqs()`, `iwl_mld_toggle_tx_ant()`, and `iwl_mld_get_lowest_rate()`. Internal helpers choose firmware queues, build TX commands, compute checksum/offload-assist bits, translate mac80211 and firmware rates, and segment GSO traffic.

## Control Flow

TXQ allocation starts from `mld->txqs_to_add`: queue size is selected from management/HE/EHT constraints, AP watchdog is disabled, `iwl_trans_txq_alloc()` allocates the SCD queue, and `fw_id_to_txq[]` is published under RCU. `iwl_mld_tx_from_txq()` serializes concurrent drainers with `tx_request`, dequeues mac80211 SKBs while not stopped-full, and hands each SKB to either TSO handling or direct MPDU TX.

`iwl_mld_tx_mpdu()` resolves the firmware queue from station TXQ/VIF type/ROC state, drops invalid/nullfunc frames, allocates a device TX command, optionally appends P2P NoA to probe responses, fills `TX_CMD`, clears mac80211 status/control-sensitive data, stores the command pointer in `driver_data[1]`, and submits through `iwl_trans_tx()`. TSO flow may produce A-MSDU-marked MPDUs when QoS, station limits, TCP/IP header constraints, and fragment limits allow it.

Firmware TX responses validate payload shape, reclaim SKBs up to SSN, free TX command storage, map firmware status to mac80211 ACK status, trigger debug time points on failures, convert initial rate for radiotap/status, and update antenna fallback and MPDU counters. Compressed BA notifications reclaim aggregated descriptors by queue/index and update station counters. Flush sends `TXPATH_FLUSH`, validates the response, and reclaims affected queues in flush mode.

## State and Persistence Behavior

Per-TXQ firmware identity and status live in `struct iwl_mld_txq`; `fw_id_to_txq[]` and `fw_id_to_link_sta[]` are RCU maps. `mgmt_tx_ant` and per-station `data_tx_ant` are toggled on selected failures. SKB command ownership is transient through `info->driver_data[1]`. Low-latency counters are updated when frames are queued.

## Dependencies and Integration Points

Depends on mac80211 TXQ/VIF/STA/link/rate/status APIs, Linux GSO/checksum helpers, iwl transport TXQ/TX/reclaim primitives, firmware datapath APIs (`SCD_QUEUE_CONFIG_CMD`, `TX_CMD`, `TXPATH_FLUSH`, BA/TX notifications), and local MLD station/VIF/link/time-sync/low-latency helpers.

## Risks

Risks include wrong queue selection for management/off-channel/P2P/NAN traffic, accessing `info->control` after it is invalidated, TSO/A-MSDU size or fragment miscalculation, misreporting ACK status during reclaim/flush, and over-broad antenna toggling that interferes with normal rate control.

## Test Signals

Exercise AP/STA/P2P/NAN/monitor TX, off-channel management frames, TSO and non-TSO traffic, HE/EHT A-MSDU limits, injected rates, restart with pending TXQs, TX failure/ACK status, compressed BA reclaim, station flush, and IPv4/IPv6 checksum offload fallback paths.
