# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_common.c

## Purpose
Provides shared CPM/QE MURAM allocation and address conversion helpers. It discovers the MURAM data region from device tree, maps it, backs allocations with a gen_pool, tracks allocated blocks for size-aware freeing, and exports managed and unmanaged allocation APIs.

## Important APIs, types, and functions
Exports `cpm_muram_init`, `cpm_muram_alloc`, `cpm_muram_free`, `devm_cpm_muram_alloc`, `cpm_muram_alloc_fixed`, `devm_cpm_muram_alloc_fixed`, `cpm_muram_addr`, `cpm_muram_offset`, `cpm_muram_dma`, and `cpm_muram_free_addr`. `struct muram_block` stores allocation offset and size in `muram_block_list`. `cpm_muram_alloc_common` centralizes gen_pool allocation, zeroing, and list tracking.

## Control flow and state behavior
Initialization finds `"fsl,cpm-muram-data"` or legacy `"data-only"`, creates a gen_pool, translates the zero address to establish the physical base, adds all resource ranges with a `GENPOOL_OFFSET`, and maps the full physical span. Allocations are serialized by `cpm_muram_lock`, allocate a tracking node with `GFP_ATOMIC`, use either first-fit alignment or fixed-offset gen_pool algorithms, subtract `GENPOOL_OFFSET`, zero the MMIO memory, and record the block. Frees search the list for the offset, recover the size, free the gen_pool range, and drop the tracking node.

## Dependencies and integration points
Shared by QE reset/SDMA setup and CPM/QE communication drivers that need internal multi-user RAM. It depends on OF address translation, `genalloc`, big-endian or MMIO-safe zeroing, and devres for managed variants.

## Risks and test signals
If `cpm_muram_free` is called with an unknown offset, `size` remains zero and `gen_pool_free` is still called with zero length; behavior should be checked against gen_pool expectations. The global block list is not initialized from preexisting firmware allocations, so fixed allocations must align with device-tree ranges. Test signals include successful MURAM discovery, aligned allocation, fixed allocation conflict handling, devm release on driver detach, and correct DMA address conversion.
