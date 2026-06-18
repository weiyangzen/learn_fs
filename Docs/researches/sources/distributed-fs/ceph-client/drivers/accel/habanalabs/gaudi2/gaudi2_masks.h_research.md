# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2_masks.h

## Purpose
This private header collects Gaudi2 bit masks and composed register values used across the driver. It gives implementation files named masks for queue-manager error handling, protection, enable/idle/stop/flush bits, engine idle checks, PCIe and MME errors, sync-manager values, MMU/ASID protection bits, rotator halt bits, MSI-X address matching, and PCIe wrapper SEI interrupt fields.

## Important APIs, types, and functions
- Queue-manager masks compose error message enable, stop-on-error enable, protection/trust, normal enable, PDMA-specific enables, idle checks, ARC idle checks, stop bits, and flush bits.
- `MME_ARCH_IDLE_MASK`, `TPC_IDLE_MASK`, and `CGM_IDLE_MASK` group the architecture status bits needed to decide whether engines are idle.
- Arbiter and PCIe masks cover QM arbiter overflow/watchdog/LBW errors and PCIe FLR control interrupt masking.
- MME accumulator interrupt masks identify WBC response errors and arithmetic positive/negative infinity or NaN conditions.
- Sync-manager completion queue constants define high-to-low compare/mask values and low-bit extraction.
- `MMU_STATIC_MULTI_PAGE_SIZE_HOP4_PAGE_SIZE_MASK` and `STLB_HOP_CONFIGURATION_ONLY_LARGE_PAGE_MASK` wrap generated register field masks.
- `AXUSER_HB_SEC_ASID_MASK`, `AXUSER_HB_SEC_MMBP_MASK`, and `MMUBP_ASID_MASK` define the ASID/MMU-bypass bits used by CoreSight ETR trace AWUSER/ARUSER programming.
- Rotator MSS halt masks identify WBC, RSB, and MRSB halt bits.
- PCIe DBI MSI-X address-match masks and PCIe wrapper SEI interrupt indication/mask fields name low-level interrupt bits.

## Control flow
The header has no executable flow. It influences runtime flow by giving implementation files exact values to write to hardware registers or compare against hardware status. For example, queue setup can write `QMAN_ENABLE` or PDMA-specific enable masks, stop paths can use the `QM_GLBL_CFG*` stop/flush masks, idle polling can compare against `QM_IDLE_MASK` and `TPC_IDLE_MASK`, and CoreSight ETR can use `MMUBP_ASID_MASK` in `RMWREG32` calls to preserve unrelated AWUSER/ARUSER bits while updating the ASID/MMU-bypass field.

## State and persistence behavior
No state is stored in this file. The masks drive persistent hardware register state when used by implementation files. Because some macros are composed write values rather than pure field masks, confusing those categories could leave queues trusted, enabled, stopped, flushed, or error-reporting incorrectly until reset or reprogramming.

## Dependencies and integration points
The file depends on the generated Gaudi2 register header for shift and mask constants. It is included by `gaudi2_coresight_regs.h` and likely by other Gaudi2 implementation files that configure queues, engines, MMU, PCIe, rotator, and protection/error paths. Its `MMUBP_ASID_MASK` is directly integrated with CoreSight ETR address-space configuration in `gaudi2_coresight.c`.

## Risks and edge cases
- Several macros are full register write values while others are bit masks for read/modify/write; callers must use them in the correct mode.
- The typo `CHOISE` in QM arbiter masks is part of the public private-name surface and could propagate.
- Hard-coded literals such as `0x100`, `0x40`, CQ compare values, and AXUSER masks rely on generated headers and hardware documentation staying aligned.
- Shifted constants use plain `1` and small integer literals in many places; if a future field crosses 31 bits, callers may need widened literals.
- Error and idle masks are derived from representative DCORE0/PDMA0/TPC0 register definitions and assume identical bit layouts across duplicated engines.

## Test signals
Signals include successful queue enable/disable and idle polling, expected stop-on-error behavior, trusted/untrusted protection transitions, accurate MME/TPC idle detection, CoreSight ETR trace writes using the caller ASID, rotator halt paths affecting the intended sub-blocks, PCIe FLR/MSI-X masking behaving as expected, and interrupt/error handlers decoding the same bits that hardware reports.
