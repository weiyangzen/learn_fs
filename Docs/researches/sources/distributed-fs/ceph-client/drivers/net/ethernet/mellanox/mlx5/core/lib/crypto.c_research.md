# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/crypto.c

Purpose: Manages mlx5 encryption key objects, including direct one-key creation and pooled bulk DEK allocation for TLS/IPsec/MACsec/PSP offloads.

Important APIs and flow: `mlx5_create_encryption_key()` and `mlx5_destroy_encryption_key()` wrap direct firmware general-object create/destroy. `mlx5_crypto_dek_init()` enables bulk DEK support when crypto caps expose `log_dek_max_alloc`, runs `SYNC_CRYPTO`, and stores the bulk object range. `mlx5_crypto_dek_pool_create()` initializes per-purpose pool lists/work. `mlx5_crypto_dek_create()` either creates a direct key or pops a free object offset from a bulk and modifies it with key material. `mlx5_crypto_dek_destroy()` returns pooled keys; a sync work item revalidates freed keys and a destroy work item frees excess idle bulks.

State and dependencies: Pools track total, available, and in-use counts plus partial/full/available/sync/wait/destroy lists. Bulks track base object ID, bitmaps for `in_use` and `need_sync`, and availability cursor. Locks are a mutex for pool lists and a spinlock for destroy-list transfer. The code depends on mlx5 command execution, encryption key object layout, PDN from `mlx5e_res`, workqueues, bitmaps, and secure stack zeroing of key material.

Risks and test signals: Key size is limited to 128 or 256 bits; 128-bit keys are placed in the second key slot. Pool correctness depends on bitmap state transitions and `SYNC_CRYPTO` thresholds. Tests should cover direct and pooled modes, invalid key sizes, command failures, pool exhaustion/add bulk, sync threshold behavior, destroy during pending work, wait-for-free handling, and no key leakage after modify/create commands.
