# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mr.c

## Purpose
`mr.c` implements mlx4 memory translation resources: memory translation table (MTT) range allocation, memory protection table (MPT) reservation and hardware enablement, memory region (MR) and memory window (MW) lifecycle, and translation-page writes. It is the core resource manager used by upper mlx4 Ethernet and RDMA consumers before queue pairs can DMA into registered buffers.

## Important APIs, types, and functions
- MTT allocation uses the private `struct mlx4_buddy` allocator through `mlx4_buddy_alloc()`, `mlx4_buddy_free()`, `mlx4_buddy_init()`, and `mlx4_buddy_cleanup()`.
- Public MTT APIs include `mlx4_mtt_init()`, `mlx4_mtt_cleanup()`, `mlx4_mtt_addr()`, `mlx4_write_mtt()`, and `mlx4_buf_write_mtt()`.
- MPT/MR hardware transitions use `mlx4_SW2HW_MPT()`, `mlx4_HW2SW_MPT()`, `mlx4_mr_hw_get_mpt()`, `mlx4_mr_hw_write_mpt()`, `mlx4_mr_hw_put_mpt()`, `mlx4_mr_hw_change_pd()`, and `mlx4_mr_hw_change_access()`.
- MR lifecycle is handled by `mlx4_mr_alloc()`, `mlx4_mr_free()`, `mlx4_mr_rereg_mem_write()`, `mlx4_mr_rereg_mem_cleanup()`, and `mlx4_mr_enable()`.
- MW lifecycle is handled by `mlx4_mw_alloc()`, `mlx4_mw_enable()`, and `mlx4_mw_free()`.
- Table setup and teardown are `mlx4_init_mr_table()`, `mlx4_cleanup_mr_table()`, and `mlx4_SYNC_TPT()`.

## Control flow and integration
Normal MR creation reserves an MPT index with `mlx4_mpt_reserve()`, initializes an MTT range with `mlx4_mtt_init()`, writes page translations through `mlx4_write_mtt()` or `mlx4_buf_write_mtt()`, and then enables the MR with `mlx4_mr_enable()`. Enablement maps ICM for the MPT entry, fills a command mailbox with the key, PD, access flags, IOVA, size, page shift, and MTT address, then issues `MLX4_CMD_SW2HW_MPT`. Freeing reverses the state: if the entry is hardware-owned it is moved back with `HW2SW_MPT`, MTTs are released, ICM is unmapped, and the MPT bitmap entry is freed.

The file has native and multi-function paths. Native functions directly manage `priv->mr_table` bitmaps, ICM tables, and DMA-visible MTT entries. Multi-function devices forward reserve, map, free, query, and write operations to the master through wrapped mlx4 resource commands such as `RES_MTT`, `RES_MPT`, `RES_OP_RESERVE`, `RES_OP_MAP_ICM`, and `MLX4_CMD_WRITE_MTT`.

## State and persistence behavior
Runtime state lives in `mlx4_priv(dev)->mr_table`, especially `mpt_bitmap`, `mtt_buddy`, `dmpt_table`, and `mtt_table`. Each `struct mlx4_mr` persists its key, PD, IOVA, size, access flags, enabled state, and embedded `struct mlx4_mtt`. MTT entries are DMA-visible hardware state and are explicitly synchronized for CPU and device access when written in native mode. MPT entries transition between software-owned and hardware-owned states; errors in this transition leave resources reserved but not usable until cleanup.

## Dependencies
The implementation depends on mlx4 command helpers, mailbox allocation, ICM table mapping, bitmap allocation, DMA synchronization, endian conversion, kernel spinlocks, vmalloc-backed bitmaps, and capability values from `dev->caps`. It is integrated with RDMA core users through exported GPL symbols and with virtualization through wrapped command opcodes.

## Risks
- The buddy allocator assumes power-of-two table geometry; wrong `num_mtts` or `log_mtts_per_seg` values can corrupt range accounting.
- MR re-registration must clean up replacement MTTs on failure or stale translation state can leak.
- `mlx4_mr_hw_get_mpt()` requires external serialization; concurrent callers can race `HW2SW_MPT` and mailbox ownership.
- Native MPT writes rely on memory barriers and `mlx4_SYNC_TPT()`. Missing ordering would expose partially initialized entries to hardware.
- Multi-function error paths log failed releases but cannot force master cleanup, so leaked reserved MPT/MTT resources are possible after command failures.

## Test signals
Useful validation includes MR/MW allocation and free stress, zero-page physical MRs, fast-register MRs with `page_shift == 0`, reregistration with changed IOVA and size, MTT writes crossing page boundaries, slave and master resource command paths, injected mailbox allocation failures, injected `SW2HW_MPT`/`HW2SW_MPT` failures, and teardown checks for bitmap/ICM leaks.
