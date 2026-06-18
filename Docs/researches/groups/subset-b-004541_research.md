# subset-b-004541 mlx5 eswitch research

Grouped research for the source files assigned to subset-b-004541. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.h

Purpose: Declares shared E-Switch ACL helper entry points used by legacy and offload ingress/egress ACL implementations. The header centralizes flow-table creation/destruction helpers and common ingress allow-rule destruction so mode-specific files can share the same vport ACL storage in `struct mlx5_vport`.

Important APIs/types/functions: `esw_acl_table_create()` creates an ingress or egress ACL flow table for a vport and namespace. Egress helpers expose VLAN ACL setup/teardown and group management. Ingress helpers expose table and allow-rule cleanup. The only direct type dependency is `struct mlx5_eswitch`, `struct mlx5_vport`, and `struct mlx5_flow_destination` from `eswitch.h` and mlx5 flow steering.

Control flow and integration: This header is included by `ingress_lgcy.c`, `ingress_ofld.c`, and corresponding egress ACL sources. Callers create tables, groups, and rules in mode-specific order, but cleanup is funneled through these declarations to avoid duplicated manipulation of `vport->ingress.acl`, `vport->egress`, and common allow rules.

State and persistence: No state is stored in the header. The declared helpers mutate per-vport ACL handles, flow groups, flow rules, and counters held under mlx5 vport structures. Those resources are hardware steering objects and must be destroyed before vport teardown.

Dependencies and risks: Correctness depends on callers matching create and destroy paths and not leaving stale `struct mlx5_flow_handle` or `struct mlx5_flow_group` pointers. Header staleness would cause mode-specific ACL files to diverge. Test signals include successful SR-IOV enable/disable, VLAN/spoof-check toggles, and no leaked flow tables on error unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_lgcy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_lgcy.c

Purpose: Implements legacy-mode ingress ACL programming for non-manager vports. It enforces spoof-check and VST VLAN behavior by allowing a matched ingress packet and optionally dropping all unmatched packets with a drop counter.

Important APIs/types/functions: `esw_acl_ingress_lgcy_setup()` is the main setup path, and `esw_acl_ingress_lgcy_cleanup()` tears down rules, groups, table, and drop counter. Internal helpers create four ordered groups: untagged+SMAC spoof-check, untagged-only, spoof-check-only, and drop. `esw_acl_ingress_lgcy_rules_destroy()` removes per-vport allow/drop rules.

Control flow: Setup first destroys existing legacy ingress rules, creates or reuses a drop flow counter when supported, and exits through cleanup if VLAN, QoS, and spoof-check are all disabled. It lazily creates an ingress ACL table with four FTEs and the four groups, builds a flow spec matching VLAN tag and/or source MAC, adds an allow rule, and adds a drop rule only when a VLAN check or spoof-check requires a deny fallback. On error it calls full cleanup, so partially-created groups and counters are not left active.

State and persistence: State lives in `vport->ingress.acl`, `vport->ingress.allow_rule`, `vport->ingress.legacy.drop_rule`, legacy group pointers, and `drop_counter`. The counter persists across rule recreation until final cleanup, allowing drop stats to be queried by legacy code.

Dependencies and integration: Uses mlx5 flow steering APIs, `esw_vst_mode_is_steering()`, firmware capabilities such as `flow_counter` and `vport_cvlan_insert_always`, Ethernet MAC helpers, and the common ACL helper functions. It is invoked by `esw_legacy_vport_acl_setup()` and by legacy configuration changes such as spoof-check updates.

Risks and test signals: Risk centers on group ordering, VLAN mode differences, missing counter support, and rollback correctness. Regressions show as spoof-check bypass, VLAN-tag acceptance/rejection errors, unexpected ingress drops, or leaked ACL objects during vport disable. Useful tests include legacy SR-IOV with VST VLAN, QoS-only VLAN tag insertion, spoof-check enable/disable with invalid MAC, and drop counter queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_lgcy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_ofld.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_ofld.c

Purpose: Programs switchdev/offload-mode ingress ACL rules. Its job is to tag packets with vport metadata for source-port matching, push priority VLAN tags for VF prio-tag mode, and optionally install an uplink source-port drop rule used by LAG-related paths.

Important APIs/types/functions: Public entry points are `esw_acl_ingress_ofld_setup()`, `esw_acl_ingress_ofld_cleanup()`, `mlx5_esw_acl_ingress_vport_metadata_update()`, `mlx5_esw_acl_ingress_vport_drop_rule_create()`, and `mlx5_esw_acl_ingress_vport_drop_rule_destroy()`. Internal pieces allocate modify-header actions for `metadata_reg_c_0`, create priority-tag allow rules, create drop groups, and manage metadata/prio/drop flow groups.

Control flow: `esw_acl_ingress_ofld_setup()` is a no-op unless metadata matching or prio-tag is required. The internal setup path counts required FTEs, creates the ingress ACL table, creates groups in deterministic order, and then installs metadata and prio-tag rules. Metadata updates destroy existing rules, update `vport->metadata`, and recreate rules, rolling the metadata value back to `default_metadata` on failure. Drop-rule create lazily creates the ACL if missing and cleans it up only if this call created it.

State and persistence: State is stored in `vport->ingress.acl`, common `allow_rule`, and `vport->ingress.offloads` members for modify headers, metadata/prio/drop groups, and drop rule. `vport->metadata` is persistent vport state used by subsequent match construction.

Dependencies and integration: Relies on mlx5 metadata match/set helpers, firmware capabilities `prio_tag_required`, vport type helpers, flow steering, modify-header allocation, and common ACL cleanup. Consumers include offloads mode vport setup, metadata refresh paths, and LAG/uplink drop handling.

Risks and test signals: Key risks are incorrect FTE sizing when capabilities combine, stale modify headers on metadata updates, and cleanup of lazily-created uplink ACLs. Test signals include switchdev VF traffic with metadata matching, prio-tag-required firmware, vport metadata rewrite, LAG drop rule create/destroy, and repeated setup/cleanup without flow object leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_ofld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/lgcy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/lgcy.h

Purpose: Declares external ACL APIs used when the E-Switch is in legacy mode. It gives legacy mode code a narrow interface for ingress and egress ACL setup/cleanup without exposing group or rule internals.

Important APIs/types/functions: The header declares `esw_acl_egress_lgcy_setup()`, `esw_acl_egress_lgcy_cleanup()`, `esw_acl_ingress_lgcy_setup()`, and `esw_acl_ingress_lgcy_cleanup()`. It depends on `eswitch.h` for `struct mlx5_eswitch` and `struct mlx5_vport`.

Control flow and integration: `legacy.c` calls the ingress then egress setup functions for non-manager vports, and unwinds ingress if egress setup fails. Cleanup is ordered egress then ingress. This header is the contract between generic legacy vport handling and ACL implementation files.

State and persistence: The header stores no state. Its declared functions manage vport ACL tables, groups, rules, and counters owned by `struct mlx5_vport`.

Risks and test signals: The main risk is API drift between legacy ACL implementation and vport lifecycle. Test signals are successful compile under legacy eswitch support, clean SR-IOV legacy enable/disable, and correct ACL recreation after VLAN/spoof-check changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/lgcy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ofld.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ofld.h

Purpose: Declares ACL APIs for switchdev/offload mode and supplies no-op or success stubs for selected ingress drop helpers when `CONFIG_MLX5_ESWITCH` is disabled.

Important APIs/types/functions: Egress declarations cover setup/cleanup, bounce-rule destruction, bond/unbond, and `mlx5_esw_acl_egress_fwd2vport_supported()`. Ingress declarations cover offload setup/cleanup, vport metadata update, and source-port drop rule create/destroy. The inline support helper requires offloads mode, metadata matching, and `egress_acl_forward_to_vport`.

Control flow and integration: Offloads and LAG code call these functions while configuring vport ACLs and representor behavior. The preprocessor split keeps callers compilable without eswitch support for drop-rule helpers, while most offload ACL APIs only exist when the feature is enabled.

State and persistence: The header has no storage. It defines the contract for mutating per-vport ingress/egress offloads ACL state, metadata rules, bounce rules, and bonding-related forwarding.

Dependencies and risks: It depends on mode and capability checks being accurate. A false positive from `mlx5_esw_acl_egress_fwd2vport_supported()` could route traffic to unsupported ACL actions. Test signals include build coverage with and without `CONFIG_MLX5_ESWITCH`, offloads mode ACL setup, egress fwd-to-vport paths, and LAG bond/unbond ACL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ofld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/adj_vport.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/adj_vport.c

Purpose: Creates, registers, and destroys adjacent E-Switch vports for delegated VHCAs. These synthetic/adjacent vports let the local eswitch manage representors and ACL namespaces for functions owned by another VHCA.

Important APIs/types/functions: `mlx5_esw_adjacent_vhcas_setup()` queries delegated VHCA records and creates adjacent vports. `mlx5_esw_adjacent_vhcas_cleanup()` destroys all adjacent VF vports. `mlx5_esw_adj_vport_modify()` sends `MODIFY_VPORT_STATE` to connect/disconnect ingress and egress. Internal helpers wrap firmware `CREATE_ESW_VPORT` and `DESTROY_ESW_VPORT`, allocate/free `struct mlx5_vport`, add/remove ACL namespaces, and add/remove offload representors.

Control flow: Setup checks `delegated_vhca_max`, allocates a query output buffer, issues `QUERY_DELEGATED_VHCA`, and iterates returned function RID records. Each vport create calls firmware, allocates eswitch vport metadata, marks the xarray entry as VF, stores adjacency identity and parent PCI/function IDs, creates ACL namespaces, and adds the offloads representor. Failure unwinds namespaces, vport allocation, and firmware vport creation. Cleanup scans VF vports and destroys those with `vport->adjacent`.

State and persistence: State persists in `esw->vports`, `esw->last_vport_idx`, `vport->adjacent`, `vport->vhca_id`, and `vport->adj_info`. Firmware also has created ESW vport objects. Destruction decrements `last_vport_idx`, which assumes adjacent vport count changes in stack order.

Dependencies and integration: Integrates with firmware commands, xarray vport storage, ACL namespace management in flow steering, offloads representor add/remove, and devlink port attribute handling that reads `vport->adj_info`.

Risks and test signals: Risks include partial setup leaks, stale `last_vport_idx` if adjacent vports become non-LIFO, and failure to remove ACL namespaces before destroying firmware vports. Test signals include delegated VHCA enumeration, representor creation for adjacent functions, devlink PF/VF numbering for adjacent vports, repeated setup/cleanup, and vport state connect/disconnect command success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/adj_vport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge.c

Purpose: Implements mlx5 eswitch bridge offload for unicast FDB, VLAN filtering, VLAN push/pop, bridge port lifecycle, ageing, switchdev notifications, and bridge-level ingress/egress flow tables. It is the main state machine behind switchdev bridge acceleration.

Important APIs/types/functions: Public functions include `mlx5_esw_bridge_init()`, `mlx5_esw_bridge_cleanup()`, vport link/unlink and peer link/unlink, FDB create/remove/update/mark-deleted, `mlx5_esw_bridge_update()`, VLAN filtering/protocol/port VLAN setters, ageing-time setter, multicast enable wrapper, and MDB add/delete wrappers. Internal helpers create ingress and egress flow tables/groups, packet reformat objects, FDB entries, VLAN objects, and per-port metadata.

Control flow: Bridge initialization allocates `struct mlx5_esw_bridge_offloads`, initializes bridge list and port xarray, and hooks debugfs. The first bridge lookup lazily creates global ingress and skip tables; each new bridge creates a per-bridge egress table and rhashtables for FDB/MDB. Port link gets or creates the bridge and inserts a `mlx5_esw_bridge_port` keyed by vport plus owner VHCA. FDB create allocates a counter, creates ingress rule to forward to bridge egress table and count, optionally creates a VLAN-filter skip rule, creates egress rule to the destination vport, inserts into rhashtable/list, and notifies switchdev. Removal and cleanup delete flow rules, counters, lists, and hash entries.

State and persistence: Global offload state lives in `esw->br_offloads`, `br_offloads->bridges`, `br_offloads->ports`, global ingress groups, IGMP/MLD fields populated by multicast code, and debugfs root. Per-bridge state includes ifindex, refcount, rhashtables/lists, egress flow table/groups, miss-rule packet reformat, ageing time, VLAN protocol, and flags. Per-port VLAN xarrays store `struct mlx5_esw_bridge_vlan`; FDB entries store MAC/VID, device, vport owner, ingress/egress/filter handles, counter, lastuse, and flags.

Dependencies and integration: Uses mlx5 flow steering, packet reformat and modify-header APIs, metadata-reg matching, switchdev notifier calls, RTNL assertions, devcom peer traversal for merged eswitch, multicast helpers from `bridge_mcast.c`, debugfs helpers, and tracepoints. It expects vport metadata matching to be enabled before global ingress table creation.

Risks and test signals: Risk areas include hardware capability branching for VLAN pop miss handling, exact table index sizing, switchdev notification ordering, concurrent asynchronous FDB events after port/VLAN deletion, peer eswitch lookup, and error unwinds across multiple hardware objects. Test signals include bridge join/leave, FDB add/delete/ageing, VLAN filtering on/off, PVID and untagged VLAN push/pop, 802.1Q and 802.1ad proto changes, merged-eswitch peer ports, debugfs FDB output, and no WARNs during bridge cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge.h

Purpose: Public bridge-offload interface and top-level offload state definition for mlx5 eswitch bridge acceleration.

Important APIs/types/functions: `struct mlx5_esw_bridge_offloads` stores the owning eswitch, bridge list, port xarray, debugfs root, notifier/workqueue fields, global ingress/skip tables, ingress groups, and multicast protocol handles. Declarations expose lifecycle, port link/unlink, peer link/unlink, FDB update/create/remove, ageing and VLAN controls, multicast toggle, per-port VLAN add/delete, and MDB add/delete.

Control flow and integration: Switchdev and representor code call this API to map Linux bridge events to eswitch hardware objects. `bridge.c` owns most definitions; `bridge_mcast.c` extends multicast/MDB behavior. The notifier/workqueue fields show this object is designed to integrate with netdev/switchdev/blocking notifier paths even though this file only declares the state.

State and persistence: The structure is persistent for the life of eswitch bridge offloads and is attached to `esw->br_offloads`. It caches hardware table/group/flow handles that must be cleaned before the eswitch is dismantled.

Risks and test signals: The risk is mismatched lifecycle ownership between external notifier users and internal bridge cleanup. Test signals include successful compile against all bridge users, offloads init/cleanup under RTNL, and bridge event flows correctly finding the right `mlx5_esw_bridge_offloads` instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_debugfs.c

Purpose: Provides debugfs visibility into bridge offload FDB entries. It creates a per-eswitch `bridge` debugfs directory and a per-Linux-bridge `fdb` seq_file.

Important APIs/types/functions: `mlx5_esw_bridge_debugfs_offloads_init()` and cleanup manage the top-level debugfs directory. `mlx5_esw_bridge_debugfs_init()` and cleanup manage each bridge directory and `fdb` file. Seq operations iterate `bridge->fdb_list` and print device, MAC, VLAN, cached packets/bytes/lastuse, and flags.

Control flow: Opening the seq file starts under `rtnl_lock()`, returns a header token for position zero, iterates the FDB list using seq list helpers, queries cached counter values with `mlx5_fc_query_cached_raw()`, and releases RTNL in `stop`. Cleanup uses recursive debugfs removal.

State and persistence: Stores dentry pointers in `br_offloads->debugfs_root` and `bridge->debugfs_dir`. It does not own FDB entries but reads their list and counters while protected by RTNL.

Dependencies and risks: Depends on debugfs, seq_file, RTNL serialization, bridge private structs, and flow counter caching. Risks include exposing stale data if entries are mutated outside RTNL or dereferencing entries whose counters have been destroyed. Test signals include `debugfs` file creation/removal with bridge lifecycle and sensible FDB output after traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_mcast.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_mcast.c

Purpose: Implements multicast bridge offload and MDB handling for mlx5 eswitch bridge acceleration. It handles MDB membership replication, per-port multicast flow tables, VLAN multicast pop rules, and global IGMP/MLD trap/skip rules.

Important APIs/types/functions: Public/internal-to-bridge exports include MDB init/cleanup, `mlx5_esw_bridge_port_mdb_attach()` and detach, MDB VLAN/bridge flushes, port multicast init/cleanup, VLAN multicast init/cleanup, and bridge multicast enable/disable. Internal helpers create MDB egress flows, per-port multicast tables/groups/flows, global IGMP/MLD groups and flow handles, and peer filter flows for merged eswitch.

Control flow: MDB attach requires multicast enabled, gets or creates an MDB entry keyed by multicast MAC plus VID, inserts the port in the entry xarray, and recreates the egress multicast flow with one destination per port. Detach removes a port and either deletes the entry or recreates the flow for the remaining ports. Multicast enable first creates shared ingress IGMP/MLD groups and rules if not already present, sets the bridge flag, and initializes each existing bridge port. Disable tears down port multicast state, clears the flag, and removes global rules only when no bridge still has multicast enabled.

State and persistence: MDB state lives in `bridge->mdb_ht` and `bridge->mdb_list`; each MDB entry owns a port xarray, port count, and egress flow handle. Per-port multicast state lives in `port->mcast` flow table, groups, filter rule, and forwarding rule. VLAN multicast state uses `vlan->mcast_handle`. Global IGMP/MLD state is stored in `br_offloads` ingress group and handle members.

Dependencies and integration: Depends on `bridge_priv.h` state, mlx5 flow steering, metadata matching, `FLOW_CONTEXT_UPLINK_HAIRPIN_EN`, hardware multipath and uplink hairpin capabilities checked by `bridge.c`, devcom peer owner lookup, ICMPv6 flex parser support for MLD, and bridge tracepoints.

Risks and test signals: Risks include failed flow recreation after membership changes leaving software MDB accepted but hardware stale, global multicast rule lifetime across multiple bridges, missing ICMPv6 parser support, and uplink hairpin/multipath capability mismatches. Test signals include multicast enable/disable, IGMP and MLD snooping traffic, MDB add/delete on several ports and VLANs, untagged VLAN multicast pop, merged-eswitch peer ports, and cleanup after bridge/VLAN/port removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_mcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_priv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_priv.h

Purpose: Defines private bridge-offload table sizing, flow-table levels, flags, keys, state objects, and internal function contracts shared by `bridge.c`, `bridge_mcast.c`, `bridge_debugfs.c`, and bridge tracepoints.

Important APIs/types/functions: Defines large fixed group sizes and index ranges for ingress, egress, skip, and multicast tables, with static asserts for total sizes. Key state types are `mlx5_esw_bridge_fdb_entry`, `mlx5_esw_bridge_mdb_entry`, `mlx5_esw_bridge_vlan`, `mlx5_esw_bridge_port`, and `mlx5_esw_bridge`. It declares helper functions for table creation, port keys, multicast/MDB init/cleanup, debugfs, and bridge multicast enable/disable.

Control flow and integration: The table constants are used directly when creating hardware flow groups so group ordering matches match specificity. Private structs link software bridge state to flow handles, counters, packet reformat objects, modify headers, rhashtables, xarrays, and list nodes. The declarations define how unicast, multicast, debugfs, and tracepoint files interoperate without exposing internals in public `bridge.h`.

State and persistence: This header defines all persistent in-memory bridge offload state. FDB entries hold ingress/egress/filter flow handles and counters; VLANs own push/pop/mcast resources; ports own VLAN xarrays and multicast tables; bridges own FDB/MDB tables and egress resources.

Risks and test signals: Risks include changing group size/index constants without preserving total table sizes, adding fields without cleanup coverage, or using port keys inconsistently across xarrays. Test signals include build-time static asserts, runtime bridge table creation, VLAN and multicast behavior across all table groups, and leak-free cleanup on bridge destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/devlink_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/devlink_port.c

Purpose: Creates, initializes, registers, unregisters, and describes devlink ports for mlx5 eswitch PF, VF, EC VF, and SF vports in offloads mode.

Important APIs/types/functions: PF/VF APIs are `mlx5_esw_offloads_pf_vf_devlink_port_init()` and cleanup. SF APIs are `mlx5_esw_offloads_sf_devlink_port_init()` and cleanup. Registration APIs are `mlx5_esw_offloads_devlink_port_register()`, unregister, and lookup. Static devlink ops expose port function attributes including HW address, RoCE, migratable, IPsec offload knobs under XFRM, max IO EQs, SF deletion, and state controls. PF registration may add a `max_SFs` devlink resource.

Control flow: Init allocates or attaches `struct mlx5_devlink_port`, populates switch ID and PCI PF/VF/SF attrs, stores it on the vport, and initializes mlx5 devlink port glue. Register selects ops by vport kind, computes the devlink port index, registers the port, creates a devlink rate leaf, and optionally registers PF resources. Unregister removes resources, detaches QoS parent, destroys the rate leaf, and unregisters the port.

State and persistence: State persists as `vport->dl_port` and in devlink's registered port/rate/resource objects. Adjacent vports alter VF attrs using `vport->adj_info`. Rate parent state is reset through QoS before devlink port teardown.

Dependencies and integration: Depends on devlink, mlx5 devlink helpers, eswitch vport type helpers, PCI identity, system image GUID, SF manager, XFRM offload callbacks, and QoS `mlx5_esw_qos_vport_update_parent()`.

Risks and test signals: Risks include wrong controller/PF/VF numbering for ECPF, external controller, EC VF, or adjacent vports; registration unwind if rate leaf creation fails; and stale QoS parent on unregister. Test signals include devlink port listing for PF/VF/SF/adjacent vports, devlink rate operations, PF max_SFs resource, XFRM function attributes, and clean unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/devlink_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/bridge_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/bridge_tracepoint.h

Purpose: Defines tracepoints for mlx5 bridge offload lifecycle and multicast membership changes.

Important APIs/types/functions: Trace event classes cover FDB entries, VLANs, bridge ports, and MDB port attach/detach. Events include FDB init/refresh/cleanup, VLAN create/cleanup, vport init/cleanup, and MDB attach/detach. Each event copies relevant fields into trace entries and prints compact identifiers such as netdev name, MAC, VID, flags, use age, port count, and offload state.

Control flow and integration: `bridge.c` defines `CREATE_TRACE_POINTS` before including this file, generating tracepoint definitions. `bridge_mcast.c` includes it for trace event calls. The include path/file macros at the end point ftrace to `esw/diag/bridge_tracepoint`.

State and persistence: Tracepoints store no persistent driver state, but snapshot fields from bridge private structs at call time. FDB `used` is derived from jiffies minus `lastuse`.

Dependencies and risks: Depends on `bridge_priv.h`, `netdev_name()`, tracepoint infrastructure, and stable private struct fields. Risks are trace format regressions, dereferencing invalid objects if tracepoints are called after cleanup ordering changes, and overhead on frequent FDB refresh paths. Test signals include successful trace event registration and correct fields when enabling mlx5 bridge tracepoints during bridge FDB/VLAN/MDB operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/bridge_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/qos_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/qos_tracepoint.h

Purpose: Defines tracepoints for mlx5 eswitch QoS scheduling element create/config/destroy events.

Important APIs/types/functions: Events include `mlx5_esw_vport_qos_create`, `mlx5_esw_vport_qos_config`, `mlx5_esw_vport_qos_destroy`, `mlx5_esw_node_qos_create`, `mlx5_esw_node_qos_config`, and `mlx5_esw_node_qos_destroy`. Trace payloads capture device name, vport id, scheduling element index, bandwidth share, max rate, parent pointer, node pointer, and TSAR index.

Control flow and integration: `qos.c` defines `CREATE_TRACE_POINTS` before inclusion. Tracepoints call `mlx5_esw_qos_vport_get_sched_elem_ix()` and `mlx5_esw_qos_vport_get_parent()`, so QoS code must provide those helpers and call tracepoints while vport/node state is valid.

State and persistence: No persistent state is stored by the tracepoint header. It snapshots QoS node/vport fields for ftrace/perf consumers.

Dependencies and risks: Depends on `eswitch.h`, `qos.h`, tracepoint infrastructure, and valid QoS state at call sites. Risks include stale helper assumptions during teardown and trace ABI churn. Test signals include enabling mlx5 QoS trace events while setting devlink rates, creating/deleting rate nodes, and moving parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/qos_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.c

Purpose: Implements an offloads indirection flow table used when uplink-to-VF/SF traffic needs source rewrite and optional decap recirculation before final vport forwarding.

Important APIs/types/functions: Public functions are `mlx5_esw_indir_table_init()`, destroy, `mlx5_esw_indir_table_needed()`, `mlx5_esw_indir_table_decap_vport()`, `mlx5_esw_indir_table_get()`, and put. Internal state includes `mlx5_esw_indir_table`, per-vport entries, and reference-counted recirculation rules with modify headers.

Control flow: `needed()` selects the indirection path for uplink ingress, VF/SF destination, same device, and source rewrite flag. `get()` locks the table, reuses or creates an entry by destination vport, increments forward refs or creates/references a decap recirculation rule, and returns the entry flow table. Entry creation builds an unmanaged FDB table at level 1 with recirc and fwd groups, optional recirc rule to chain table 0/1, and a fwd rule to the vport. `put()` decrements either forward ref or decap rule ref and destroys table, groups, rules, and entry when both references are gone.

State and persistence: State lives in `esw->fdb_table.offloads.indir`, its mutex, hash table, per-entry flow table/group/rule handles, `fwd_ref`, and recirc rule refcount/modify-header. Chain table references are acquired with `mlx5_chains_get_table()` and released on last recirc rule put.

Dependencies and integration: Depends on CLS_ACT, mlx5 chains, TC modify-header action builder, metadata register mapping, FDB namespace flow steering, tunnel decap attributes, source-port metadata helpers, and eswitch offload flow attributes.

Risks and test signals: Risks include asymmetric get/put for decap versus non-decap flows, chain table reference leaks, modify-header deallocation on failure, and hash key collisions if vport keying changes. Test signals include TC flows from uplink to VF/SF with source rewrite, decap recirculation, repeated add/delete sharing one destination vport, and no leaked unmanaged tables or chain refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.h

Purpose: Declares the eswitch indirection-table API and provides stubs when `CONFIG_MLX5_CLS_ACT` is disabled.

Important APIs/types/functions: Declares init/destroy, get/put, `needed()`, and `decap_vport()` helpers. Stubs return NULL, `ERR_PTR(-EOPNOTSUPP)`, false, or 0 as appropriate when TC action offload support is not compiled.

Control flow and integration: TC offload code can call the API unconditionally and rely on the compile-time branch to either use real indirection tables or decline support. The real implementation in `indir_table.c` is available only with CLS_ACT.

State and persistence: The header owns no state, but its opaque `struct mlx5_esw_indir_table` pointer is stored under eswitch FDB offloads state by callers.

Risks and test signals: Risks include callers not checking `ERR_PTR(-EOPNOTSUPP)` in stub builds or mismatching get/put. Test signals include build coverage with and without `CONFIG_MLX5_CLS_ACT`, TC flower flows that require indirection, and graceful rejection when unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec.c

Purpose: Manages VF IPsec offload capabilities through eswitch-managed HCA capability queries and updates on other functions.

Important APIs/types/functions: Public functions query and set VF crypto and packet/full IPsec offload support: `mlx5_esw_ipsec_vf_offload_get()`, `mlx5_esw_ipsec_vf_offload_supported()`, `mlx5_esw_ipsec_vf_crypto_offload_supported()`, `mlx5_esw_ipsec_vf_packet_offload_supported()`, `mlx5_esw_ipsec_vf_crypto_offload_set()`, and packet set. Internal helpers get/set generic `ipsec_offload`, set typed IPsec caps, and set crypto auxiliary Ethernet offload `insert_trailer`.

Control flow: Capability get first verifies generic VF IPsec offload is meaningful and enabled, then reads IPsec caps into `vport->info.ipsec_crypto_enabled` and `ipsec_packet_enabled`. Set-by-type rejects PF vport, optionally sets crypto auxiliary caps, enables generic IPsec before typed caps when turning on, and when turning off clears typed cap, refreshes current state, and disables generic IPsec only if both typed capabilities are now off.

State and persistence: Persistent state is firmware HCA capability state for the target vport/function and cached booleans in `vport->info`. Query/set buffers are temporary kernel allocations.

Dependencies and integration: Depends on VHCA resource manager support, other-function capability query/set commands, firmware feature detection via `reformat_add_esp_trasport`, IPsec cap groups, Ethernet offload caps, flow table decap support, and eswitch devlink port function IPsec knobs.

Risks and test signals: Risks include enabling typed caps without generic cap, failing to disable generic cap only when safe, stale cached state on set failure, and firmware generations that misreport IPsec support. Test signals include devlink port function IPsec crypto/packet get/set on VFs, unsupported PF attempts, old firmware capability rejection, and both crypto plus packet toggled independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.c

Purpose: Provides eswitch/FDB-specific flow steering glue for mlx5e IPsec offload. It maps IPsec RX object IDs into metadata, selects FDB flow levels and destinations, and restores uplink destinations for TC flows affected by IPsec.

Important APIs/types/functions: `mlx5_esw_ipsec_rx_create_attr_set()` and TX equivalent fill flow-creation attributes for FDB crypto priorities and levels. `mlx5_esw_ipsec_rx_status_pass_dest_get()` returns chain table 0/1 as pass destination. `mlx5_esw_ipsec_rx_setup_modify_header()` allocates a mapped ID and modify-header action in reg C1. `mlx5_esw_ipsec_rx_rule_add_match_obj()` matches that mapped ID. Mapping removal/search helpers manage `ipsec->ipsec_obj_id_map`. `mlx5_esw_ipsec_restore_dest_uplink()` walks representor TC flows and restores IPsec destinations.

Control flow: RX SA setup allocates a compact xarray ID for a hardware IPsec object, writes it into metadata reg C1 using tunnel bit fields, installs the modify header, and later matches status rules on the shifted mapped ID. On modify-header allocation failure the ID is erased. Restore-destination scans loaded representors and their TC flow hash tables, and for each non-multipath flow calls `mlx5_eswitch_restore_ipsec_rule()`.

State and persistence: State lives in each SA entry's `rx_mapped_id`, the global `ipsec_obj_id_map`, modify-header handles installed in flow actions, and existing TC flow rules. Flow levels are constants scoped to FDB crypto ingress/egress priority lanes.

Dependencies and integration: Depends on FDB chains, mlx5e IPsec structures, TC flow tables under CLS_ACT, eswitch TC restore helpers, xarray allocation under BH context, and metadata register layout shared with tunnel fields.

Risks and test signals: Risks include mapped ID exhaustion, missing erase on teardown, metadata bit overlap with tunnel fields, chain table reference expectations, and iterating TC flows while representors unload. Test signals include IPsec RX SA install/remove, status rule matching, mapped object lookup from RX path, TC offload coexistence, and restore after uplink destination changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.h

Purpose: Declares eswitch-specific IPsec flow-steering hooks and provides disabled stubs when eswitch support is not built.

Important APIs/types/functions: Declares RX/TX attribute setters, RX status pass destination getter, RX modify-header setup, RX mapped ID removal/search, uplink destination restore, and RX rule match augmentation. Stubs return `-EINVAL` for operations that require hardware/eswitch state and no-op for void helpers.

Control flow and integration: Generic mlx5e IPsec code can call these hooks to specialize flow creation for FDB/eswitch operation while building without eswitch support. `ipsec_fs.c` provides the actual implementation under `CONFIG_MLX5_ESWITCH`.

State and persistence: The header stores no state. It abstracts SA entry state, IPsec object ID maps, and flow action mutation owned by implementation code.

Risks and test signals: Risks include generic callers not handling `-EINVAL` from stubs, stale prototypes as mlx5e IPsec structures evolve, and missing include coverage for forward declarations. Test signals include builds with and without eswitch, IPsec offload setup in switchdev mode, and clean fallback when eswitch IPsec FS is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.c

Purpose: Implements legacy-mode eswitch FDB setup, VEPA mode, vport ACL orchestration, drop-stat queries, and legacy sriov vport configuration controls.

Important APIs/types/functions: Public entry points include `esw_legacy_enable()`, disable, `mlx5_eswitch_set_vepa()`, get, `esw_legacy_vport_acl_setup()`, cleanup, `mlx5_esw_query_vport_drop_stats()`, `mlx5_eswitch_set_vport_vlan()`, spoofchk/trust setters, and `mlx5_eswitch_set_vport_rate()`. Internal helpers create/destroy legacy FDB and VEPA tables and rules.

Control flow: Legacy enable creates the FDB table with address, allmulti, and promisc groups, initializes VF link state to auto, then enables PF/VF vports for UC/MC/promisc events. VEPA set creates a small higher-priority VEPA table with an uplink-to-FDB rule and a default star rule to uplink, or removes those rules and table when disabled. Vport ACL setup skips manager vports, installs ingress legacy ACL, then egress legacy ACL, unwinding ingress on egress failure. Configuration setters lock `esw->state_lock`, validate mode/permissions, update vport info, and recreate ACLs or notify vport change handlers when needed.

State and persistence: State lives in `esw->fdb_table.legacy` flow tables/groups/rules, `esw->user_count`, `esw->mc_promisc`, vport info fields such as VLAN/QoS/spoofchk/trusted/link state, and ACL counters used for drop stats.

Dependencies and integration: Uses flow steering, flow table pools, common eswitch vport lifecycle, legacy ACL headers, QoS rate setter, vport down stats firmware query, and permission/mode helpers. It bridges older SR-IOV netlink controls with mlx5 hardware steering.

Risks and test signals: Risks include FDB group size/index errors, VEPA partial rule leaks, legacy/offloads mode compatibility semantics for VLAN 0, spoof-check rollback on ACL failure, and drop stats double-counting. Test signals include enabling/disabling legacy SR-IOV, VEPA on/off, UC/MC/promisc updates, VLAN/spoofchk/trust/rate settings, vport down stats, and manager-vport ACL skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.h

Purpose: Declares legacy eswitch lifecycle, vport ACL, and drop-stat APIs.

Important APIs/types/functions: Exposes `esw_legacy_enable()`, `esw_legacy_disable()`, `esw_legacy_vport_acl_setup()`, `esw_legacy_vport_acl_cleanup()`, and `mlx5_esw_query_vport_drop_stats()`. It also defines the legacy SR-IOV vport event mask for UC, MC, and promiscuous changes.

Control flow and integration: `eswitch.c` and related vport lifecycle code use this interface when entering/leaving legacy mode or enabling/disabling individual vports. ACL setup/cleanup connect legacy mode to ACL implementation files.

State and persistence: No state is stored here. Declared functions mutate eswitch legacy FDB state and per-vport ACL/counter state.

Risks and test signals: Risks are duplicated event-mask definitions drifting from implementation and API drift with `legacy.c`. Test signals include compile coverage and legacy mode transitions with correct event subscriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/qos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/qos.c

Purpose: Implements eswitch QoS scheduling hierarchy management for vport rate limits, minimum-rate shares, devlink rate nodes, traffic-class arbitration, and parent-child rate object relationships.

Important APIs/types/functions: Public APIs include `mlx5_esw_qos_init()`, cleanup, vport rate set/get/disable/free, scheduler index/parent accessors, `mlx5_esw_qos_modify_vport_rate()`, devlink leaf setters for tx_share/tx_max/tc_bw, devlink node setters/new/delete/parent set, and `mlx5_esw_qos_vport_update_parent()`. Internal core types are `mlx5_qos_domain` with a mutex and node list, `mlx5_esw_sched_node`, and enum `sched_node_type` covering root vports TSAR, vport, TC arbiter TSAR, rate limiter, vport TC, and vports TC TSAR.

Control flow: QoS domain init allocates a mutex-protected domain. QoS hardware root TSAR is created lazily by `esw_qos_get()` and destroyed by refcounted `esw_qos_put()`. Setting vport min/max creates a vport scheduling node if absent, configures max rate or recalculates DWRR bandwidth share, and prunes empty nodes. Devlink node creation creates a vports TSAR under the root; parent updates destroy/recreate or reparent scheduling elements while preserving rate fields where possible. TC bandwidth enables a TC arbiter node, creates per-TC vports TSAR children, then converts vport children into per-TC vport elements or rate-limit elements depending on whether TC arbitration is on a vport or parent node. Disable paths tear down vport TC nodes, arbiters, and rate limiters and restore vports to ordinary nodes.

State and persistence: Persistent state includes `esw->qos.domain`, `esw->qos.refcnt`, `esw->qos.root_tsar_ix`, every `mlx5_esw_sched_node` list relationship, hardware scheduling element IDs, max/min rates, computed `bw_share`, TC bandwidth arrays, and `vport->qos.sched_node/sched_nodes`. State is in memory plus firmware scheduling hierarchy objects.

Dependencies and integration: Relies on mlx5 scheduling commands, QoS firmware capabilities, devlink rate callbacks, eswitch mode/permission checks, link-speed querying through LAG/uplink and port helpers, tracepoints, and devlink port unregister cleanup. `legacy.c` also calls vport rate setting for legacy controls.

Risks and test signals: Risks include rollback failures when reparenting nodes or switching TC arbitration modes, hierarchy depth limit mistakes, min-rate normalization across nested parents, unsupported TC bandwidth indices, byte-per-second to Mbps conversion errors, cross-eswitch parent assignment, and root TSAR refcount leaks. Test signals include devlink rate leaf tx_share/tx_max/tc_bw, node create/delete, leaf/node parent changes, nested hierarchy depth errors, LAG link-speed validation, vport disable while parented warning coverage, and tracepoint events for create/config/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/qos.c -->
