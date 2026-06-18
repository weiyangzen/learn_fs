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
