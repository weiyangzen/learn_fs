# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.h

## Purpose

`pci_irq.h` is the private header for mlx5 PCI IRQ pool internals. It defines IRQ naming limits, the EQ-reference accounting multiplier, the IRQ pool structure, the SF-pool classifier, and low-level IRQ object functions used by `pci_irq.c` and IRQ affinity code.

## Important APIs, Types, and Functions

The key type is `struct mlx5_irq_pool`, containing a fixed prefix name, xarray index limits, a mutex serializing IRQ creation/destruction, the IRQ xarray, min/max sharing thresholds expressed in EQ references, optional per-CPU SF accounting, and the owning `mlx5_core_dev`. The opaque `struct mlx5_irq` and `struct cpu_rmap` declarations allow consumers to hold IRQ handles without seeing object layout.

Declared functions are `mlx5_irq_alloc()`, `mlx5_irq_get_locked()`, `mlx5_irq_read_locked()`, `mlx5_irq_put()`, and `mlx5_irq_get_pool()`. The inline `mlx5_irq_pool_is_sf_pool()` classifies pools whose name begins with `mlx5_sf`.

## Control Flow

This header has no runtime control flow, but its contract assumes callers hold `pool->lock` when using the `_locked` helpers and that pool indexes are bounded by `xa_num_irqs`. The name and formatted-name constants are used to keep Linux IRQ names inside fixed buffers while appending PCI identity.

## State and Persistence Behavior

The header defines the persistent pool fields that back the IRQ lifecycle: xarray contents, lock, thresholds, and per-CPU accounting. It does not allocate storage itself.

## Dependencies and Integration Points

It depends on `linux/mlx5/driver.h` for `struct mlx5_core_dev` and on Linux xarray/mutex types through included driver headers. It is consumed by `pci_irq.c` and any lower-level affinity helper that needs to inspect or increment IRQ refcounts under the pool lock.

## Risks and Test Signals

`mlx5_irq_pool_is_sf_pool()` uses a string prefix convention rather than an explicit enum, so new SF pool names must retain the `mlx5_sf` prefix. Compile testing should cover `CONFIG_MLX5_SF` and non-SF builds, and lockdep should validate that `_locked` helpers are called under `pool->lock`.
