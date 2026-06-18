# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.h

## Purpose
This header declares the mlx5 IB counters subsystem interface used by the rest of the mlx5 RDMA driver.

## Important APIs, types, and functions
Declared functions include `mlx5_ib_counters_init`, `mlx5_ib_counters_cleanup`, `mlx5_ib_counters_clear_description`, `mlx5_ib_flow_counters_set_data`, `mlx5_ib_get_counters_id`, and `mlx5r_is_opfc_shared_and_in_use`. The header includes `mlx5_ib.h` for device, counter, and flow-counter types.

## Control flow
There is no executable flow. Callers use this interface during device initialization/cleanup, QP setup requiring a counter id, flow creation with user counters, and optional operational flow counter sharing.

## State and persistence behavior
The header owns no state. It defines access to runtime state managed by `counters.c`: firmware Q counter ids, descriptor arrays, flow counters, per-QP counter bindings, and user flow-counter descriptions.

## Dependencies and integration points
It is the internal boundary between general mlx5 IB code and the counters implementation. It ties flow creation, QP configuration, and device lifecycle to the stats subsystem.

## Risks
The main risks are prototype drift with `counters.c`, exposing helper semantics that depend on shared operational flow-counter lifetime, and callers assuming a valid counter id before `mlx5_ib_counters_init` has allocated one.

## Test signals
Compile all mlx5 IB configurations and exercise device init/cleanup, QP counter id retrieval, flow counter setup, and operational counter sharing paths.
