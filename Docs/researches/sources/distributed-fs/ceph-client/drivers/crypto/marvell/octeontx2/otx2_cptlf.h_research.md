# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.h

## Purpose
This header defines CPT LF queue sizing, LF state structures, hardware operation callbacks, instruction-queue allocation/configuration helpers, queue enable/disable helpers, and command-send primitives. It is the bridge between hardware register definitions and PF/VF LF lifecycle code.

## Important APIs and types
Important constants include `OTX2_CPT_USER_REQUESTED_QLEN_MSGS`, `OTX2_CPT_INST_QLEN_MSGS`, `OTX2_CPT_INST_QLEN_BYTES`, `OTX2_CPT_INST_GRP_QLEN_BYTES`, `OTX2_CPT_ALL_ENG_GRPS_MASK`, and `OTX2_CPT_MAX_LFS_NUM`. Key types are `struct otx2_cpt_inst_queue`, `struct otx2_cptlf_wqe`, `struct otx2_cptlf_info`, `struct cpt_hw_ops`, `struct otx2_lmt_info`, and `struct otx2_cptlfs_info`. Important inline APIs include `otx2_cpt_alloc_instruction_queues()`, `otx2_cpt_free_instruction_queues()`, `otx2_cptlf_disable_iqueues()`, `otx2_cptlf_enable_iqueues()`, `otx2_cpt_fill_inst()`, `otx2_cpt_send_cmd()`, and `otx2_cptlf_set_dev_info()`.

## Control flow
LF setup allocates coherent instruction queue memory with space for group queue and flow-control metadata, aligns queue base, writes `Q_BASE` and `Q_SIZE`, and enables execution/enqueue bits. Disable clears enqueue, marks execution disabled, waits for pending queue pointers and in-flight counters to drain, delays for queue write flushing, and requests LF reset through mailbox. `otx2_cpt_fill_inst()` maps software IQ command words into the 64-byte hardware instruction. `otx2_cpt_send_cmd()` writes instructions to the LMT line, uses `dma_wmb()`, and retries `otx2_lmt_flush()` until the store succeeds.

## State and persistence
`otx2_cptlfs_info` is the main shared LF state object, containing device pointers, mailbox, hardware ops, LF array, engine-group numbers, state atomics, block address, global slot, and context-length override. Queue memory is DMA coherent and transient. State is not persisted across driver removal.

## Dependencies and integration points
The header depends on Marvell LMT assembly helpers, RVU mailbox types, hardware-type unions, and request-manager declarations. PF/VF main files initialize `otx2_cptlfs_info`; request manager uses `ops->send_cmd()` and completion-code callbacks; CN10K support can override LMT and SG behavior.

## Risks and edge cases
Queue-size arithmetic includes a documented 320-entry workaround for LDWB behavior; changing it can expose hardware errata. Disable loops can timeout but continue after warnings, so higher layers must tolerate residual hardware conditions. `otx2_cpt_send_cmd()` spins until LMTST success, which assumes hardware eventually accepts the store. Correct memory barriers are essential before MMIO submission.

## Test signals
Signals include queue memory alignment checks, successful queue drain on reset/remove, LMTST submission under load, CN10KB context-flush programming, no DMA API complaints for coherent queues, and crypto throughput scaling with one LF per CPU up to configured limits.
