<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.h

Purpose: exposes the small shared OMAP crypto scatterlist-copy contract used by multiple hardware crypto drivers.

Important APIs and definitions: return-like internal status values distinguish `OMAP_CRYPTO_NOT_ALIGNED` from `OMAP_CRYPTO_BAD_DATA_LENGTH`. Device copy state uses `OMAP_CRYPTO_DATA_COPIED` and `OMAP_CRYPTO_SG_COPIED`, masked by `OMAP_CRYPTO_COPY_MASK` and shifted into per-driver flag fields. Caller option flags request input data copy, forced copy, zero padding, and single-entry list behavior. The exported functions are `omap_crypto_align_sg()` and `omap_crypto_cleanup()`.

Control flow and integration: drivers call `omap_crypto_align_sg()` before programming DMA or PIO, passing the current SG pointer by reference and a caller-owned replacement SG. Completion calls `omap_crypto_cleanup()` with the same flag shift and preserved original output SG when copyback is required.

State and persistence: the header defines no state. Its contract is stateful through the caller's shifted flag bits and through mutated SG pointers that must remain valid until cleanup.

Dependencies: Linux scatterlists, bit operations, and the implementation in `omap-crypto.c`.

Risks and test signals: callers must allocate enough inline `new_sg` storage when forcing a single entry and must keep flag shifts disjoint. Test signals are successful OMAP AES/DES operations with unaligned offsets, short final lengths, in-place requests, and cleanup on failures between input and output alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.h -->
