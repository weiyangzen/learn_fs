# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_qm_regs.h

## Purpose

`dma6_qm_regs.h` is the generated QMAN map for Gaudi DMA6. It defines 406 `mmDMA6_QM_*` offsets from `0x5C8000` through `0x5C8D00`; `gaudi_blocks.h` lists `mmDMA6_QM_BASE` as `0x7FFC5C8000ull`. DMA6_QM belongs to the HBM DMA queue-manager set.

## Important APIs, Types, And Register Groups

The header exposes macros only. It includes global QMAN config/status/protection/error registers, secure/non-secure property banks, message enables, PQ and CQ registers, CP message base banks, LDMA offset registers, fence data/counts, CP status/current instruction/barrier/debug controls, ARUSER/AWUSER controls, ARB configuration/credits/choice/status/error registers, CGM/local-range/priority/rate-limit controls, indirect APB gateway registers, and global error payload fields.

## Control Flow And State

There is no local code. HBM queue setup uses the shared layout through `DMA_QMAN_OFFSET`; direct reset paths write `mmDMA6_QM_GLBL_CFG0` and `mmDMA6_QM_GLBL_CFG1`. Initialization configures queues, command processor message bases for sync manager signaling, ARB watchdog, error messages, protection, and enable state. HBM stop writes a five-CP stop mask.

State is maintained in hardware: PQ/CQ pointers and status, CP message/fence registers, ARB credits, CGM state, rate-limit settings, non-secure ASID fields, and error-capture registers. `gaudi_mmu_prepare()` updates all five DMA6 QMAN non-secure property registers; `gaudi_restore_qm_registers()` resets ARB config.

## Dependencies And Integration Points

The file is included by `gaudi_regs.h` and relies on the regular QMAN block spacing used by `DMA_QMAN_OFFSET`. Integration points include HBM DMA queue init, disable/stop, MMU ASID preparation, engine idle diagnostics, event-to-QMAN-base descriptions, and reset restoration. Field-level bits are interpreted through sibling generated mask/shift headers.

## Risks And Test Signals

Risks include queue initialization to the wrong address, failure to stop all HBM CP streams, broken sync-manager message routing, and ASID/security mismatches. Test signals are successful DMA6 HBM queue submissions, idle QMAN/CGM status after stop, no ARB or global QMAN error causes, correct ASID updates, and stable behavior after reset/restore.
