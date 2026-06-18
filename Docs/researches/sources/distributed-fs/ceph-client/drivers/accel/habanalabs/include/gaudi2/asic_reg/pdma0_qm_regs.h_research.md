<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_regs.h

## Purpose
`pdma0_qm_regs.h` is the Gaudi2 PDMA0 queue manager MMIO address map. It is auto-generated, guarded by `ASIC_REG_PDMA0_QM_REGS_H_`, and exports 518 `mmPDMA0_QM_*` address macros spanning `0x4C8A000` through `0x4C8AD70`. The block covers global queue-manager control, producer and completion queues, command processor state, indirect gateway, arbitration, error reporting, interrupts, ARC auxiliary windows, and performance counters.

## Important APIs, Types, And Functions
There are no functions or structs. The important API is the address macro namespace:

- Global registers: `mmPDMA0_QM_GLBL_CFG0`, `GLBL_CFG1`, `GLBL_CFG2`, error config/status/message-enable, `GLBL_AXCACHE`, `GLBL_PROT`, and global status.
- PQ registers for four queues: base low/high, size, producer index, consumer index, config, and status.
- CQ registers for five queues: config/status, pointer low/high, transfer size, control, control consumer index, and input FIFO state.
- CP registers for five command processors: message base windows, fence data/count registers, predicate state, current instruction, input data, debug and status.
- PQC and direct push registers, local range and L2H compare/mask registers, HBW/LBW rate limiters, arbitration config/credits/weights, indirect APB gateway, SEI status/mask, ARC AUX base address, and perf counters.

## Control Flow
The header does not execute. It drives register-access control flow in callers. Driver code programs queue memory windows, initializes producer/completion queues, sets command processor metadata, controls rate limiters and arbitration, then reads status/error registers while submitting and draining work. The companion mask file provides safe field encodings for these addresses.

## State And Persistence
All state is in hardware registers at the exported addresses. Queue pointer, size, status, fence, predicate, interrupt, error, and performance counter values are volatile MMIO values whose lifetime is defined by hardware reset, firmware sequencing, or explicit driver writes. The address macros are compile-time constants and carry no runtime persistence.

## Dependencies
This header depends only on the preprocessor. Runtime use depends on the Gaudi2 register access layer, `pdma0_qm_masks.h`, and generated base-range definitions used by security and reset code.

## Integration Points
`gaudi2_security.c` references `mmPDMA0_QM_BASE`, PDMA0 QM ARC AUX ranges, and many PDMA0 QM registers while defining security/protection behavior. Queue setup, reset handling, and debug flows in the Gaudi2 device code use this address map to communicate with the PDMA0 command submission engine.

## Risks
Address drift is high impact: an incorrect constant can target the wrong hardware register, corrupt queue-manager state, or weaken protected-register filtering. Large repeated families increase off-by-one and wrong-instance risk, especially around CQ/CP instance count and 64-entry arbitration tables. Generated files should not be manually edited because local fixes can diverge from the source hardware description.

## Test Signals
Relevant tests are register-map sanity checks, protected-range validation, DMA queue bring-up, command submission/completion stress, reset and reinitialization, interrupt/error injection where available, and comparison with hardware register XML or firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_regs.h -->
