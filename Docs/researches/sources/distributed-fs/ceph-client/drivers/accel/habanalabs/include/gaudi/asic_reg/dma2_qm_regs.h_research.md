# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_qm_regs.h

## Purpose

`dma2_qm_regs.h` is the generated register map for Gaudi `DMA2_QM`, prototype `QMAN`. It defines 406 `mmDMA2_QM_*` register offsets from `0x548000` to `0x548D00`; `gaudi_blocks.h` maps the full base as `0x7FFC548000ull`. DMA2 is an HBM DMA queue manager.

## Important APIs, Types, And Register Groups

The exported interface is macro-only. Register groups mirror the QMAN layout: global config/protection/error routing, five secure and five non-secure property registers, global status/message enable, four producer queues, five completion queues, CP message bases, LDMA source/destination/size offsets, fence read data/counts, CP status and current-instruction registers, barrier and debug registers, ARUSER/AWUSER fields, arbitration credit/choice/status/error registers, CGM controls, local range, strict-priority and rate limit configuration, indirect APB gateway, and global error address/data registers.

## Control Flow And State

No control flow is present in the header. The driver initializes HBM DMA QMANs through `gaudi_init_hbm_dma_qman()`, using `dma_id * DMA_QMAN_OFFSET` to program the same layout. DMA2-specific macros are used directly in `gaudi_disable_hbm_dma_qmans()` and `gaudi_stop_hbm_dma_qmans()`, where HBM QMANs stop five CPs via `0x1F << DMA0_QM_GLBL_CFG1_CP_STOP_SHIFT`. `gaudi_mmu_prepare()` writes `mmDMA2_QM_GLBL_NON_SECURE_PROPS_0..4`.

Hardware state covered by this header includes PQ/CQ base pointers and indexes, CP message and fence registers, ARB credits and status, CGM status, local range and rate-limit configuration, and error address/data payloads. These values persist in the device until reset, restore, or explicit driver writes. `gaudi_restore_qm_registers()` resets ARB configuration across DMA QMANs by common offset.

## Dependencies And Integration Points

The header is included by `gaudi_regs.h` and shares field definitions with DMA0 QMAN masks/shifts. `DMA_QMAN_OFFSET` depends on the regular spacing of QMAN bases. DMA2 participates in HBM DMA queue setup, MMU context preparation, queue disable/stop flows, engine idle reports, and event descriptions derived from `GAUDI_EVENT_DMA0_QM ... GAUDI_EVENT_DMA7_QM`.

## Risks And Test Signals

The largest risks are incorrect HBM queue programming and ASID/security mismatches. The fifth CQ/CP slot and `0x1F` stop mask matter for HBM DMA, unlike PCI DMA queue managers that expose four CP queues. Regression signals include HBM DMA initialization success, absence of QMAN RAZWI messages, `QM_GLBL_STS0` and `CGM_STS` becoming idle after stop, correct MMU ASID switching, and no queue corruption after reset/restore.
