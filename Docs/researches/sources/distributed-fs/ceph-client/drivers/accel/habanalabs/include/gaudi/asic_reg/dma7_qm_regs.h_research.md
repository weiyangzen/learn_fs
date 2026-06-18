<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_qm_regs.h

### Purpose
`dma7_qm_regs.h` is an auto-generated Gaudi ASIC register-address catalog for the DMA7 queue manager block, identified in the file as `DMA7_QM` with prototype `QMAN`. It exposes 406 `mmDMA7_QM_*` constants spanning `0x5E8000` through `0x5E8D00`, so driver code can program DMA7 queue-manager MMIO registers by symbolic name instead of hard-coded offsets.

### Important APIs, Types, And Functions
There are no functions, structs, enums, or executable control-flow APIs. The public surface is the include guard `ASIC_REG_DMA7_QM_REGS_H_` plus `#define` constants. Important register families include `GLBL_*` configuration/status/security properties, `PQ_*` producer queue base/size/index/config/status registers, `CQ_*` completion queue config/pointer/status registers, `CP_*` command processor message bases, LDMA offsets, fence counters, current-instruction/status/debug registers, `ARB_*` arbitration and credit registers, `CGM_*` clock-gating/management registers, local range, rate-limiter, indirect APB gateway, and global error/memory-init status registers.

### Control Flow
The file has no runtime branches. Its implicit control flow is the queue-manager programming sequence used by consumers: configure global queue-manager properties, set producer queue base/size and producer/consumer indexes, configure completion queues, program command-processor message bases and LDMA offsets, tune arbitration/credits/rate limiting, then read status/error/fence/current-instruction registers while queues execute. Initialization code references `mmDMA7_QM_GLBL_CFG0` and `mmDMA7_QM_GLBL_CFG1` to reset/stop parts of the block, and MMU/security code uses the secure/non-secure property registers and protection-bit offsets.

### State, Persistence, And Dependencies
The header itself persists no state, but each macro names device-resident state in the Gaudi MMIO aperture. Persistent hardware state includes queue bases and indexes, CQ pointers and sizes, secure/non-secure ARUSER/AWUSER properties, command processor fence counters and message-base addresses, arbitration credits, and error/status latches. The file depends on the hardware register-generation pipeline remaining synchronized with the Gaudi DMA7 QMAN specification. Consumers depend on common Habanalabs register access helpers such as `WREG32()`/`RREG32()`, bitfield headers for shifts and masks, and the broader Gaudi security/MMU initialization code.

### Integration Points
`gaudi.c` writes `mmDMA7_QM_GLBL_CFG0` and `mmDMA7_QM_GLBL_CFG1` during block initialization/shutdown and prepares `mmDMA7_QM_GLBL_NON_SECURE_PROPS_0..4` for ASID/MMU handling. `gaudi_security.c` derives protection-bit addresses from `mmDMA7_QM_BASE` and many `mmDMA7_QM_*` offsets, including global, PQ, CQ, and CP ranges, so this map is also part of the driver's security programming surface. Queue-manager command submission and diagnostics elsewhere include this generated header indirectly through the Gaudi ASIC register umbrella headers.

### Risks
The main risk is register drift: a wrong address silently directs MMIO writes to the wrong hardware register. DMA7 queue-manager errors can corrupt command queues, completion queues, arbitration fairness, or security attributes. The repeated per-engine arrays are index-sensitive; using a DMA0/DMA1 or PQ/CQ index with the wrong constant can misconfigure a different queue. Because this is generated, manual edits are especially risky and should be replaced by regenerating from the ASIC database. Security-sensitive constants such as secure/non-secure properties, AXUSER fields, and protection-bit locations need extra scrutiny because incorrect values can overexpose privileged DMA paths.

### Test Signals
Useful signals include successful Gaudi probe and DMA7 queue-manager initialization, queue submission/completion through DMA7, no unexpected values in `GLBL_ERR_*` or `ARB_ERR_*`, stable producer/consumer/CQ pointer movement under DMA load, command processor fence-counter progress, suspend/reset recovery without stale queue state, and security tests showing DMA7 protected registers and non-secure properties are programmed as intended. Static validation should compare all generated addresses against the authoritative ASIC register database and ensure no duplicate or out-of-range `mmDMA7_QM_*` definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_qm_regs.h -->
