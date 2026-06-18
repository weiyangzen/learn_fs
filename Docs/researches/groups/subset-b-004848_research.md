# subset-b-004848 mwifiex research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_ioctl.c

## Purpose
`sta_ioctl.c` is the station-side control/configuration surface for mwifiex. It bridges cfg80211/netdev requests and internal driver callers into firmware commands for association, multicast filtering, host sleep, power save, TX power, security material, regulatory country handling, remain-on-channel, statistics, register/EEPROM access, and generic IE storage.

## Important APIs, Types, and Functions
Key exported or externally consumed entry points include `mwifiex_copy_mcast_addr`, `mwifiex_wait_queue_complete`, `mwifiex_request_set_multicast_list`, `mwifiex_fill_new_bss_desc`, `mwifiex_dnld_txpwr_table`, `mwifiex_bss_start`, `mwifiex_set_hs_params`, `mwifiex_cancel_hs`, `mwifiex_enable_hs`, `mwifiex_get_bss_info`, `mwifiex_disable_auto_ds`, `mwifiex_drv_get_data_rate`, `mwifiex_set_tx_power`, `mwifiex_drv_set_power`, `mwifiex_set_encode`, `mwifiex_get_ver_ext`, `mwifiex_remain_on_chan_cfg`, `mwifiex_get_stats_info`, `mwifiex_reg_write`, `mwifiex_reg_read`, `mwifiex_eeprom_read`, `mwifiex_set_gen_ie`, `mwifiex_get_wakeup_reason`, and `mwifiex_get_chan_info`. Internally, the file owns helpers for WPA/WAPI/WPS IE parsing, WEP/WPA/WAPI key programming, country IE processing, regulatory power table loading, and generic IE/ARP filter handling.

## Control Flow and Integration
Association starts in `mwifiex_bss_start`: optional country IE processing updates adapter regulatory state and downloads TX power limits, then a temporary `mwifiex_bssdescriptor` is filled from cfg80211 BSS IEs. STA/P2P client mode checks network compatibility, blocks netdev queues, clears old association response state, and calls `mwifiex_associate`, retrying shared-key auth for auto-WEP failures. Ad-hoc mode either joins a compatible scanned BSS or starts a new IBSS. Multicast changes first adjust `priv->curr_pkt_filter`; selected multicast lists are sent with `HostCmd_CMD_MAC_MULTICAST_ADR`, and filter changes are committed with `HostCmd_CMD_MAC_CONTROL`.

Host sleep flow is split between configuration and activation. `mwifiex_set_hs_params` stores or sends `adapter->hs_cfg`, refusing HS changes during PPS/UAPSD. `mwifiex_enable_hs` optionally disconnects all interfaces on suspend, stops scheduled scan when needed, sets `MWIFIEX_IS_HS_ENABLING`, cancels pending commands, sends synchronous HS enable, and waits on `hs_activate_wait_q`.

Security flow stores user IEs and key state in `priv`. WPA/RSN/WAPI/WPS IEs are detected from generic IE buffers; WEP keys are cached in `priv->wep_key`, update `sec_info.wep_enabled`, and toggle firmware packet filter WEP enable. WPA/WAPI keys are forwarded as `HostCmd_CMD_802_11_KEY_MATERIAL`; IBSS WPA-None duplicates the key as PTK and GTK.

## State and Persistence Behavior
Persistent mutable state includes `adapter->country_code`, `adapter->domain_reg`, `adapter->rgpower_data`, `adapter->config_bands`, `adapter->hs_cfg`, `adapter->ps_mode`, `adapter->arp_filter`, `priv->curr_pkt_filter`, `priv->sec_info`, WEP key slots, `priv->wpa_ie`, `priv->wapi_ie`, heap-allocated `priv->wps_ie`, `priv->gen_ie_buf`, `priv->assoc_rsp_size`, and `priv->attempted_bss_desc`. Firmware state is kept in sync through synchronous and asynchronous `mwifiex_send_cmd` calls. The file also exposes direct register and EEPROM commands, which are stateful firmware/hardware probes rather than local persistence.

## Dependencies and Risks
The file depends heavily on cfg80211 BSS/IE APIs, firmware command definitions in `fw.h`/`ioctl.h`, WMM/11n helpers, device-tree and firmware-loader APIs for regulatory power tables, and adapter/private locking disciplines from the broader driver. Risks concentrate around variable-length IE parsing and TLV/key copying, firmware command synchronization, lifetime of BSS IE buffers under RCU, `priv->wps_ie` allocation/replacement, and privileged register/EEPROM access. Country IE length validation and TX power range checks are explicit guardrails; generic IE parsing still depends on well-formed element lengths to advance through buffers.

## Test Signals
Useful signals are association success/failure counters, cfg80211 connect/disconnect outcomes, host-sleep suspend/resume success, multicast/promiscuous packet behavior, WEP/WPA/WAPI key programming, remain-on-channel callbacks, regulatory power table request logs, data-rate and stats queries, and error logs from `mwifiex_wait_queue_complete`, malformed IE/key sizes, and firmware command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_rx.c

## Purpose
`sta_rx.c` handles station-mode receive buffers after the generic transport path has selected a `mwifiex_private`. It validates firmware RX descriptors, dispatches management frames, reconstructs Ethernet headers from firmware SNAP/802.2 frames, filters selected gratuitous ARP/IPv6 neighbor advertisements in HS2 mode, records RX rate/SNR/noise statistics, and invokes 11n reorder logic for unicast traffic.

## Important APIs, Types, and Functions
The public functions are `mwifiex_process_sta_rx_packet` and `mwifiex_process_rx_packet`. The local helper `mwifiex_discard_gratuitous_arp` inspects ARP replies/requests and IPv6 neighbor advertisements for same-source/destination address patterns. Important data structures include firmware `struct rxpd`, `struct rx_packet_hdr`, `struct mwifiex_arp_eth_header`, `struct mwifiex_sta_node`, and skb control metadata populated by `txrx.c`.

## Control Flow and Integration
`mwifiex_process_sta_rx_packet` starts with `rxpd` fields: packet type, offset, length, and sequence number. It bounds-checks `rx_pkt_offset + rx_pkt_length` and the embedded Ethernet header before any dereference. Management packets are passed to `mwifiex_process_mgmt_packet` and then freed. Non-unicast, non-11n, or packets addressed away from the current STA MAC bypass reorder and go straight to `mwifiex_process_rx_packet`.

For reorder-eligible packets, the transmit address is either the packet source for RA-based or TDLS traffic, or the current BSS MAC for infrastructure STA traffic. TDLS packets update the peer station node `rx_seq` and auto-TDLS signal cache. The packet is then passed to `mwifiex_11n_rx_reorder_pkt`; BAR or failed reorder paths free the skb and increment `rx_dropped` on error.

`mwifiex_process_rx_packet` converts firmware-provided LLC/SNAP frames to Ethernet II when the RFC1042/bridge-tunnel headers match, pulls the firmware descriptor and excess header bytes, optionally drops gratuitous address-resolution frames under `priv->hs2_enabled`, detects TDLS action frames by ethertype, updates per-priv RXPD rate fields for unicast packets, records histogram data, and finally calls `mwifiex_recv_packet`.

## State and Persistence Behavior
This file updates `priv->stats.rx_dropped`, `priv->rxpd_rate`, `priv->rxpd_htinfo`, `priv->rx_seq[]`, TDLS peer `rx_seq[]`, auto-TDLS RSSI/noise state, and histogram counters through `mwifiex_hist_data_add`. It consumes and frees SKBs; ownership either moves to the network stack through `mwifiex_recv_packet`, to reorder queues, or is explicitly freed on validation/drop paths.

## Dependencies and Risks
Dependencies include Linux Ethernet/IPv6/neighbor headers, mwifiex firmware descriptors, TDLS processing, 11n reorder, and utility RX forwarding. The key risks are descriptor offset/length trust, header reconstruction pointer arithmetic, and ensuring SKB ownership is clear across direct receive, reorder, BAR, management, and drop paths. Gratuitous IPv6 inspection assumes the ICMPv6 header is present after earlier length checks that only guarantee Ethernet/SNAP coverage, so malformed short IPv6 payloads are an edge worth fuzzing.

## Test Signals
Test with malformed RX offsets/lengths, management packet delivery, unicast reorder and BAR handling, multicast bypass, TDLS action frame parsing, HS2 gratuitous ARP/NA filtering, histogram increments, and netdev RX counters. Useful logs include "wrong rx packet", "Rx of mgmt packet failed", and "recv packet failed".
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_tx.c

## Purpose
`sta_tx.c` prepares station-mode transmit packets for firmware. It inserts firmware TxPD descriptors into SKBs, handles management-frame length/offset quirks, requests TX status for selected EAPOL/action frames, marks TDLS packets, and builds firmware NULL data packets used by power-save and PPS/UAPSD flows.

## Important APIs, Types, and Functions
The main entry points are `mwifiex_process_sta_txpd`, `mwifiex_send_null_packet`, and `mwifiex_check_last_packet_indication`. Important types are `struct txpd`, `struct mwifiex_txinfo` in `skb->cb`, `struct mwifiex_tx_param`, and adapter/private WMM state such as `user_pri_pkt_tx_ctrl`, `pkt_tx_ctrl`, `pps_uapsd_mode`, `sleep_period`, and `tx_lock_flag`.

## Control Flow and Integration
`mwifiex_process_sta_txpd` assumes enough headroom has already been reserved by the caller. It detects management frames, computes DMA alignment padding relative to the interface header, pushes `struct txpd`, fills BSS number/type, packet length, priority, WMM delay, optional TX status token, priority-specific TX control, PPS/UAPSD last-packet indication, and TDLS flags. It adjusts `tx_pkt_offset` for management frames and finally pushes the bus-specific interface header.

`mwifiex_send_null_packet` is a direct firmware send path. It refuses to send if the device is surprise-removed, the STA is disconnected, data is already in flight, or the transport port is not ready. It allocates a small SKB, reserves descriptor/interface headroom, fills a TxPD with high priority and supplied power-management flags, then calls `host_to_card` through USB data endpoint or the generic data type. It frees the SKB on synchronous completion/error and sets `tx_lock_flag` when a NULL packet is accepted or in progress.

`mwifiex_check_last_packet_indication` checks whether WMM queues and command queues are empty before allowing a last-packet indication; otherwise it sets `adapter->delay_null_pkt` to defer that indication.

## State and Persistence Behavior
The file mutates only transient packet descriptors plus adapter power-save control flags. Persistent effects are `adapter->tx_lock_flag` and `adapter->delay_null_pkt`; packet state is encoded into TxPD fields and `skb->cb`. NULL-packet sends update debug failure counters on transport failure.

## Dependencies and Risks
Dependencies include WMM queue accounting, generic `host_to_card` operations, USB endpoint selection, management-frame SKB tagging, and power-save state owned by event/command paths. Risks center on headroom/alignment assumptions, exact packet-length handling for management frames, and avoiding deadlock in PPS/UAPSD where `tx_lock_flag` intentionally stops data until firmware wakes/completes. NULL packets bypass normal WMM queueing, so transport readiness checks are critical.

## Test Signals
Test STA data and management TX descriptor layout, EAPOL/action TX status tokens, TDLS flag propagation, NULL-packet sends for power save, behavior when `data_sent` or USB port blocked, and recovery of `tx_lock_flag` after transport completion or EBUSY paths in `txrx.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/sta_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/tdls.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/tdls.c

## Purpose
`tdls.c` implements Tunneled Direct Link Setup support for mwifiex STA mode. It builds TDLS data/action frames, parses peer TDLS capability IEs, manages TDLS peer station-node state, holds and restores peer-bound packets while links are being created or torn down, drives firmware TDLS operation/configuration commands, and implements an auto-TDLS timer based on peer signal thresholds.

## Important APIs, Types, and Functions
Externally used functions include `mwifiex_send_tdls_data_frame`, `mwifiex_send_tdls_action_frame`, `mwifiex_process_tdls_action_frame`, `mwifiex_tdls_oper`, `mwifiex_get_tdls_link_status`, `mwifiex_get_tdls_list`, `mwifiex_disable_all_tdls_links`, `mwifiex_tdls_check_tx`, `mwifiex_flush_auto_tdls_list`, `mwifiex_add_auto_tdls_peer`, `mwifiex_auto_tdls_update_peer_status`, `mwifiex_auto_tdls_update_peer_signal`, `mwifiex_check_auto_tdls`, `mwifiex_setup_auto_tdls_timer`, `mwifiex_clean_auto_tdls`, and TDLS channel-switch config helpers. Local builders append supported rates, AID, HT/VHT capabilities and operations, extended capabilities, WMM, 20/40 coexistence, supported channels, operating classes, and link IDs.

## Control Flow and Integration
Create-link flow begins in `mwifiex_tdls_oper(MWIFIEX_TDLS_CREATE_LINK)`: an existing in-progress setup is ignored; otherwise a peer station node is created, status becomes `TDLS_SETUP_INPROGRESS`, packets for that MAC are moved from WMM RA queues to `priv->tdls_txq`, and `HostCmd_CMD_TDLS_OPER` is sent. When enable succeeds, peer HT/VHT state drives AMPDU and max-AMSDU configuration, optional channel-switch firmware configuration is issued, RX sequence state is reset, held packets are restored into TDLS RA queues, and auto-TDLS status is updated. Disable/failed enable paths clean reorder/BA state, remove station nodes, restore queued packets as normal traffic, and send disable commands.

Frame construction is split between encapsulated TDLS data frames and public TDLS discovery action frames. Both allocate bounded SKBs, reserve mwifiex headroom, write fixed 802.11/TDLS fields, append capability IEs, copy caller-provided extra IEs, add link IE last, initialize `mwifiex_txinfo`, and queue through `mwifiex_queue_tx_pkt`. Received TDLS action frames are validated by ethertype/category/action length, then parsed IE-by-IE into the peer node capability cache.

Auto-TDLS is timer-driven. `mwifiex_check_auto_tdls` periodically marks stale RSSI samples for discovery, requests teardown for weak/unknown linked peers, and requests setup for strong unlinked peers under a failure-count limit. `mwifiex_tdls_check_tx` consumes this state on outgoing packets and invokes cfg80211 TDLS setup or sends discovery requests.

## State and Persistence Behavior
State lives in `priv->sta_list` station nodes (`tdls_status`, capability cache, HT/VHT flags, `rx_seq`, `ampdu_sta`, max-AMSDU), `priv->tdls_txq`, WMM RA queues and counters, `priv->auto_tdls_list`, `auto_tdls_timer_active`, and `check_tdls_tx`. Firmware TDLS state is changed through `HostCmd_CMD_TDLS_OPER` and `HostCmd_CMD_TDLS_CONFIG`.

## Dependencies and Risks
Dependencies include cfg80211 TDLS requests, mwifiex WMM/11n/11ac helpers, station-list locking, reorder/BA cleanup, firmware TDLS commands, and SKB queue ownership. Risks include variable-length IE parsing, use of peer MAC from packet data, packet ownership while moving between WMM queues and `tdls_txq`, timer/list races, and broad cleanup calls (`mwifiex_11n_cleanup_reorder_tbl`, delete-all BA streams) that affect more than one peer. Channel-switching state also gates command/TX paths through utilities, so incomplete teardown can stall traffic.

## Test Signals
Exercise TDLS setup/confirm/teardown/discovery frame generation, malformed TDLS frame parsing, packet hold/restore during setup failure and success, auto-TDLS RSSI threshold transitions, channel-switch start/stop commands, TDLS list/debug output, and traffic behavior while a peer is in setup or off-channel state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/tdls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/txrx.c

## Purpose
`txrx.c` is the generic data-path dispatcher shared by all mwifiex buses and roles. It routes RX buffers to STA or uAP handlers, prepares and sends TX packets through role-specific TxPD builders and bus `host_to_card` operations, drains the deferred TX queue, completes TX accounting/freeing, wakes netdev queues, and processes firmware TX-status events for EAPOL/action-management acknowledgements.

## Important APIs, Types, and Functions
Key APIs are `mwifiex_handle_rx_packet`, `mwifiex_process_tx`, `mwifiex_process_tx_queue`, `mwifiex_write_data_complete`, and `mwifiex_parse_tx_status_event`. The local `mwifiex_host_to_card` retries/dequeues queued packets. Important data structures are `struct rxpd`, `struct txpd`, `struct mwifiex_txinfo`, `struct mwifiex_rxinfo`, `struct mwifiex_tx_param`, `adapter->tx_data_q`, `adapter->tx_queued`, `adapter->tx_pending`, `priv->wmm_tx_pending[]`, and `priv->ack_status_frames`.

## Control Flow and Integration
RX handling reads BSS number/type from firmware `rxpd`, finds the matching private interface, initializes skb RX control metadata, and dispatches to `mwifiex_process_uap_rx_packet` for AP role or `mwifiex_process_sta_rx_packet` otherwise. Missing interface state drops the packet.

TX starts in `mwifiex_process_tx`, which rejects empty or insufficient-headroom SKBs. uAP packets update destination station TX stats and call `mwifiex_process_uap_txpd`; station packets call `mwifiex_process_sta_txpd`. If `adapter->data_sent` or `tx_lock_flag` is set, the fully prepared SKB is queued on `adapter->tx_data_q` and accounted in `tx_queued`. Otherwise it is sent through USB endpoint `priv->usb_port` or generic data type. Return handling distinguishes no-resource, busy, hard failure, in-progress, malformed, and synchronous success. Busy during PPS/UAPSD can clear the last-packet flag and unlock TX.

`mwifiex_process_tx_queue` repeatedly dequeues while transport is not blocked. It passes `next_pkt_len` hints for bus aggregation and requeues at the head on EBUSY. Completion resolves `priv` from TXCB, updates netdev trans_start, handles bridged-packet accounting, skips normal stats for aggregate wrapper SKBs, updates success/error counters, decrements pending counts, and wakes WMM netdev queues below `LOW_TX_PENDING`. TX-status events remove ack SKBs from an IDR and notify cfg80211 or `skb_complete_wifi_ack`.

## State and Persistence Behavior
This file mutates transport gating (`data_sent` is owned by bus callbacks but observed here), deferred queue contents, atomic queue counters, per-interface TX stats, per-WMM pending counts, bridged-packet counters, debug failure counters, and ack-status IDR entries. SKB ownership is transferred to transport, queued internally, or freed on completion.

## Dependencies and Risks
Dependencies include STA/uAP TxPD/RX handlers, bus `if_ops`, WMM queue mappings, netdev queue APIs, cfg80211 management TX status, and the ack-status lock/IDR. Risks are queue accounting imbalance on aggregate versus non-aggregate paths, SKB ownership on mixed synchronous/asynchronous bus returns, EBUSY requeue ordering, and keeping `tx_lock_flag` consistent with power-save NULL packet semantics.

## Test Signals
Probe RX BSS dispatch, TX with insufficient headroom, USB/non-USB sends, EBUSY requeue, aggregate completion, bridged packet accounting, netdev queue wakeups, TX timeout counter reset, EAPOL/action ACK reporting, and queue draining after bus completion clears `data_sent`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_cmd.c

## Purpose
`uap_cmd.c` builds firmware commands and TLVs for mwifiex AP/uAP operation. It translates cfg80211 AP settings and station parameters into firmware-understandable security, rate, WMM, HT/VHT, channel, beacon, threshold, custom IE, BSS start/stop, deauth, and add-station commands.

## Important APIs, Types, and Functions
Public helpers include `mwifiex_set_secure_params`, `mwifiex_set_ht_params`, `mwifiex_set_vht_params`, `mwifiex_set_tpc_params`, `mwifiex_set_vht_width`, `mwifiex_set_uap_rates`, `mwifiex_set_sys_config_invalid_data`, `mwifiex_set_wmm_params`, `mwifiex_config_uap_11d`, `mwifiex_uap_prepare_cmd`, `mwifiex_uap_set_channel`, and `mwifiex_config_start_uap`. Internal command builders include `mwifiex_uap_bss_wpa`, `mwifiex_uap_bss_wep`, `mwifiex_uap_bss_param_prepare`, `mwifiex_uap_custom_ie_prepare`, `mwifiex_cmd_uap_sys_config`, `mwifiex_cmd_uap_bss_start`, `mwifiex_cmd_uap_sta_deauth`, and `mwifiex_cmd_uap_add_station`.

## Control Flow and Integration
AP start configuration is assembled into `struct mwifiex_uap_bss_param`. Security parsing maps cfg80211 privacy/auth/AKM/cipher selections into firmware protocol/key-management/cipher fields, including static WEP material copied from `priv->wep_key`. HT/VHT/TPC/WMM/rate helpers extract IEs from beacon head/tail. `mwifiex_uap_bss_param_prepare` then appends TLVs for MAC, SSID/broadcast SSID, rates, channel/band, beacon/DTIM, RTS/fragment/retry, WPA/WEP security, auth type, encryption protocol, HT capability, WMM capability, station ageout timers, power constraint, and PS ageout timer.

`mwifiex_uap_prepare_cmd` dispatches command numbers to sys-config, BSS start/stop/reset/list, deauth, channel report, or add-station builders. Host MLME BSS start optionally adds a `TLV_TYPE_HOST_MLME`. Add-station command creation updates/creates the station node, copies AID/listen interval/capability, emits STA flags, extended capability, supported rates, QoS, HT/VHT, and opmode TLVs, and initializes peer AMPDU and RX sequence state.

`mwifiex_uap_set_channel` maps cfg80211 chandef to channel/band/secondary-channel fields and updates adapter `config_bands`; band changes trigger domain-info and TX power table downloads. `mwifiex_config_start_uap` sends sys-config and BSS-start commands, then updates MAC_CONTROL for WEP packet filtering.

## State and Persistence Behavior
The file mutates `priv->sec_info`, `priv->wmm_enabled`, `priv->ap_11n_enabled`, `priv->ap_11ac_enabled`, `priv->bss_chandef`, `priv->curr_pkt_filter`, station-node fields, and `adapter->config_bands`. Firmware state persists through `HostCmd_CMD_UAP_SYS_CONFIG`, `HostCmd_CMD_UAP_BSS_START`, `HostCmd_CMD_11AC_CFG`, `HostCmd_CMD_ADD_NEW_STATION`, `HostCmd_CMD_MAC_CONTROL`, and related AP commands.

## Dependencies and Risks
Dependencies include cfg80211 AP settings, Linux 802.11 IE structs, mwifiex 11n/11ac helpers, station-list utilities, regulatory/TX power download functions, and firmware TLV layouts. Risks are TLV buffer-size assumptions, malformed or oversized beacon IEs, security mode mismatch between `sec_info` and firmware TLVs, incorrect band/secondary-channel encoding, and station-node mutation during command preparation before firmware acceptance.

## Test Signals
Test AP start for open, WPA/WPA2/SAE, static WEP, WMM on/off, HT/VHT widths, country IE 11D enable, custom IE programming, add/remove station with HT/VHT/QoS params, channel width transitions, and failure paths from sys-config/BSS-start/MAC_CONTROL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_event.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_event.c

## Purpose
`uap_event.c` handles firmware events for AP/uAP interfaces. It reports station association/deauthentication to cfg80211, creates and removes station nodes, initializes peer 11n aggregation state, tracks BSS active/idle/start state, parses AP capability TLVs, handles BA/AMSDU/scan/TX-status/power-save/radar/channel events, and forwards shared events to generic mwifiex handlers.

## Important APIs, Types, and Functions
The main public function is `mwifiex_process_uap_event`. The local `mwifiex_check_uap_capabilities` parses BSS-start event TLVs to set AP HT/VHT/WMM state and queue priorities. Important structures include `struct mwifiex_assoc_event`, `struct station_info`, `struct mwifiex_sta_node`, `struct host_cmd_ds_11n_batimeout`, and firmware event buffers `adapter->event_body` and `adapter->event_skb`.

## Control Flow and Integration
On `EVENT_UAP_STA_ASSOC`, the handler allocates `station_info`, extracts association request IEs from `TLV_TYPE_UAP_MGMT_FRAME` events, calls `cfg80211_new_sta`, adds a station node, and, when AP 11n is enabled, parses HT capabilities and initializes per-TID AMPDU permission and RX sequence state. `EVENT_UAP_STA_DEAUTH` notifies cfg80211, deletes RX reorder and TX BA state for the peer, removes WMM RA list entries, and deletes the station node.

`EVENT_UAP_BSS_IDLE` marks media and port closed, cleans TX/RX queues, and removes all station nodes. `EVENT_UAP_BSS_ACTIVE` opens media/port. `EVENT_UAP_BSS_START` sets port closed until active, updates netdev MAC from event body, resets histograms, and parses capability TLVs. Shared events update `adapter->tx_buf_size`, respond to ADDBA, delete BA streams, process BA timeout, handle ext scan reports, parse TX status, drive power-save sleep/awake transitions, process channel/radar/BT coexistence/TX pause/multichannel/RXBA sync, and report remain-on-channel expiration to cfg80211.

## State and Persistence Behavior
Persistent driver state includes `priv->media_connected`, `priv->port_open`, `priv->ap_11n_enabled`, `priv->ap_11ac_enabled`, `priv->wmm_enabled`, station list contents, per-peer AMPDU/RX sequence state, `adapter->tx_buf_size`, `adapter->ps_state`, `adapter->pps_uapsd_mode`, wakeup flags, `adapter->tx_lock_flag`, histograms, and remain-on-channel config. Firmware event contents are consumed from adapter event buffers.

## Dependencies and Risks
Dependencies include cfg80211 station and remain-on-channel APIs, WMM setup, 11n BA/reorder helpers, radar/11h handlers, TX status parsing in `txrx.c`, NULL-packet power-save flow in `sta_tx.c`, and station utilities in `util.c`. Risks include trusting event-body layout/length for association IEs and BSS MAC updates, station-info allocation failures, cleanup ordering during idle/deauth, and power-save state transitions that can leave `tx_lock_flag` or wake flags inconsistent.

## Test Signals
Exercise station assoc/deauth events, malformed association event lengths, AP start/active/idle ordering, WMM/HT/VHT capability parsing, BA add/delete/timeout, AMSDU control, ext scan, TX status, PS_SLEEP/PS_AWAKE with NULL packet generation, radar/channel report events, remain-on-channel expiration, and queue cleanup on BSS idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_txrx.c

## Purpose
`uap_txrx.c` implements AP-mode packet receive, intra-BSS forwarding/bridging, and AP TxPD preparation. It validates uAP RX descriptors, forwards multicast/broadcast and intra-BSS unicast frames back into mwifiex TX queues, sends inter-BSS traffic to the kernel, updates per-station statistics, manages a bridged-packet pressure threshold, and invokes 11n reorder for AP clients.

## Important APIs, Types, and Functions
Public APIs are `mwifiex_handle_uap_rx_forward`, `mwifiex_uap_recv_packet`, `mwifiex_process_uap_rx_packet`, and `mwifiex_process_uap_txpd`. Local helpers `mwifiex_uap_del_tx_pkts_in_ralist`, `mwifiex_uap_cleanup_tx_queues`, and `mwifiex_uap_queue_bridged_pkt` delete queued bridged packets fairly and queue firmware-received frames for AP retransmission. Important types are `struct uap_rxpd`, `struct uap_txpd`, `struct rx_packet_hdr`, `struct mwifiex_sta_node`, WMM RA lists, and skb TX control flags.

## Control Flow and Integration
`mwifiex_process_uap_rx_packet` reads uAP RX descriptor type/offset/length, validates embedded Ethernet header and packet bounds, handles management packets via `mwifiex_process_mgmt_packet`, records per-peer RX sequence for non-BAR packets, and either forwards directly or uses `mwifiex_11n_rx_reorder_pkt` when AP 11n reorder state exists. Direct forwarding goes to `mwifiex_handle_uap_rx_forward`.

Forwarding checks media connection and destination address. Multicast packets are copied: the copy is queued back to AP TX for wireless clients and the original is delivered upward. Intra-BSS unicast to an associated station is queued to TX and not delivered to the kernel. Other unicast traffic is converted by `mwifiex_process_rx_packet` and forwarded to the OS.

`mwifiex_uap_queue_bridged_pkt` reconstructs Ethernet II frames from firmware SNAP headers, ensures enough headroom, sets TXCB BSS and `MWIFIEX_BUF_FLAG_BRIDGED_PKT`, updates source station RX stats, accounts unicast bridged traffic as RX, queues into WMM, increments `tx_pending` and `pending_bridged_pkts`, and schedules main work. When bridged packet count reaches the high threshold, cleanup removes bridged packets from RA queues until the low threshold is reached. `mwifiex_process_uap_txpd` mirrors station TxPD building with uAP descriptor layout.

## State and Persistence Behavior
The file mutates `adapter->pending_bridged_pkts`, `adapter->tx_pending`, `priv->wmm_tx_pending`, WMM RA queues/counters, `priv->stats`, peer `stats`, peer `rx_seq`, and `priv->del_list_idx` for fair cleanup. SKB ownership moves between receive, copied bridge SKBs, WMM queues, reorder queues, network stack, or free paths.

## Dependencies and Risks
Dependencies include WMM queueing, 11n aggregation/reorder, shared RX conversion in `sta_rx.c`, shared receive delivery in `util.c`, station-list utilities, and generic TX completion. Risks are SKB ownership with copied multicast frames, bridge packet counter imbalance, descriptor offset trust, cleanup while RA lists are paused, and headroom reallocation failures. The bridged-packet pressure policy intentionally drops queued bridge traffic under load.

## Test Signals
Test AP multicast copy-and-deliver behavior, intra-BSS unicast bridging, inter-BSS routing to kernel, malformed descriptor drops, management RX, 11n reorder/BAR behavior, bridged threshold cleanup, per-station stats, and uAP TxPD layout for data and management frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.c

## Purpose
`usb.c` is the mwifiex USB bus driver. It binds supported Marvell/NXP USB Wi-Fi IDs, discovers endpoints, downloads firmware when needed, allocates and submits RX/TX URBs, demultiplexes command/event/data packets, implements suspend/resume/disconnect/coredump hooks, supports multi-channel USB port resync, provides bus `if_ops`, and optionally aggregates TX data packets for USB efficiency.

## Important APIs, Types, and Functions
Important local functions include `mwifiex_usb_probe`, `mwifiex_usb_suspend`, `mwifiex_usb_resume`, `mwifiex_usb_disconnect`, `mwifiex_usb_recv`, `mwifiex_usb_rx_complete`, `mwifiex_usb_tx_complete`, `mwifiex_usb_submit_rx_urb`, `mwifiex_usb_host_to_card`, TX aggregation helpers, `mwifiex_usb_rx_init`, `mwifiex_usb_tx_init`, `mwifiex_register_dev`, `mwifiex_unregister_dev`, `mwifiex_prog_fw_w_helper`, and `mwifiex_usb_dnld_fw`. The exported integration object is `usb_ops`, a `struct mwifiex_if_ops` installed via `mwifiex_add_card`.

## Control Flow and Integration
Probe allocates `struct usb_card_rec`, determines boot state from PID, scans endpoint descriptors for command/event and data IN/OUT endpoints, validates minimal firmware-download endpoints, stores interface data, and calls `mwifiex_add_card`. Firmware download uses synchronous bulk messages on the command endpoint, sends a winner probe, streams firmware blocks with sequence numbers, retries on transfer/CRC failures, and expects the device to re-enumerate or change boot state before RX/TX init proceeds.

RX URBs complete in `mwifiex_usb_rx_complete`. Successful command/event endpoint packets are passed to `mwifiex_usb_recv`, which strips the interface header, attaches command responses to `adapter->curr_cmd`, stores event cause/body/SKB, or queues data SKBs on `adapter->rx_data_q`. It schedules main work and resubmits command URBs only after command/event completion; data URBs are resubmitted immediately unless `rx_pending` is high.

TX goes through `mwifiex_usb_host_to_card`. Command packets use the single command URB. Data packets select a `usb_tx_data_port`, respect `tx_data_urb_pending`, optionally aggregate packets into an aligned aggregate SKB with MWIFIEX_TYPE_AGGR_DATA_V2 headers and a timer-bound hold window, and submit URBs. TX completion clears command/data sent flags, completes data SKBs, unblocks ports, handles multi-channel resync, and schedules main work.

Suspend waits for firmware load, enables host sleep, sets `MWIFIEX_IS_SUSPENDED`, and kills URBs. Resume clears suspension, resubmits RX URBs, and cancels host sleep asynchronously. Disconnect deauthenticates, sends firmware shutdown when appropriate, and removes the card.

## State and Persistence Behavior
State lives in `usb_card_rec`: endpoint numbers/types, boot state, URB contexts, pending URB atomics, command/data SKBs, multi-channel port state, aggregation queues/timers, and firmware completion. Adapter-level persistent effects include `fw_name`, `tx_buf_size`, `ext_scan`, `usb_mc_status`, `usb_mc_setup`, `data_sent`, `cmd_sent`, event/command flags, `rx_pending`, work flags, and power-save flags.

## Dependencies and Risks
Dependencies include Linux USB core, firmware loader via common mwifiex core, `mwifiex_if_ops`, SKB queue APIs, timers, and power-management helpers in station ioctl/TX. Risks include asynchronous URB lifetime and SKB ownership, endpoint descriptor assumptions for ready devices, aggregation counter/timer races, suspend/disconnect completion ordering, high RX pending leaving data URB contexts without SKBs until resubmission, and firmware-download retry/boot-state ambiguity.

## Test Signals
Test probe on each PID, firmware download and re-enumeration, command/event/data RX demux, high RX pending throttling and `submit_rem_rx_urbs`, data TX with and without aggregation, URB submit failure, port blocking/resync for multi-channel, suspend/resume host sleep, disconnect during in-flight URBs, coredump trigger, and module firmware declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.h

## Purpose
`usb.h` defines the USB bus contract for mwifiex: supported vendor/product IDs, firmware file names, firmware-download protocol structures, endpoint/URB constants, USB card state, URB contexts, and TX aggregation bookkeeping used by `usb.c`.

## Important APIs, Types, and Functions
There are no functions exported here. Key constants include `USB8XXX_VID`, PID pairs for 8766/8797/8801/8997 firmware-download and firmware-ready modes, `USB8XXX_FW_DNLD`, `USB8XXX_FW_READY`, `MWIFIEX_TX_DATA_PORT`, `MWIFIEX_TX_DATA_URB`, `MWIFIEX_RX_DATA_URB`, `MWIFIEX_USB_TIMEOUT`, default firmware names, and firmware block protocol constants such as `FW_DNLD_TX_BUF_SIZE`, `FW_DNLD_RX_BUF_SIZE`, `FW_HAS_LAST_BLOCK`, and `FW_CMD_7`.

Core structures are `struct urb_context` for per-URB adapter/SKB/URB/endpoint state, `struct tx_aggr_tmr_cnxt` and `struct usb_tx_aggr` for timer-bound TX aggregation, `struct usb_tx_data_port` for each USB data OUT port, `struct usb_card_rec` for all USB device state, and packed `struct fw_header`, `struct fw_sync_header`, and `struct fw_data` for firmware download.

## Control Flow and Integration
`usb.c` allocates and fills these structures during probe and init. RX/TX callbacks recover `urb_context` from `urb->context`. Data endpoints use `usb_tx_data_port` to track URB slots, port block status, current ring index, and aggregation lists. Firmware download writes `struct fw_data` blocks and reads `struct fw_sync_header` responses according to constants in this header.

## State and Persistence Behavior
The header models persistent runtime state rather than implementing behavior. `usb_card_rec` persists for the lifetime of the USB interface and owns endpoint descriptors, completion, URB pending atomics, SKB/URB contexts, firmware boot state, multi-channel resync flag, and per-port aggregation state. The packed firmware structs encode host-device wire format and must remain layout-stable.

## Dependencies and Risks
The header depends on Linux USB and completion APIs plus mwifiex core types declared elsewhere. Risks are ABI/layout drift in packed firmware structs, mismatched PID-to-firmware naming, incorrect endpoint count constants causing ring overrun or underutilization, and aggregation timer/lock fields being used without proper initialization in `usb.c`.

## Test Signals
Compile-time signals include structure size/layout, firmware macro use, and successful `usb.c` build. Runtime signals include correct endpoint discovery, firmware file selection for each PID, URB ring allocation counts, aggregation timer initialization, and firmware block protocol interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.c

## Purpose
`util.c` provides shared mwifiex helpers for firmware init/shutdown, debug state collection/formatting, management-frame parsing and cfg80211 delivery, host-MLME disconnect indication, final Ethernet packet delivery, synchronous command completion wakeups, station-list management, TDLS command gating, peer HT capability setup, RX histograms, DMA-aligned RX SKB allocation, and firmware dump event triggering.

## Important APIs, Types, and Functions
Key APIs include `mwifiex_init_shutdown_fw`, `mwifiex_get_debug_info`, `mwifiex_debug_info_to_buffer`, `mwifiex_host_mlme_disconnect`, `mwifiex_process_mgmt_packet`, `mwifiex_recv_packet`, `mwifiex_complete_cmd`, `mwifiex_get_sta_entry`, `mwifiex_is_tdls_chan_switching`, `mwifiex_is_send_cmd_allowed`, `mwifiex_add_sta_entry`, `mwifiex_set_sta_ht_cap`, `mwifiex_del_sta_entry`, `mwifiex_del_all_sta_list`, histogram helpers, `mwifiex_alloc_dma_align_buf`, and `mwifiex_fw_dump_event`. The static `items[]` table maps debug output names to fields in `mwifiex_debug_info` or `mwifiex_adapter`.

## Control Flow and Integration
Debug collection copies adapter/private counters, queue state, BA tables, TDLS peers, power-save flags, command/event history, and transport counters into `mwifiex_debug_info`; formatting iterates the debug descriptor table and appends BA/reorder/TDLS table summaries. Management RX first validates registration and packet length, strips RXPD and firmware packet length, removes address4, handles TDLS discovery response and drops BACK action frames, optionally reports host-MLME auth/deauth/disassoc through cfg80211 under wiphy lock, logs uAP host-MLME events, and finally calls `cfg80211_rx_mgmt`.

`mwifiex_recv_packet` is the final data delivery helper: it updates RX counters, updates AP source station stats, fills netdev/protocol/checksum fields, adjusts `skb->truesize` for large USB/PCIe allocations, and calls `netif_rx`. Station-list helpers add/find/delete nodes under `sta_list_spinlock` where mutation is needed. TDLS gating helpers scan station nodes for `TDLS_CHAN_SWITCHING` or `TDLS_IN_OFF_CHAN` and block commands while peers are off base channel.

## State and Persistence Behavior
State touched includes debug info snapshots, `priv->auth_flag`, `priv->auth_alg`, station list nodes, peer HT flags/max-AMSDU, histogram atomics, packet statistics, AP peer statistics, and adapter command wait queue status. `mwifiex_complete_cmd` sets the command wait condition and wakes waiters; `mwifiex_alloc_dma_align_buf` returns SKBs whose data pointer is aligned for DMA.

## Dependencies and Risks
Dependencies include cfg80211 management APIs, 11n BA/reorder inspection, TDLS list helpers, WMM/debug fields, netdev RX, SKB allocation, and firmware command dispatch. Risks are debug buffer sizing because formatting uses repeated `sprintf`, management frame length/pointer assumptions during address4 removal, station-list traversal callers that rely on external locking, and histogram index ranges derived directly from firmware rate/SNR/NF values.

## Test Signals
Test debugfs/output formatting, command wait wakeups, management frame delivery for host MLME STA/uAP, BACK action drop, TDLS discovery RSSI update, netif RX packet counters, station add/delete/list cleanup, TDLS command blocking while off-channel, histogram reset/add bounds, DMA alignment, and firmware dump command dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.h

## Purpose
`util.h` defines small shared utility types and inline helpers used by mwifiex data paths and diagnostics. Its main role is to structure the `skb->cb` private area so RX/TX metadata and DMA mapping information can be stored consistently across bus and core code.

## Important APIs, Types, and Functions
Key types are `struct mwifiex_dma_mapping`, holding a DMA address and length, `struct mwifiex_cb`, which overlays DMA mapping plus either `struct mwifiex_rxinfo` or `struct mwifiex_txinfo`, and `struct mwifiex_debug_data`, the debug descriptor used by `util.c`. Important inline APIs are `MWIFIEX_SKB_RXCB`, `MWIFIEX_SKB_TXCB`, `mwifiex_store_mapping`, `mwifiex_get_mapping`, `MWIFIEX_SKB_DMA_ADDR`, and `le16_unaligned_add_cpu`. The header also exposes `mwifiex_debug_info_to_buffer`.

## Control Flow and Integration
TX/RX code calls `MWIFIEX_SKB_TXCB` or `MWIFIEX_SKB_RXCB` to interpret `skb->cb` as mwifiex metadata. Bus-specific DMA paths can store mappings with `mwifiex_store_mapping` and later recover only the DMA address with `MWIFIEX_SKB_DMA_ADDR`. `BUILD_BUG_ON` in the RX accessor ensures the combined control block fits in Linux `skb->cb`.

## State and Persistence Behavior
The header does not own persistent state, but its layout controls transient per-SKB state used throughout the driver. Because RX and TX metadata share a union, callers must not expect both to be valid simultaneously. DMA mapping state persists only for the lifetime of the SKB and must match bus unmap/completion ownership.

## Dependencies and Risks
Dependencies include Linux SKB layout, DMA address types, unaligned little-endian helpers, and mwifiex RX/TX info structs declared elsewhere. Risks are control-block size growth, accidental reuse of the union as both RX and TX metadata, stale DMA mapping after SKB cloning/reuse, and assuming natural alignment for little-endian updates where only the helper is safe.

## Test Signals
Build-time failure from `BUILD_BUG_ON` is the primary guard. Runtime signals include correct BSS metadata propagation in `txrx.c`, DMA unmap correctness in bus drivers, no metadata corruption through SKB copies/aggregation, and successful debug formatting through `mwifiex_debug_info_to_buffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/util.h -->
