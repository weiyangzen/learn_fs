<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.c

Purpose: manages QCE DMA channel acquisition, shared result/ignore buffers, SG-table assembly, DMA descriptor preparation, issue, and termination.

Important APIs and functions: `devm_qce_dma_request()` requests `tx` and `rx` DMA channels, allocates a combined result/ignore buffer, sets `ignore_buf`, and registers devm cleanup. `qce_sgtable_add()` appends up to `max_len` bytes from an existing SG list into a preallocated SG table. `qce_dma_prep_sgs()` prepares RX-channel MEM_TO_DEV and TX-channel DEV_TO_MEM slave SG descriptors, installing the completion callback on the TX descriptor. `qce_dma_issue_pending()` starts both channels; `qce_dma_terminate_all()` terminates both.

Control flow: algorithm files build/mapping SGs, call `qce_dma_prep_sgs()`, issue pending DMA, then program hardware. Completion terminates both channels before unmapping and reading result buffers.

State and persistence: `struct qce_dma_data` holds channel pointers and persistent shared buffers for the device lifetime. SG tables are caller-owned per request.

Dependencies and integration: DMAengine slave SG API, QCE result dump layout, devm cleanup, and algorithm-specific SG construction.

Risks and test signals: channel naming can be confusing because helper parameters use RX/TX from CE perspective while directions are MEM_TO_DEV/DEV_TO_MEM. `qce_sgtable_add()` requires a table with unused entries and valid pages. Test DMA request probe deferral, descriptor prep failures, SG lists longer than max length, in-place versus diff-dst, and termination errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.c -->
