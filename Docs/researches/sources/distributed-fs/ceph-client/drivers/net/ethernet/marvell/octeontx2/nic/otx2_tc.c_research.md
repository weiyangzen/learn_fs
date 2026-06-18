# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_tc.c

## Purpose
`otx2_tc.c` implements TC offload for the RVU NIC: clsact flower ingress rules, matchall ingress/egress policing, MCAM rule management, redirect/mirror actions, skb mark support, and HTB handoff. It converts Linux TC flow rules into NPC MCAM and NIX scheduler/policer mailbox requests.

## Important APIs, Types, and Functions
Exports include `otx2_setup_tc()`, `otx2_setup_tc_cls_flower()`, `otx2_init_tc()`, `otx2_shutdown_tc()`, `otx2_tc_apply_ingress_police_rules()`, `otx2_add_mcam_flow_entry()`, `otx2_del_mcam_flow_entry()`, and `otx2_tc_add_to_flow_list()`. Core helpers are `otx2_tc_prepare_flow()`, `otx2_tc_parse_actions()`, `otx2_tc_add_flow()`, `otx2_tc_del_flow()`, `otx2_tc_get_flow_stats()`, and rate helpers such as `otx2_get_txschq_rate_regval()`.

## Control Flow
`otx2_setup_tc()` dispatches `TC_SETUP_BLOCK` to ingress/egress clsact callbacks and `TC_SETUP_QDISC_HTB` to QoS. Flower replace allocates an `otx2_tc_flow`, validates supported dissector keys, fills an `npc_install_flow_req`, parses actions, assigns/reorders an MCAM entry by priority, and syncs it through the AF mailbox. Destroy reverses MCAM programming, CN10K policer mapping, multicast group allocation, and list membership. Stats read MCAM counters and update TC stats deltas. Matchall installs program scheduler rate or CN10K ingress policers directly.

## State and Persistence
Software state lives in `flow_cfg->flow_list_tc`, `flow_cfg->nr_flows`, `flow_cfg->mark_flows`, `nic->rq_bmap`, TC flags, and per-flow cached request/stats. Hardware state persists in NPC MCAM entries, MCAM counters, NIX multicast groups, CN10K leaf bandwidth profiles, and scheduler PIR registers until deleted or interface reset.

## Dependencies and Integration Points
The file depends on Linux flow dissector, `pkt_cls`, TC action APIs, AF mailbox alloc/sync helpers, CN10K policer helpers, representor metadata, QoS APIs, and netdev feature gating. Representor TC paths temporarily bind master `otx2_nic` fields to a representor's `flow_cfg` and `pcifunc`.

## Risks and Edge Cases
Only specific dissector keys and actions are supported; unsupported masks must fail cleanly. MCAM priority reordering deletes/reinstalls entries and must preserve counters. Ingress policing is CN10K-only and consumes RQs, with RQ 0 reserved. The mark-flow refcount clearing logic is sensitive because TC mark enablement affects RX skb marks. Multicast mirror group cleanup must run on all delete/error paths. Interface-down cases intentionally defer some ingress policer reprogramming.

## Test Signals
Exercise flower add/delete/stats for DMAC, VLAN/CVLAN, IPv4/IPv6, ports, TCP flags, MPLS, ICMP, IPsec SPI, mark, redirect, queue mapping, mirror, drop, and accept. Test matchall police on ingress/egress, unsupported key/action errors with extack text, MCAM exhaustion, rule priority ordering, interface down/up with stored ingress policers, CN10K vs OTX2 platform gating, and representor TC rules.
