<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_masks.h

## Purpose
`pdma0_qm_masks.h` defines the bit positions and masks for the Gaudi2 PDMA0 queue manager register block. It is paired with `pdma0_qm_regs.h`: the register header supplies `mmPDMA0_QM_*` addresses and this mask header supplies the field encoding contract for those registers. The file is auto-generated, GPL-2.0 tagged, guarded by `ASIC_REG_PDMA0_QM_MASKS_H_`, and contains 767 `#define` macros.

## Important APIs, Types, And Functions
There are no C types or functions. The API surface is a macro namespace:

- Global queue-manager controls and status: `PDMA0_QM_GLBL_CFG*`, `PDMA0_QM_GLBL_ERR_CFG*`, `PDMA0_QM_GLBL_STS*`, `PDMA0_QM_GLBL_ERR_STS_*`, `PDMA0_QM_GLBL_ERR_MSG_EN_*`, and `PDMA0_QM_GLBL_PROT_*`.
- Producer queue fields for four queues: `PDMA0_QM_PQ_BASE_*`, `PDMA0_QM_PQ_SIZE_*`, `PDMA0_QM_PQ_PI_*`, `PDMA0_QM_PQ_CI_*`, `PDMA0_QM_PQ_CFG*`, and `PDMA0_QM_PQ_STS*`.
- Completion queue fields for five queues: `PDMA0_QM_CQ_CFG*`, `PDMA0_QM_CQ_STS*`, `PDMA0_QM_CQ_PTR_*`, `PDMA0_QM_CQ_TSIZE*`, `PDMA0_QM_CQ_CTL*`, and `PDMA0_QM_CQ_IFIFO*`.
- Command processor fields: `PDMA0_QM_CP_MSG_BASE*`, `PDMA0_QM_CP_FENCE*`, `PDMA0_QM_CP_PRED*`, `PDMA0_QM_CP_CURRENT_INST_*`, and `PDMA0_QM_CP_STS_*`.
- PQC, arbitration, indirect gateway, rate limiter, AXI/cache, local range, error, interrupt, and performance counter fields.

The macros follow the generated convention `<register>_<field>_SHIFT` plus `<register>_<field>_MASK`. Callers should combine these with kernel bitfield helpers rather than hard-coded shifts.

## Control Flow
The header contains no control flow. Runtime control flow occurs in driver code that writes queue bases, sizes, producer/consumer indices, command processor message windows, arbitration weights, and interrupt masks using the companion register addresses. A typical sequence is: program base/size fields, configure queue and command processor limits, enable error reporting and global queue manager behavior, then poll status/error fields during execution or reset.

## State And Persistence
The macros describe volatile hardware state, not software-owned persistent state. Fields such as queue producer and consumer indices, inflight/free/credit counts, fence counters, global idle/stop bits, and performance counters reflect device state in MMIO registers. Some values persist across driver calls until hardware reset or explicit reprogramming; the header itself stores no data.

## Dependencies
The file depends only on the C preprocessor and its include guard. Effective use depends on:

- `pdma0_qm_regs.h` for matching register addresses.
- Linux register helpers and bitfield helpers in the Gaudi2 driver.
- Hardware documentation/generator consistency for reserved bits, field widths, and queue counts.

## Integration Points
Gaudi2 security code references the PDMA0 QM address range and many PDMA0 QM registers when constructing allowed or protected register lists. Queue-manager setup and diagnostics in the Gaudi2 driver use the same macro namespace to configure command submission, completion queues, command processor fences, interrupts, and error handling. These masks are also part of ABI-adjacent behavior because incorrect queue programming can affect DMA execution visible to user workloads.

## Risks
The main risk is drift between generated masks and silicon/firmware expectations. A wrong mask can silently corrupt adjacent reserved fields, misprogram queue pointers, leave errors unmasked, or break security assumptions around protected queue-manager registers. Repeated queue families also create indexing risk: code that assumes strides or counts must match the generated layout, especially for four PQ instances, five CQ/CP instances, and 64 arbitration-credit entries.

## Test Signals
Useful signals include successful Gaudi2 boot and firmware load, command queue submission/completion under DMA workloads, no unexpected `GLBL_ERR_STS` bits, correct interrupt masking/unmasking, security-regression checks for protected PDMA0 QM ranges, reset/reinit tests that verify idle/stop status, and register smoke tests that compare generated masks against known hardware register specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_masks.h -->
