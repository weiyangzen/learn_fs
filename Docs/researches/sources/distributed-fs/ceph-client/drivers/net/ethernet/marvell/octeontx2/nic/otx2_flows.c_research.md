# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_flows.c

`otx2_flows.c` owns NPC MCAM flow management for unicast filters, ntuple ethtool rules, VF VLAN flows, RX VLAN offload, TC shared state, RSS-context cleanup, and CGX/RPM DMAC filter integration. It translates ethtool flow specs into `npc_install_flow_req` mailbox requests and keeps driver rule lists synchronized with hardware entries.

Initialization and teardown APIs are `otx2_mcam_flow_init`, `otx2vf_mcam_flow_init`, `otx2_mcam_entry_init`, `otx2_alloc_mcam_entries`, `otx2_mcam_flow_del`, `otx2_destroy_ntuple_flows`, and `otx2_destroy_mcam_flows`. Rule APIs are `otx2_add_flow`, `otx2_remove_flow`, `otx2_get_flow`, `otx2_get_all_flows`, and `otx2_get_maxflows`. MAC/VLAN helpers include `otx2_add_macfilter`, `otx2_del_macfilter`, `otx2_enable_rxvlan`, and DMAC reinstall/update helpers.

Probe allocates `flow_cfg`, lists, bitmaps, default MCAM entries for unicast/VLAN/VF VLAN, checks field support, then allocates ntuple entries. EtHTool add requests validate queue and location, allocate or update an `otx2_flow`, classify DMAC-filter-only rules, program either CGX/RPM DMAC or NPC MCAM, and insert the rule in sorted order. Removal reverses the hardware path and deletes the list node.

State includes `flow_ent`, `def_ent`, offsets, `dmacflt_bmap`, `bmap_to_dmacindex`, active `flow_list`, TC flow list, max counts, and counters; `mac_table` tracks unicast filters. Dependencies include AF/NPC mailbox messages, ethtool RXNFC structures, IPv6 helpers, DCB BPID updates, RSS contexts, devlink MCAM settings, and VF VLAN setup.

Risks include short MCAM allocations, the DMAC rule location offset after `max_flows`, list mutation serialization assumptions, profile-dependent VLAN/AH/ESP support, and correct reversal of PFC BPID changes. Test Ethernet/IPv4/IPv6/TCP/UDP/SCTP/drop/queue/VF/RSS/VLAN rules, unsupported masks, unicast sync, devlink count changes, RX VLAN offload, DMAC table full cases, reopen reinstall, and destroy paths.
