<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_input.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_input.c

Purpose: implements ingress processing for bridge ports. It is the bridge RX handler, validates incoming frames, handles reserved link-local MACs, invokes bridge netfilter pre-routing/local-in hooks, applies VLAN ingress policy, learns source MACs, enforces locked-port/MAB policy, integrates multicast snooping and neighbour suppression, performs FDB lookup, forwards/floods frames, and passes frames up to the bridge netdevice when local delivery is needed.

Important APIs, types, and functions:

- `br_get_rx_handler()` returns either `br_handle_frame()` or a DSA dummy handler.
- `br_handle_frame()` is installed as the lower device RX handler and decides whether the bridge consumes or passes an skb.
- `br_handle_frame_finish()` is the main post-netfilter ingress bridge pipeline and is exported.
- `br_pass_frame_up()` delivers an skb to the bridge device through `NF_BR_LOCAL_IN` and `netif_receive_skb()`.
- `nf_hook_bridge_pre()` runs `NF_BR_PRE_ROUTING`, including manual queue handling when bridge netfilter is enabled.
- `br_add_frame()` and `br_del_frame()` maintain a bridge-private list of protocol frame handlers, used by MRP.

Core control flow:

- `br_handle_frame()` ignores loopback skbs, drops invalid source MAC addresses, obtains a writable shared skb, clears the bridge skb control block, handles VLAN tunnel metadata, and checks reserved link-local destinations. STP and LLDP addresses are passed locally or selectively forwarded based on group forward masks; pause frames are dropped.
- Before normal forwarding, registered bridge frame-type handlers are consulted. If an MRP handler consumes an ETH_P_MRP frame, bridge normal forwarding is bypassed.
- For regular frames, non-MST ports must be in forwarding or learning state before entering `nf_hook_bridge_pre()`. With MST enabled, state filtering is deferred to VLAN ingress logic because state is per-MSTI/VLAN.
- `nf_hook_bridge_pre()` either runs bridge pre-routing hooks, handles `br_netfilter_broute` pass-through, queue/drop/stolen verdicts, or directly calls `br_handle_frame_finish()`.
- `br_handle_frame_finish()` obtains the bridge port, selects effective STP state, calls `br_allowed_ingress()` to validate VLAN and update VID/state/vlan output, enforces locked-port and MAB behavior, marks switchdev source information, learns the source with `br_fdb_update()` when enabled, classifies destination as unicast/multicast/broadcast, handles IGMP/MLD receive logic, and drops learning-state frames after learning.
- For unicast, it looks up the destination FDB entry by `(dest, vid)` with an optional fallback to VLAN 0 local entries. Local entries go to `br_pass_frame_up()`, non-local known entries go to `br_forward()`, and unknown entries flood.
- For multicast, it obtains the MDB entry, decides whether local receive is required based on host joins, router status, querier state, and all-multicast flags, then uses `br_multicast_flood()` when there is a hit or `br_flood()` otherwise. Broadcast always forces local receive.
- If `local_rcv` is true after forwarding/flooding, the original skb is delivered up through the bridge device.

State and persistence behavior:

- Persistent bridge state is updated through FDB learning (`updated`, `dst`, flags), locked MAB entries, multicast snooping state, neighbour suppression side effects, and per-packet statistics. This file itself owns transient skb control fields such as `brdev`, `promisc`, `src_port_isolated`, `proxyarp_replied`, and bridge netfilter broute state.
- Port state, VLAN state, bridge options, FDB entries, MDB entries, and multicast router state are consumed under RCU. Packet ownership transfers to forwarding, flooding, netfilter, or local receive paths.
- Local delivery resets switchdev offload marks before stacking another bridge above this one, avoiding offload-state leakage.

Dependencies and integration points:

- Depends on `br_fdb.c` for learning and destination lookup, `br_forward.c` for egress, VLAN helpers for ingress/egress policy, multicast snooping for IGMP/MLD/MDB decisions, neighbour suppression/proxy ARP, bridge netfilter, DSA, switchdev, and MRP frame-type registration.
- `br_if.c` installs this handler and uses the dummy handler for DSA ports so hardware bridging can coexist with packet-type handlers.
- Netfilter integration spans `NF_BR_PRE_ROUTING` and `NF_BR_LOCAL_IN`; bridge netfilter can reroute frames away from bridge forwarding through broute.

Risks and edge cases:

- Ingress ordering is security-sensitive. Source learning happens only after VLAN filtering and locked-port checks to reduce spoofing. Moving learning earlier could poison the FDB.
- Locked ports combine FDB lookup, locked flag refresh, MAB entry creation, and no-roaming behavior. Incorrect handling can bypass authentication or break legitimate authorization refresh.
- MST defers STP filtering until VLAN ingress state is known; applying classic port state too early would break per-MSTI forwarding.
- skb ownership across netfilter verdicts, forwarding, flooding, and local receive is easy to get wrong, especially with broute or queued packets.
- Reserved link-local MAC handling must preserve standards behavior for STP, pause, LLDP, and selectively forwarded group addresses.

Test signals:

- Test invalid source MAC drops, link-local reserved MAC behavior, STP state filtering, and MST per-VLAN state filtering.
- Exercise VLAN ingress failures, FDB learning, known unicast, unknown unicast flood, local MAC delivery, broadcast local receive, and promiscuous bridge receive.
- Validate locked-port and MAB behavior: miss creates locked entry, mismatch drops, locked match refreshes and drops, authorized entry forwards.
- Test bridge netfilter accept/drop/queue/broute decisions and local-in delivery.
- Verify multicast receive with IGMP/MLD, MDB hits, host joins, router ports, all-multicast, and no-querier cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_input.c -->
