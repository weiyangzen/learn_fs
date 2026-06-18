# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/irq_affinity.c

## Purpose
`irq_affinity.c` implements IRQ allocation and sharing policy for mlx5 IRQ pools. It chooses IRQs based on requested CPU affinity masks, per-CPU load, pool refcount thresholds, and SF sysfs integration.

## Important APIs, Types, And Functions
- `cpu_get`, `cpu_put`, and `cpu_get_least_loaded` maintain `pool->irqs_per_cpu` load accounting and choose the least-loaded online CPU in a requested mask.
- `irq_pool_request_irq` allocates an xarray index, builds an automatic affinity descriptor when needed, and calls `mlx5_irq_alloc`.
- `irq_pool_find_least_loaded` finds an existing IRQ whose affinity mask is a subset of the requested mask and has the smallest refcount.
- `mlx5_irq_affinity_request` is the public request path.
- `mlx5_irq_affinity_irq_release` synchronizes, removes SF sysfs entries when needed, drops the IRQ refcount, and updates CPU accounting when the IRQ is freed.

## Control Flow And State
Request takes the pool mutex, searches existing IRQs, and reuses one below `min_threshold`. If no sufficiently light IRQ exists, it tries to allocate a new IRQ. If allocation fails but a matching existing IRQ exists, it shares that IRQ. It logs overload when refcount exceeds `max_threshold`. For SF pools, a successful request creates an auxiliary-device sysfs IRQ entry after releasing the pool lock; failure rolls back the IRQ reference.

## State And Persistence Behavior
State lives in the IRQ pool xarray, IRQ refcounts, affinity masks, per-CPU counters, and optional SF sysfs entries. IRQ objects persist while referenced by EQs or other users and are freed by `mlx5_irq_put` when the last reference drops.

## Dependencies And Integration Points
The file depends on mlx5 IRQ pool internals, PCI IRQ vector mapping, CPU masks, xarray allocation, auxiliary-device sysfs helpers for SFs, and `mlx5_irq_*` refcount/mask APIs. It integrates with EQ/channel allocation that requests IRQs for completion/control paths.

## Risks And Edge Cases
If a requested mask has no online CPUs, the code falls back to the first online CPU and logs an error. Per-CPU accounting must only decrement when the IRQ is actually freed. Auto affinity descriptor allocation and xarray allocation failure need rollback. Mask-subset matching means broad requested masks can share narrower IRQs, which is intentional but can surprise callers.

## Test Signals
Request IRQs with single-CPU and multi-CPU masks, no-online-CPU masks, allocation failures with and without reusable IRQs, min/max threshold behavior, SF sysfs add/remove rollback, and release after active interrupts with `synchronize_irq`.
