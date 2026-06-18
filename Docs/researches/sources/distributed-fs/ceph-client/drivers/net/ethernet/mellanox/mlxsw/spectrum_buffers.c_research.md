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
