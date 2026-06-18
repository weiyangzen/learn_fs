# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.c

## Purpose

`qos.c` is the NIC QoS scheduling-element helper layer. It checks whether NIC SQ scheduling, bandwidth sharing, and rate limit capabilities are present, then creates, updates, and destroys root, inner, and leaf QoS nodes in the firmware scheduling hierarchy.

## Important APIs, Types, and Functions

The public helpers are `mlx5_qos_is_supported()`, `mlx5_qos_max_leaf_nodes()`, `mlx5_qos_create_leaf_node()`, `mlx5_qos_create_inner_node()`, `mlx5_qos_create_root_node()`, `mlx5_qos_update_node()`, and `mlx5_qos_destroy_node()`. Leaf nodes are firmware `QUEUE_GROUP` elements. Inner/root nodes are `TSAR` elements configured as DWRR. All operations use scheduling command wrappers from `rl.c`.

## Control Flow

Creation validates support for the desired element type and, for inner nodes, DWRR TSAR support. It fills a `scheduling_context` with parent id, element type, bandwidth share, and max average bandwidth, adds TSAR attributes for DWRR when needed, and calls `mlx5_create_scheduling_element_cmd()` in `SCHEDULING_HIERARCHY_NIC`. Update builds a context containing only bandwidth fields and passes a modify bitmask for `BW_SHARE` and `MAX_AVERAGE_BW`. Destroy calls the destroy scheduling command.

## State and Persistence Behavior

State is held by firmware scheduling elements identified by returned IDs. This file does not keep a local tree or reference counts, so callers own node lifetime, hierarchy ordering, and rollback.

## Dependencies and Integration Points

It depends on QoS capability macros, scheduling context layouts, and command wrappers in `rl.c`. It is used by higher-level mlx5e QoS and traffic-class code to build NIC queue group trees.

## Risks and Test Signals

Risks are mostly capability mismatches and caller-managed hierarchy leaks. Tests should cover devices without each QoS capability, root/inner/leaf create and destroy ordering, bandwidth update propagation, max leaf count from `log_max_qos_nic_queue_group`, and firmware errors during partial tree setup.
