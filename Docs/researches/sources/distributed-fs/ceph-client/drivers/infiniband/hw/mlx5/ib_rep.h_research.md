# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.h

## Purpose
`ib_rep.h` is the small public interface between mlx5 RDMA core code and representor support. It exposes representor initialization, cleanup, raw Ethernet profile access, netdev lookup, and send-to-vport rule creation while compiling to no-op stubs when `CONFIG_MLX5_ESWITCH` is disabled.

## Important APIs, Types, And Functions
The header declares `extern const struct mlx5_ib_profile raw_eth_profile`, `mlx5r_rep_init()`, `mlx5r_rep_cleanup()`, `create_flow_rule_vport_sq()`, and `mlx5_ib_get_rep_netdev()`. The function signatures use `struct mlx5_ib_dev`, `struct mlx5_ib_sq`, `struct mlx5_eswitch`, `struct mlx5_flow_handle`, and `struct net_device`.

## Control Flow
There is no runtime control flow beyond conditional compilation. With eswitch support enabled, callers link to `ib_rep.c`. Without eswitch support, initialization returns success, cleanup is empty, flow-rule creation returns `NULL`, and representor netdev lookup returns `NULL`.

## State And Persistence Behavior
The header owns no state. It determines whether representor state is reachable at compile time. The stub behavior makes non-eswitch builds treat representor features as absent rather than failing module initialization.

## Dependencies And Integration Points
It includes `<linux/mlx5/eswitch.h>` and `mlx5_ib.h`, making it part of the mlx5 RDMA driver's internal ABI. `main.c` uses `raw_eth_profile` and module-level `mlx5r_rep_init()/cleanup()`. QP/raw-packet flow paths use `create_flow_rule_vport_sq()`.

## Risks
Stubs returning `NULL` rely on callers interpreting `NULL` as "feature absent/no flow rule needed". Any caller that treats `NULL` as success with a required representor rule can silently skip steering. The include relationship also means changes in `mlx5_ib.h` can affect this header's users broadly.

## Test Signals
Build coverage with `CONFIG_MLX5_ESWITCH=y` and disabled, plus raw packet representor traffic tests in enabled builds and module load tests in disabled builds.
