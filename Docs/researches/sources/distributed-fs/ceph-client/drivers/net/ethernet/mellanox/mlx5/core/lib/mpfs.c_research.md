# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.c

## Purpose
`mpfs.c` manages the mlx5 Multi-Physical Function Steering L2 table for MAC-address based receive steering. It keeps a software hash of requested unicast MAC addresses, programs hardware L2 table entries when enabled, reference-counts duplicate requests, and supports global enable/disable replay of all tracked entries.

## Important APIs, types, and functions
Public functions are `mlx5_mpfs_init()`, `mlx5_mpfs_cleanup()`, exported `mlx5_mpfs_add_mac()`, exported `mlx5_mpfs_del_mac()`, `mlx5_mpfs_enable()`, and `mlx5_mpfs_disable()`. Internal helpers `set_l2table_entry_cmd()` and `del_l2table_entry_cmd()` issue firmware commands. `struct mlx5_mpfs` stores the L2 hash, mutex, enabled flag, table size, and bitmap. `struct l2table_node` extends `struct l2addr_node` with hardware index and refcount.

## Control flow
Initialization runs only for eswitch managers with an L2 table larger than one entry. It allocates the state object and a bitmap sized from `log_max_l2_table`. Adding a MAC locks the table, finds an existing hash node or allocates a new one, allocates a hardware index when enabled, sends `SET_L2_TABLE_ENTRY`, and records index/refcount. Deletion decrements the refcount, and only on the final release sends `DELETE_L2_TABLE_ENTRY`, frees the bitmap bit, and removes the hash node. Enable replays all hashed MACs into hardware; disable removes all programmed indexes while retaining software hash entries.

## State and persistence behavior
State is volatile driver memory plus hardware L2 table entries. Software hash entries persist across `mlx5_mpfs_disable()` so addresses can be restored by `mlx5_mpfs_enable()`. Cleanup expects the hash to be empty and warns otherwise, then frees the bitmap and object.

## Dependencies and integration points
The file depends on mlx5 firmware command helpers, eswitch-manager capability checks, Ethernet address helpers, bitmap allocation, and hash helpers from `mpfs.h`. It is initialized in `main.c` during once-only mlx5 core initialization and used by upper mlx5 Ethernet/eswitch code that needs shared L2 table programming.

## Risks and edge cases
Enable replay can partially program entries and return an error without rolling back entries already reprogrammed during that pass. Delete ignores firmware delete errors, which favors cleanup progress but can hide hardware-table inconsistency. Index bitmap exhaustion returns `-ENOSPC`. Refcount imbalance causes leaked hardware entries or `-ENOENT` on delete. Cleanup warning indicates callers did not delete all MACs before teardown.

## Test signals
Tests should cover add/delete/refcount for duplicate MACs, ENOSPC when the bitmap is full, disable then enable replay, firmware command failure injection during add and enable, cleanup with empty hash, non-eswitch-manager no-op behavior, and concurrent add/delete serialized by the mutex.
