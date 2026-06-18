# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-bootmem.c

## Purpose
Implements the Octeon firmware bootmem allocator: early physical allocation, named bootmem blocks, and free-list maintenance over the bootloader-supplied descriptor.

## Important APIs, Types, And Functions
The key state is `static struct cvmx_bootmem_desc *cvmx_bootmem_desc`. Main APIs are `cvmx_bootmem_init()`, `cvmx_bootmem_phy_alloc()`, `__cvmx_bootmem_phy_free()`, `cvmx_bootmem_phy_named_block_alloc()`, `cvmx_bootmem_alloc_named_range_once()`, `cvmx_bootmem_find_named_block()`, `cvmx_bootmem_free_named()`, and `cvmx_bootmem_get_desc()`. Physical list headers are accessed through `cvmx_read64_uint64()`/`cvmx_write64_uint64()` with fixed next/size offsets.

## Control Flow
Allocation validates descriptor version, size, range, and alignment, walks the sorted free list first-fit, splits blocks to create an aligned allocation, and removes the selected range. Freeing inserts a span back in address order and coalesces with neighbors. Named allocation locks around descriptor lookup, duplicate-name rejection, physical allocation, and descriptor fill.

## State, Persistence, And Dependencies
State lives in firmware bootmem structures and named-block arrays. Locking uses the descriptor spinlock unless a no-lock flag is passed for nested operations. The module depends on Octeon physical mapping helpers and descriptor version 3 for named blocks.

## Integration Points
Command queues and other executive code allocate shared state through named bootmem. Several functions are exported for kernel modules.

## Risks
Uninitialized descriptors, overlapping frees, wrong alignment, or descriptor-version mismatch can corrupt early global memory state. Physical memory accesses bypass normal virtual-memory checks.

## Test Signals
Check impossible allocation failures, duplicate-name rejection, named block reuse, free-list coalescing, and sorted non-overlapping free-list invariants after allocation/free stress.
