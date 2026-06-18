# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/devlink.c

## Purpose

`en/devlink.c` creates the nested devlink instance and devlink port used by mlx5e netdev instances.

## Important APIs, Types, and Functions

- `mlx5e_create_devlink()` allocates a nested devlink in the same net namespace as the parent core devlink, sets the parent/child relationship, registers it, and returns `struct mlx5e_dev`.
- `mlx5e_destroy_devlink()` unregisters and frees the nested devlink.
- `mlx5e_devlink_port_register()` sets physical or virtual port attributes and registers `mlx5e_dev->dl_port`.
- `mlx5e_devlink_port_unregister()` unregisters the port.
- `mlx5e_devlink_get_port_parent_id()` reads the NIC software system image GUID for switch ID.

## Control Flow

Netdev creation allocates a nested devlink with empty mlx5e-specific ops, links it under the core devlink with `devl_nested_devlink_set()`, and registers it. Port registration selects physical flavor for PFs and virtual flavor otherwise. PFs use device index as physical port number and, when eswitch manager, set switch ID from the system image GUID. Devlink port index is derived from eswitch vport index.

## State and Persistence Behavior

Persistent state includes the nested devlink object, `struct mlx5e_dev` private storage, and registered `devlink_port`. The `mlx5e_dev` stores the netdev pointer and devlink port.

## Dependencies and Integration Points

Depends on devlink nested APIs, mlx5 eswitch vport-to-port-index mapping, core devlink, system image GUID query, and `en/devlink.h`. It ties mlx5e netdevs to devlink port representation.

## Risks and Edge Cases

- `mlx5e_create_devlink()` returns `devlink_priv(devlink)` without initializing `mlx5e_dev->netdev`; callers must fill fields as needed.
- Parent nested-devlink setup failure must free the allocated devlink, which this code does.
- Port indexes depend on eswitch mapping helpers and must remain stable for userspace.

## Test Signals

Create PF and VF/SF mlx5e netdevs and inspect `devlink port show`. Verify nested devlink hierarchy, physical vs virtual flavor, switch ID in eswitch manager mode, and cleanup on netdev destroy.
