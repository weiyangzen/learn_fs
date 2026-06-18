# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/mod_hdr.c

Purpose: caches and manages mlx5 modify-header objects for TC offload actions, avoiding duplicate firmware objects for identical action sequences.

Important APIs/functions: `mlx5e_mod_hdr_tbl_init`, `mlx5e_mod_hdr_tbl_destroy`, `mlx5e_mod_hdr_attach`, `mlx5e_mod_hdr_detach`, `mlx5e_mod_hdr_get`, `mlx5e_mod_hdr_alloc`, `mlx5e_mod_hdr_dealloc`, and `mlx5e_mod_hdr_get_item`.

Control flow: attach builds a key from action bytes, looks in the table under a mutex, and either refcounts an existing handle or inserts a new handle before allocating the firmware modify-header object. A completion lets concurrent attachers wait for the first allocation result. Detach decrements the refcount and, for the final user, removes the hash entry, deallocates the firmware object if allocation succeeded, and frees the handle. The action-buffer allocator grows static or dynamic action arrays up to firmware namespace limits.

State and persistence: the table is in memory, keyed by copied action bytes and action count. Handles maintain refcount, firmware pointer, completion, and allocation result. No persistent state exists outside firmware objects.

Dependencies and integration: uses Linux hashtables/refcounts/completions and `mlx5_modify_header_alloc/dealloc`; namespace-specific limits come from FDB or NIC RX capabilities.

Risks: attach intentionally publishes an in-progress handle, so all error paths must complete and detach correctly. Static action arrays become dynamic after growth and must be deallocated only when `is_static` is false.

Test signals: identical concurrent attaches, firmware allocation failure, detach after failed attach, action-array growth from static and dynamic buffers, and max-action exhaustion.
