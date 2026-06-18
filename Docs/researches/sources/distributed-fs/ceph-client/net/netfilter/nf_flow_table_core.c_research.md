
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_core.c

Purpose: Implements the core `nf_flowtable` lifecycle and software flow cache for nftables flow offload. It allocates `struct flow_offload` objects from conntrack tuples, inserts both directions into an rhashtable, refreshes offload timeouts, reconciles conntrack state on teardown, drives garbage collection, and coordinates optional hardware offload.

Important APIs and functions: `flow_offload_alloc()` captures original/reply tuples and NAT flags from an `nf_conn`; `flow_offload_route_init()` copies route/device/encapsulation metadata from `struct nf_flow_route`; `flow_offload_add()`, `flow_offload_lookup()`, `flow_offload_refresh()`, `flow_offload_teardown()`, and `flow_offload_free()` are the main exported software-cache operations. `nf_flow_table_init()`, `nf_flow_table_free()`, `nf_flow_table_cleanup()`, and `nf_flow_table_gc_run()` own table setup, teardown, device cleanup, and GC. `nf_flow_snat_port()` and `nf_flow_dnat_port()` are shared packet-path NAT port mutators.

Control flow: module init creates the flow slab, registers per-net state/procfs, initializes offload workqueues, and registers BPF flow helpers. A flow is allocated from conntrack, route-filled, inserted twice in the rhashtable, and optionally queued for hardware offload. The delayed GC work iterates only original-direction entries, extends conntrack timeouts for active flows, tears down expired/dying/custom-GC flows, requests hardware delete/stats updates, and finally removes software entries once hardware state is dead.

State and persistence: State is in `flowtables`, each `nf_flowtable` rhashtable, per-flow flags (`NF_FLOW_SNAT`, `NF_FLOW_DNAT`, `NF_FLOW_HW`, `NF_FLOW_CLOSING`, teardown bits), route dst references, and per-net percpu stats. There is no durable persistence; all state is kernel memory tied to module/per-net/table lifetime.

Dependencies and integration: Depends on conntrack tuple/status/timeouts, nftables flowtable types, `rhashtable`, `dst_entry` routing, per-net procfs, and the offload/BPF support implemented by sibling files. Device cleanup is called by netdevice events through exported `nf_flow_table_cleanup()`.

Risks: The high-risk areas are RCU/rhashtable lifetime, dual tuple insertion rollback, dst reference ownership, conntrack timeout reconciliation after bypassing normal conntrack, hardware-offload pending/dead flag ordering, and TCP close/reopen state fixup. Tests should stress bidirectional lookup, NATed TCP/UDP flow expiry, device removal, module unload with pending offload work, and offload stats refresh.
