# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.c

## Purpose
`ipu3-mmu.c` implements the IPU3 private two-level page-table MMU, including dummy invalid mappings, lazy L2 page-table allocation, map/unmap operations, TLB invalidation, and suspend/resume hardware programming.

## Important APIs, Types, and Functions
- `struct imgu_mmu` holds device/register pointers, lock, dummy page/table state, L1/L2 tables, and public aperture geometry.
- `imgu_mmu_init()` and `imgu_mmu_exit()` allocate and destroy page tables and hardware state.
- `imgu_mmu_map()`, `imgu_mmu_map_sg()`, and `imgu_mmu_unmap()` expose mapping primitives.
- `imgu_mmu_suspend()` and `imgu_mmu_resume()` gate memory access and restore the L1 pointer.

## Control Flow
Initialization halts memory access, creates dummy mappings because the hardware has no valid bit, programs the L1 physical address, invalidates TLB, and unhalts. Mapping validates 4 KiB alignment and writes one PTE per page, allocating L2 tables on demand. Scatterlist mapping maps each segment and unmaps the prefix on error. Unmap replaces real PTEs with the dummy page until it reaches an unmapped entry or requested size.

## State and Persistence Behavior
Page tables persist in uncached CPU memory. `l2pts` tracks allocated L2 tables; L1 entries point at dummy or real L2 tables. Invalid entries point at a dummy page. Hardware state includes the L1 register, TLB, and CIO gate halt state.

## Dependencies and Integration Points
Depends on DMA/scatterlist helpers, runtime PM, register polling, x86 memory attribute calls, and IPU3 MMU registers. The DMA-map layer owns IOVA allocation and calls these primitives.

## Risks
Partial page mappings require caller unwind. Unmap stops at the first dummy PTE, so inconsistent ranges can leave later mappings. TLB invalidation is skipped when runtime PM says the device is off and relies on resume/startup invalidation. Dummy-page invalid mappings hide faults.

## Test Signals
Test aligned/unaligned arguments, busy-PTE failures, scatterlist partial unwind, repeated map/unmap, suspend/resume with live mappings, and cleanup after dynamic L2 allocation.
