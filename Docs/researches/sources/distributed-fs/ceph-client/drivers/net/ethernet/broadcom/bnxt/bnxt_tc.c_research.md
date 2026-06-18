# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_tc.c

## Purpose
Implements flower classifier hardware offload for bnxt. It parses TC flower matches/actions into bnxt flow objects, validates hardware-supported patterns, allocates/free firmware CFA flows, shares L2 and tunnel handles across compatible flows, supports VXLAN indirect offload, and periodically collects hardware flow statistics.

## Important APIs, Types, And Functions
The public driver hooks are `bnxt_tc_setup_flower()`, `bnxt_init_tc()`, `bnxt_shutdown_tc()`, and `bnxt_tc_flow_stats_work()`. Parsing is split across `bnxt_tc_parse_flow()`, `bnxt_tc_parse_actions()`, and action helpers for redirect, VLAN, tunnel encap/decap, pedit L2 rewrite, and NAT/NAPT. Firmware allocation is handled by `bnxt_hwrm_cfa_flow_alloc()` and `bnxt_hwrm_cfa_flow_free()`, with tunnel-specific helpers for decap filters and encap records. Sharing is managed through rhashtables for flows, L2 keys, decap L2 keys, decap tunnels, and encap tunnels.

## Control Flow
`bnxt_tc_setup_flower()` dispatches replace, destroy, and stats commands. On replace, `bnxt_tc_add_flow()` allocates a `bnxt_tc_flow_node`, parses the flow rule, assigns source FID and direction, validates offloadability, deletes any prior flow with the same cookie, acquires the TC lock, obtains a reference L2 flow handle, resolves or allocates a tunnel handle if required, allocates the firmware CFA flow, initializes stats state, and inserts the node into the flow table. Error unwinding releases handles in reverse order.

On destroy, `bnxt_tc_del_flow()` looks up the cookie and `__bnxt_tc_del_flow()` frees the firmware flow, releases tunnel and L2 references under the TC lock, removes the node from the flow table, and frees it with RCU. On stats, `bnxt_tc_get_flow_stats()` returns deltas accumulated by the periodic worker. The worker walks the flow rhashtable in batches, sends `HWRM_CFA_FLOW_STATS`, handles hardware counter wraparound, and updates `lastused`.

Indirect VXLAN offload registers `bnxt_tc_setup_indr_cb()` in `bnxt_init_tc()`. Binding allocates a callback-private object per tunnel netdev and routes flower callbacks back into `bnxt_tc_setup_flower()` using the PF FID.

## State And Persistence Behavior
`bp->tc_info` owns all TC offload state for the lifetime of feature enablement. Persistent in-memory objects include the flow rhashtable keyed by TC cookie, shared L2 nodes keyed by the first 16 bytes of `bnxt_tc_l2_key`, shared decap/encap tunnel nodes keyed by `struct ip_tunnel_key`, per-flow firmware handles, accumulated stats, and an indirect-block callback list. Firmware state persists until explicit free commands or driver shutdown. There is no disk persistence.

## Dependencies And Integration Points
The file integrates with Linux TC flower, `flow_rule` dissectors, `flow_action`, rhashtable, RCU freeing, neighbor/route lookup for VXLAN tunnel header resolution, VXLAN indirect devices, and bnxt HWRM CFA commands. It depends on VF representor helpers to identify representor devices and convert them to VF FIDs, and on `netdev_port_same_parent_id()` to keep redirects inside the same switch.

## Risks
Offload correctness depends on strict match/action validation. Partial MAC/VLAN wildcards, non-TCP/UDP port matches, missing ethertype masks, IPv6 tunnel keys, and unsupported pedit combinations must be rejected. Shared L2/tunnel reference management is subtle; failure paths must not leak firmware handles or leave list entries attached. Route/neighbor resolution for encap can become stale after neighbor, VLAN, or route changes. Counter wrap handling assumes firmware-programmed widths of 36 bytes bits and 28 packet bits. Concurrency spans TC callbacks, stats walks, RCU frees, and driver shutdown.

## Test Signals
Key tests are flower add/delete/replace by cookie, unsupported-pattern rejection, PF-to-VF and VF-rep-to-PF redirects, drop, VLAN push/pop, L2 rewrite, IPv4/IPv6 NAT/NAPT, VXLAN encap/decap with indirect block bind/unbind, shared L2/tunnel reference reuse, stats deltas and wraparound, firmware allocation failure unwinding, shutdown with active flows, and switchdev flows sourced from VF representors.
