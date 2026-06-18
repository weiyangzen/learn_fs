# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_rep.h

### Purpose

`en_rep.h` is the private interface for mlx5 Ethernet representors. It declares the representor RX handler object, representor lifecycle APIs, representor predicates, bonding hooks, offload-stats hooks, and the data structures used by `en_rep.c` and related representor TC, neighbor, bridge, and tunnel modules. It is compiled differently depending on `CONFIG_MLX5_ESWITCH`, providing no-op or unsupported stubs when eswitch support is disabled.

The header is state-definition heavy. It describes the software objects that let representor code track neighbor updates, tunnel encapsulation and decapsulation, TC uplink offload services, per-vport send queues, peer-eswitch forwarding rules, and representor-private netdev/profile state.

### Important APIs, Types, And Functions

When `CONFIG_MLX5_ESWITCH` is enabled, the header exposes `extern const struct mlx5e_rx_handlers mlx5e_rx_handlers_rep` and prototypes for `mlx5e_rep_init()`, `mlx5e_rep_cleanup()`, representor bonding operations, `mlx5e_rep_bond_update()`, offload-stat query helpers, `mlx5e_is_uplink_rep()`, channel activation/deactivation hooks, neighbor stats work, and representor netdev predicates.

`struct mlx5e_neigh_update_table` owns the representor neighbor hash table and list, the encapsulation lock, a netevent notifier, delayed neighbor-stats work, and a minimum stats interval. `struct mlx5e_neigh_hash_entry` is the per-neighbor object containing IPv4/IPv6 destination, family, owning mlx5e private pointer, neighbor netdev, list/hash nodes, protected encap list, refcount, last-use reporting timestamp, and RCU cleanup.

`struct mlx5_rep_uplink_priv` stores uplink-only TC/offload state: indirect TC block callback list, tunnel entropy, unready flow list and reoffload work, mapping contexts for tunnel info and encap options, post-action state, connection tracking, psample, representor bonding, tunnel encapsulation private data, OVS internal-port support, flow meters, TC action stats, and multiport-eswitch work.

`struct mlx5e_rep_priv` is the main per-representor private object. It contains the eswitch representor pointer, neighbor update table, netdev, root flow table, vport RX rule, list of vport SQs, uplink-private state, previous VF vport stats, metadata send rule, TC hash table, and representor vNIC devlink health reporter.

Tunnel offload structures include `struct mlx5e_decap_key`, `struct mlx5e_decap_entry`, `struct mlx5e_mpls_info`, and `struct mlx5e_encap_entry`. They hold Ethernet decap keys, flow lists, hash/list nodes, completions, packet reformat handles, route/tunnel device data, MPLS fields, destination MAC, generated encapsulation header, validity/no-route/decap flags, refcounts, and RCU cleanup.

`struct mlx5e_rep_sq` and `struct mlx5e_rep_sq_peer` model send-to-vport forwarding state for active SQs. Each representor SQ records the local send-to-vport rule, an xarray of peer-eswitch rules, the SQ number, and a list node.

### Control Flow

The header itself has no runtime control flow, but it defines the object graph used by representor load, channel activation, TC offload, tunnel resolution, and cleanup. Eswitch load allocates `struct mlx5e_rep_priv`, stores it in `rep->rep_data[REP_ETH].priv`, and later `mlx5e_rep_to_rep_priv()` retrieves it inline.

During representor TX/offload initialization, modules initialize the neighbor table, TC hash table, tunnel mappings, uplink-private TC services, and bonding/bridge helpers described here. During channel activation, `en_rep.c` allocates `struct mlx5e_rep_sq` records and peer rule entries from these definitions. During unload, those lists, xarrays, hash tables, refcounted objects, completions, notifiers, delayed work, and RCU objects must be drained by implementation files.

When eswitch support is disabled, the header still allows common mlx5e code to compile by providing inline stubs. `mlx5e_is_uplink_rep()` returns false, representor activation/deactivation do nothing, representor driver init returns success, cleanup does nothing, and offload-stat helpers return false or `-EOPNOTSUPP`.

### State And Persistence Behavior

All state defined here is in-memory kernel state. Neighbor, encap, decap, TC, SQ forwarding, and reporter objects exist for the lifetime of a representor or individual offloaded flow and are not persisted to disk. Some structures mirror persistent hardware state: packet reformat handles, send-to-vport flow rules, root flow tables, vport RX rules, tunnel mapping IDs, flow-meter objects, and TC action stats refer to resources programmed elsewhere into mlx5 hardware.

Lifetime management uses a mix of mutexes, spinlocks, refcounts, completions, RCU heads, delayed/work items, hash-table nodes, list nodes, hlist nodes, and xarrays. `mlx5e_neigh_hash_entry` is explicitly protected against removal while notifications or TC users reference it. Encapsulation and decapsulation entries include completions so asynchronous route/reformat resolution can signal waiting flows.

### Dependencies And Integration Points

The header depends on Linux tunnel, rhashtable, mutex, list, refcount, completion, xarray, RCU, and netdev primitives, plus mlx5 internal headers `eswitch.h`, `en.h`, and `lib/port_tun.h`. It forward-declares TC and uplink helper types so related modules can share representor private state without forcing all definitions into this header.

Integration points include `en_rep.c` for lifecycle and profile logic, `en/rep/tc.c` for representor TC offload, `en/rep/neigh.c` for neighbor tracking and stats work, `en/rep/bridge.c` for bridge offload, tunnel encapsulation code for `mlx5e_encap_entry`, decap code for `mlx5e_decap_entry`, and common mlx5e code in `en_main.c`, which calls representor predicates and activation hooks even when built without eswitch support.

### Risks

Because this header defines shared private structures, layout and lifetime changes have broad blast radius. Adding fields to `struct mlx5_rep_uplink_priv` or `struct mlx5e_rep_priv` often requires coordinated initialization and cleanup in several modules. Missing cleanup for a list, hash table, xarray, notifier, work item, or RCU callback can leak objects across representor unload or switchdev mode changes.

Concurrency requirements are implicit in the fields. Neighbor hash operations require `encap_lock`; individual encap lists require `encap_list_lock`; unready flows require `unready_flows_lock`; refcounts protect objects used by notifications and TC; completions communicate asynchronous setup results; RCU heads imply delayed freeing. New code must use the right lock/refcount for the specific subobject rather than assuming representor-wide serialization.

The `CONFIG_MLX5_ESWITCH` stubs hide representor behavior from common code when eswitch support is absent. Callers must be prepared for false or unsupported results and avoid dereferencing representor private state unless the predicate and build configuration make that valid.

### Test Signals

Compile-time signals include successful builds with and without `CONFIG_MLX5_ESWITCH`, no incomplete type misuse from forward declarations, and no missing prototype or stub mismatches. Runtime signals include representor load/unload without leaked neighbor, encap, decap, SQ, peer, or health reporter objects; TC tunnel offload flows resolving and cleaning asynchronously; neighbor notifications safely racing flow removal; peer send-to-vport rules being added and removed; representor bonding hooks updating RX rules; and common NIC code behaving identically when eswitch support is compiled out.
