<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_masks.h

## Purpose
`arc_farm_kdma_ctx_axuser_masks.h` is the generated bitfield map for the `ARC_FARM_KDMA_CTX_AXUSER` AXUSER registers. It provides 74 shift/mask macros for encoding ASID, MMU bypass, ordering, snoop, reduction, atomic, QOS, reserved, coordinate, override, and LB lock/override fields for DMA context traffic.

## Important APIs, types, and functions
There are no functions or C types. Important fields are `HB_ASID_WR/RD`, `HB_MMU_BP_WR/RD`, `HB_STRONG_ORDER_WR/RD`, `HB_NO_SNOOP_WR/RD`, `HB_WR_REDUCTION` fields for indication, dtype, op, rounding, and max, `HB_RD_ATOMIC` indication/addition-size/MSB-mask fields, `HB_QOS_WR/RD`, HB reserved bits, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD_X/Y`, HB write/read override low/high values, and LB coordinate/lock/reserved/override values.

## Control flow
The header has no runtime logic. It is used during AXUSER setup before queue or DMA traffic is allowed to run. Callers compose values using these masks and write them to the companion AXUSER register addresses; later DMA commits and QMAN commands rely on these attributes being stable.

## State and persistence behavior
The masks describe persistent hardware configuration fields. ASID, MMU bypass, ordering, snoop, QOS, reduction, atomic, and override values remain in the register bank until reset or reprogramming and can affect every subsequent transaction from the associated context.

## Dependencies and integration points
This mask header integrates with `arc_farm_kdma_ctx_axuser_regs.h` and with common code that also programs EDMA/QMAN AXUSER blocks using the same `AXUSER` prototype. It must stay aligned with security/MMU initialization, ASID allocation, and bus-routing/e2e-coordinate setup.

## Risks and edge cases
Risks include stale ASID or bypass attributes crossing context boundaries, QOS or no-snoop settings reducing coherency/performance, incorrect reduction/atomic encodings changing memory semantics, and software writing reserved bits as if they were portable feature controls. Field-width drift versus the address header or hardware spec would produce silent transaction-attribute bugs.

## Test signals
Validation includes MMU-on and MMU-bypass traffic, ASID isolation tests, HB and LB transactions, atomic/reduction paths if exposed, cache/no-snoop behavior checks, and negative tests that should produce protection or RAZWI errors for invalid ASID/security combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_axuser_masks.h -->
