<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_qm_axuser_nonsecured_regs.h

## Purpose
`pdma1_qm_axuser_nonsecured_regs.h` defines the PDMA1 queue-manager non-secured AXUSER register addresses. It is auto-generated, address-only, guarded by `ASIC_REG_PDMA1_QM_AXUSER_NONSECURED_REGS_H_`, and exports 20 macros starting at `0x4C9AB80`.

## Important APIs, Types, And Functions
The macro API mirrors the AXUSER prototype: HB ASID, MMU bypass, ordering, snoop, write reduction, read atomic, QoS, reserved, EMEM CPage, core, E2E coordination, write/read override low/high, and LB coordination/lock/reserved/override. No types or functions are declared.

## Control Flow
There is no in-header control flow. During device setup, driver code writes `mmPDMA1_QM_AXUSER_NONSECURED_HB_ASID` and `mmPDMA1_QM_AXUSER_NONSECURED_HB_MMU_BP` before using PDMA1 queue-manager traffic. This configures transaction identity for non-secured queue-manager accesses.

## State And Persistence
The state is hardware-resident AXUSER configuration. It persists until reset or explicit writes. Since these are full register addresses without masks, caller write ordering and values define all behavior.

## Dependencies
Consumers depend on Gaudi2 register access helpers and on shared AXUSER semantic definitions from hardware documentation. This file is commonly used alongside `pdma1_core_ctx_axuser_regs.h` to cover both queue-manager and core-context PDMA1 paths.

## Integration Points
Integration is with Gaudi2 MMU/ASID setup and PDMA queue-manager initialization. Correct values are needed for non-secured PDMA1 transactions to be translated and attributed properly.

## Risks
Incorrect ASID, bypass, override, or ordering attributes can break DMA isolation or cause hard-to-debug ordering/coherency failures. Because the header has no masks, broad writes can overwrite reserved or policy fields if callers do not use known-good values.

## Test Signals
Look for successful PDMA1 operation after MMU setup, multi-context ASID isolation, no unexpected RAZWI/security violations, and parity between configured QM AXUSER and core-context AXUSER registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_qm_axuser_nonsecured_regs.h -->
