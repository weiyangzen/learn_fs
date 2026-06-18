<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.c

Purpose: provides shared scatterlist alignment, copy, and cleanup helpers for OMAP crypto drivers whose hardware and DMA paths require aligned, DMA-zone-capable, block-sized buffers.

Important APIs and functions: `omap_crypto_align_sg()` checks an input/output scatterlist against total length, block size, offset alignment, optional DMA-zone requirements, and single-entry requirements. It either leaves the list in place, builds a bounded list copy with `omap_crypto_copy_sg_lists()`, or allocates a contiguous page buffer with `omap_crypto_copy_sgs()`. `omap_crypto_cleanup()` reverses the operation by copying output data back to the original scatterlist when needed and freeing allocated pages or copied SG tables. `omap_crypto_copy_data()` performs page-mapped copyback across SG boundaries.

Control flow: callers clear the relevant device copy flags, request forced copy/list behavior through `OMAP_CRYPTO_*` flags, and pass a shift selecting the in/out/assoc flag lane. Cleanup later decodes those shifted bits and frees only the resources that were actually allocated.

State and persistence: no module-global runtime state. Persistent effects are the caller's mutated SG pointer and copy flags. Allocated buffers live only for one crypto request and must be cleaned up by the caller on all completion/error paths.

Dependencies and integration: used by OMAP DES and AES-style drivers before DMA/PIO submission. Depends on scatterlist helpers, `scatterwalk_map_and_copy()`, `__get_free_pages(GFP_ATOMIC)`, `kmap_atomic()`, and cache flushing for copied output pages.

Risks and test signals: page allocation order is derived from aligned length; mismatched cleanup length/order leaks memory or frees the wrong range. Copyback with offsets is high risk for partial SGs. Test aligned SGs, bad total length, forced-copy, in-place encryption, single-entry forcing, CONFIG_ZONE_DMA systems, and error unwinds after only one side has been copied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.c -->
