
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_core.c

Purpose: Core NAT engine for conntrack-backed tuple mapping. It selects unique NAT tuples, stores NAT state in conntrack, maintains a by-source mapping hash, registers per-net NAT hook indirection, supports ctnetlink/BPF/session decode integration, and cleans NAT state on module removal.

Important APIs and functions: `nf_ct_nat_ext_add()`, `nf_nat_setup_info()`, `nf_nat_alloc_null_binding()`, `nf_nat_packet()`, and `nf_nat_inet_fn()` are central exported entry points. Tuple selection is handled by `get_unique_tuple()`, `find_appropriate_src()`, `find_best_ips_proto()`, and `nf_nat_l4proto_unique_tuple()`. Collision handling uses `nf_nat_used_tuple_new()` and `nf_nat_used_tuple_harder()`. Hook registration is via `nf_nat_register_fn()` and `nf_nat_unregister_fn()`.

Control flow: NAT setup is allowed only on unconfirmed conntracks. It inverts the reply tuple into the current forward tuple, selects a unique mapped tuple within the requested range, alters the reply tuple, sets NAT status bits, adds seqadj when helpers need payload-size adjustment, and inserts source mappings into `nf_nat_bysource`. At packet time, `nf_nat_inet_fn()` initializes NAT through registered NAT rule hooks or null binding for new/related flows, then calls `nf_nat_packet()` to apply manipulation. Register functions lazily create per-family hook arrays whose private entries point to user NAT hooks.

State and persistence: Global state includes `nf_nat_bysource`, hash size/random key, per-bucket locks, NAT proto mutex, and RCU `nf_nat_hook`. Per-net state stores NAT hook arrays and users. Conntrack stores NAT extension, reply tuple, status bits, bysource node, and optional seqadj. No durable persistence exists.

Dependencies and integration: Integrates deeply with conntrack core, zones, helper expectations, netfilter hook infrastructure, ctnetlink NAT attribute parsing, xfrm session decode, BPF NAT kfunc registration, and protocol packet manipulation in `nf_nat_proto.c`.

Risks: Major risks are tuple collision races, source-map hash lifetime, offloaded/time-wait connection eviction, NAT setup after confirmation, hook indirection RCU lifetime, null-binding cleanup on module unload, range randomization/offset correctness, and sequence-adjust extension allocation. Test signals include high-concurrency tuple allocation, port range exhaustion, persistent/random/offset ranges, zones, helper seqadj, ctnetlink-created NAT, unregister while hooks are active, module unload cleanup, and xfrm decode after NAT.
