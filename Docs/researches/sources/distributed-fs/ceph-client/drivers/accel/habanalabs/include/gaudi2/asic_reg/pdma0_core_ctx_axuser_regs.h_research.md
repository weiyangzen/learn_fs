<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_axuser_regs.h

## Purpose
`pdma0_core_ctx_axuser_regs.h` defines AXUSER attribute registers for PDMA0 core context transactions. It controls the metadata attached to DMA context-originated HB/LB AXI traffic.

## Important APIs, types, and functions
The file exports `mmPDMA0_CORE_CTX_AXUSER_*` macros for HB ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved/page/core/E2E fields, read/write overrides, and LB coordinate/lock/reserved/override controls. It has no functions or types.

## Control flow
No executable flow exists. PDMA initialization or security setup programs these registers before enabling context execution, ensuring DMA context reads/writes use correct ASID, MMU, ordering, snoop, and fabric metadata.

## State and persistence
The hardware persists AXUSER policy for PDMA0 context traffic until reset or reconfiguration. It is static policy, not per-transfer software state.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file complements `pdma0_core_ctx_regs.h`, `pdma0_core_regs.h`, and Gaudi2 MMU/security setup.

## Risks and test signals
Wrong attributes can cause DMA to bypass translation incorrectly, hit protection faults, or violate ordering/snoop expectations. Test signals include PDMA context transfers in secure and non-secure modes, MMU bypass tests, coherency/no-snoop validation, and absence of fabric protection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_axuser_regs.h -->
