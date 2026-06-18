<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_nonsecured_regs.h

## Purpose
`pdma0_qm_axuser_nonsecured_regs.h` defines AXUSER attributes for non-secured PDMA0 queue-manager traffic.

## Important APIs, types, and functions
The file exports `mmPDMA0_QM_AXUSER_NONSECURED_*` macros for HB ASID, MMU bypass, ordering, no-snoop, write reduction, read atomic, QoS, reserved/page/core/E2E metadata, read/write override low/high registers, and LB coordinate/lock/reserved/override controls. It has no functions or types.

## Control flow
No code executes. Initialization programs these registers before non-secure PDMA queue traffic is enabled. Queue submissions then inherit this transaction metadata when the QMAN reads/writes queues or messages.

## State and persistence
The hardware persists non-secure QMAN AXUSER policy until reset or reconfiguration. It governs a traffic class, not individual software descriptors.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block integrates with `pdma0_qm_axuser_secured_regs.h`, PDMA QMAN setup, MMU/security mode, and fabric protection configuration.

## Risks and test signals
Incorrect non-secure attributes can cause queue reads/writes to bypass translation wrongly or fail protection checks. Test signals include non-secure PDMA queue submission, MMU/protection fault injection, no-snoop/coherency validation, and correct behavior when switching security modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_qm_axuser_nonsecured_regs.h -->
