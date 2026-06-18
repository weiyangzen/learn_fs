# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_irq.h

## Purpose
`mlx5_irq.h` declares the mlx5 IRQ table, IRQ pool, vector request/release, notifier, affinity, and MSI-X vector-count APIs used by EQ, completion, SF, and SR-IOV code.

## Important APIs, types, and functions
The header defines `MLX5_COMP_EQS_PER_SF`, forward-declares IRQ and pool types, and declares table lifecycle (`mlx5_irq_table_init/create/destroy/cleanup/free_irqs`), pool/vector accessors, MSI-X vector-count helpers, control/completion IRQ request/release, notifier attach/detach, IRQ affinity mask/index/number getters, and SF affinity request helpers. When `CONFIG_MLX5_SF` is disabled, affinity helpers return `-EOPNOTSUPP` or fall back to normal release.

## Control flow
The header itself has only stub control flow for non-SF builds. Runtime users initialize the IRQ table, create vectors during device load, request vectors for EQs or completion queues, attach notifier blocks, and release vectors during unload.

## State and persistence behavior
No state is stored in the header. IRQ state is owned by implementation files and connected to `struct mlx5_core_dev` and `struct mlx5_irq_table`.

## Dependencies and integration points
It depends on mlx5 driver types, Linux notifier blocks, CPU masks, IRQ affinity descriptors, and optional SF support. It integrates IRQ allocation with EQ creation, SF scheduling, SR-IOV MSI-X configuration, and netdev/RDMA completion paths.

## Risks and edge cases
Callers must balance vector requests/releases and notifier attach/detach. Disabled SF builds return error pointers for affinity requests, so callers need robust fallback. MSI-X count changes for VFs must coordinate with PCI/SR-IOV state.

## Test signals
Test IRQ table init/create/destroy across probe/unload, control IRQ request/release, completion vector allocation, notifier delivery and detach, CPU affinity behavior, SF affinity on enabled builds, non-SF stubs, and SR-IOV MSI-X vector-count get/set.
