<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_cfm.c

Purpose: implements bridge Connectivity Fault Management (CFM) MEP and peer-MEP state, Continuity Check Message (CCM) transmit/receive processing, defect detection timers, and CFM frame interception for the bridge.

Important APIs, types, and functions: MEP lookup helpers `br_mep_find`, `br_mep_find_ifindex`, `br_peer_mep_find`, and `br_mep_get_port` drive object resolution. Public configuration APIs include `br_cfm_mep_create`, `br_cfm_mep_delete`, `br_cfm_mep_config_set`, `br_cfm_cc_config_set`, `br_cfm_cc_peer_mep_add`, `br_cfm_cc_peer_mep_remove`, `br_cfm_cc_rdi_set`, `br_cfm_cc_ccm_tx`, `br_cfm_mep_count`, `br_cfm_peer_mep_count`, `br_cfm_created`, and `br_cfm_port_del`. Runtime frame/timer helpers include `ccm_frame_build`, `ccm_tx_work_expired`, `ccm_rx_work_expired`, `ccm_tlv_extract`, and `br_cfm_frame_rx`.

Control flow: creating the first MEP registers an `ETH_P_CFM` bridge frame handler; deleting the last removes it. MEP creation validates port-domain/down-MEP constraints and enforces one port MEP per port. CC configuration enables or disables peer timers and resets sequence counters. Peer MEP add starts receive defect monitoring if CC is enabled. RX handling consumes CFM frames at or below the local MD level, validates version, opcode, MAID, peer MEP ID, and interval, updates peer status flags and sequence tracking, clears defects on valid reception, parses up to four TLVs, and notifies netlink listeners on defect changes. TX scheduling builds CCM frames with sequence number, local MEP ID, MAID, optional port/interface TLVs, and sends them until a configured period expires.

State and persistence: CFM state lives under `br->mep_list` as RCU hlist entries. Each MEP stores creation/configuration, RDI, CC config, TX info, status flags, sequence numbers, a port RCU pointer, peer list, and delayed TX work. Each peer stores status, miss count, and delayed RX work. State persists until netlink deletion, port deletion, or bridge teardown.

Dependencies and integration points: depends on `br_private_cfm.h`, UAPI CFM bridge attributes, bridge frame-type registration, RCU, RTNL, delayed work on `system_percpu_wq`, netlink notifications through `br_info_notify`, and bridge port lifecycle.

Risks: delayed work and RCU deletion must be synchronized to avoid use-after-free. The 3.25 interval defect logic depends on timer cadence and jiffies conversion. Sequence numbers are tracked per MEP, not per peer, which is important for interpreting multiple peer behavior. Partial TLV parsing intentionally handles status TLVs only. CFM frame consumption rules can affect forwarding at different maintenance-domain levels.

Test signals: bridge CFM netlink create/config/delete tests, peer add/remove, CCM TX period start/stop/update, RX of valid CCMs, wrong MAID/interval/opcode/version/MD level, TLV extraction, defect notification after missed intervals, port deletion cleanup, and RCU/workqueue debug testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm.c -->
