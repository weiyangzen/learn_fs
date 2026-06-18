# sources/distributed-fs/ceph-client/mm/dmapool_test.c

## Purpose
`dmapool_test.c` is a loadable timing and smoke-test module for the DMA pool allocator. It creates a synthetic device, builds pools with representative object sizes and alignments, repeatedly allocates and frees many blocks, and prints elapsed microseconds for each parameter set.

## Important APIs, types, and functions
`struct dma_pool_pair` stores one CPU pointer and DMA handle returned by `dma_pool_alloc()`. `struct dmapool_parms` describes a pool size, alignment, and boundary. `pool_parms[]` covers sizes from 16 bytes through 4096 bytes plus a nontrivial `{ size = 68, align = 32, boundary = 4096 }` case.

`nr_blocks()` scales the test block count by object size and clamps it between 1024 and 8192. `dmapool_test_alloc()` allocates all requested blocks, frees them, and unwinds partially successful allocations on failure. `dmapool_test_block()` allocates the pair array, creates a `dma_pool`, runs `NR_TESTS` allocation/free loops, yields with `cond_resched()` when needed, prints timing, and destroys the pool. `dmapool_checks()` is the module init routine that registers the fake device, configures DMA ops and a 64-bit coherent mask, and runs all parameter sets.

## Control flow
On module load, `dmapool_checks()` names and registers `test_dev`, assigns a release callback, clears DMA ops, installs `dma_mask`, and calls `dma_set_mask_and_coherent()`. It then iterates over `pool_parms[]`. Each iteration creates a pool, runs 100 full allocate/free passes over the chosen number of blocks, prints one line of timing, and tears the pool down. If any allocation, registration, or mask setup fails, the function jumps through cleanup labels to delete and put the device.

## State and persistence
The module uses file-scope `pool`, `test_dev`, and `dma_mask`. All test allocations are temporary and should be freed before each parameter case returns. There is no persistent state beyond printk output. `dmapool_exit()` is empty because all work is performed synchronously at module initialization.

## Dependencies and integration points
The test depends on the DMA mapping layer, device core registration, `dma_pool_create()/alloc/free/destroy()`, kernel timing via `ktime_get()` and `ktime_us_delta()`, scheduler rescheduling, and module init/exit infrastructure. It uses `kzalloc_objs()` for the pair array and `DMA_BIT_MASK(64)` to make the synthetic device broadly DMA-capable.

## Risks and test signals
The module is a timing smoke test, not a correctness proof. It does not validate returned alignment, boundary crossing, data poisoning, sysfs counters, or DMA API debug state. The synthetic device setup is minimal and may not model IOMMU-heavy real devices. A useful pass signal is successful module load producing timing lines for all parameter sets without allocation failure or DMA mask setup failure. Failures in this test point toward allocator regressions in page splitting, high-volume allocation/free loops, or fake-device DMA setup assumptions.
