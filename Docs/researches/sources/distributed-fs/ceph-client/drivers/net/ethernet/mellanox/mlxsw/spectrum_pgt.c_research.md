# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_pgt.c

## Purpose
This file manages the Port Group Table used for multicast/replication membership. It allocates MID indexes, optionally contiguous MID ranges, tracks per-MID port memberships, and writes SMID2 hardware entries.

## Important APIs, Types, And Functions
Public APIs are `mlxsw_sp_pgt_init()`, `mlxsw_sp_pgt_fini()`, `mlxsw_sp_pgt_mid_alloc()`, `mlxsw_sp_pgt_mid_free()`, `mlxsw_sp_pgt_mid_alloc_range()`, `mlxsw_sp_pgt_mid_free_range()`, and `mlxsw_sp_pgt_entry_port_set()`. Internal structures are `mlxsw_sp_pgt`, `mlxsw_sp_pgt_entry`, and `mlxsw_sp_pgt_entry_port`. Helpers create/destroy MID entries, lookup port membership, pack SMID2 port masks, and add/delete ports under a mutex.

## Control Flow
Init validates `PGT_SIZE`, initializes an IDR and mutex, and records whether SMPE index programming is valid. MID allocation reserves IDR slots with `NULL`; entry creation later replaces the reserved slot with a `pgt_entry`. Adding a port gets or creates the entry, writes SMID2 membership true, and links a port record. Deleting a port removes the list node, writes membership false, and destroys the entry if it becomes empty. Range allocation reserves a contiguous cyclic interval and rolls back on partial failure.

## State And Persistence
State is runtime in `mlxsw_sp->pgt`: IDR slots, lock, table size, and SMPE validity. Hardware state is SMID2 membership per MID/local-port. Finalization warns if the IDR is not empty.

## Dependencies And Integration Points
The file depends on core resource query `PGT_SIZE`, IDR, mutexes, refcount-era membership usage from multicast/flooding code, and SMID2 register packing. Other Spectrum subsystems use MIDs to represent replication groups.

## Risks And Edge Cases
MID slots can be reserved without a `pgt_entry`; `mlxsw_sp_pgt_mid_free()` expects to remove a `NULL` slot and warns otherwise. `mlxsw_sp_pgt_entry_port_add()` does not explicitly reject duplicate local ports, so callers should not add the same port twice for one MID. Hardware write failure on delete is ignored after list removal. Range allocation assumes the cyclic cursor interval is available as a block.

## Test Signals
Test MID allocation/free, contiguous range allocation rollback, add/delete membership hardware writes, duplicate membership attempts, SMPE-valid and invalid modes, PGT exhaustion, and WARN-free fini after all users release MIDs.
