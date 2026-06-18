# sources/distributed-fs/ceph-client/include/net/netfilter/nf_flow_table.h

Purpose: Defines the kernel-side flowtable offload model used by netfilter/nftables to accelerate established conntrack flows in software, hardware, XDP, TC, and route-direct transmit paths.

Important APIs/types/functions: `struct nf_flowtable`, `nf_flowtable_type`, `flow_offload`, `flow_offload_tuple`, `nf_flow_route`, and `nf_flow_rule` are the core data carriers. Exported operations include `flow_offload_alloc/free`, `flow_offload_add/refresh/lookup`, `nf_flow_table_init/free`, GC cleanup helpers, NAT port rewrite helpers, IPv4/IPv6 hook functions, offload add/del/stats/flush/setup, route rule builders, and optional BPF registration. Inline callback management uses `flow_block_cb_lookup/alloc/free` under `flow_block_lock`.

Control flow: conntrack creates a `flow_offload`; routing fills bidirectional `nf_flow_route`; the flow is added to the rhashtable; packet hooks look up tuples and transmit through neighbor, direct, XFRM, TC, or offload paths; GC tears down stale, closing, or device-removed flows. Hardware callbacks are registered per device and retain flowtable references through type `get/put`.

State and persistence: State is in rhashtable tuples, conntrack references, timeout jiffies, flow flags, per-net flow table stats, delayed GC work, flow block callbacks, and optional hardware state bits. It is runtime only and must be cleaned on device teardown and namespace exit.

Dependencies/integration: Depends on conntrack tuple directions, `flow_offload.h`, dst cache, PPPoE parsing, rhashtable, netdevice lifecycle, nftables flowtables, BPF/BTF, procfs stats, and flow block offload callbacks.

Risks/test signals: Validate tuple hash-key boundaries around `__hash`, bidirectional NAT flags, PPPoE `pskb_may_pull`, stale dst cookies, refcount symmetry in offload callbacks, device unregister cleanup, GC races, and hardware offload failure fallback. Tests should exercise IPv4/IPv6 flowtable rules, NAT offload, device removal, module unload, proc stats, and offload callback duplicate registration.
