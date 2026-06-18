
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_offload.c

Purpose: Converts software flowtable entries into TC flower hardware-offload rules and manages asynchronous add, delete, and stats workqueues for offloaded flows.

Important APIs and functions: `nf_flow_rule_route_ipv4()` and `nf_flow_rule_route_ipv6()` build action lists for L2 rewrite, VLAN/PPPoE/tunnel actions, NAT mangles, checksum updates, and redirect. `nf_flow_offload_add()`, `nf_flow_offload_del()`, and `nf_flow_offload_stats()` queue work. `nf_flow_table_offload_setup()` binds or unbinds a flowtable to a netdevice or indirect offload provider. `nf_flow_table_offload_init()` and `_exit()` manage the three workqueues.

Control flow: Rule allocation builds a dissector/match from the flow tuple, including ingress ifindex, VLAN keys, IPv4/IPv6 addresses, L4 protocol, TCP FIN/RST mask, ports, and optional lwt tunnel keys. Route-action builders append decap/encap, Ethernet source/destination mangles, VLAN/PPPoE actions, IP/port NAT mangles, checksum actions for IPv4 NAT, and redirect. Work handlers call driver block callbacks with `FLOW_CLS_REPLACE`, `FLOW_CLS_DESTROY`, or `FLOW_CLS_STATS`, then update conntrack `IPS_HW_OFFLOAD_BIT`, flow timeout, accounting, and flow hardware lifecycle flags.

State and persistence: Persistent state is workqueue pointers, `flowtable->flow_block`, block callback lists protected by `flow_block_lock`, per-flow hardware flags, and transient `struct flow_offload_work`. There is no durable persistence.

Dependencies and integration: Integrates with TC flower (`TC_SETUP_CLSFLOWER`, `TC_SETUP_FT`), netdevice `ndo_setup_tc`, indirect flow block offload, lwtunnel metadata, conntrack accounting, and the core GC state machine. If software hardware offload is disabled, setup falls back to XDP mapping.

Risks: Hardware rule parity with software forwarding is subtle. Risks include action array overflow (`NF_FLOW_RULE_ACTION_MAX`), leaking dev references held by redirect actions, stale neighbour MACs, bidirectional flag differences, races around `NF_FLOW_HW_PENDING`, stats double-accounting, and cleanup of indirect block callbacks. Tests should bind/unbind devices, exercise driver failure paths, compare software and hardware NAT/VLAN/tunnel behavior, and unload with pending add/delete/stats work.
