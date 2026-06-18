# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.h

Purpose: Declares mlx5 crypto key-purpose constants and APIs for encryption key creation, pooled DEK allocation, and bulk DEK subsystem lifecycle.

Important APIs and types: Enumerates accelerator key purposes for TLS, IPsec, MACsec, PSP, and count sentinel. Forward-declares `mlx5_crypto_dek_pool`, `mlx5_crypto_dek`, and `mlx5_crypto_dek_priv`. Exports direct key create/destroy, pool create/destroy, DEK create/destroy/get-id, and init/cleanup for bulk DEK support.

State and dependencies: The API hides pool internals from feature users; consumers receive `struct mlx5_crypto_dek *` and use `mlx5_crypto_dek_get_id()` for firmware object references. It depends on mlx5 core device definitions and general object key purpose constants.

Risks and test signals: Callers must pair create/destroy with the same pool and not retain IDs after destroy. Build users should validate all four key purposes and both direct and pooled feature availability paths.
