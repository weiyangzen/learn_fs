# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.c

## Purpose

`reporter_vnic.c` implements a devlink health reporter named `vnic` that diagnoses vNIC environment counters and optional ICM consumption.

## Important APIs, Types, and Functions

- `mlx5_reporter_vnic_create()` / `mlx5_reporter_vnic_destroy()` manage the devlink health reporter in `dev->priv.health.vnic_reporter`.
- `mlx5_reporter_vnic_diagnose_counters()` issues `QUERY_VNIC_ENV` for a vport and writes supported counters into a devlink fmsg.
- `mlx5_reporter_vnic_diagnose_counter_icm()` reads `NIC_CAP` and `VHCA_ICM_CTRL` to expose ICM consumption when supported.
- `mlx5_reporter_vnic_diagnose()` is the reporter diagnose callback for the local vport.

## Control Flow

Diagnose builds a command input for vport 0 or a requested other vport, executes `query_vnic_env`, starts a nested fmsg object, then conditionally emits counters based on `MLX5_CAP_GEN()` feature bits. ICM reporting first checks `nic_cap_reg`, reads whether `vhca_icm_ctrl` is available, resolves vport to VHCA ID for other-vport mode, and reads current allocated ICM.

## State and Persistence Behavior

Persistent state is limited to the reporter pointer in health state. Counter data is sampled on demand and emitted to devlink messages; it is not cached.

## Dependencies and Integration Points

Depends on devlink health reporter APIs, mlx5 command interface, vport VHCA lookup, `en_stats.h` counter macros, and core devlink access. It integrates with core health reporter creation/destruction.

## Risks and Edge Cases

- `mlx5_cmd_exec_inout()` return value in `mlx5_reporter_vnic_diagnose_counters()` is ignored, so failed `QUERY_VNIC_ENV` can produce zero/default output.
- devlink fmsg helper return values are ignored, consistent with many reporters but less robust under message construction failures.
- Other-vport ICM reporting depends on successful vport-to-VHCA lookup.

## Test Signals

Run `devlink health diagnose` for the vNIC reporter across devices with different counter capabilities. Inject command failures and verify logs/output behavior. Test other-vport counter export through callers that pass `other_vport=true`.
