# subset-b-004560 research

Grouped research report for the mlxsw Spectrum buffer, counter, DCB, dpipe, ethtool, FID, and TC-flow support files. Each section preserves the original source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_buffers.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_buffers.c

## Purpose
`spectrum_buffers.c` owns Spectrum shared-buffer and per-port headroom programming. It translates bytes to hardware cells, initializes switch buffer pools and per-port pool/TC bindings, exposes devlink shared-buffer callbacks, snapshots and clears occupancy counters, and applies lossless/lossy priority-buffer headroom layouts used by DCB and pause/PFC configuration.

## Important APIs, Types, and Functions
Important state types are `struct mlxsw_sp_sb`, `struct mlxsw_sp_sb_port`, `struct mlxsw_sp_sb_pr`, `struct mlxsw_sp_sb_cm`, `struct mlxsw_sp_sb_pm`, `struct mlxsw_sp_sb_vals`, and `struct mlxsw_sp_sb_ops`. Exported entry points include `mlxsw_sp_buffers_init()`, `mlxsw_sp_buffers_fini()`, `mlxsw_sp_port_buffers_init()`, `mlxsw_sp_port_buffers_fini()`, `mlxsw_sp_cells_bytes()`, `mlxsw_sp_bytes_cells()`, `mlxsw_sp_hdroom_configure()`, devlink SB callbacks such as `mlxsw_sp_sb_pool_get()`, `mlxsw_sp_sb_pool_set()`, `mlxsw_sp_sb_port_pool_set()`, `mlxsw_sp_sb_tc_pool_bind_set()`, `mlxsw_sp_sb_occ_snapshot()`, and `mlxsw_sp_sb_occ_max_clear()`. Generation-specific data is supplied by `mlxsw_sp1_sb_vals`, `mlxsw_sp2_sb_vals`, and `mlxsw_sp{1,2,3}_sb_ops`.

## Control Flow
Switch initialization validates core resources for cell size, guaranteed shared-buffer size, and maximum headroom; allocates `mlxsw_sp->sb`; allocates per-port pool/TC state for all local ports; writes pool resources, CPU-port TC bindings, CPU-port pool thresholds, and multicast buffer limits; then registers devlink shared-buffer index 0. Port initialization allocates `port->hdroom`, configures default DCB-mode headroom, writes initial TC-to-pool bindings, and writes per-port pool thresholds. Headroom updates are staged: configure nonzero target buffers first, update priority-to-buffer mapping, then shrink buffers that become unused, and finally update the internal buffer. Error paths attempt to restore the previous buffer and priority-map state.

## State and Persistence Behavior
Runtime state lives in `mlxsw_sp->sb`, per-port `mlxsw_sp->sb->ports[local_port]`, and each `mlxsw_sp_port->hdroom`. Hardware persistence is through register writes to SBPR, SBCM, SBPM, SBMM, PBMC, PPTB, SBIB, and SBSR-related registers; it lasts until driver teardown or device reset. Occupancy snapshots cache current and max values in `cm->occ` and `pm->occ` for devlink queries. Static `mlxsw_sp_sb_vals` tables define reset-time pool sizing, freeze policy, CPU-pool defaults, and multicast configuration.

## Dependencies and Integration Points
This file depends on core resource discovery, devlink shared-buffer APIs, register pack/unpack helpers in `reg.h`, port metadata from `struct mlxsw_sp_port`, DCB headroom callers in `spectrum_dcb.c`, pause configuration in `spectrum_ethtool.c`, and generation-selected `sb_vals`/`sb_ops` installed by Spectrum core bring-up.

## Risks and Edge Cases
Headroom sizing is sensitive to cell rounding, MTU, link speed, and eight-lane port adjustment. The staged headroom update reduces packet-drop risk but still has rollback gaps if multiple hardware writes fail. Several pools and TC bindings are intentionally frozen, so devlink setters must reject changes with clear extack messages. CPU ingress quotas are unsupported and skipped. Occupancy snapshot batching must obey SBSR page and record limits or values can be assigned to the wrong port/TC. `MLXSW_SP_SB_INFI` and `MLXSW_SP_SB_REST` require careful conversion so pool allocations do not exceed total shared buffer.

## Test Signals
Useful signals include successful Spectrum probe, `devlink sb show`, pool and TC bind get/set behavior including forbidden changes, pause/PFC and ETS reconfiguration without unexpected drops, occupancy snapshot and max-clear results under traffic, MTU/speed changes on 1x/2x/4x/8x ports, and teardown without WARNs for leaked shared-buffer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_buffers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.c

## Purpose
`spectrum_cnt.c` implements the Spectrum counter allocator and devlink resource accounting for hardware counter banks. It divides the global counter pool into flow and RIF sub-pools, allocates contiguous counter entries sized by hardware resource data, and exposes active usage through devlink resource occupancy callbacks.

## Important APIs, Types, and Functions
The central types are `struct mlxsw_sp_counter_pool` and `struct mlxsw_sp_counter_sub_pool`. Public functions are `mlxsw_sp_counter_resources_register()`, `mlxsw_sp_counter_pool_init()`, `mlxsw_sp_counter_pool_fini()`, `mlxsw_sp_counter_alloc()`, and `mlxsw_sp_counter_free()`. Static helpers register per-resource occupancy callbacks and derive sub-pool base indexes, entry sizes, and sizes from devlink and core resource values.

## Control Flow
Resource registration first reads `COUNTER_POOL_SIZE` and `COUNTER_BANK_SIZE`, registers the top-level devlink counter resource, then registers subresources according to the statically configured bank counts. Runtime pool initialization allocates a flexible `mlxsw_sp_counter_pool`, copies the static sub-pool descriptors, reads configured devlink resource sizes, allocates a bitmap covering the whole counter pool, and registers occupancy callbacks for the top resource and each subresource. Allocation locks the bitmap, scans the requested sub-pool range for the next zero bit, verifies that the full hardware entry size fits before the sub-pool stop index, sets all bits in the entry, and increments atomic occupancy counters. Free clears the same number of bits and decrements occupancies.

## State and Persistence Behavior
State is in `mlxsw_sp->counter_pool`, the allocation bitmap, per-sub-pool base indexes, entry sizes, and atomic active-entry counters. No filesystem persistence exists. Hardware counter indexes are persistent only while the driver instance and corresponding offloaded objects hold them.

## Dependencies and Integration Points
The allocator is used by flow, RIF, nexthop, and devlink dpipe counter users through the public header. It depends on core resources `COUNTER_POOL_SIZE`, `COUNTER_BANK_SIZE`, `COUNTER_SIZE_PACKETS_BYTES`, and `COUNTER_SIZE_ROUTER_BASIC`, and on devlink resource registration/occupancy APIs.

## Risks and Edge Cases
Sub-pool sizes can contain a non-integer number of counter entries, so the overflow check after `find_next_zero_bit()` is essential. Allocation does not validate `sub_pool_id` beyond array indexing, so callers must pass a valid enum. Free only checks against global pool size; callers must free with the same sub-pool type and index returned by allocation. Resource registration can partially register subresources without local rollback if a later register call fails, relying on higher-level devlink teardown behavior.

## Test Signals
Signals include devlink resource tree sizing for the counter pool and flow/RIF children, occupancy increments/decrements when flow/RIF counters are enabled, `-ENOBUFS` when sub-pools fill, and no WARNs from `mlxsw_sp_counter_pool_fini()` for active entries or non-empty bitmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.h

## Purpose
`spectrum_cnt.h` declares the counter sub-pool IDs and public counter-pool API used by Spectrum flow, router, and devlink inspection code.

## Important APIs, Types, and Functions
The header defines `enum mlxsw_sp_counter_sub_pool_id` with RIF and flow sub-pools, and declares `mlxsw_sp_counter_alloc()`, `mlxsw_sp_counter_free()`, `mlxsw_sp_counter_pool_init()`, `mlxsw_sp_counter_pool_fini()`, and `mlxsw_sp_counter_resources_register()`.

## Control Flow
The header has no execution flow. It establishes the required lifecycle: register devlink resources, initialize the pool during device bring-up, allocate/free indexes for offloaded users, and finish the pool during teardown after all users have released counters.

## State and Persistence Behavior
No state is stored in the header. It references `struct mlxsw_sp` and `struct mlxsw_core` owners whose implementation state is in `spectrum_cnt.c`.

## Dependencies and Integration Points
It includes `core.h` and `spectrum.h`, so users inherit Spectrum core type definitions. The API integrates with offload modules that need packet/byte or router-basic counters without knowing the internal bank layout.

## Risks and Edge Cases
The enum order must match the static sub-pool descriptor array in `spectrum_cnt.c`. Callers must pair alloc/free with the same sub-pool ID and must not use indexes after freeing them.

## Test Signals
Compile coverage validates declarations. Runtime signals come from all counter users successfully allocating and freeing counters, plus devlink resource occupancy matching active offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dcb.c

## Purpose
`spectrum_dcb.c` implements the netdev DCBNL operations for Spectrum ports. It exposes IEEE ETS, max-rate, PFC, APP priority mapping, DCBX mode, and buffer controls, and translates those requests into Spectrum scheduler, QoS trust, rewrite-map, PFC, and headroom-buffer register programming.

## Important APIs, Types, and Functions
The main exported lifecycle functions are `mlxsw_sp_port_dcb_init()` and `mlxsw_sp_port_dcb_fini()`. The DCBNL operation table `mlxsw_sp_dcbnl_ops` wires callbacks for `ieee_getets`, `ieee_setets`, `ieee_getmaxrate`, `ieee_setmaxrate`, `ieee_getpfc`, `ieee_setpfc`, `ieee_setapp`, `ieee_delapp`, `getdcbx`, `setdcbx`, `dcbnl_getbuffer`, and `dcbnl_setbuffer`. Important helpers include ETS validation and rollback, APP DSCP/priority map generation, QoS trust toggling through QPTS/QRWE, PFC counter reads through PPCNT, and headroom recomputation through the buffer API.

## Control Flow
Initialization allocates per-port `ieee_ets`, `ieee_maxrate`, and `ieee_pfc` state, sets default trust to PCP, and attaches DCBNL ops to the netdev. ETS set validates TSA modes and bandwidth sum, programs egress scheduler weights per TC, programs priority-to-TC mappings, recomputes ingress headroom based on ETS buffer indexes, and only then copies the requested ETS state. APP set validates selectors, updates the kernel DCB APP database, derives default priority, DSCP-to-priority map, priority-to-DSCP rewrite map, programs QPDP/QPDPM/QPDSM, and toggles trust to DSCP when DSCP entries exist or PCP otherwise. PFC set rejects coexistence with link-level PAUSE, adjusts headroom delay and lossiness, programs PFC register state, and rolls headroom back on hardware failure.

## State and Persistence Behavior
Per-port state is stored under `mlxsw_sp_port->dcb` and in `mlxsw_sp_port->hdroom`. Hardware state is written to QEEC, priority-to-TC registers, QPTS, QRWE, QPDP, QPDPM, QPDSM, PFCC, and PPCNT query registers. It persists until later DCB changes, port teardown, or hardware reset. The Linux DCB APP database is updated before hardware programming and rolled back on set failure.

## Dependencies and Integration Points
The file depends on Linux DCBNL and DCB APP helpers, Spectrum scheduler APIs such as `mlxsw_sp_port_ets_set()` and `mlxsw_sp_port_ets_maxrate_set()`, pause state from ethtool/link handling, register packers in `reg.h`, and headroom functions from `spectrum_buffers.c`.

## Risks and Edge Cases
ETS rollback restores scheduler and priority mappings but ignores errors while rolling back. APP delete reports hardware update errors but keeps the kernel DCB database deletion. PFC and link-level PAUSE are mutually exclusive and must remain coordinated with ethtool pause handling. Buffer set is only accepted in TC headroom mode and can fail if requested buffers exceed shared headroom. Trust toggling changes DSCP rewrite behavior, so incomplete APP programming would misclassify traffic.

## Test Signals
Signals include `dcb` tool get/set output, ETS bandwidth validation, max-rate programming per TC, DSCP APP entries changing QoS trust state, PFC counters increasing under PFC traffic, rejection of PAUSE/PFC conflicts, buffer get/set in TC mode, and no leaked DCB allocations on port teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.c

## Purpose
`spectrum_dpipe.c` exposes parts of the Spectrum routing pipeline through devlink dpipe. It registers metadata headers and four tables: egress RIF (`mlxsw_erif`), IPv4 host (`mlxsw_host4`), IPv6 host (`mlxsw_host6`), and adjacency (`mlxsw_adj`). The tables dump matches, actions, entries, sizes, resources, and optional counters for RIFs, neighbors, and nexthops.

## Important APIs, Types, and Functions
Public functions are `mlxsw_sp_dpipe_init()` and `mlxsw_sp_dpipe_fini()`. Static table ops include ERIF dump/counter/size callbacks, shared host4/host6 entry preparation and enumeration, and adjacency table match/action/entry/counter callbacks. Metadata fields include `erif_port`, `l3_forward`, `l3_drop`, `adj_index`, `adj_size`, and `adj_hash_index`.

## Control Flow
Initialization registers dpipe headers, then registers ERIF, host4, host6, and adjacency tables, assigning KVD resource IDs to host and adjacency tables. ERIF entries iterate all possible RIF indexes under the router mutex, skip missing or device-less RIFs, and paginate devlink entry contexts when netlink messages fill. Host tables iterate RIF neighbor lists, filter by AF_INET or AF_INET6, skip ignored IPv6 neighbors, fill match values for RIF and destination IP, action value for destination MAC, and optional counters. The adjacency table iterates forwarding nexthops that are not IP-in-IP, fills adjacency index/size/hash and destination MAC/eRIF actions, and can enable or disable nexthop counters while updating hardware adjacency entries.

## State and Persistence Behavior
The file does not own long-lived objects beyond devlink dpipe registrations. It observes router, RIF, neighbor, and nexthop state under `mlxsw_sp->router->lock`. Enabling dpipe counters can allocate RIF, neighbor, or nexthop counters and update hardware; disabling releases them. Dump entry allocations are temporary and freed with `devlink_dpipe_entry_clear()`.

## Dependencies and Integration Points
It integrates with devlink dpipe, Spectrum router/RIF/neigh/nexthop APIs, KVD resource identifiers, counter helpers behind router objects, and standard devlink ethernet/IPv4/IPv6 headers. Table names are shared with `spectrum_dpipe.h`.

## Risks and Edge Cases
Dump pagination is stateful; skip counters must remain correct when a message fills midway through a RIF or nexthop iteration. Entry preparation allocates multiple value buffers and depends on `devlink_dpipe_entry_clear()` to release partially allocated state. Counter enable paths are best-effort for ERIF/host tables but adjacency counter enable has rollback for already-enabled nexthops. Router contents may change between paginated dump passes, although the router mutex serializes each full dump.

## Test Signals
Signals include `devlink dpipe table show/dump` for all four tables, resource association for host4/host6/adj, valid ifindex mappings for RIF fields, host table dumps for IPv4 and IPv6 neighbors, adjacency dumps for ECMP/nexthop groups, counter toggling, and clean unregister order on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.h

## Purpose
`spectrum_dpipe.h` declares the Spectrum dpipe lifecycle API and stable devlink dpipe table names.

## Important APIs, Types, and Functions
The header declares `mlxsw_sp_dpipe_init()` and `mlxsw_sp_dpipe_fini()`, and defines table-name macros `MLXSW_SP_DPIPE_TABLE_NAME_ERIF`, `MLXSW_SP_DPIPE_TABLE_NAME_HOST4`, `MLXSW_SP_DPIPE_TABLE_NAME_HOST6`, and `MLXSW_SP_DPIPE_TABLE_NAME_ADJ`.

## Control Flow
There is no execution path in the header. It defines the initialization and teardown contract implemented by `spectrum_dpipe.c` and consumed by Spectrum core device bring-up/teardown.

## State and Persistence Behavior
The header stores no state. The names it defines become user-visible devlink table identifiers and therefore should remain stable.

## Dependencies and Integration Points
The declarations require `struct mlxsw_sp` from the Spectrum core headers included by users. The table names are consumed by dpipe table registration, resource assignment, and userspace devlink commands.

## Risks and Edge Cases
Changing table-name macros would break userspace scripts and tests that refer to existing devlink dpipe tables. Missing init/fini calls would leave dpipe headers or tables unregistered.

## Test Signals
Compile coverage plus `devlink dpipe table show` confirming the four expected table names are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ethtool.c

## Purpose
`spectrum_ethtool.c` implements Spectrum netdev ethtool operations and link-mode conversion. It reports driver/firmware identity, link extended state, pause settings, statistics, module EEPROM and power controls, timestamp capabilities, standards-based MAC/PHY/RMON stats, module reset, and generation-specific PTYS speed/link-mode mapping for Spectrum-1 and Spectrum-2-or-newer devices.

## Important APIs, Types, and Functions
The exported objects are `mlxsw_sp_port_ethtool_ops`, `mlxsw_sp1_port_type_speed_ops`, and `mlxsw_sp2_port_type_speed_ops`. Key functions include pause get/set, link ksettings get/set, stats string/count/data callbacks, module EEPROM/page accessors, `mlxsw_sp_get_ts_info()`, MAC/PHY/control/RMON stats helpers, `mlxsw_sp_reset()`, and module power-mode get/set. Link-mode tables are `mlxsw_sp1_port_link_mode[]` and `mlxsw_sp2_port_link_mode[]`.

## Control Flow
EtHTool callbacks are dispatched from the netdev operation table. Pause set rejects autonegotiated pause and PFC coexistence, recomputes port headroom for link-level PAUSE, writes PFCC, updates software pause bits, and rolls headroom back on failure. Stats collection builds string arrays from several PPCNT counter groups, per-priority counters, per-TC counters, PTP ops, and transceiver overheat counters, then queries PPCNT groups to fill values. Link ksettings query reads PTYS, converts supported/admin/oper protocol masks through generation-specific ops, and sets port connector type. Link ksettings set converts requested autoneg advertisement or forced speed/lanes back to PTYS masks, intersects with capabilities, writes PTYS, records autoneg state, and toggles admin status if the netdev is running.

## State and Persistence Behavior
Software state updated here includes `mlxsw_sp_port->link.rx_pause`, `tx_pause`, `autoneg`, and module overheat baseline-derived statistics. Hardware state is accessed through PTYS, PFCC, PDDR, PPCNT, MLCR, module EEPROM/power environment helpers, and module reset commands. Link-mode operation tables are static and selected by device generation.

## Dependencies and Integration Points
The file depends on Linux ethtool APIs, Spectrum register helpers, `core_env` module-management helpers, PTP ops, buffer headroom functions, DCB PFC state, netdev carrier/admin status, and generation-specific Spectrum core setup that chooses the correct `port_type_speed_ops`.

## Risks and Edge Cases
Pause and PFC are mutually exclusive across this file and `spectrum_dcb.c`. Link-mode conversion must respect port lane width; Spectrum-2 forced speed selection differs when userspace specifies lane count versus speed only. `mlxsw_sp2_from_ptys_link_mode()` uses a representative ethtool bit from each mask list, so table ordering matters. Many stats silently remain zero on register query errors. Extended link state returns `-ENODATA` when link is up, status opcode is zero, or the firmware opcode is unmapped.

## Test Signals
Signals include `ethtool -i`, `ethtool -a/-A`, `ethtool -S`, `ethtool --show-eee` absence expectations, `ethtool -k` unaffected operation, `ethtool <dev>` link mode reports for Spectrum-1 and Spectrum-2+, forced speed/lane changes, module EEPROM and power-mode commands, RMON/MAC/PHY stats, LED identify, link-down extended-state mapping, and PTP stats count consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_fid.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_fid.c

## Purpose
`spectrum_fid.c` manages Spectrum forwarding identifiers. It allocates, indexes, references, configures, and tears down 802.1Q FIDs, 802.1D bridge FIDs, router FIDs, and a dummy FID; maintains FID and VNI lookup tables; programs FID-to-RIF, VID/VNI-to-FID, port-VID-to-FID, egress VID, flooding, and router-port mappings; and abstracts Spectrum-1 controlled flooding versus Spectrum-2 controlled or CFF flood modes.

## Important APIs, Types, and Functions
Core types include `struct mlxsw_sp_fid_core`, `struct mlxsw_sp_fid`, `struct mlxsw_sp_fid_family`, `struct mlxsw_sp_fid_ops`, `struct mlxsw_sp_fid_flood_profile`, and family-specific 802.1Q/802.1D wrappers. Public APIs include FID lookup/get/put functions, VNI and NVE flood-index setters, RIF set/unset, flood membership updates, port VID map/unmap, FID type/index/RIF accessors, per-port FID init/fini, LAG join/leave hooks, and `mlxsw_sp{1,2}_fid_core_ops`.

## Control Flow
Core initialization allocates `fid_core`, initializes rhashtables for FID index and VNI, allocates per-port mapping counters, registers each family template, allocates PGT ranges for flood-capable families, and initializes flood tables or CFF flood profiles. `mlxsw_sp_fid_get()` first searches the family list using the family compare op; otherwise it allocates the family-specific object, allocates an index, sets up family-private fields, programs hardware through the family configure op, inserts into the rhashtable, links into the family list, and sets the refcount. `mlxsw_sp_fid_put()` reverses this when the refcount reaches zero. Port VID mapping writes SVFA mappings, egress VID mappings through SMPE/REIV, tracks ordered `(local_port, vid)` entries, and transitions ports between VLAN and virtual-port mode when the first or last port-VID-to-FID mapping appears. RIF set updates SFMR, VNI mapping, VID mappings, and REIV entries with rollback.

## State and Persistence Behavior
Software state is in `mlxsw_sp->fid_core`, family bitmaps/lists, FID refcounts, VNI and FID rhashtables, `port_fid_mappings[]`, per-FID port/VID lists, VNI validity, NVE flood-index validity, and current RIF pointer. Hardware state is persisted through SFMR, SVFA, SMPE, REIV, SFGC, SFFP, and PGT programming until FID teardown or reset. CFF profile programming is global during Spectrum-2 initialization.

## Dependencies and Integration Points
The file integrates with bridge VLAN and FDB offload (`br_fdb_clear_offload()`), NVE/VXLAN support, router/RIF objects, port VLAN lists, LAG state, PGT helpers, core flood-mode selection, resource limits such as max ports/LAGs/NVE flood profiles, and Spectrum register helpers.

## Risks and Edge Cases
FID setup spans multiple hardware tables with rollback paths that must keep software lists, bitmaps, and rhashtables consistent. VNI insertion happens before hardware programming and must be removed on failure. Port virtual-mode transitions touch every existing VLAN on the port and can fail mid-transition. Ordered `port_vid_list` is relied on by REIV page updates. RFID CFF placement depends on port and LAG offsets, including CPU-port exclusion. Teardown warns if port VID mappings remain. Flood profile IDs must be valid for firmware limits.

## Test Signals
Signals include bridge VLAN creation/removal, VLAN-aware and VLAN-unaware bridge FIDs, router interface creation on VLAN/FID/subport paths, VXLAN VNI association and FDB offload clearing, unknown unicast/multicast/broadcast flooding behavior, port LAG join/leave, Spectrum-1 controlled flood mode and Spectrum-2 CFF/controlled modes, FID refcount teardown without WARNs, and hardware table programming failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_fid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flow.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flow.c

## Purpose
`spectrum_flow.c` bridges Linux TC block offload plumbing to Spectrum ACL flower and matchall/mall offload handlers. It creates and tracks per-block driver state, binds shared TC blocks to Spectrum ports on ingress or egress, dispatches classifier commands, and tears down flow-block state when TC releases the block callback.

## Important APIs, Types, and Functions
Public functions are `mlxsw_sp_flow_block_create()`, `mlxsw_sp_flow_block_destroy()`, and `mlxsw_sp_setup_tc_block_clsact()`. Important helpers include flow-block binding lookup, bind/unbind, mall callback dispatch, flower callback dispatch, the common `mlxsw_sp_flow_block_cb()`, and `mlxsw_sp_tc_block_release()`. A static global `mlxsw_sp_block_cb_list` is used as the TC driver block list.

## Control Flow
On `FLOW_BLOCK_BIND`, the code looks up an existing `flow_block_cb` for the TC block and Spectrum instance. If none exists, it allocates a new `mlxsw_sp_flow_block`, allocates a TC callback wrapper, and marks it for registration. It increments the callback refcount, validates ingress/egress blocker rule counts, binds mall state to the port, allocates a binding record, optionally binds existing ACL rulesets to the new port binding, updates ingress or egress binding counts, stores the block pointer in the port, and registers the callback in TC and the global driver list if this was the first binding. On `FLOW_BLOCK_UNBIND`, it clears the port pointer, removes the binding, unbinds rulesets and mall state, decrements the TC callback refcount, and removes/frees the callback when the last binding goes away.

## State and Persistence Behavior
State is in allocated `mlxsw_sp_flow_block` objects, their binding lists, mall state, ruleset status, ingress/egress binding counts, blocker rule counts, TC `flow_block_cb` refcounts, and per-port ingress/egress flow-block pointers. It persists only while TC blocks are bound. Hardware ACL/mall state is owned by called flower/mall helpers.

## Dependencies and Integration Points
The file integrates with Linux TC block offload APIs, `flow_block_cb` reference management, clsact ingress/egress setup, Spectrum ACL rulesets, flower offload functions, and matchall/mall handlers. Extack messages are used to explain unsupported bind directions when blocker rules exist.

## Risks and Edge Cases
Shared blocks can bind to multiple ports and directions, so refcounting and binding-count accounting must stay exact. Unsupported rules tracked by ingress/egress blocker counts prevent later binding in that direction. Bind failure after callback incref must correctly free an unregistered callback when appropriate. Unbind tolerates missing callbacks but ignores unbind errors except for refcount removal. Destroy warns if bindings still exist.

## Test Signals
Signals include TC flower replace/destroy/stats/template commands, matchall mirror/police actions through mall handlers, shared block binding to multiple ports, ingress and egress clsact binding and unbinding, extack messages for blocked directions, and no leaked `flow_block_cb` or WARNs after qdisc removal and port teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flow.c -->
