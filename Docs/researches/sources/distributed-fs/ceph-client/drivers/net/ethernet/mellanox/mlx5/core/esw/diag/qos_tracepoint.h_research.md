# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/diag/qos_tracepoint.h

Purpose: Defines tracepoints for mlx5 eswitch QoS scheduling element create/config/destroy events.

Important APIs/types/functions: Events include `mlx5_esw_vport_qos_create`, `mlx5_esw_vport_qos_config`, `mlx5_esw_vport_qos_destroy`, `mlx5_esw_node_qos_create`, `mlx5_esw_node_qos_config`, and `mlx5_esw_node_qos_destroy`. Trace payloads capture device name, vport id, scheduling element index, bandwidth share, max rate, parent pointer, node pointer, and TSAR index.

Control flow and integration: `qos.c` defines `CREATE_TRACE_POINTS` before inclusion. Tracepoints call `mlx5_esw_qos_vport_get_sched_elem_ix()` and `mlx5_esw_qos_vport_get_parent()`, so QoS code must provide those helpers and call tracepoints while vport/node state is valid.

State and persistence: No persistent state is stored by the tracepoint header. It snapshots QoS node/vport fields for ftrace/perf consumers.

Dependencies and risks: Depends on `eswitch.h`, `qos.h`, tracepoint infrastructure, and valid QoS state at call sites. Risks include stale helper assumptions during teardown and trace ABI churn. Test signals include enabling mlx5 QoS trace events while setting devlink rates, creating/deleting rate nodes, and moving parents.
