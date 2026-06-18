# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mapping.h

Purpose: declares the mlx5e generic mapping context API for allocating stable ids for arbitrary fixed-size data blobs.

Important APIs/functions: opaque `struct mapping_ctx`; `mapping_add`, `mapping_remove`, `mapping_find`, `mapping_create`, `mapping_destroy`, and `mapping_create_for_id`.

Control flow: users create a context for a fixed data size and maximum id, add data to receive an id, later find data by id, and remove ids when offloaded state is no longer needed. `mapping_create_for_id` reuses a shared context for a hardware/software identity tuple.

State and persistence: describes xarray-backed id lookup, data hashing, RCU reads, and optional delayed removal to avoid hardware id reuse races.

Dependencies and integration: no heavy includes; consumers include it from TC/offload paths that store ids in firmware metadata registers.

Risks: callers must provide buffers of exactly the configured data size and balance add/remove calls.

Test signals: API users should test id allocation boundaries, duplicate data coalescing, and delayed-removal behavior.
