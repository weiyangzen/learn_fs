# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.h

## Purpose
This header declares the flow-steering-to-direct-rule bridge state embedded in generic FS objects and exposes the DR command table accessor when software steering is enabled.

## Important APIs, Types, And Functions
Wrapper structures are `mlx5_fs_dr_action`, `mlx5_fs_dr_rule`, `mlx5_fs_dr_domain`, `mlx5_fs_dr_matcher`, and `mlx5_fs_dr_table`. Public declarations under `CONFIG_MLX5_SW_STEERING` are `mlx5_fs_dr_is_supported()`, `mlx5_fs_dr_action_get_pkt_reformat_id()`, and `mlx5_fs_cmd_get_dr_cmds()`. The disabled-config stubs return unsupported/null values.

## Control Flow
No runtime flow is implemented here. Compile-time flow depends on `CONFIG_MLX5_SW_STEERING`: enabled builds use `fs_dr.c`; disabled builds compile stub functions so generic flow steering can call the accessors safely.

## State And Persistence
The wrapper structs persist DR pointers inside generic FS resources. `mlx5_fs_dr_rule` also stores an array of fs_dr-created actions and a count for reverse-order cleanup on delete.

## Dependencies And Integration Points
It includes public `mlx5dr.h` and forward-declares flow root namespace and FTE types. It is included by the flow steering core and by `fs_dr.c`.

## Risks
Incorrect ownership assumptions around `mlx5_fs_dr_rule.dr_actions` can leak or double-free DR actions. The stubs must continue to match enabled prototypes or disabled builds fail.

## Test Signals
Build both enabled and disabled `CONFIG_MLX5_SW_STEERING` configurations. Runtime tests should verify packet reformat ID retrieval and rule action cleanup through the stored wrappers.
