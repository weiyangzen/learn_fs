<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_regs.h

## Purpose
`dcore0_edma0_core_regs.h` is the generated address map for the `DCORE0_EDMA0_CORE` DMA core control/status block in the `0x41CB000-0x41CBE34` range. It exposes 67 `mm...` constants for enabling, halting, flushing, protection, clock gating, HB/LB read and write limits, AXI cache attributes, inflight counters, error reporting, context status snapshots, debug counters, local-to-host filtering, idle indications, and APB enable controls.

## Important APIs, types, and functions
The header has no functions or types. Major register groups are `CFG_0/1`, `PROT`, `CKG`, `RD_GLBL`, HB/LB read max outstanding/size/arcache/inflight/rate-limit registers, HB/LB write max outstanding/AWID/AWCACHE/inflight/rate-limit registers, write-completion controls, `ERR_CFG`, `ERR_CAUSE`, error-message address/data registers, `STS0/STS1`, read/write context status selectors and snapshots, `PWRLP_*`, `DBG_*`, APB base/enabler registers, `E2E_CRED_ASYNC_CFG`, L2H compare/mask pairs, and `IDLE_IND_MASK`.

## Control flow
The file only defines addresses. Runtime code typically enables the core via `CFG_0`, tunes outstanding/rate/cache limits, programs error handling, submits contexts through the sibling context bank, polls `STS0.BUSY` and `STS1.IS_HALT`, and uses `CFG_1` halt/flush bits during teardown or reset. Debug flows read descriptor counts, buffer status, descriptor ids, and context snapshot registers selected by `STS_RD_CTX_SEL` or `STS_WR_CTX_SEL`.

## State and persistence behavior
All state is in the DMA hardware block. Configuration and error-message routing persist until reset or reprogramming; status and inflight counters change as DMA traffic progresses. `ERR_CAUSE` and debug/status registers provide latched or sampled state used by recovery paths, while halt/flush bits can block forward progress if left asserted.

## Dependencies and integration points
This address map integrates with the matching DMA core mask header, the context register bank for descriptor details, AXUSER programming, QMAN command submission, reset/recovery code, and device error interrupt handlers. It is one generated instance of the common `DMA_CORE` prototype, so consumers often share code across KDMA and EDMA blocks while substituting the base macro namespace.

## Risks and edge cases
Subtle bugs come from treating KDMA and EDMA instances as interchangeable while using the wrong base address, leaving halt/flush asserted, masking `ERR_CAUSE` bits unintentionally, or setting HB/LB outstanding and rate limits outside hardware expectations. The L2H compare/mask and APB enabler registers can affect address filtering and debug access, so stale values can create hard-to-debug traffic drops.

## Test signals
Test signals include successful engine enable/disable, DMA traffic under HB and LB paths, correct busy-to-idle transitions, recovery after halt/flush, populated debug descriptor counters during load, and expected interrupt/error-message behavior when HB/LB read/write faults or descriptor overflow are injected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_core_regs.h -->
