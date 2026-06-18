# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.c

## Purpose
`qat_bl.c` converts Linux scatterlists into QAT firmware buffer-list descriptors and frees their DMA mappings. It supports in-place and out-of-place operations, small inline descriptor storage, dynamic descriptor allocation, source/destination skip offsets, and optional extra destination overflow buffers.

## Important APIs, Types, And Functions
Public functions are `qat_bl_sgl_to_bufl()` and `qat_bl_free_bufl()`. The internal worker `__qat_bl_sgl_to_bufl()` performs the mapping and descriptor construction. The implementation fills `struct qat_request_buffs`, `qat_alg_buf_list`, and `qat_alg_buf` structures declared in `qat_bl.h`.

## Control Flow
`qat_bl_sgl_to_bufl()` extracts optional parameters and calls the internal converter. The converter counts source SG entries, chooses inline fixed storage for up to `QAT_MAX_BUFF_DESC` descriptors or allocates a larger list, maps each non-empty source segment after applying `sskip`, records DMA address/length, maps the source descriptor list itself, then either reuses the same list for in-place operations or builds/maps a destination list after `dskip` with an optional extra destination buffer. On failure it unwinds partially mapped destination and source buffers and descriptor-list mappings. `qat_bl_free_bufl()` reverses successful mappings and frees dynamic lists.

## State And Persistence Behavior
Buffer-list state persists only for one in-flight request. `sgl_src_valid` and `sgl_dst_valid` indicate whether inline storage inside `qat_request_buffs` is used or whether memory must be freed. DMA mappings remain valid until the service callback calls `qat_bl_free_bufl()`.

## Dependencies And Integration Points
It depends on Linux DMA mapping, scatterlist helpers, QAT accelerator device wrappers, and `qat_crypto.h`. It is used by symmetric and compression paths to convert Crypto API/acomp scatterlists into firmware SGL pointers.

## Risks
The code uses `dma_map_single()` on `sg_virt()` rather than `dma_map_sg()`, so it assumes CPU-addressable scatterlist entries. Skip handling must keep descriptor lengths consistent with mapped sizes. In out-of-place operations, extra destination buffers are not counted in `num_mapped_bufs` because they are already DMA-mapped elsewhere. Error unwinding loops over original SG counts while zero-length segments may have been skipped, so initialized `DMA_MAPPING_ERROR` sentinels are important.

## Test Signals
Tests should cover in-place and out-of-place SGLs, more than four descriptors, zero-length SG entries, source/destination skip offsets, compression overflow extra destination buffers, DMA mapping failures, and callback cleanup under success and firmware error.
