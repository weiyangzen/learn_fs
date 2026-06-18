# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.c

## Purpose
This file implements mlx5 RDMA statistics and counters support. It allocates device/port Q counters, builds RDMA hw stats descriptors, reads queue, congestion, PPCNT, vport, and optional operational flow counters, implements RDMA per-QP counter binding, and supports user flow counters attached to flow steering.

## Important APIs, types, and functions
Public functions are `mlx5_ib_counters_init`, `mlx5_ib_counters_cleanup`, `mlx5_ib_counters_clear_description`, `mlx5_ib_flow_counters_set_data`, `mlx5_ib_get_counters_id`, and `mlx5r_is_opfc_shared_and_in_use`. Important local types include `struct mlx5_ib_counter` descriptor templates and `struct mlx5_rdma_counter`, which extends `rdma_counter` with operational flow counters and a QPN xarray. Major helpers include `mlx5_ib_read_counters`, `mlx5_ib_query_q_counters`, `mlx5_ib_query_q_counters_vport`, `mlx5_ib_query_ext_ppcnt_counters`, `do_get_hw_stats`, `do_get_op_stat`, `do_per_qp_get_op_stat`, `mlx5_ib_counter_bind_qp`, `mlx5_ib_counter_unbind_qp`, `mlx5_ib_modify_stat`, `mlx5_ib_alloc_counters`, and `mlx5_ib_dealloc_counters`.

## Control flow
Initialization always registers generic ib counters ops, then, if firmware supports QP counters, registers hw stats ops for normal or switchdev mode and allocates per-port counter sets. Allocation computes descriptor counts based on capabilities, allocates descriptor/offset arrays, fills names and offsets, then allocates firmware Q counter sets. Switchdev allocates a real device counter set and an optional vport helper set.

Stats reads select the correct counter set through `get_counters`. Q counters are read with `QUERY_Q_COUNTER`; vport representors use `other_vport` and aggregation; extended PPCNT uses `mlx5_core_access_reg` on `MLX5_REG_PPCNT`; congestion counters use `mlx5_lag_query_cong_counters` from the native port mdev. Optional operational counters are flow counters created on demand by `modify_hw_stat`; packet and byte pairs may share the same flow counter object. Per-QP RDMA counters allocate a Q counter lazily during bind, set the QP counter id, optionally bind operational flow counters to the QP through flow steering, update stats by querying both Q counters and per-QP flow counters, and undo bindings on unbind/dealloc.

User flow counters are created through `mlx5_ib_flow_counters_set_data`: optional userspace descriptions map packet/byte hardware slots to user buffer indices, a flow counter object is created if needed, and read operations query packet/byte values and place them by description index.

## State and persistence behavior
Driver state includes per-port `mlx5_ib_counters` arrays of stat descriptors, offsets, firmware Q counter ids, and operational flow-counter handles/rules. Per-QP state includes an RDMA counter id, stats buffer, optional flow counters, and a QPN xarray. User flow counters store descriptions and a hardware flow counter handle. All state is runtime firmware/kernel state and is destroyed during cleanup, dealloc, or flow counter destruction.

## Dependencies and integration points
This file integrates with RDMA core `ib_device_ops`, `rdma_hw_stats`, `rdma_counter`, mlx5 firmware Q counters, PPCNT registers, LAG congestion counter queries, eswitch representors/vports, flow steering operational counters, QP counter assignment, uverbs flow counter ABI data, and capability macros.

## Risks
Risk areas include descriptor count/offset mismatches, switchdev port-index selection, optional stat enable/disable sharing semantics, QP bind rollback when flow-counter binding fails, per-QP xarray cleanup, flow counter description lifetime under `usecnt`, counter id leaks on partial allocation, and inconsistent handling of byte versus packet counters. Capability-conditioned arrays must remain aligned with descriptor counts or stats indices will be wrong.

## Test signals
Cover normal and switchdev stats allocation, stats reads with each capability combination, vport representor aggregation, congestion and PPCNT counters, optional stat enable/disable including shared packet/byte counters, per-QP counter bind/unbind/update/dealloc, user flow counters with valid and invalid descriptions, failure injection for Q counter and flow counter allocation, and cleanup leak checks.
