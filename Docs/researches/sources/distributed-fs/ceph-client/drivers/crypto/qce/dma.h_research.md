<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.h

Purpose: defines QCE DMA buffer sizes, result-dump layout, DMA state, and helper prototypes.

Important types and constants: `QCE_BAM_BURST_SIZE` is 64 bytes. Result dumps include authentication IV, authentication byte counts, encryption counter IV, and status words. `QCE_RESULT_BUF_SZ` aligns the result dump to a BAM burst; `QCE_IGNORE_BUF_SZ` reserves two burst sizes. `struct qce_dma_data` stores TX/RX DMA channels, shared result buffer, and ignore buffer.

Control flow and integration: algorithm code appends `result_buf` as a destination SG to capture hardware result dumps; common status/IV code reads from `struct qce_result_dump` after DMA completion. DMA helpers declared here are implemented in `dma.c` and used by SHA, skcipher, and AEAD files.

State and persistence: result and ignore buffers persist for the platform-device lifetime and are reused across serialized requests.

Dependencies: DMAengine and QCE core/algorithm files.

Risks and test signals: buffer sizing must match hardware result dump and BAM burst alignment. Test cache coherency and DMA mapping of the result buffer across all algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.h -->
