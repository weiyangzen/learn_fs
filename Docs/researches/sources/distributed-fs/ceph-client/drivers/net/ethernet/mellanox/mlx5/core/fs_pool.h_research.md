# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_pool.h

## Purpose
`fs_pool.h` declares the generic mlx5 flow-steering bulk pool abstraction. It lets resource-specific code supply bulk creation, destruction, and threshold policy while sharing bitmap/list accounting.

## Important APIs, Types, And Functions
- `struct mlx5_fs_bulk` contains a pool list node, number of units, and free-unit bitmap.
- `struct mlx5_fs_pool_index` returns a bulk pointer plus unit index to callers.
- `struct mlx5_fs_pool_ops` provides `bulk_create`, `bulk_destroy`, and `update_threshold` callbacks.
- `struct mlx5_fs_pool` stores the device, caller context, callback table, mutex, full/partial/unused lists, and available/used/threshold counters.
- Declared functions cover bulk init/bitmap/cleanup/free-count and pool init/cleanup/acquire/release.

## Control Flow And State
This header models ownership around a pool initialized once, repeatedly acquiring and releasing indexes, then cleaning up after users are gone. It intentionally does not define how a backend maps an index into a resource; the backend stores enclosing data around `struct mlx5_fs_bulk`.

## Dependencies And Integration Points
It depends on `linux/mlx5/driver.h` for device types and kernel primitives. The immediate integration point in this subset is `fs_counters.c`, which embeds `struct mlx5_fs_bulk` in `struct mlx5_fc_bulk` and maps pool indexes to flow counters.

## Risks And Edge Cases
Backends must ensure `bulk_destroy` can detect busy bulks, and users must keep the returned bulk/index valid until release. The pool is not RCU-safe; access is serialized by the internal mutex, but resource users outside acquire/release still need their own lifetime rules.

## Test Signals
Compile and runtime coverage should include at least one real backend, allocation failure paths, release error paths, threshold updates, and cleanup after complete drain.
