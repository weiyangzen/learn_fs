# sources/distributed-fs/ceph-client/net/bridge/br_vlan.c

## Purpose
Implements the Linux bridge VLAN database, including bridge-wide and per-port VLAN membership, PVID/untagged flags, VLAN protocol/default-PVID controls, ingress and egress filtering, VLAN stats, bridge-binding VLAN device carrier updates, rtnetlink VLAN add/delete/dump handlers, switchdev/8021q device-filter programming, and integration with multicast, MST, tunnel, FDB, and forwarding path state.

## Important APIs, Types, And Functions
The main state is `struct net_bridge_vlan_group` with an rhashtable and ordered VLAN list, and `struct net_bridge_vlan` entries that can be bridge master VLANs or port VLANs. Key APIs include `br_vlan_add`, `br_vlan_delete`, `br_vlan_flush`, `nbp_vlan_add`, `nbp_vlan_delete`, `nbp_vlan_flush`, `br_allowed_ingress`, `br_allowed_egress`, `br_should_learn`, `br_handle_vlan`, `br_vlan_filter_toggle`, `br_vlan_set_proto`, `br_vlan_set_default_pvid`, `br_vlan_get_pvid*`, `br_vlan_get_info*`, `br_vlan_notify`, `br_vlan_rtnl_init`, and `br_vlan_rtnl_uninit`.

## Control Flow
VLAN add paths allocate or find a VLAN entry, program hardware through switchdev or software 8021q filters, ensure a master VLAN exists for port VLANs, attach stats and multicast contexts, add local FDB entries, publish the entry through rhashtable/list insertion, commit PVID/untagged flags, and notify consumers. Delete/flush paths remove PVID state, hardware filters, FDB entries, tunnel mappings, multicast contexts, list/hash membership, and references before RCU freeing. Ingress validates tags, assigns PVID for untagged or priority-tagged frames, updates VLAN stats, checks per-VLAN STP/MST state, and drops invalid frames. Egress validates membership/state, optionally strips tags, updates stats, and applies VLAN tunnel metadata. Rtnetlink handlers parse `RTM_NEWVLAN`, `RTM_DELVLAN`, and `RTM_GETVLAN`, support ranges, dump compressed ranges, and dispatch option processing.

## State And Persistence Behavior
All state is in kernel memory under RTNL/RCU: VLAN groups, per-VLAN refcounts, PVID state with memory barriers, per-CPU stats, bridge options, multicast contexts, local FDB rows, switchdev attributes, and upper VLAN-device carrier state. There is no disk persistence; durable configuration is expected from userspace replay. RCU freeing protects readers, and RTNL protects mutation.

## Dependencies And Integration Points
Depends on `br_private.h`, `br_private_tunnel.h`, rhashtable, rtnetlink, switchdev, 8021q `vlan_vid_add/del`, bridge FDB, multicast snooping, MST state, netdevice notifiers, and netlink VLAN DB attributes. It exports bridge VLAN query helpers for other modules such as nft bridge meta, and it calls `br_vlan_process_options` / `br_vlan_rtm_process_global_options` from `br_vlan_options.c` plus tunnel helpers from `br_vlan_tunnel.c`.

## Risks And Test Signals
Risk concentrates in rollback after partial switchdev/filter/FDB failures, master VLAN refcount handling, PVID memory ordering, range notification correctness, default PVID changes across many ports, VLAN protocol migration, RCU lifetime, stats sharing versus per-port stats, and tag handling with forwarding offload or QinQ. Good signals are rtnetlink VLAN add/delete/range dumps, bridge selftests for VLAN filtering and default PVID, switchdev fallback tests, multicast/MST option tests, carrier propagation for bridge-bound VLAN devices, and packet tests for untagged, priority-tagged, protocol-mismatched, ingress-drop, and egress-untag paths.
