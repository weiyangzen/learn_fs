# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.h

## Purpose

`devlink.h` is the internal contract for mlx5 core devlink IDs, trap state, devlink allocation, param registration, and trap operations. It also exposes the inline helper used by auxiliary-device support checks to determine whether Ethernet is enabled by devlink driver-init state.

## Important APIs, Types, and Functions

- `enum mlx5_devlink_resource_id` and `enum mlx5_devlink_port_resource_id` define resource identifiers for SF counts.
- `enum mlx5_devlink_param_id` reserves vendor param IDs after generic devlink IDs.
- `struct mlx5_trap_ctx`, `struct mlx5_devlink_trap`, and `struct mlx5_devlink_trap_event_ctx` model trap action state and notifier payload.
- Prototypes cover trap registration/reporting/action lookup, devlink allocation/free, and param registration/unregistration.
- `mlx5_core_is_eth_enabled()` reads `DEVLINK_PARAM_GENERIC_ID_ENABLE_ETH` driver-init value and returns false on lookup failure.

## Control Flow

Callers include this header to register core devlink objects early in PCI/core-device setup, then register params and traps after devlink exists. Trap consumers use the action getters/report helper while lower layers send notifier events on action changes.

## State and Persistence Behavior

The header itself has no storage, but its contracts mutate devlink param state and `dev->priv.traps`. The Ethernet-enable helper depends on devlink driver-init value state.

## Dependencies and Integration Points

It depends on `<net/devlink.h>`, `struct mlx5_core_dev`, and `priv_to_devlink()`. It is used by core devlink implementation, auxiliary-device support checks, Ethernet, eswitch, and trap producers.

## Risks and Edge Cases

- Vendor param enum order is ABI-sensitive inside the driver; new IDs should be appended carefully.
- `mlx5_core_is_eth_enabled()` treats read failure as disabled, which is conservative but can suppress Ethernet aux creation if params are not registered yet.
- Trap action is stored as `int` in `struct mlx5_trap_ctx` while most callers use `enum devlink_trap_action`.

## Test Signals

Compile all users after adding params/traps. Validate devlink params are registered before `mlx5_core_is_eth_enabled()` is used for aux-device creation. Exercise trap action get/report paths.
