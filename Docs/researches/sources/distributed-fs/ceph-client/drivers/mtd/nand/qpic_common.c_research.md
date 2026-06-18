# sources/distributed-fs/ceph-client/drivers/mtd/nand/qpic_common.c

## Purpose
`qpic_common.c` provides exported common DMA helpers for Qualcomm QPIC NAND controller drivers. It abstracts BAM and ADM DMA descriptor construction, submission, register/data transfer helpers, read-register buffer synchronization, and controller allocation/unallocation.

## Important APIs, Types, and Functions
Exported functions include `qcom_alloc_bam_transaction()`, `qcom_free_bam_transaction()`, `qcom_clear_bam_transaction()`, `qcom_qpic_bam_dma_done()`, `qcom_nandc_dev_to_mem()`, `qcom_prepare_bam_async_desc()`, `qcom_prep_bam_dma_desc_cmd()`, `qcom_prep_bam_dma_desc_data()`, `qcom_prep_adm_dma_desc()`, `qcom_read_reg_dma()`, `qcom_write_reg_dma()`, `qcom_read_data_dma()`, `qcom_write_data_dma()`, `qcom_submit_descs()`, `qcom_clear_read_regs()`, `qcom_nandc_alloc()`, and `qcom_nandc_unalloc()`. It relies on `struct qcom_nand_controller`, `struct bam_transaction`, `struct desc_info`, and QPIC constants from `linux/mtd/nand-qpic-common.h`.

## Control Flow
Allocation sets a 32-bit coherent DMA mask, allocates a small data buffer, register shadow structures, and a register-read buffer. BAM-capable controllers map the read buffer, request `tx`, `rx`, and `cmd` channels, and allocate an initial one-codeword BAM transaction; non-BAM controllers request a single `rxtx` ADM channel. Per-operation helpers append command or data scatterlist entries. BAM command descriptors collect command elements, split SGLs at `NAND_BAM_NEXT_SGL`, and may immediately prepare fenced command descriptors on `NAND_BAM_NWD`. ADM descriptors configure slave source/destination, maxburst, optional CRCI flow control, map one SGL, and enqueue it. `qcom_submit_descs()` finalizes any pending BAM SGLs, submits all descriptors, waits for BAM completion via the last command descriptor callback or ADM completion via `dma_sync_wait()`, then unmaps and frees all descriptors.

## State and Persistence
No flash state is directly persisted here; this layer schedules DMA that other QPIC code uses to issue flash commands. Volatile state includes BAM position counters, command/data SGL arrays, descriptor lists, DMA mappings, channel handles, register read cursor, and the completion used to signal BAM transaction completion.

## Dependencies and Integration Points
The file depends on DMAengine, Qualcomm ADM/BAM DMA APIs, platform DMA channel names, QPIC register-address helpers/macros, and MTD QPIC controller code that prepares NAND operations. It exports symbols for raw NAND and SPI-NAND QPIC drivers.

## Risks
Descriptor array bounds are checked, but flag sequencing is subtle; missing `NAND_BAM_NEXT_SGL`, `NAND_BAM_NWD`, or interrupt flags can leave no completion callback or wrong fences. `qcom_submit_descs()` assumes BAM `last_cmd_desc` exists before assigning the callback. DMA mappings must be unmapped on all error paths; the common cleanup loop handles queued descriptors but callers must clear transaction positions between operations. Allocation cleanup for BAM frees channels/mappings but `qcom_nandc_unalloc()` does not free `bam_txn`, so callers must pair it with `qcom_free_bam_transaction()`.

## Test Signals
Test with both BAM and ADM controller variants. Useful signals are DMA channel probe success/failure, descriptor queue lengths, timeout returns from `qcom_submit_descs()`, correct read ID/status flow-control reads, clean unmap/free under injected descriptor preparation failures, and successful page read/write paths in the consuming QPIC NAND drivers.
