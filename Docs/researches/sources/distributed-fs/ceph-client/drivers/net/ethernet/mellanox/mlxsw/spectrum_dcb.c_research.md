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
