# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.c

## Purpose

`fman_muram.c` provides a small allocator wrapper for FMan MURAM, the internal multi-user RAM used by FMan blocks for structures such as DMA CAM and BMI FIFO. It maps a physical MURAM partition, creates a genalloc pool, zeroes memory, and returns offsets suitable for programming into FMan registers.

## Important APIs, Types, And Functions

The private `struct muram_info` stores a `gen_pool`, virtual base, and physical base. Public functions are `fman_muram_init()`, `fman_muram_offset_to_vbase()`, `fman_muram_alloc()`, and `fman_muram_free_mem()`. Internal `fman_muram_vbase_to_offset()` converts allocated virtual addresses back to hardware offsets.

## Control Flow

`fman_muram_init()` allocates `muram_info`, creates a gen_pool with 64-byte granularity, ioremaps the physical MURAM range, adds the virtual/physical mapping to the pool, zeroes the partition, and returns the handle. `fman_muram_alloc()` allocates from the pool, zeroes the allocation, and returns an offset from the mapped base. `fman_muram_free_mem()` converts an offset back to virtual address and frees the range.

## State And Persistence Behavior

Allocator state is held in the gen_pool and the virtual mapping. Allocated blocks are returned as offsets, not virtual addresses, matching FMan register programming. Memory is zeroed both at partition initialization and per allocation. There is no public destroy function in this subset, so pool/mapping teardown is absent for normal driver removal.

## Dependencies And Integration Points

The file depends on Linux IO, slab, and genalloc APIs. FMan core uses it to allocate DMA CAM and FIFO space, and any other FMan component can convert offsets back to virtual base for direct initialization.

## Risks And Edge Cases

Allocation failure returns `-ENOMEM` cast through `unsigned long`, so callers must use `IS_ERR_VALUE()` rather than NULL checks. Missing destroy/unmap support can matter for hot-unplug or probe-failure cleanup beyond the paths shown. `fman_muram_free_mem()` trusts offset and size; invalid inputs can corrupt the pool.

## Test Signals

Tests should cover init failure at allocation, pool creation, ioremap, and pool-add stages; allocation alignment and zeroing; offset-to-vbase round trips; freeing and reallocating; and caller behavior for `IS_ERR_VALUE()` allocation errors.
