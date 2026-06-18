# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/mlx5_ifc_vhca_event.h

## Purpose

`sf/mlx5_ifc_vhca_event.h` defines firmware interface layouts for querying and modifying VHCA state. It is the local IFC extension used by SF/VHCA event code.

## Important APIs and Types

`enum mlx5_ifc_vhca_state` defines firmware states: INVALID, ALLOCATED, ACTIVE, IN_USE, and TEARDOWN_REQUEST. `struct mlx5_ifc_vhca_state_context_bits` contains `arm_change_event`, `vhca_state`, and `sw_function_id`. Query and modify command input/output bit structs define opcode, UID, op_mod, embedded CPU flag, function id, field select bits, and the state context.

## Control Flow and State

The header has no executable flow. Its bit layouts are consumed by `vhca_event.c`, `sf/hw_table.c`, and `sf/devlink.c` via `MLX5_SET()`/`MLX5_GET()` macros to arm events, read states, and set user-visible software function ids.

## Dependencies and Integration Points

It is tightly coupled to firmware command opcodes `QUERY_VHCA_STATE` and `MODIFY_VHCA_STATE`. It integrates with devlink SF state, hardware table deferred free, and auxiliary SF device discovery.

## Risks and Test Signals

Any mismatch with firmware layout would corrupt event arming or state decoding. Validate by querying all expected states on real firmware, checking `sw_function_id` round trips after allocation, and ensuring field select bits modify only intended fields.
