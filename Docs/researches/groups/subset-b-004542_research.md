# subset-b-004542 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/qos.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/qos.h

## Purpose
Declares the mlx5 E-Switch QoS interface used by core eswitch lifecycle code, vport configuration paths, and devlink rate operations. The header is active only under `CONFIG_MLX5_ESWITCH` and exposes the scheduling-domain and vport/node rate APIs implemented elsewhere.

## Important APIs, Types, and Functions
The lifecycle entry points are `mlx5_esw_qos_init()` and `mlx5_esw_qos_cleanup()`, paired with `mlx5_esw_qos_vport_disable()` and `mlx5_esw_qos_vport_qos_free()` for vport teardown and configuration reset. Per-vport rate control is exposed through `mlx5_esw_qos_set_vport_rate()`, `mlx5_esw_qos_get_vport_rate()`, `mlx5_esw_qos_vport_get_sched_elem_ix()`, `mlx5_esw_qos_vport_get_parent()`, and `mlx5_esw_qos_vport_update_parent()` as declared in `eswitch.h`. Devlink rate integration is represented by leaf and node setters for `tx_share`, `tx_max`, TC bandwidth arrays, parent changes, and node create/delete callbacks.

## Control Flow and State
This header has no executable control flow. Its prototypes describe the QoS state model stored in `struct mlx5_eswitch` and `struct mlx5_vport`: the eswitch owns a QoS domain with a refcount and root TSAR index, while each vport may own a scheduling node and optional per-TC scheduling nodes. Callers must honor the QoS domain lock noted in `eswitch.h`; state is persistent in firmware scheduling elements and mirrored by vport pointers.

## Dependencies and Integration Points
Depends on `struct mlx5_eswitch`, `struct mlx5_vport`, `struct mlx5_esw_sched_node`, `struct devlink_rate`, and `struct netlink_ext_ack` declarations from the eswitch, devlink, and QoS implementation layers. It is included by `eswitch.c` for init/cleanup and vport disable, by vport configuration code for VF rate APIs, and by devlink rate registration code for hierarchical rate tree operations.

## Risks and Test Signals
The main risks are lock-order mistakes around QoS domain state, leaked scheduling nodes when vports are disabled or VF info is cleared, inconsistent `min_rate`/`max_rate` reporting, and devlink parent changes leaving firmware and software hierarchy out of sync. Useful signals include devlink rate node/leaf create-delete tests, repeated SR-IOV enable/disable with configured rates, TC bandwidth validation, vport reset/clear paths, and lockdep coverage around QoS mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/vporttbl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/vporttbl.c

## Purpose
Implements reference-counted per-vport FDB table caching for eswitch offloads. TC split/mirror forwarding paths request a flow table keyed by chain, priority, vport, local VHCA ID, and namespace attributes; the module creates the table on first use and destroys it after the last rule releases it.

## Important APIs, Types, and Functions
`struct mlx5_vport_key` is a packed hash key containing `chain`, `prio`, `vport`, `vhca_id`, and `vport_ns`. `struct mlx5_vport_table` stores the hash node, `struct mlx5_flow_table *fdb`, rule reference count, and key. `mlx5_esw_vporttbl_get()` is the public acquire path; `mlx5_esw_vporttbl_put()` is the public release path. Internal helpers initialize namespace flags from the eswitch encap mode, create auto-grouped flow tables, hash flow attrs into keys, and look up entries under the vports table mutex.

## Control Flow and State
`mlx5_esw_vporttbl_get()` locks `esw->fdb_table.offloads.vports.lock`, mutates the caller-provided namespace flags for tunnel reformat/decap when encap is enabled, computes a `jhash()` over the packed key, and searches `esw->fdb_table.offloads.vports.table`. A hit increments `num_rules`; a miss allocates an entry, obtains the FDB namespace, creates an auto-grouped FDB table with priority `FDB_PER_VPORT`, sets `num_rules = 1`, and inserts the entry in the hash. `mlx5_esw_vporttbl_put()` recomputes the same key, decrements `num_rules`, and on zero removes the hash entry, destroys the flow table, and frees the cache node.

## Dependencies and Integration Points
Depends on `eswitch.h` for `struct esw_vport_tbl_namespace`, `struct mlx5_vport_tbl_attr`, eswitch state, and warning helpers. It integrates with `eswitch_offloads.c` through `mlx5_esw_vporttbl_get/put()` in split offloaded rule handling and in pre-opening per-vport level-1 tables when chain priorities are unsupported. It also depends on flow steering APIs `mlx5_get_flow_namespace()`, `mlx5_create_auto_grouped_flow_table()`, and `mlx5_destroy_flow_table()`.

## Risks and Test Signals
The caller-owned `vport_ns->flags` object is modified on every get/put, so shared namespace instances must tolerate idempotent flag widening when encap is enabled. Correctness depends on always balancing get/put for split and forwarding rules; a missing put leaks flow tables, while an extra put can destroy a table still referenced by hardware rules. The packed key avoids padding instability, but any future field addition must preserve hash and memcmp behavior. Test signals include TC split flow add/delete loops, encap mode toggles, failure injection around table creation, hash collision coverage, and leak checks after eswitch offloads disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/vporttbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch.c

## Purpose
Provides the core mlx5 E-Switch implementation: device eligibility, vport allocation and lifecycle, legacy FDB programming, vport event resynchronization, SR-IOV/SF/PF/ECPF load and unload, devlink parameters, admin configuration, mode/user locking, and exported query helpers. It is the mode-neutral base that calls either legacy or offloads backends.

## Important APIs, Types, and Functions
Public lifecycle APIs include `mlx5_eswitch_init()`, `mlx5_eswitch_cleanup()`, `mlx5_eswitch_enable()`, `mlx5_eswitch_enable_locked()`, `mlx5_eswitch_disable_sriov()`, `mlx5_eswitch_disable_locked()`, and `mlx5_eswitch_disable()`. Vport APIs include `mlx5_esw_vport_alloc/free()`, `mlx5_eswitch_get_vport()`, `mlx5_esw_vport_enable()`, `mlx5_esw_vport_disable()`, PF/VF/SF load helpers, and `mlx5_eswitch_enable_pf_vf_vports()`. Admin/config APIs set MAC, state, VLAN, spoofcheck, trust, rate, and expose VF config/stats. Lock/reference APIs include `mlx5_esw_hold/release()`, `mlx5_esw_get/put()`, `mlx5_esw_try_lock()`, `mlx5_esw_lock()`, and `mlx5_esw_unlock()`.

## Control Flow and State
Initialization registers the multiport devlink parameter, allocates `struct mlx5_eswitch`, creates debugfs and a single-thread workqueue, queries ECPF host-function state, initializes all static vports in an xarray with type marks, initializes offload representor state, initializes QoS, and sets default legacy mode plus encap defaults. Enable asserts devlink locking, disables LAG changes around first FDB creation, creates ACL namespaces, registers NIC vport-change EQ notifier, initializes QoS, then calls `esw_legacy_enable()` or `esw_offloads_enable()`. Disable unregisters notifiers, notifies users of mode exit, tears down backend FDB state, cleans ACL namespaces, and destroys devlink rate nodes for offloads.

## State and Persistence Behavior
Persistent software state is centered in `struct mlx5_eswitch`: vports xarray, mode, flags, enabled vport count, `state_lock`, `mode_lock`, user count, offload state, QoS state, host-function counters, IPsec VF count, and devlink/workqueue/debugfs resources. Vport state stores MAC, VLAN, link state, trusted/spoofcheck flags, RoCE/migration/IPsec bits, VHCA ID, QoS nodes, enabled events, PF activation state, and optional devlink port. Hardware persistence is programmed through NIC vport contexts, ESW vport contexts, ACL namespaces, MPFS, flow tables, and vport counters; vport info is intentionally retained across disable where needed to restore configuration.

## Dependencies and Integration Points
Depends on firmware command helpers (`mlx5_cmd_exec*`, vport cap/query/modify calls), flow steering, MPFS, LAG, ECPF, IPsec acceleration, legacy/offload ACL modules, QoS, devlink, debugfs, xarray, workqueues, and notifier chains. `eswitch_offloads.c` supplies offloads backend lifecycle and representor operations; `esw/legacy.h` and legacy ACL code supply legacy FDB behavior. It exports mode and total-vport helpers to other mlx5 modules and uses devlink locks for user-visible mode/config changes.

## Risks and Test Signals
High-risk areas are enable/disable unwind ordering, notifier/workqueue races with vport disable, xarray mark/range assumptions for VF/SF/ECVF iteration, lock ordering between `state_lock`, devlink lock, `mode_lock`, LAG changes, and backend cleanup, and stale vport info after partial failures. Legacy MAC/multicast code is sensitive to refcounts for MPFS, multicast uplink rules, allmulti/promisc rules, and `mc_promisc` conversions. Test signals include SR-IOV enable/disable cycles in legacy and switchdev modes, ECPF host PF/VF function-change events, SF load/unload, VF MAC/VLAN/spoof/trust/rate operations, vport stats, IPsec block/unblock interactions, lockdep, KASAN leak checks, and devlink mode transition failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch.h

## Purpose
Defines the mlx5 E-Switch internal ABI: core data structures, flags, vport and FDB state, offload attributes, iterator macros, exported function prototypes, devlink hooks, and no-op stubs when `CONFIG_MLX5_ESWITCH` is disabled. It is the shared contract between core eswitch code, offloads, legacy ACLs, representors, TC, bridge, QoS, devlink, IPsec, LAG, and SF support.

## Important APIs, Types, and Functions
Key types include `struct mlx5_eswitch`, `struct mlx5_vport`, `struct mlx5_eswitch_fdb`, `struct mlx5_esw_offload`, `struct mlx5_vport_info`, ingress/egress ACL structures, `struct mlx5_esw_flow_attr`, `struct mlx5_vport_tbl_attr`, and `struct esw_vport_tbl_namespace`. Important enums and flags describe mapped object types, vport events, egress ACL kind, metadata features, FDB-created state, destination flags, VLAN action flags, flow match levels, and xarray vport marks. The header declares lifecycle, vport config, offloaded rule, term table, restore, devlink mode/inline/encap, representor, VHCA map, mode lock, block/unblock, IPsec, LAG demux, and QoS entry points.

## Control Flow and State
Executable logic is mostly inline helpers and iterator macros. `mlx5_esw_allowed()` gates operations to eswitch-manager devices. Helpers classify manager/owner vports, translate devlink port indexes, test FDB creation, derive first host vport, and dispatch xarray iteration over all, VF, host-function, ECVF, and representor entries. Compile-time stubs preserve callers when eswitch support is disabled, returning success/no-op for lifecycle calls and capability-style errors for unsupported flow operations.

## State and Persistence Behavior
`struct mlx5_eswitch` is the persistent in-kernel owner for an eswitch instance: it stores the core device, notifier, legacy and offloads FDB union, multicast table, debugfs root, workqueue, vports xarray, mode and flags, locks, QoS domain, bridge/offload state, enabled counts, host function state, devcom pairing, IPsec count, and operation-in-progress flag. `struct mlx5_vport` persists per-vport address lists, promisc/allmulti rules, ACL tables, metadata, VHCA ID, adjacent/delegated info, admin info, QoS nodes, enabled state, xarray index, and devlink port. `struct mlx5_esw_flow_attr` carries TC offload per-rule state including input reps, VLAN edits, destinations, packet reformats, tunnel and decap data.

## Dependencies and Integration Points
Includes kernel networking/devlink/xarray headers, mlx5 device/vport/flow steering public headers, MPFS and fs-chains libraries, SF support, TC connection tracking, and TC sample support. It is included by `eswitch.c`, `eswitch_offloads.c`, `esw/vporttbl.c`, ACL modules, bridge/offload modules, representor code, TC offload code, IPsec offload paths, and devlink port-function handlers. The fallback stubs are integration-critical for builds without eswitch support.

## Risks and Test Signals
Because this is a broad internal ABI, layout or semantic changes can break many subsystems at once. Risks include stale comments versus lock requirements, exhausting xarray marks, incorrect vport iteration bounds on ECPF/ECVF systems, destination array overflow relative to `MLX5_MAX_FLOW_FWD_VPORTS`, metadata bit-field collisions with TC internal ports or tunnel marks, and stub behavior diverging from real behavior. Test signals include `allyesconfig` and no-eswitch builds, sparse/compile coverage for all users, switchdev TC offload tests, devlink port-function tests, multiport/LAG pairing, SF and ECPF topologies, and lockdep around mode and QoS locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads.c

## Purpose
Implements mlx5 switchdev/offloads mode. It programs offloaded FDB/flow-steering resources, TC flow insertion and deletion, vport source metadata, representor loading, peer eswitch pairing, active/inactive switchdev transitions, devlink mode/inline/encap controls, devlink port-function settings, VHCA maps, and IPsec-related forwarding adjustments.

## Important APIs, Types, and Functions
Rule APIs include `mlx5_eswitch_add_offloaded_rule()`, `mlx5_eswitch_add_fwd_rule()`, `mlx5_eswitch_del_offloaded_rule()`, `mlx5_eswitch_del_fwd_rule()`, `mlx5_eswitch_add_send_to_vport_rule()`, `mlx5_eswitch_add_send_to_vport_meta_rule()`, `esw_add_restore_rule()`, and `mlx5_eswitch_create_vport_rx_rule()`. Lifecycle APIs are `esw_offloads_init/cleanup()`, `esw_offloads_enable/disable()`, `mlx5_devlink_eswitch_mode_set/get()`, inline and encap devlink setters/getters, and active/inactive helpers. Representor and peer APIs cover vport rep add/remove/register/unregister/load/unload, `mlx5_esw_offloads_devcom_init/cleanup()`, single-FDB add/delete, and protocol-device lookup. Metadata/VHCA APIs allocate/free match metadata, expose metadata for match/set, map VHCA IDs to vports, and validate external controllers.

## Control Flow and State
Offloads enable initializes term-table locking and adjacent VHCAs, enables RoCE, initializes host number and per-vport metadata, configures firmware to pass reg C metadata, creates a mapping pool for reg C0 chain/user metadata, initializes steering, toggles FDB active/inactive state, loads the uplink representor first, and then enables PF/VF/ECPF/SF vports through the core eswitch loader. Steering initialization zeros the offload FDB union, initializes per-vport table cache and indirect tables, creates uplink/manager ACLs, creates the offloads namespace table, optional restore table, slow FDB and TC miss FDB, chain tables, slow-path send-to-vport/miss groups, vport RX groups, and the final vport RX drop rule. Disable reverses those resources, destroys the mapping pool and metadata, disables RoCE, cleans adjacent VHCAs, and restores active FDB when leaving inactive switchdev.

## Rule Programming Behavior
`mlx5_eswitch_add_offloaded_rule()` validates switchdev mode, VLAN action support, and IPsec forwarding constraints, builds `mlx5_flow_act`, adds VLAN/reformat/count/meter/ASO/mod-header details, sets source flow metadata, builds destinations, chooses the target FDB table, and installs either a direct rule or a termination-table rule. Destination setup supports slow path, sample, accept, MTU range post-meter tables, indirect tables for source rewrite, chain source-port rewrite, vport forwarding, IPsec policy table forwarding, `dest_ft`, `dest_chain`, and extra split tables. Split flows use per-vport FDB tables from `vporttbl.c`; non-split chain/priority flows use fs-chains. Deletion removes hardware rules, releases term tables, decrements flow count, and releases vport/chain/indirect references.

## State and Persistence Behavior
Persistent software state lives in `esw->offloads` and `esw->fdb_table.offloads`: flow tables, groups, counters, chains, indirect table object, representor xarray, peer flow lists, encap/decap/mod-header/term-table hashes and locks, metadata IDA, VHCA xarray, devcom pairing, inline mode, encap mode, block counters, flow count, host number, drop root, miss rules, and per-vport table cache. Firmware/hardware state includes flow table roots, FDB namespace steering mode, metadata pass-through bits, vport metadata ACL tags, drop roots with counters, peer namespace pairing, vport representor devlink ports, HCA caps for RoCE/migration/EQs/IPsec, and host PF HCA activation.

## Dependencies and Integration Points
Depends on flow steering core, fs-chains, term-table and indirect-table modules, offload ACL modules, representor ops, RDMA RoCE enablement, TC offload structures, TC meter/sample/internal-port support, devlink, LAG/devcom, firmware reset detection, mapping contexts, IPsec flow tables, xarray/IDA, and firmware command helpers. It is invoked by `eswitch.c` mode lifecycle and by TC/classifier code that installs eswitch offloaded rules. It also exports symbols for representor, LAG demux, metadata, and send-to-vport paths used across the mlx5 driver.

## Risks and Test Signals
The highest risks are resource unwind mismatches across the long enable and steering init paths, unbalanced chain/vport/indirect-table references in rule add/delete failure paths, metadata enablement differences between paired eswitches, active/inactive switchdev drop-root correctness, mode changes while flows, IPsec objects, traps, or users are active, and representor state transitions across ETH/IB rep types. Other risks include destination array sizing, unsupported source-port rewrite combinations, stale VHCA maps, ECPF function-change races, encap table recreation failure rollback, and devlink netns immutability handling. Test signals include switchdev mode toggles including inactive mode, TC flower offload add/delete for split, chain, meter, sample, tunnel, decap, and IPsec cases, multiport/LAG peer pairing, representor load/unload and IB reload, devlink inline/encap errors while flows exist, metadata disabled/enabled builds, ECPF host VF count changes, failure injection on each steering creation stage, lockdep, and leak/counter checks after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads.c -->
