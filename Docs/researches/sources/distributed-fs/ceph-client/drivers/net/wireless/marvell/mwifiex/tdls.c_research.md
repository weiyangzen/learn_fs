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
