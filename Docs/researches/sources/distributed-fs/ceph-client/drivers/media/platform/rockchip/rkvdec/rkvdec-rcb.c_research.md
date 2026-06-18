# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.c

Purpose: implements the Rows and Columns Buffer manager used by newer Rockchip decoder variants. RCB buffers are per-context auxiliary work areas whose sizes are derived from decoded picture width or height and whose addresses are programmed by the VDPU381/VDPU383 H.264 and HEVC backends.

Important APIs and functions: `rkvdec_allocate_rcb`, `rkvdec_free_rcb`, `rkvdec_rcb_buf_dma_addr`, `rkvdec_rcb_buf_size`, and `rkvdec_rcb_buf_count`. Internal `rkvdec_rcb_size` applies each `struct rcb_size_info` multiplier against either picture width or picture height.

Control flow: streaming start calls allocation with the variant RCB table. Each requested buffer first attempts SRAM allocation from the optional device-tree `sram` gen_pool; if an IOMMU domain is present, the SRAM physical address is mapped through the domain and the register-visible DMA address is replaced with the virtual/IOMMU address. Failed SRAM allocation or mapping falls back to coherent DMA memory. On partial failure, `rkvdec_free_rcb` tears down every successfully allocated entry.

State and persistence: state is transient and hangs off `ctx->rcb_config`; each entry records CPU pointer, DMA/register address, size, and allocation type. No state persists beyond the V4L2 streaming session. SRAM mappings are explicitly unmapped and gen_pool regions freed; DMA allocations are freed with `dma_free_coherent`.

Dependencies and integration points: depends on `rkvdec.h`, `rkvdec-rcb.h`, genalloc, DMA coherent allocation, and optional IOMMU APIs. Integrated from `rkvdec_start_streaming`, freed from error and stop paths, and consumed by VDPU38x codec register programming.

Risks: the code uses devm allocation for per-stream metadata and then manually frees it, which is valid with `devm_kfree` but makes lifetime assumptions important. IOMMU mapping uses the SRAM CPU pointer value as the IOVA. Buffer IDs are trusted by accessors. Size calculations are multiplier based and may become wrong if hardware tables or alignment requirements change.

Test signals: exercise VDPU381/VDPU383 streaming with and without SRAM, with and without an IOMMU, and force allocation fallback/failure. Useful checks are no IOMMU faults, RCB register addresses matching allocation type, clean stream stop, and kmemleak/dma-debug silence.
