# Research: subset-b-004561

This grouped report covers mlxsw Spectrum classifier, tunnel, multicast routing, resource allocation, policing, port-range, and PTP support files. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flower.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flower.c

## Purpose
This file translates Linux TC flower offload rules into mlxsw ACL rules. It validates supported match keys and action sequences, builds ACL key masks, allocates hardware side resources such as L4 port-range registers and policers, enforces ordering with matchall rules, and exposes replace/destroy/stats/template helpers used by the Spectrum flow-block code.

## Important APIs, Types, And Functions
Key entry points are `mlxsw_sp_flower_replace()`, `mlxsw_sp_flower_destroy()`, `mlxsw_sp_flower_stats()`, `mlxsw_sp_flower_tmplt_create()`, `mlxsw_sp_flower_tmplt_destroy()`, and `mlxsw_sp_flower_prio_get()`. Parsing is split across `mlxsw_sp_flower_parse()`, action parsing in `mlxsw_sp_flower_parse_actions()`, metadata ingress-ifindex handling, IPv4/IPv6 address key builders, exact L4 port matching, range matching via `mlxsw_sp_port_range_reg_get()`, TCP flags, and IP TTL/ECN/DSCP. Action helpers are delegated to ACL rule-info APIs for count, drop, trap, goto, redirect, mirror, VLAN, priority, mangle, police, and sample.

## Control Flow
Replace first checks priority compatibility with installed matchall filters, gets or creates the flower ACL ruleset for the chain, creates an ACL rule keyed by the TC cookie, parses matches and actions into `rulei`, commits the rule-info object, then installs the rule. Destroy looks up the same ruleset and cookie, deletes the rule from hardware, destroys it, and releases the ruleset. Stats query the installed ACL rule counters and feed `flow_stats_update()`. Template create parses a representative rule into element usage and keeps a ruleset reference; destroy drops the template-held reference plus the lookup reference.

## State And Persistence
The file owns no persistent on-disk state. It mutates in-memory ACL rulesets, rule blocker flags, TC stats objects, and per-rule resource references. Hardware-visible state includes ACL entries, counters, policer bindings, port-range key bits, mirroring/sampling actions, VLAN and mangle actions, and goto group identifiers. Error paths destroy partially created ACL rules and release rulesets, while port-range register lifetime is tied to ACL rule-info cleanup in lower layers.

## Dependencies And Integration Points
It depends on Linux flow dissector and TC action APIs, `netlink_ext_ack` diagnostics, mlxsw ACL/flex-key infrastructure, flow-block binding state, matchall priority queries, policer core, SPAN/sample actions, FID redirection helpers, and `spectrum_port_range.c`. It is part of the switchdev/TC offload path and integrates with devlink-visible ACL resources indirectly through the ACL subsystem.

## Risks And Edge Cases
Unsupported keys or actions must return clear extack errors because silent fallback would misrepresent hardware offload. Drop and redirect actions set ingress/egress binding blockers, so future mixed binding behavior depends on those flags. IPv6 mangle is explicitly rejected after action parsing if any mangle touched `rulei->ipv6_valid`. Port-range allocations can fail or exhaust limited hardware bits. Priority checks prevent flower and matchall from being ordered in a way hardware cannot reproduce. Policer validation only supports byte-rate single-rate policing, power-of-two burst after kernel rounding, drop exceed, and pipe/accept conform action.

## Test Signals
Useful tests include TC flower add/delete/stats for exact L2/L3/L4 keys, L4 range keys, ingress-ifindex metadata, drop/trap/goto/redirect/mirror/sample/police actions, invalid action combinations, mixed ingress/egress binding rejection, matchall priority conflicts, template create/destroy reference balance, and devlink resource pressure for port-range registers and policers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.c

## Purpose
This file provides GRE-over-IPv4 and GRE-over-IPv6 offload operations for Spectrum IP-in-IP routing. It extracts Linux tunnel parameters, validates offloadable tunnel shapes, programs underlay nexthop and decapsulation registers, manages IPv6 destination-address KVDL references, initializes tunnel ECN mapping tables, and exposes underlay-device lookup.

## Important APIs, Types, And Functions
Exported helpers include `mlxsw_sp_ipip_netdev_parms4()`, `mlxsw_sp_ipip_netdev_parms6()`, `mlxsw_sp_ipip_netdev_saddr()`, `mlxsw_sp_l3addr_is_zero()`, `mlxsw_sp_ipip_ecn_encap_init()`, `mlxsw_sp_ipip_ecn_decap_init()`, and `mlxsw_sp_ipip_netdev_ul_dev_get()`. Operation tables are `mlxsw_sp1_ipip_ops_arr[]` and `mlxsw_sp2_ipip_ops_arr[]`, each containing GRE4 and GRE6 `mlxsw_sp_ipip_ops`. GRE-specific callbacks initialize parameters, update RATR nexthops, build RTDP decap entries, produce overlay loopback RIF configuration, handle netdev parameter changes, and set/unset remote IPv6 address references.

## Control Flow
Tunnel offload starts by reading `ip_tunnel` or `ip6_tnl` parameters and ensuring local and remote addresses are set, TTL and TOS/class inheritance match hardware assumptions, and no unsupported tunnel flags are present beyond optional keys. Nexthop updates pack `MLXSW_REG_RATR_TYPE_IPIP` with the loopback RIF and either an IPv4 DIP or IPv6 KVDL pointer. Decap programming writes RTDP with SIP filtering that matches Linux tunnel demux behavior and traps decap errors. Overlay netdev changes decide whether to rebuild tunnel state, update only nexthops, or update decap based on changed source, keys, link, and destination.

## State And Persistence
State lives in `struct mlxsw_sp_ipip_entry`, especially cached tunnel parameters, overlay device, loopback RIF, decap FIB entry, DIP KVDL index, and list node. Hardware state is register-backed RATR adjacency entries, RTDP tunnel entries, RITR loopback attributes, KVDL IPv6 address storage, parsing-depth requirements, and ECN remap tables. Nothing is persisted beyond current driver/hardware lifetime.

## Dependencies And Integration Points
The file depends on Linux IP tunnel and IPv6 tunnel internals, mlxsw router/IPIP management functions declared elsewhere, KVDL IPv6 address reference helpers, ECN helpers, RTDP/RATR/TIEEM/TIDEM register packing, and trap IDs for decap ECN errors. It is consumed through `spectrum_ipip.h` by router and RIF code.

## Risks And Edge Cases
Incomplete tunnels with zero local or remote address are valid Linux constructs but intentionally not offloaded. GRE key handling must distinguish input and output keys. IPv6 GRE depends on correct acquire/release of address KVDL references during netdev changes and rollback. The checked-out source contains a duplicated function declaration line before the GRE6 loopback config, which is a compile-risk signal. ECN table initialization must cover all inner/outer ECN combinations and trap invalid decap cases consistently.

## Test Signals
Test GRE4/GRE6 tunnel add/remove, keyed and unkeyed tunnels, remote/local address changes, underlay link changes, nexthop refresh, IPv6 address KVDL leak checks, rejection of unsupported flags/TOS/TTL/incomplete tunnels, ECN decap trap behavior, and offload survival across tunnel parameter churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.h

## Purpose
This header defines the IP-in-IP offload interface shared between tunnel-specific code and Spectrum router/RIF users. It centralizes tunnel type IDs, cached tunnel parameters, per-tunnel entry state, operation callbacks, and parameter extraction helpers for IPv4 and IPv6 GRE devices.

## Important APIs, Types, And Functions
The public helpers are `mlxsw_sp_ipip_netdev_parms4()`, `mlxsw_sp_ipip_netdev_parms6()`, `mlxsw_sp_ipip_netdev_saddr()`, and `mlxsw_sp_l3addr_is_zero()`. `enum mlxsw_sp_ipip_type` defines GRE4, GRE6, and max. `struct mlxsw_sp_ipip_parms` stores underlay protocol, source/destination L3 addresses, link index, and input/output keys. `struct mlxsw_sp_ipip_entry` tracks the overlay netdev, loopback RIF, decap FIB entry, cached params, DIP KVDL index, and list membership. `struct mlxsw_sp_ipip_ops` is the callback vector for capability checks, nexthop programming, loopback configuration, decap programming, netdev changes, and remote-address lifecycle. The header exports Spectrum-1 and Spectrum-2 operation arrays.

## Control Flow
Router code identifies a tunnel type, selects an ops table entry, validates `can_offload()`, creates an overlay loopback RIF from `ol_loopback_config()`, calls `rem_ip_addr_set()` for address-backed resources, programs decap through `decap_config()`, and refreshes nexthops through `nexthop_update()`. Netdev notifier paths use `ol_netdev_change()` to reconcile runtime tunnel changes with hardware state.

## State And Persistence
The header defines only runtime data structures. `mlxsw_sp_ipip_entry` is the durable in-memory representation for as long as a tunnel is offloaded; hardware persistence is handled by the implementation file through registers and KVDL entries.

## Dependencies And Integration Points
It includes Spectrum router definitions, Linux FIB/tunnel headers, and IPv6 tunnel definitions. It is integrated by router, RIF, and nexthop code that need a protocol-neutral IPIP offload contract.

## Risks And Edge Cases
The ops ABI assumes callbacks maintain KVDL and RIF lifetimes across rollback. Callers must respect `inc_parsing_depth` and `double_rif_entry` generation differences. The `ol_dev` pointer is a live netdev dependency and must be protected by the router/netdev notifier lifecycle. New tunnel types require both enum expansion and ops-array population.

## Test Signals
Build coverage should catch missing callback implementations. Runtime signals include successful GRE4/GRE6 offload creation, netdev-change reconciliation, address reference release, nexthop updates, and generation-specific behavior for Spectrum-1 versus Spectrum-2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_kvdl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_kvdl.c

## Purpose
This file is the generic KVDL allocation wrapper for Spectrum. KVDL is shared hardware key-value storage used by many features for adjacency, tunnel, multicast, IPv6 address, and other object pointers. The wrapper hides generation-specific allocators behind `mlxsw_sp_kvdl_ops` and serializes allocation/free operations.

## Important APIs, Types, And Functions
`struct mlxsw_sp_kvdl` stores the selected ops vector, a mutex, and private allocator storage. Public entry points are `mlxsw_sp_kvdl_init()`, `mlxsw_sp_kvdl_fini()`, `mlxsw_sp_kvdl_alloc()`, `mlxsw_sp_kvdl_free()`, and `mlxsw_sp_kvdl_alloc_count_query()`. Allocation takes an entry type, entry count, and output index; free mirrors type/count/index.

## Control Flow
Initialization allocates the wrapper plus ops-private storage, initializes the mutex, stores the ops pointer from `mlxsw_sp`, assigns `mlxsw_sp->kvdl`, and calls the generation-specific `init()`. Alloc/free lock `kvdl_lock`, call through to `alloc()` or `free()`, and unlock. Finalization calls the backend `fini()`, destroys the mutex, and frees the wrapper.

## State And Persistence
All state is runtime in memory plus hardware allocator state managed by backend ops. The mutex protects allocation metadata, not consumers' higher-level object lifetimes. There is no persistent storage.

## Dependencies And Integration Points
The wrapper is used by IPIP, NVE, multicast routing TCAM, adjacency, and other Spectrum subsystems that need hardware KVDL entries. Backend ops are selected by the device generation in `struct mlxsw_sp`.

## Risks And Edge Cases
The caller is responsible for matching type/count/index on free. `alloc_count_query()` is not locked in this wrapper, so backend implementations must be safe for their own query semantics or callers must tolerate races. Init failure correctly destroys the mutex and frees memory, but callers must avoid using `mlxsw_sp->kvdl` after failed init.

## Test Signals
Check feature allocation under concurrent TC/tunnel/multicast churn, KVDL exhaustion behavior, matching allocation count queries, module unload with no backend leak warnings, and generation-specific backend init/fini coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_kvdl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_matchall.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_matchall.c

## Purpose
This file implements TC matchall offload for Spectrum flow blocks. It supports block-wide mirror and sample actions, binds them to every port currently attached to a flow block, maintains priority constraints relative to flower rules, and supplies generation-specific sampling implementations.

## Important APIs, Types, And Functions
Public entry points are `mlxsw_sp_mall_replace()`, `mlxsw_sp_mall_destroy()`, `mlxsw_sp_mall_port_bind()`, `mlxsw_sp_mall_port_unbind()`, and `mlxsw_sp_mall_prio_get()`. Internal helpers manage entry lookup, SPAN mirror add/delete, sample trigger parameter set/unset, per-port rule add/delete, priority min/max recomputation, and Spectrum-1/Spectrum-2 sample ops. `mlxsw_sp1_mall_ops` programs MPSC sampling and supports ingress only; `mlxsw_sp2_mall_ops` uses a CPU SPAN session and supports ingress/egress triggers.

## Control Flow
Replace validates one action, chain 0, non-mixed binding, and `ETH_P_ALL`, then checks flower priority ordering. It allocates a mall entry from the TC cookie/action, applies the action to each bound port, rolls back already-bound ports on failure, increments rule/blocker counters, links the entry, and updates min/max priorities. Destroy unlinks by cookie, decrements counters, removes the action from bound ports, and frees via RCU because sampled RX packets can still reference the entry. Port bind/unbind replay or remove all mall entries for a single port.

## State And Persistence
State is stored in the flow block's `mall.list`, min/max priority fields, rule count, and ingress/egress blocker counters. Per-entry state includes cookie, priority, ingress flag, mirror target/SPAN ID, or sample params/SPAN ID. Hardware state includes SPAN agents, analyzed-port refs, sample trigger parameters, MPSC register state, and Spectrum-2 CPU SPAN bindings.

## Dependencies And Integration Points
The file depends on flow-offload action parsing, Spectrum flow-block binding lists, SPAN infrastructure, psample trigger parameter management, and hardware registers MPSC for Spectrum-1. It coordinates with `spectrum_flower.c` through bidirectional priority checks.

## Risks And Edge Cases
Matchall and flower priority constraints differ for ingress and egress and must remain symmetric. Rollback relies on list iterator position after a failed per-port add. RCU free is required for in-flight sampled packets. Spectrum-1 sampling rejects egress and out-of-range MPSC rates. The checked-out source shows a duplicated priority-comparison line in the egress flower conflict branch, a compile-risk signal in this tree.

## Test Signals
Exercise matchall mirror/sample add/delete, port bind/unbind replay, rollback by injecting SPAN/sample failures, flower priority conflicts, Spectrum-1 ingress-only sampling rejection, Spectrum-2 CPU sampling, RCU teardown under sampled traffic, and mixed ingress/egress binding rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_matchall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.c

## Purpose
This file implements the generic multicast-routing offload core. It tracks multicast routing tables, virtual interfaces, multicast forwarding cache routes, route-to-VIF relationships, route action decisions, catchall trap routes, and periodic hardware counter synchronization. Hardware programming is delegated through `mlxsw_sp_mr_ops`.

## Important APIs, Types, And Functions
Key types are `struct mlxsw_sp_mr`, `mlxsw_sp_mr_table`, `mlxsw_sp_mr_vif`, `mlxsw_sp_mr_route`, and route/VIF list-entry structures. Public APIs include `mlxsw_sp_mr_init()`, `mlxsw_sp_mr_fini()`, `mlxsw_sp_mr_table_create()`, `mlxsw_sp_mr_table_destroy()`, `mlxsw_sp_mr_table_flush()`, `mlxsw_sp_mr_table_empty()`, route add/delete, VIF add/delete, RIF add/delete, and RIF MTU update. Protocol-specific tables build IPv4 and IPv6 route keys, reject proxy `(*,*)` routes, and classify regular VIFs.

## Control Flow
Initialization allocates core state, initializes backend ops, and schedules delayed stats work. Table create initializes route hash/list state, per-VIF lists, protocol ops, and a catchall trap route. Route add validates the MFC, creates a route object linked to iVIF/eVIFs, computes min MTU and action, detects duplicate/proxy cases, writes hardware through ops, inserts into list/hash, and updates `MFC_OFFLOAD`. Replace reuses the original route private state and swaps data structures after hardware update. VIF/RIF resolve and unresolve paths update affected routes' iRIF/eRIF lists, min MTU, actions, and offload flags.

## State And Persistence
Runtime state includes the global table list, per-table VIF array, route hash table and list, cached route action/min MTU, retained `mr_mfc` refs, and backend private blobs. Hardware state lives behind ops calls. Periodic stats work reads backend counters and writes packet/byte/lastuse into kernel MFC counters. No on-disk state exists.

## Dependencies And Integration Points
The file integrates Linux IPv4/IPv6 multicast routing structures, router RIF objects, delayed work, rhashtable, and backend implementations such as `spectrum_mr_tcam.c`. It updates kernel MFC offload flags and counters, so it is tied to the multicast router control plane.

## Risks And Edge Cases
Route action changes depend on VIF regularity, RIF presence, `(*,G)` ingress membership, and valid eVIF count. Error rollback during VIF resolution must reverse partial iRIF/eRIF changes. `route_list_lock` protects route lists but hash operations are also used outside some list locks. MTU increases are not recomputed globally in `mlxsw_sp_mr_rif_mtu_update()`, only decreases update min MTU. The checked-out source contains duplicated assignments/calls in a few locations, which are compile or review-risk signals.

## Test Signals
Test IPv4/IPv6 `(S,G)` and `(*,G)` route add/replace/delete, proxy-route rejection, unresolved VIF trap behavior, tunnel/register VIF trap-and-forward behavior, RIF add/del resolving existing routes, MTU decrease propagation, table flush/destroy warnings, delayed stats updates to MFC counters, and backend error rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.h

## Purpose
This header defines the generic multicast-routing offload contract used by Spectrum router code and backend hardware implementations. It describes route keys, route values, actions, backend operation vectors, and the public table/route/VIF/RIF lifecycle API.

## Important APIs, Types, And Functions
`enum mlxsw_sp_mr_route_action` distinguishes forward, trap, and trap-and-forward. `struct mlxsw_sp_mr_route_key` stores VR ID, protocol, group/source addresses, and masks. `struct mlxsw_sp_mr_route_info` carries action, ingress RIF, egress RIF array, count, and minimum MTU. `struct mlxsw_sp_mr_route_params` combines key, value, and priority. `struct mlxsw_sp_mr_ops` is the backend ABI with init/fini, create/update/destroy, stats, action/min-MTU/iRIF/eRIF updates, and private-size fields. Public functions cover core init/fini, route add/delete, VIF add/delete, RIF add/delete/MTU update, table create/destroy/flush, and emptiness checks.

## Control Flow
Users create an MR core with a backend ops vector, create per-VR/protocol tables, add VIFs and routes as multicast routing events arrive, and notify the core when RIFs appear/disappear or change MTU. The core then calls backend ops with route params and incremental updates.

## State And Persistence
The header declares opaque `mlxsw_sp_mr` and `mlxsw_sp_mr_table` types; concrete state is in `spectrum_mr.c` and backend-private blobs. All state is runtime only.

## Dependencies And Integration Points
It includes Linux `mroute`/`mroute6`, Spectrum router types, and main Spectrum definitions. It is consumed by router multicast code and TCAM backend code.

## Risks And Edge Cases
Backend implementers must honor the update semantics: some updates are ordered so route action changes make iRIF/eRIF changes visible at the right time. `erif_indices` is caller-allocated and only valid for the duration of the backend call. New route actions or priorities require synchronized core/backend updates.

## Test Signals
Compile all backend ops implementations, verify route create/update/destroy ABI use, route stats propagation, and correct behavior for VIF/RIF event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.c

## Purpose
This file implements the multicast-routing backend that programs routes into ACL/TCAM with flexible actions. It converts generic MR route parameters into TCAM entries, action blocks, flow counters, and KVDL-backed egress RIF lists.

## Important APIs, Types, And Functions
The exported backend is `mlxsw_sp_mr_tcam_ops`. Internal state includes `struct mlxsw_sp_mr_tcam`, `mlxsw_sp_mr_tcam_route`, `mlxsw_sp_mr_tcam_erif_list`, and `mlxsw_sp_mr_erif_sublist`. Important helpers allocate/flush/commit RIGR2 eRIF sublists, create/destroy AFA blocks, populate eRIF lists, create/update/destroy routes through generation-specific `mlxsw_sp_mr_tcam_ops`, read flow counters, and incrementally update action, min MTU, iRIF, and eRIF membership.

## Control Flow
Backend init verifies `MC_ERIF_LIST_ENTRIES`, allocates generation-private TCAM state, and calls the lower TCAM ops init. Route create stores key/action/iRIF/min-MTU, builds a KVDL eRIF list, allocates a flow counter, creates an AFA block with counter plus trap or multicast-router action, allocates route-private TCAM storage, and inserts the route into hardware. Updates build a new eRIF list and AFA block first, update the TCAM entry atomically through lower ops, then destroy old action/list state. eRIF deletion similarly constructs a replacement list without the removed RIF before swapping.

## State And Persistence
Per-route runtime state includes eRIF KVDL sublists, current AFA block, counter index, route action, key, iRIF, min MTU, and lower-backend private state. Hardware state includes TCAM route entries, AFA blocks, flow counters, and RIGR2 linked-list KVDL records. No durable persistence exists beyond hardware programming lifetime.

## Dependencies And Integration Points
It depends on the generic MR core, KVDL allocator, flow counter allocator, AFA block APIs, ACL flex actions, hardware RIGR2 packing, and generation-specific MR TCAM lower ops stored in `mlxsw_sp->mr_tcam_ops`.

## Risks And Edge Cases
RIGR2 list commit assumes not-yet-pointed entries need no rollback on write failure. Action updates must avoid replacing the old AFA block until TCAM update succeeds. `route_irif_update()` only allows iRIF mutation while the route is trapped. eRIF removal creates a full copy, so KVDL pressure can make deletion fail. The checked-out source contains a duplicated function signature fragment near `mlxsw_sp_mr_tcam_erif_populate()`, a compile-risk signal.

## Test Signals
Test route create/update/destroy for trap, forward, and trap-and-forward, eRIF list sizes above one RIGR2 entry, eRIF add/delete rollback, flow counter reads, KVDL exhaustion, min-MTU/action/iRIF updates, lower TCAM update failure injection, and backend init failure when resources are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.h

## Purpose
This small header exposes the TCAM multicast-routing backend to the generic MR core.

## Important APIs, Types, And Functions
It includes Spectrum and generic MR definitions and declares `extern const struct mlxsw_sp_mr_ops mlxsw_sp_mr_tcam_ops;`.

## Control Flow
Device initialization can pass `mlxsw_sp_mr_tcam_ops` to `mlxsw_sp_mr_init()` to select the TCAM/AFA implementation for multicast routing. The rest of the backend behavior is implemented in `spectrum_mr_tcam.c`.

## State And Persistence
The header declares no state. Runtime state is allocated by the backend's `.init` and per-route create callbacks.

## Dependencies And Integration Points
It is a bridge between files that want a generic `mlxsw_sp_mr_ops` provider and the TCAM backend implementation.

## Risks And Edge Cases
Any signature drift in `struct mlxsw_sp_mr_ops` must be reflected in the implementation, not this header. Missing inclusion where the backend is selected would break initialization at compile time.

## Test Signals
Build coverage and successful MR initialization with `mlxsw_sp_mr_tcam_ops` are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.c

## Purpose
This file implements the shared NVE/VXLAN offload core. It manages global NVE tunnel lifetime, multicast flood lists, per-FID VNI enable/disable, FDB replay/offload cleanup, IPv6 address mappings for learned remote endpoints, NVE QoS/ECN initialization, and per-port tunnel decap queue setup.

## Important APIs, Types, And Functions
Public APIs include `mlxsw_sp_nve_init()`, `mlxsw_sp_nve_fini()`, `mlxsw_sp_nve_fid_enable()`, `mlxsw_sp_nve_fid_disable()`, `mlxsw_sp_nve_flood_ip_add()`, `mlxsw_sp_nve_flood_ip_del()`, IPv6 KVDL/map helpers, `mlxsw_sp_nve_learned_ip_resolve()`, and port init/fini. Internal structures represent multicast lists keyed by FID, linked TN UMT records, IPv4/IPv6 multicast entries, and MAC/FID-to-IPv6 endpoint mappings.

## Control Flow
Initialization allocates `mlxsw_sp_nve`, initializes multicast and IPv6 rhashtables, programs tunnel QoS and ECN maps, and queries per-record resource limits. FID enable validates VXLAN parameters through type ops, derives a config, rejects conflicting global tunnel configs, initializes the global tunnel on the first FID, sets the FID VNI, and replays VXLAN FDB entries. FID disable flushes flood IPs, hardware FDB entries, IPv6 maps, clears VXLAN offload flags, clears the FID VNI, and decrements global tunnel usage. Flood-IP add/create paths allocate list records in KVDL and write linked TN UMT entries; delete/flush carefully preserve the FID's first-record pointer semantics.

## State And Persistence
Runtime state includes the current global NVE config, multicast-list hash table, IPv6 endpoint hash/list, number of active NVE tunnels, max record sizes, tunnel KVDL index, and underlay RIF index for Spectrum-2. Hardware state includes TNQCR/TNEEM/TNDEM QoS/ECN maps, TN UMT records, FID flood indexes, VNI association, NVE FDB entries, KVDL IPv6 addresses, and global tunnel registers programmed by type-specific ops.

## Dependencies And Integration Points
The file depends on VXLAN ops through `spectrum_nve_vxlan.c`, FID APIs, router underlay RIF/decap promotion, KVDL, IPv6 address reference helpers, switchdev notifier FDB replay, SFDF FDB flush registers, and devlink resources for NVE multicast entries.

## Risks And Edge Cases
Only one global tunnel config can be active; mismatched VXLAN devices are rejected once a tunnel exists. Multicast record deletion is delicate because the first KVDL record index is stored in the FID; deleting first or middle records requires pointer rewrites or KVDL index swaps. IPv6 address maps must release address references on replace/delete/flush. The checked-out source contains several duplicated tokens/braces/comments and a duplicated `ops` declaration in `mlxsw_sp_nve_fid_enable()`, which are compile-risk signals. Many paths assume RTNL for FID/netdev operations.

## Test Signals
Test NVE init/fini, VXLAN FID enable/disable, conflicting tunnel configs, FDB replay and clear-offload behavior, IPv4/IPv6 flood IP add/delete/flush across multiple KVDL records, IPv6 endpoint replace/delete reference balance, ECN mapping traps, FDB flush by FID, and WARN-free unload after all FIDs are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.h

## Purpose
This header defines the shared NVE offload model and type-specific operations used by VXLAN support.

## Important APIs, Types, And Functions
`struct mlxsw_sp_nve_config` captures tunnel type, TTL, learning, UDP destination port, flow label, underlay table/protocol/source IP. `struct mlxsw_sp_nve` stores current config, multicast and IPv6 rhashtables, active tunnel count, resource limits, tunnel index, and Spectrum-2 underlay RIF. `struct mlxsw_sp_nve_ops` defines type-specific capability checks, config derivation, init/fini, FDB replay, and FDB offload clearing. The header exports Spectrum-1 and Spectrum-2 VXLAN ops.

## Control Flow
NVE core code selects an ops object by NVE type, asks it whether a candidate device can be offloaded, derives a normalized config, initializes or reuses the global tunnel, and delegates FDB replay/offload clearing to type-specific code.

## State And Persistence
The header declares runtime-only in-memory state. Hardware programming and resource references are managed by `spectrum_nve.c` and `spectrum_nve_vxlan.c`.

## Dependencies And Integration Points
It includes netlink, rhashtable, and Spectrum base types. It integrates FID/NVE core logic with VXLAN-specific implementation.

## Risks And Edge Cases
Because `num_nve_tunnels` is protected by RTNL, callers must honor RTNL around tunnel enable/disable. Adding new NVE types requires filling ops arrays and ensuring config equality semantics are valid for shared global tunnel state.

## Test Signals
Compile ops providers, validate config derivation for IPv4/IPv6 VXLAN, test multi-FID reuse of one tunnel config, and verify RTNL assertions in enable/disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve_vxlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve_vxlan.c

## Purpose
This file provides VXLAN-specific NVE operations for Spectrum-1 and Spectrum-2+. It validates Linux VXLAN device configuration, converts it to mlxsw NVE config, programs global VXLAN tunnel registers, controls parsing depth and UDP destination port parsing, promotes router decap, and replays/clears VXLAN FDB offload state.

## Important APIs, Types, And Functions
Exported ops are `mlxsw_sp1_nve_vxlan_ops` and `mlxsw_sp2_nve_vxlan_ops`. Shared helpers validate IPv4/IPv6 flags, reject unsupported VXLAN attributes, derive source underlay protocol/IP, and pack TNGCR with TTL/source IP and randomized UDP source-port prefix. Spectrum-1 paths program TNGCR underlay VR and RTDP NVE entry. Spectrum-2 paths additionally program TNPC learning, underlay RIF, SPVTR tunnel-port VLAN mode, SPVID decap ethertype behavior, and RTDP egress RIF.

## Control Flow
Capability validation rejects multicast remote IP, missing source IP, bound local interface, non-default source-port range, non-inherit TOS, TTL inherit or zero TTL, nonzero flow label, unsupported flags, and Spectrum-1 802.1ad bridge VXLAN. Init sets VXLAN UDP destination parsing, increases parsing depth, programs generation-specific tunnel config, writes RTDP, and promotes router decap. Error paths clear config, decrease parsing depth, and reset UDP parsing. Fini demotes decap and reverses init state. FDB replay calls `vxlan_fdb_replay()` with the mlxsw switchdev notifier.

## State And Persistence
No large local state is owned. It writes global tunnel hardware state and stores Spectrum-2 underlay RIF index in `nve->ul_rif_index`. VXLAN offload marks live in the VXLAN/FDB subsystem and are replayed or cleared through kernel VXLAN helpers.

## Dependencies And Integration Points
Dependencies include Linux VXLAN internals, random byte generation for UDP source-port prefix, Spectrum parsing-depth and UDP-port parsing controls, router underlay VR/RIF and decap promotion, register packers TNGCR/RTDP/TNPC/SPVTR/SPVID, and switchdev notifier FDB replay.

## Risks And Edge Cases
VXLAN offload is intentionally narrow and rejects many valid software configurations. Spectrum-2 init must release the underlay RIF on every failure after acquisition. Random UDP source-port prefix should remain within Linux VXLAN default range. Parsing depth and UDP destination port must be balanced on all error/fini paths. Global tunnel config sharing means per-device differences are rejected by NVE core.

## Test Signals
Test accepted IPv4 and IPv6 VXLAN configs, rejected unsupported flags and TTL/TOS/source/remote settings, Spectrum-1 802.1ad rejection, Spectrum-2 underlay RIF get/put balance, RTDP programming, FDB replay errors and cleanup, and tunnel fini after multiple enabled FIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve_vxlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_pgt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_pgt.c

## Purpose
This file manages the Port Group Table used for multicast/replication membership. It allocates MID indexes, optionally contiguous MID ranges, tracks per-MID port memberships, and writes SMID2 hardware entries.

## Important APIs, Types, And Functions
Public APIs are `mlxsw_sp_pgt_init()`, `mlxsw_sp_pgt_fini()`, `mlxsw_sp_pgt_mid_alloc()`, `mlxsw_sp_pgt_mid_free()`, `mlxsw_sp_pgt_mid_alloc_range()`, `mlxsw_sp_pgt_mid_free_range()`, and `mlxsw_sp_pgt_entry_port_set()`. Internal structures are `mlxsw_sp_pgt`, `mlxsw_sp_pgt_entry`, and `mlxsw_sp_pgt_entry_port`. Helpers create/destroy MID entries, lookup port membership, pack SMID2 port masks, and add/delete ports under a mutex.

## Control Flow
Init validates `PGT_SIZE`, initializes an IDR and mutex, and records whether SMPE index programming is valid. MID allocation reserves IDR slots with `NULL`; entry creation later replaces the reserved slot with a `pgt_entry`. Adding a port gets or creates the entry, writes SMID2 membership true, and links a port record. Deleting a port removes the list node, writes membership false, and destroys the entry if it becomes empty. Range allocation reserves a contiguous cyclic interval and rolls back on partial failure.

## State And Persistence
State is runtime in `mlxsw_sp->pgt`: IDR slots, lock, table size, and SMPE validity. Hardware state is SMID2 membership per MID/local-port. Finalization warns if the IDR is not empty.

## Dependencies And Integration Points
The file depends on core resource query `PGT_SIZE`, IDR, mutexes, refcount-era membership usage from multicast/flooding code, and SMID2 register packing. Other Spectrum subsystems use MIDs to represent replication groups.

## Risks And Edge Cases
MID slots can be reserved without a `pgt_entry`; `mlxsw_sp_pgt_mid_free()` expects to remove a `NULL` slot and warns otherwise. `mlxsw_sp_pgt_entry_port_add()` does not explicitly reject duplicate local ports, so callers should not add the same port twice for one MID. Hardware write failure on delete is ignored after list removal. Range allocation assumes the cyclic cursor interval is available as a block.

## Test Signals
Test MID allocation/free, contiguous range allocation rollback, add/delete membership hardware writes, duplicate membership attempts, SMPE-valid and invalid modes, PGT exhaustion, and WARN-free fini after all users release MIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_pgt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_policer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_policer.c

## Purpose
This file implements Spectrum policer allocation, validation, hardware programming, counter query, and devlink resource registration. The implemented family is global single-rate byte policers, used by TC police actions and ACL actions.

## Important APIs, Types, And Functions
Public APIs include `mlxsw_sp_policers_init()`, `mlxsw_sp_policers_fini()`, `mlxsw_sp_policer_add()`, `mlxsw_sp_policer_del()`, `mlxsw_sp_policer_drops_counter_get()`, and `mlxsw_sp_policer_resources_register()`. Core structures are `mlxsw_sp_policer_core`, `mlxsw_sp_policer_family`, and `mlxsw_sp_policer`. Family ops allocate/free indexes with IDR, validate params, initialize QPCR hardware, and register occupancy callbacks. Generation ops set allowable burst-size bit ranges for Spectrum-1 versus Spectrum-2.

## Control Flow
Init allocates the core, runs generation init, and registers each policer family. The single-rate family skips CPU-reserved policer indexes by using `MAX_CPU_POLICERS` as start and `MAX_GLOBAL_POLICERS` as end, registers devlink occupancy, and initializes the IDR. Add validates byte policing, power-of-two burst, burst/rate limits, allocates a policer object/index, writes QPCR with CIR and burst size, clears the counter, and returns the index. Delete removes the index and frees the object. Counter query reads QPCR violate count.

## State And Persistence
State is runtime: per-family IDR, mutex, start/end index, atomic policer count, params, and index. Hardware QPCR state persists until reprogrammed/reset. Devlink resource occupancy is derived from the atomic count.

## Dependencies And Integration Points
It depends on devlink resource APIs, mlxsw core resource discovery, QPCR register definitions, IDR, mutexes, and TC/ACL policer users. `spectrum_flower.c` validates TC police actions before requesting ACL policer action programming.

## Risks And Edge Cases
Only bandwidth policers are supported; packet-rate, average-rate, peak-rate, and overhead modes are rejected elsewhere or here. Burst conversion maps bytes to 512-bit units and depends on power-of-two inputs. Resource registration has two devlink calls without local unwind if the second fails. The checked-out source contains a duplicated family lookup line in `mlxsw_sp_policer_add()`, a review/compile-risk signal.

## Test Signals
Test valid/invalid TC police offloads, burst/rate lower and upper limits, policer exhaustion, QPCR counter reads, add failure rollback, devlink resource occupancy, generation-specific burst limits, and unload warnings for leaked policers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_policer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_port_range.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_port_range.c

## Purpose
This file manages ACL L4 port-range registers. TC flower range matches consume a small hardware register indexed by a bit in the ACL `l4_port_range` key; this file deduplicates identical ranges, reference-counts them, programs PPRR registers, and exposes devlink occupancy.

## Important APIs, Types, And Functions
Public APIs are `mlxsw_sp_port_range_init()`, `mlxsw_sp_port_range_fini()`, `mlxsw_sp_port_range_reg_get()`, and `mlxsw_sp_port_range_reg_put()`. `struct mlxsw_sp_port_range_reg` stores min/max/source flag/refcount/index. `struct mlxsw_sp_port_range_core` stores an xarray, ID limits, and atomic count. Internal helpers configure PPRR, create/destroy/find range registers, and report occupancy.

## Control Flow
Init validates `ACL_MAX_L4_PORT_RANGE`, warns if the resource exceeds the 16 ACL key bits, initializes an allocating xarray, and registers devlink occupancy. Get searches for an identical range and increments its refcount, or allocates a new xarray index, writes PPRR for IPv4/IPv6 and TCP/UDP source or destination matching, increments occupancy, and returns the index. Put loads by index, decrements refcount, and destroys the register when it reaches zero.

## State And Persistence
Runtime state is the xarray of active range registers, refcounts, and occupancy count. Hardware state is PPRR content by register index. No persistent storage exists.

## Dependencies And Integration Points
It integrates with `spectrum_flower.c` ports-range parsing and devlink resource accounting. It uses xarray allocation, Linux refcounting, and PPRR register packers.

## Risks And Edge Cases
Get/find is a linear scan over active xarray entries; the hardware resource is small, but concurrency assumptions rely on higher-level serialization because there is no local lock around xarray operations. A failed PPRR write erases the allocated xarray slot. `put()` warns and returns if the index is unknown, which helps catch ACL cleanup imbalance. Register bits are limited to a `u16` ACL key element.

## Test Signals
Test duplicate range sharing, source and destination ranges, exhaustion extack, PPRR write failure rollback, refcounted destroy on final put, devlink occupancy, flower rule add/delete cleanup, and WARN-free fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_port_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.c

## Purpose
This file implements Precision Time Protocol hardware timestamping and PHC support for Spectrum. It provides different clock and packet timestamp paths for Spectrum-1 and Spectrum-2+, hwtstamp get/set operations, PTP trap programming, timestamp matching/garbage collection, shaper setup, ethtool timestamp capabilities, and PTP-specific stats.

## Important APIs, Types, And Functions
Clock APIs include `mlxsw_sp1_ptp_clock_init/fini()` and `mlxsw_sp2_ptp_clock_init/fini()`. State APIs include `mlxsw_sp1_ptp_init/fini()` and `mlxsw_sp2_ptp_init/fini()`. Packet paths are `mlxsw_sp1_ptp_receive()`, `mlxsw_sp1_ptp_transmitted()`, `mlxsw_sp1_ptp_got_timestamp()`, `mlxsw_sp2_ptp_receive()`, and `mlxsw_sp2_ptp_transmitted()`. Hwtstamp APIs are generation-specific get/set and ts-info helpers. Spectrum-1 uses a cyclecounter/timecounter plus an unmatched packet/timestamp rhltable. Spectrum-2 reads UTC registers and reconstructs CQE timestamps.

## Control Flow
Spectrum-1 clock init configures a cyclecounter over free-running FRC registers, starts overflow work, and registers a PTP clock. Its packet path parses PTP headers, matches trapped packets with separately delivered timestamps by port/message/domain/sequence/direction, attaches timestamps when both pieces arrive, or passes packets/timestamps through after GC. Hwtstamp set computes global ingress/egress message-type masks across all ports, updates MTPPPC, balances parsing depth, stores per-port config, and updates the PTP shaper. Spectrum-2 clock init sets UTC time to zero and registers the PHC. Spectrum-2 hwtstamp config is global/refcounted across ports and uses MTPCPC; ingress and egress timestamping must be enabled or disabled together.

## State And Persistence
Spectrum-1 state includes the PTP clock timecounter, overflow work, unmatched hash table, GC work/cycle counter, per-port hwtstamp config/type masks, and GC stats. Spectrum-2 state includes a global hwtstamp config, enabled-port refcount, and mutex. Hardware state includes MTUTC time/frequency adjustment, MTPPS set-at-next-second scheduling, MTPTPT trap mapping, MTPPPC/MTPCPC timestamp classification, MOGCR FIFO clear behavior, QEEC shaper enable, QPSC shaper parameters, and CQE timestamp fields.

## Dependencies And Integration Points
The file depends on Linux PTP clock, timecounter/cyclecounter, hwtstamp, ptp classifier/parser, SKB timestamp APIs, rhashtable/rhltable, mlxsw core register reads, trap IDs, parsing-depth control, port speed queries, and RX/TX listener paths. It is called from port hwtstamp ioctls, ethtool ts-info, trap listeners, and TX completion paths.

## Risks And Edge Cases
Spectrum-1 matching must handle packet-before-timestamp and timestamp-before-packet ordering, duplicate keys, port removal while packets are pending, softirq versus workqueue delivery, and hash growth limits. Spectrum-1 global MTPPPC masks are recomputed from all ports, so parsing-depth balance must stay correct. Spectrum-2 only supports event filters and requires symmetric RX/TX enablement. CQE timestamp reconstruction uses low 8 seconds bits and current UTC, so large delays around wrap would be risky. The checked-out source contains duplicated signature/declaration lines in Spectrum-2 clock and duplicated local declarations in Spectrum-1 update code, compile-risk signals.

## Test Signals
Test PHC register/unregister, `phc2sys` time set/adjust/frequency adjust, hwtstamp ioctl get/set for supported and rejected filters, Spectrum-1 packet/timestamp matching in both arrival orders, GC counters, port removal with pending entries, shaper changes on speed and timestamp state, Spectrum-2 CQE timestamp reconstruction, global refcount enable/disable across multiple ports, and trap programming cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.h

## Purpose
This header declares Spectrum PTP clock, state, packet, hwtstamp, ts-info, shaper, and stats interfaces. It also provides no-op or software-fallback inline definitions when `CONFIG_PTP_1588_CLOCK` is not reachable.

## Important APIs, Types, And Functions
When PTP is enabled, it declares Spectrum-1 and Spectrum-2 clock init/fini, PTP state init/fini, RX/TX packet timestamp handlers, Spectrum-1 timestamp notification, hwtstamp get/set, shaper work, ts-info, and stats helpers. When PTP support is disabled, clock/state init return `NULL`, hwtstamp setters return `-EOPNOTSUPP`, receive falls back to normal RX listener handling, transmit frees SKBs, and stats counts are zero. Spectrum-2 shaper/stats helpers are inline no-ops even outside the disabled block.

## Control Flow
Main Spectrum initialization can call the generation-appropriate clock and state init functions regardless of config. Port hwtstamp operations call generation-specific setters/getters. Trap and TX completion paths call generation-specific receive/transmitted functions; disabled builds degrade to non-timestamp behavior.

## State And Persistence
The header declares opaque `mlxsw_sp_ptp_clock` and references `mlxsw_sp_ptp_state` without defining their internals. Runtime state is implemented in `spectrum_ptp.c`; no persistent storage exists.

## Dependencies And Integration Points
It depends on Linux device and rhashtable types, forward declarations for Spectrum device/port, and PTP/hwtstamp types when enabled through included kernel headers in users. It integrates with RX listeners and SKB freeing in disabled mode.

## Risks And Edge Cases
Callers must tolerate `NULL` clock/state when PTP support is disabled. Disabled-mode TX handlers consume SKBs, so callers must not reuse them. API shape differs by generation, especially Spectrum-1 timestamp notifications and shaper work.

## Test Signals
Build with and without `CONFIG_PTP_1588_CLOCK`, verify timestamp ioctls return `-EOPNOTSUPP` in disabled builds, confirm normal RX/TX behavior without PTP, and verify enabled builds link all generation-specific functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.h -->
