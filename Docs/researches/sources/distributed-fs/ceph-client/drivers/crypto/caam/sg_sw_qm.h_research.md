# sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm.h

Purpose: converts Linux DMA-mapped scatterlists into DPAA/QMan `struct qm_sg_entry` link-table entries used by CAAM queue-interface paths.

Important APIs: `__dma_to_qm_sg()` writes the DMA address, clears buffer-pool metadata, and stores an offset with `QM_SG_OFF_MASK`. `dma_to_qm_sg_one()`, `_last()`, `_ext()`, and `_last_ext()` build normal, final, extension, and final-extension entries. `sg_to_qm_sg()` walks a scatterlist for a requested byte length and returns the last generated entry; `sg_to_qm_sg_last()` then marks that entry final.

Control flow and state: the conversion loop repeatedly takes `min(sg_dma_len(sg), len)`, emits one hardware entry, advances `sg_next()`, and decrements the remaining length. No persistent state is kept; the caller owns DMA mapping, output table storage, and final hardware submission.

Dependencies and integration points: depends on `<soc/fsl/qman.h>`, `regs.h`, QMan byte-order helpers, Linux scatterlist DMA APIs, and CAAM QI users that include a hardware link table in frame descriptors.

Risks and test signals: risks include passing an unmapped or too-short scatterlist, output table under-allocation, offset truncation, and no explicit null guard if `len` exceeds the SG chain. Test signals include QMan SG entries with correct final/extension flags, exact byte coverage for partial last segments, and successful CAAM queue-interface requests with multi-entry input and output buffers.
