# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mcg.c

## Purpose
`mcg.c` provides simple exported firmware-command wrappers to attach and detach queue pairs from InfiniBand multicast groups on mlx5 devices.

## Important APIs, types, and functions
The file exports `mlx5_core_attach_mcg()` and `mlx5_core_detach_mcg()`. Both take `struct mlx5_core_dev *`, an InfiniBand multicast GID (`union ib_gid *mgid`), and a QP number. They fill the corresponding firmware command input layout and execute the command.

## Control flow
Attach zeroes the command input, sets opcode `MLX5_CMD_OP_ATTACH_TO_MCG`, sets `qpn`, copies the multicast GID into the command payload, and calls `mlx5_cmd_exec_in()`. Detach follows the same pattern with opcode `MLX5_CMD_OP_DETACH_FROM_MCG`.

## State and persistence behavior
The file stores no software state. Successful commands mutate firmware multicast group membership for the specified QP until detached or the HCA is reset/teardown.

## Dependencies and integration points
It depends on RDMA `ib_verbs.h`, mlx5 command execution, and generated command layouts. It is used by RDMA/core mlx5 consumers that need multicast group membership management.

## Risks and edge cases
There is no local validation of QP number or GID; firmware enforces validity. Attach/detach imbalance can leave multicast membership active or cause detach failures. Command errors are returned directly to callers.

## Test signals
RDMA multicast join/leave tests, invalid QPN/GID command failures, repeated attach/detach, and unload/reset cleanup of multicast memberships provide coverage.
