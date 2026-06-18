# sources/distributed-fs/ceph-client/include/net/flow_offload.h

Purpose: defines the kernel traffic-control flow offload contract between classifiers/actions and hardware or indirect offload drivers. It wraps dissector keys as mask/key pairs, enumerates action ids, models action entries, flow rules, stats, flow blocks, block callbacks, classifier commands, and standalone offloaded actions.

Important APIs/types: `struct flow_match_*` pairs map directly onto flow dissector key structs. `flow_rule_match_*()` functions extract typed match views. `enum flow_action_id` covers accept/drop/trap/goto, redirect/mirred ingress/egress, VLAN/MPLS/PPPoE edits, tunnel encap/decap, mangle/add/csum/mark/ptype/priority/queue/sample/police/conntrack/gate/jump/pipe/continue. `struct flow_action_entry` stores action-specific union data, cookies, stats preference, destructor hooks, and user cookies. `flow_rule_alloc()` and `offload_action_alloc()` allocate flexible-array rules/actions.

Control flow and state: offload setup builds a `flow_rule` from match and action arrays, checks driver support, then binds callbacks into `struct flow_block`. Inline checks reject mixed hardware-stat modes, unsupported control flags, and unsupported encapsulation flags with netlink extended ACKs. `flow_stats_update()` accumulates packets, bytes, drops, max last-used time, and used hardware-stat mode.

Dependencies and integration: depends on lists, netlink, flow dissector, net devices, qdiscs, tc setup types, tunnel info, conntrack flowtables, psample, and action-gate entries. It is the bridge between tc flower/action code and NIC driver callbacks, including indirect device registration.

Risks: flexible-array sizing, action union interpretation, refcounted block callbacks, and list movement are high-risk. Drivers must not accept unsupported masks silently. Tests should exercise every action id translation, mixed hardware stats rejection, block bind/unbind lifetimes, callback refcounts, indirect offload registration, and extack messages for unsupported control flags.
