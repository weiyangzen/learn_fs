# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_qm_regs.h

## Purpose

`dma5_qm_regs.h` is the generated QMAN register-offset header for Gaudi DMA5. It defines 406 `mmDMA5_QM_*` macros from `0x5A8000` to `0x5A8D00`; `gaudi_blocks.h` maps `mmDMA5_QM_BASE` to `0x7FFC5A8000ull`. DMA5_QM is handled by the driver as a PCI DMA queue manager and is also named in collective-queue comments in `gaudiP.h`.

## Important APIs, Types, And Register Groups

The file has no functions or types. It provides global QMAN config/protection/status/error macros, secure and non-secure property banks, PQ/CQ registers, CP message base banks, LDMA offset registers, fence data/count/status registers, CP status/current instruction/barrier/debug registers, AXI user controls, ARB credit/choice/status/error macros, CGM/local-range/rate-limit controls, indirect APB gateway registers, and global error payload macros.

## Control Flow And State

No local control flow exists. `gaudi_init_pci_dma_qman()` can initialize DMA5 via common DMA QMAN offset arithmetic, programming queue memory, command processor message bases, barrier config, error message routing, ARB watchdog, protection, and `GLBL_CFG1`. Reset paths directly disable and stop DMA5 QMAN with PCI four-CP masks. `gaudi_get_fence_addr()` directly maps DMA5 queue IDs 0..3 to `mmDMA5_QM_CP_FENCE2_RDATA_0..3`.

State persists as queue pointers, CP message/fence state, ARB credits, CGM status, rate-limit configuration, non-secure ASID bits, and error-capture payloads. `gaudi_mmu_prepare()` writes all five DMA5 QMAN non-secure property registers, even though PCI-visible queues use four CP streams. `gaudi_restore_qm_registers()` resets ARB config across all DMA QMANs.

## Dependencies And Integration Points

The header is included via `gaudi_regs.h`; its spacing must match `DMA_QMAN_OFFSET`. It integrates with PCI DMA queue setup, PCI QMAN disable/stop, queue fence address resolution, engine idle checks, MMU context preparation, event reporting, and reset restoration. Field-level semantics are imported from sibling QMAN shift/mask headers.

## Risks And Test Signals

Risk concentrates around PCI DMA queue and fence behavior: wrong offsets can make user-visible queues fail, return wrong fence addresses, or miss completions. Errors in global error routing can hide PCI DMA faults. Test signals include DMA5 queue submissions completing, correct fence readback for DMA5 queues, clean PCI DMA stop/disable, no QMAN/ARB error status, idle status after reset, and ASID updates not breaking DMA5 work.
