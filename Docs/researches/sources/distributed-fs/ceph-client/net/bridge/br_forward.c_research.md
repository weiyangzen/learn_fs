<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_forward.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_forward.c

Purpose: implements bridge egress forwarding and flooding. It decides whether a frame can be delivered to a port, applies egress VLAN handling, invokes bridge netfilter hooks, queues packets to lower devices, handles clone-on-flood semantics, and contains multicast-specific replication support when IGMP snooping is enabled.

Important APIs, types, and functions:

- `br_forward()` forwards one skb to a selected bridge port, optionally cloning when the original must also be delivered locally.
- `br_flood()` floods unknown unicast, multicast, or broadcast traffic to eligible ports.
- `br_multicast_flood()` performs MDB/router-port aware multicast replication under `CONFIG_BRIDGE_IGMP_SNOOPING`.
- `br_forward_finish()` and `br_dev_queue_push_xmit()` are netfilter continuation/output helpers and are exported for bridge users.
- `should_deliver()` is the central egress eligibility test. It checks hairpin mode, origin port, STP/MST state, VLAN egress permission, switchdev egress permission, and isolated-port rules.
- `maybe_deliver()` and `deliver_clone()` implement the "clone all but the final skb" flooding pattern.

Core control flow:

- `br_forward()` first handles backup-port redirection: if the destination port has a configured backup and the primary link is not running or has no carrier, it redirects to the backup and records `backup_nhid` in the bridge skb control block. It then runs `should_deliver()`. If local receive is also needed, it clones and forwards the clone; otherwise it consumes the original skb. If delivery is rejected and no local receive is pending, it frees the skb.
- `__br_forward()` marks switchdev forwarding offload before VLAN handling so `br_handle_vlan()` can decide whether to pop or keep VLAN headers. It changes `skb->dev` to the egress device and selects `NF_BR_FORWARD` for transit frames or `NF_BR_LOCAL_OUT` for locally originated frames. Transit frames reject LRO skbs and fix checksums; local netpoll frames bypass normal qdisc transmit through `br_netpoll_send_skb()`.
- `br_forward_finish()` clears skb timestamps and invokes `NF_BR_POST_ROUTING`; `br_dev_queue_push_xmit()` restores the Ethernet header, rejects non-forwardable frames, drops fake routes, fixes partial checksum VLAN network header positioning, sets switchdev offload forwarding marks, and calls `dev_queue_xmit()`.
- `br_flood()` iterates the bridge port list under RCU. It skips ports according to per-port flood flags (`BR_FLOOD`, `BR_MCAST_FLOOD`, `BR_BCAST_FLOOD`), proxy ARP/neighbour suppression, and the shared delivery rules. It clones to the previous selected port and saves the current port for final zero-copy delivery.
- `br_multicast_flood()` merges MDB port groups and multicast router ports, handles multicast-to-unicast replication by copying the skb and rewriting destination MACs, respects include/block flags for source-specific multicast, and again sends only the final copy without cloning.

State and persistence behavior:

- This file keeps almost no persistent state itself. It consumes bridge, port, VLAN, multicast, and skb control-block state maintained elsewhere.
- It mutates transient skb fields: Ethernet header position, `skb->dev`, checksum metadata, network header for VLAN partial checksum, switchdev offload marks, traffic-control miss indication, multicast statistics, and bridge private skb control fields.
- Drop accounting uses device statistics and skb drop reasons such as no transmit target or no memory. Multicast TX accounting is updated through `br_multicast_count()`.

Dependencies and integration points:

- Egress VLAN policy comes from `br_handle_vlan()`, `br_allowed_egress()`, and VLAN groups.
- Netfilter integration uses `NF_HOOK()` for `NF_BR_FORWARD`, `NF_BR_LOCAL_OUT`, and `NF_BR_POST_ROUTING`.
- Switchdev integration uses egress permission checks and offload forwarding marks to keep hardware and software forwarding behavior aligned.
- `br_input.c` calls `br_forward()`, `br_flood()`, and `br_multicast_flood()` after ingress learning and destination lookup.
- Netpoll, multicast snooping, proxy ARP, neighbour suppression, MST/STP state, isolated ports, backup ports, and qdisc transmit are all part of the egress decision surface.

Risks and edge cases:

- Ownership of the skb is subtle. Flooding intentionally clones only earlier deliveries and gives the original skb to the final egress or local receive path. Any new branch must preserve that ownership model.
- `should_deliver()` combines multiple policy systems. A change in ordering can affect VLAN filtering, MST forwarding, hardware offload domains, hairpin forwarding, or isolated port behavior.
- Backup-port redirection depends on RCU pointers and link state checks. It records backup nexthop state in the skb control block for later consumers.
- Multicast-to-unicast replication temporarily pushes and pulls the Ethernet header around `pskb_copy()`. Header offset mistakes would corrupt outgoing frames.
- Partial checksum VLAN handling relies on correct VLAN protocol/depth parsing before transmit.

Test signals:

- Forward known unicast, unknown unicast flood, broadcast, and multicast traffic across ports with combinations of hairpin, isolated, flood flags, VLAN filtering, and MST/STP state.
- Validate backup-port redirection by dropping carrier on a primary port and checking egress and `backup_nhid` behavior.
- Exercise netfilter bridge hooks at forward, local-out, and post-routing points.
- With IGMP snooping, test MDB-only multicast, router-port replication, multicast-to-unicast, source include/exclude, and blocked MDB port groups.
- Monitor skb drop reasons, `tx_dropped`, multicast counters, and switchdev offload marks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_forward.c -->
