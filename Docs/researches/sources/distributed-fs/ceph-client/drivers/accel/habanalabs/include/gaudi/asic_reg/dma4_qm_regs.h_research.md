# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_qm_regs.h

## Purpose

`dma4_qm_regs.h` defines the generated Gaudi `DMA4_QM` QMAN register offsets. It exposes 406 `mmDMA4_QM_*` constants in the `0x588000..0x588D00` range; `gaudi_blocks.h` places the full base at `0x7FFC588000ull`. DMA4_QM is part of the HBM DMA queue-manager group.

## Important APIs, Types, And Register Groups

No functions or types are declared. Macro groups cover global QMAN config/status/protection/error registers, secure and non-secure properties, message enables, producer queues, completion queues, CP message base banks, LDMA offsets, fences, CP current instruction/status/barrier/debug fields, AXI user controls, ARB credit/choice/status/error controls, CGM and local range registers, priority/rate-limit/AXCACHE controls, indirect gateway registers, and global error capture.

## Control Flow And State

The header itself has no control flow. `gaudi_init_hbm_dma_qman()` uses the common QMAN offsets to configure DMA4 queues, command processor message bases for monitor/SOB signaling, error messages, ARB watchdog, protection, and enable state. Direct HBM reset paths disable `mmDMA4_QM_GLBL_CFG0` and stop CPs with `mmDMA4_QM_GLBL_CFG1`.

State persists in device registers: queue base addresses and indexes, CQ descriptors, CP message and fence values, ARB credits, rate limits, MMU ASID properties, and error payloads. `gaudi_mmu_prepare()` writes `mmDMA4_QM_GLBL_NON_SECURE_PROPS_0..4`; `gaudi_restore_qm_registers()` resets DMA QMAN ARB configuration by offset.

## Dependencies And Integration Points

The header is aggregated by `gaudi_regs.h`. Address consistency is required by `DMA_QMAN_OFFSET`. It integrates with HBM DMA QMAN initialization, HBM disable/stop, MMU context preparation, queue event reporting, QMAN idle checks, and reset restoration. The field masks/shifts are defined in sibling generated headers and are typically referenced through DMA0 names.

## Risks And Test Signals

Risk areas are queue corruption, missed completions, incorrect fence data, misrouted monitor/SOB messages, and reset races if the five-CP stop mask does not hit the intended register. Test signals include HBM DMA4 queue execution, idle `QM_GLBL_STS0`/`CGM_STS` after drain, no QMAN/ARB error causes, correct ASID updates, and successful reinitialization after reset.
