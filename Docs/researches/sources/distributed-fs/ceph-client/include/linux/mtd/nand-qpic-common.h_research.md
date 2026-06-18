# sources/distributed-fs/ceph-client/include/linux/mtd/nand-qpic-common.h

## Purpose

Defines Qualcomm QPIC NAND controller common register offsets, bit fields, DMA transaction structures, controller property/state structures, and helper prototypes shared by QPIC raw NAND and SPI NAND support.

## Important APIs, Types, and Functions

Important types are `struct bam_transaction`, `struct desc_info`, `struct nandc_regs`, `struct qcom_nand_controller`, and `struct qcom_nandc_props`. Important helpers allocate/clear/free BAM transactions, prepare BAM/ADM descriptors, read/write registers and data through DMA, submit descriptors, and allocate/unallocate controller resources.

Source-visible symbols include structs: `struct bam_transaction`, `struct bam_cmd_element *bam_ce;`, `struct scatterlist *cmd_sgl;`, `struct scatterlist *data_sgl;`, `struct dma_async_tx_descriptor *last_data_desc;`, `struct dma_async_tx_descriptor *last_cmd_desc;`, `struct completion txn_done;`, `struct desc_info`, `struct dma_async_tx_descriptor *dma_desc;`, `struct list_head node;`, `struct scatterlist adm_sgl;`, `struct`; enums: `enum dma_data_direction dir;`; typedefs: none visible in this header; prototypes: `void qcom_free_bam_transaction(struct qcom_nand_controller *nandc);`, `void qcom_clear_bam_transaction(struct qcom_nand_controller *nandc);`, `void qcom_qpic_bam_dma_done(void *data);`, `void qcom_nandc_dev_to_mem(struct qcom_nand_controller *nandc, bool is_cpu);`, `int qcom_submit_descs(struct qcom_nand_controller *nandc);`, `void qcom_clear_read_regs(struct qcom_nand_controller *nandc);`, `void qcom_nandc_unalloc(struct qcom_nand_controller *nandc);`, `int qcom_nandc_alloc(struct qcom_nand_controller *nandc);`; representative macros: `__MTD_NAND_QPIC_COMMON_H__`, `READ_LOCATION_OFFSET_MASK`, `READ_LOCATION_SIZE_MASK`, `READ_LOCATION_LAST_MASK`, `NAND_DEV_CMD_VLD_VAL`, `dev_cmd_reg_addr`, `reg_buf_dma_addr`, `QPIC_PER_CW_CMD_ELEMENTS`, `QPIC_PER_CW_CMD_SGL`, `QPIC_PER_CW_DATA_SGL`, `QPIC_NAND_COMPLETION_TIMEOUT`, `NAND_BAM_NO_EOT`, `NAND_BAM_NWD`, `NAND_BAM_NEXT_SGL`, `NAND_ERASED_CW_SET`, `MAX_ADDRESS_CYCLE`.

## Control Flow

Drivers populate `nandc_regs`, translate register writes into BAM command elements or ADM descriptors, queue command/data scatterlists, submit DMA, wait for `txn_done`, then read status/error registers. Constants describe page read/program/erase ops, ECC modes, erased-codeword detection, read-location registers, and controller version fields.

## State and Persistence Behavior

Runtime state includes MMIO base, clocks, DMA channels, descriptor lists, local data and register-read buffers, DMA addresses, max codewords per page, cached command-valid registers, and whether status reads are part of exec-op write handling. Persistent data is NAND contents only.

## Dependencies and Integration Points

It integrates with Linux DMA engine, scatterlists, completions, clocks, raw NAND controller ops, QPIC SPI NAND glue, and Qualcomm DT match-data properties.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Descriptor sizing, EOT/NWD flags, erased-codeword detection state, codeword count, and ECC mode selection are all hardware-critical. DMA buffer lifetime or register-offset mistakes can hang the controller or corrupt flash.

## Test Signals

Validate descriptor construction for BAM and ADM, ECC mode/page geometry combinations, erased-page detection, timeout cleanup, multi-chip host lists, and register programming against hardware traces.

Source read signal: 483 lines, 14608 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
