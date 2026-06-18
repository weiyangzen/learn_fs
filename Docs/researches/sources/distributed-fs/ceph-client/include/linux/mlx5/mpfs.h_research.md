# sources/distributed-fs/ceph-client/include/linux/mlx5/mpfs.h

## Purpose
This header declares the mlx5 MPFS MAC filtering hook used by other mlx5 components to add or remove MAC addresses from firmware-managed multi-physical-function steering/filtering state. It also provides no-op stubs when `CONFIG_MLX5_MPFS` is disabled.

## Important APIs, Types, And Data
- `struct mlx5_core_dev` is forward-declared to avoid including the full driver header.
- `mlx5_mpfs_add_mac(struct mlx5_core_dev *dev, u8 *mac)` registers a MAC address for the device when MPFS is enabled.
- `mlx5_mpfs_del_mac(struct mlx5_core_dev *dev, u8 *mac)` removes the registered MAC address.
- Disabled-config inline stubs return 0, making callers independent of the build option.

## Control Flow
Callers invoke add during netdev/vport setup and delete during teardown or address change. Under `CONFIG_MLX5_MPFS`, implementation code performs actual firmware or steering table updates. Without MPFS, calls succeed without side effects.

## State And Persistence
When enabled, MPFS state is expected to live in the mlx5 device/firmware or driver-private steering tables. The header itself stores nothing. Disabled builds persist no MPFS state and treat every add/delete as successful.

## Dependencies And Integration Points
The API integrates with mlx5 core device lifecycle and Ethernet address management. It depends on the Kconfig symbol `CONFIG_MLX5_MPFS` and `u8` from kernel integer typedefs.

## Risks
The no-op fallback can hide missing filtering behavior in configurations that expected hardware MPFS enforcement. Callers must ensure MAC pointers reference at least `ETH_ALEN` bytes and have stable contents for the duration of the call. Enabled implementations must handle duplicate adds and deletes of absent MACs consistently.

## Test Signals
Compile both enabled and disabled MPFS configurations. Runtime tests should verify MAC filter programming on enabled hardware, duplicate add/delete behavior, teardown cleanup, and that disabled builds do not fail callers that treat MPFS as optional.
