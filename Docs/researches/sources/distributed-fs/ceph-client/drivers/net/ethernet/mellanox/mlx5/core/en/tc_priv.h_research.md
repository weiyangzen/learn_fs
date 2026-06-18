# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_priv.h

Purpose: provides private TC offload structures and helper declarations shared by mlx5 Ethernet TC implementation files. For this subset it is the central contract tying conntrack, tunnel encap/decap, hairpin, slow path, post actions, and flow flags together.

Important APIs and types: `enum MLX5E_TC_FLOW_FLAG_*` extends exported TC flags with driver-private lifecycle flags such as `OFFLOADED`, `SLOW`, `NOT_READY`, `DELETED`, `TUN_RX`, and `FAILED`. `struct mlx5e_tc_flow_parse_attr` carries parsed tunnel info per destination, MPLS info, filter device, flow spec, pedit state, modify-header actions, mirred ifindexes, and action parse state. `struct mlx5e_tc_flow` is the private flow object with hardware rule handles, encap/decap attachments, route attachments, hairpin/peer lists, original device, temporary list node, refcount, completions, attributes, and chain mapping. It also declares rule offload/unoffload, post-action, slow-path, namespace, counter, internal-port, flow-meter, and match-header helper APIs.

Control flow: parser code fills `parse_attr`; action-specific files attach encap, decap, CT, hairpin, or post-action resources to `mlx5e_tc_flow`; offload functions install the hardware rules and set flags; delete paths detach resources and use completions/refcounts to serialize teardown. The inline flag helpers wrap bit operations with memory barriers so data fields are visible before flags are observed by concurrent paths.

State and persistence: runtime state lives in `mlx5e_tc_flow` objects and their linked resources. The temporary flow list and `tmp_entry_index` are intentionally reused during neighbor and route updates. `init_done` and `del_hw_done` completions are important persistence points for concurrent update workers.

Dependencies and integration points: depends on public `en_tc.h`, action parser state, mlx5 flow specs and attrs, eswitch flow attributes, tunnel encap entries, route entries, decap entries, hairpin entries, counters, internal ports, and flow meters. Many files in this subset depend on this header to avoid exposing these internals publicly.

Risks and test signals: incorrect flag ordering or list ownership can cause use-after-free or stale hardware rules. Tunnel updates rely on array-indexed `encaps` and `encap_routes` matching destination indexes. Test signals include KCSAN/KASAN under concurrent TC add/delete and route/neigh updates, multi-destination encap, slow-path transition tests, and compile coverage for optional features.
