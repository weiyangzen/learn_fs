# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/dm.c

Purpose: Manages software-owned ICM device memory regions for steering, header modify, header modify pattern, and indirect encapsulation objects.

Important APIs and flow: `mlx5_dm_create()` checks SW ICM object support and allocates bitmaps for each firmware-advertised memory range, including v2 header modify pattern support. `mlx5_dm_sw_icm_alloc()` validates power-of-two block-aligned length, selects the memory range for the requested `enum mlx5_sw_icm_type`, finds aligned free blocks in the bitmap, creates a SW ICM general object, and returns physical address plus object ID. `mlx5_dm_sw_icm_dealloc()` destroys the object and clears the bitmap range. `mlx5_dm_cleanup()` warns on nonempty allocation bitmaps and frees them.

State and dependencies: `struct mlx5_dm` stores per-type allocation bitmaps protected by a spinlock. Size and base addresses come from device memory capabilities and `MLX5_LOG_SW_ICM_BLOCK_SIZE()`. The object command path uses `CREATE_GENERAL_OBJECT`/`DESTROY_GENERAL_OBJECT` with optional UID.

Risks and test signals: Address arithmetic must match firmware log sizes and alignment masks; command failure must clear pre-reserved bitmap bits. Tests should cover unsupported types/caps, invalid length/alignment, full-range exhaustion, allocation/deallocation symmetry, UID propagation, cleanup leak warnings, and v1/v2 capability combinations.
