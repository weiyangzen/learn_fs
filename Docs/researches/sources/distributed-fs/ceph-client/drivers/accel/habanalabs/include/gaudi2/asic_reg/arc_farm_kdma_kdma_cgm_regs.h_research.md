<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_kdma_cgm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_kdma_cgm_regs.h

## Purpose
`arc_farm_kdma_kdma_cgm_regs.h` is the generated address map for the ARC farm KDMA clock-gating manager (`ARC_FARM_KDMA_KDMA_CGM`), prototype `QMAN_CGM`. It defines the three register addresses `CFG`, `STS`, and `CFG1` in the 0x4E8BE00-0x4E8BE08 range.

## Important APIs, types, and functions
The only API is three `mmARC_FARM_KDMA_KDMA_CGM_*` constants. `CFG` and `CFG1` are configuration entry points for clock-gating behavior; `STS` is the matching status readback register. Field definitions are not present in this file, so users must rely on the generated mask/spec companion or existing hardware programming sequences.

## Control flow
There is no software control flow. Initialization or power-management code writes clock-gating configuration, then may read `STS` to confirm the manager accepted or reflected the requested state. Reset paths should return these registers to the expected default before KDMA/QMAN work starts.

## State and persistence behavior
Clock-gating configuration is persistent hardware state until reset or reprogramming. A stale or invalid setting can make a block appear idle, gated, or unresponsive even if queue/DMA context registers are otherwise correctly programmed.

## Dependencies and integration points
This header integrates with KDMA/QMAN power-management setup and any common `QMAN_CGM` helper used across Gaudi2 blocks. It is adjacent to the ARC farm KDMA core and context banks and should be programmed in a sequence compatible with those blocks' enable/halt state.

## Risks and edge cases
The risk is low at compile time but high at runtime: there are only addresses, no field masks, so callers can write magic values with little local type safety. Bad clock-gating values can create intermittent hangs that look like queue or DMA bugs.

## Test signals
Test signals include KDMA initialization after cold boot and reset, clock-gating status readback, sustained DMA traffic with clock gating enabled, and no timeout when transitioning the block between idle and active states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_kdma_cgm_regs.h -->
