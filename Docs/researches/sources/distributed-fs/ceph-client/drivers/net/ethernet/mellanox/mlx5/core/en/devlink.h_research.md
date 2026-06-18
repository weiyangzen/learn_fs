# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.h

## Purpose

`en/devlink.h` declares mlx5e nested devlink and devlink-port lifecycle helpers.

## Important APIs, Types, and Functions

- `mlx5e_create_devlink()` / `mlx5e_destroy_devlink()` manage nested devlink allocation/registration.
- `mlx5e_devlink_port_register()` / `mlx5e_devlink_port_unregister()` manage the netdev's devlink port.

## Control Flow

Ethernet netdev setup uses these declarations to create devlink representation before registering the port and netdev, then tears them down in reverse.

## State and Persistence Behavior

The implementation persists nested devlink and `devlink_port` state for the netdev lifetime.

## Dependencies and Integration Points

Depends on `<net/devlink.h>` and `en.h` for `struct mlx5e_dev`. Integrates mlx5e with core devlink hierarchy.

## Risks and Edge Cases

Callers must unregister the port before destroying the nested devlink and must keep `struct mlx5e_dev` lifetime tied to the devlink private storage.

## Test Signals

Compile netdev creation/destruction paths and verify devlink port registration/unregistration under PF and non-PF devices.
