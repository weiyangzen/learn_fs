<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_secured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_secured_regs.h

## Purpose
`pdma0_qm_axuser_secured_regs.h` defines AXUSER attributes for secured PDMA0 queue-manager traffic.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_AXUSER_SECURED_*` macros for HB ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved/page/core/E2E metadata, read/write override registers, and LB coordinate/lock/reserved/override controls. No C functions or types exist.

## Control flow
There is no executable flow. Secure-mode initialization programs these attributes before secured QMAN queues or firmware-controlled submissions run. Hardware applies them to secured PDMA QMAN AXI transactions.

## State and persistence
The attributes persist as secured traffic policy until reset or explicit reprogramming. They must stay consistent with firmware security expectations and the MMU/protection tables.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with the non-secured AXUSER block, PDMA QMAN/core setup, and `gaudi2_security.c`.

## Risks and test signals
Wrong secured attributes can break secure firmware operation or accidentally downgrade protected traffic. Test signals include secure PDMA queue operation, protection tests distinguishing secured from non-secured traffic, correct ASID/MMU behavior, and no APB/fabric secure-write errors during queue traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_secured_regs.h -->
