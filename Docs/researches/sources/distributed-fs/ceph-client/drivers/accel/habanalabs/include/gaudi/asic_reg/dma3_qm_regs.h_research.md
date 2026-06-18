# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_qm_regs.h

## Purpose

`dma3_qm_regs.h` is the generated QMAN register map for Gaudi DMA3. It defines 406 `mmDMA3_QM_*` offsets over `0x568000..0x568D00`; `gaudi_blocks.h` maps `mmDMA3_QM_BASE` at `0x7FFC568000ull`. DMA3_QM is used as an HBM DMA queue manager.

## Important APIs, Types, And Register Groups

The API is the macro namespace. The layout includes global configuration/status/protection/error registers, secure and non-secure property banks, PQ and CQ configuration/base/index/status registers, CP message base and LDMA offset registers, fence data/counts/status, CP status/current instruction/barrier/debug registers, ARUSER/AWUSER controls, ARB credit and selection registers, ARB error/status registers, CGM controls, local range and CSMR priority, HBW/LBW rate limits, AXCACHE, indirect APB gateway, and global error payload registers.

## Control Flow And State

No code executes in the header. The driver uses the common QMAN layout through `DMA_QMAN_OFFSET` and direct HBM QMAN stop/disable writes. During HBM QMAN setup, `gaudi_init_hbm_dma_qman()` programs queue memory, queue indexes, command-processor message bases, barriers, error message routing, ARB watchdog, global protection, and enable state. HBM stop code writes DMA3's `GLBL_CFG1` with a five-CP stop mask.

Hardware state includes queue producer/consumer positions, CQ state, command processor message routing, fence counters, ARB credits, rate limits, ASID bits, and error-capture state. `gaudi_mmu_prepare()` updates all five DMA3 QMAN non-secure property registers. `gaudi_restore_qm_registers()` resets ARB configuration by common DMA index.

## Dependencies And Integration Points

`gaudi_regs.h` includes the header. `gaudiP.h` requires the address spacing to match `DMA_QMAN_OFFSET`. Integration points are HBM DMA queue setup, HBM disable/stop, MMU ASID preparation, QMAN idle diagnostics, event-to-QMAN-base reporting, and reset restoration. Field semantics are provided by DMA0 QMAN mask/shift headers.

## Risks And Test Signals

Risks center on HBM QMAN command processor control: wrong queue or CP offsets can stall work, lose completions, misroute sync object messages, or leave queues active during reset. ASID property drift can create translation faults. Tests/signals include HBM queue workloads using DMA3, clean QMAN idle output, no ARB/QMAN error causes, correct ASID updates, and successful reset/stall behavior with all five CPs stopped.
