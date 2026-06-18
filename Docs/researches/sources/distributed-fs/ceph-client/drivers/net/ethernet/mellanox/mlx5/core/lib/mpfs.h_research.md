# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.h

## Purpose
`mpfs.h` defines the internal MAC-address hash helpers and public MPFS lifecycle hooks for mlx5 L2 table steering. It also provides no-op stubs when `CONFIG_MLX5_MPFS` is disabled.

## Important APIs, types, and functions
The header defines `MLX5_L2_ADDR_HASH_SIZE`, `MLX5_L2_ADDR_HASH()`, `struct l2addr_node`, iteration macros `mlx5_mpfs_foreach()` and `for_each_l2hash_node()`, and allocation/search/delete macros `l2addr_hash_find()`, `l2addr_hash_add()`, and `l2addr_hash_del()`. Public MPFS functions are declared or stubbed: `mlx5_mpfs_init()`, `mlx5_mpfs_cleanup()`, `mlx5_mpfs_enable()`, and `mlx5_mpfs_disable()`.

## Control flow
This header contributes macro-expanded control flow for hash users. Hash lookup uses the last MAC byte as a bucket and scans with `hlist_for_each_entry()`. Hash add allocates a typed node, copies the address, and inserts at the bucket head. Delete removes the hlist node and frees the containing object.

## State and persistence behavior
No state is owned by the header. It defines the layout convention used by MPFS nodes: any typed node must embed `struct l2addr_node node`. Hashing by the last MAC byte is simple and stable but not cryptographic or balanced for adversarial input.

## Dependencies and integration points
The header depends on Linux Ethernet address helpers, hlist, allocation helpers, and mlx5 device declarations. It is consumed by `mpfs.c` and can support other mlx5 L2-address hash users that embed the same node shape.

## Risks and edge cases
The hash macros are type-sensitive and assume the caller's struct has a member named `node`. They perform allocation/free directly, so callers must avoid double free and must serialize access externally. A single-byte hash can cluster addresses with common low bytes. Stubbed builds return success for init/enable and do nothing for cleanup/disable, so callers must tolerate MPFS absence.

## Test signals
Build both `CONFIG_MLX5_MPFS` enabled and disabled. Runtime coverage comes through MPFS add/delete/replay tests, hash collision behavior, cleanup with all nodes removed, and static analysis for macro users that embed the expected member names.
