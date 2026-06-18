# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.h

Purpose: Declares the mlx5 Geneve TLV option object API.

Important APIs and types: Forward-declares opaque `struct mlx5_geneve` and exports create/destroy plus TLV option add/delete when `CONFIG_MLX5_ESWITCH` is enabled. Without eswitch support, create returns NULL, destroy/delete are no-ops, and add returns success.

State and dependencies: Depends on `<net/geneve.h>` for `struct geneve_opt` and mlx5 driver types. The API hides firmware object ID and refcount details.

Risks and test signals: Stub behavior means callers must not treat a NULL object as fatal in non-eswitch builds. Build tests should cover both branches and ensure add/delete pairing in offload users.
