# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispreg.h

## Purpose
`ispreg.h` is the central register offset and bitfield map for the OMAP3 ISP driver. For this subset it supplies all CCP2, CCDC/SBL, histogram, H3A, preview, resizer, CSI-2, CSI PHY, and SoC control-register constants used by the implementation files.

## Important APIs, Types, And Functions
- No functions or types are defined; the file is a macro contract.
- Top-level ISP macros cover revision, sysconfig/status, IRQ enables/status, ISP control, and timing-control registers.
- CCP2 macros define sysconfig/reset, LCx IRQ/status/control/data registers, memory-channel registers, and control-bit shifts/masks.
- SBL macros define overflow flags, read/write path registers, and SDR request-expansion fields used for bandwidth throttling.
- Histogram/H3A macros define stats engine register offsets, PCR bits, window/paxel fields, histogram bin/gain/region fields, and busy bits.
- Preview/resizer macros define processing register offsets, table addresses, enable bits, format/YC position fields, matrix/offset shifts, crop size fields, and resizer filter coefficient fields.
- CSI-2/CSI PHY macros define receiver sysconfig, IRQ, control, PHY config, context registers, timing fields, PHY timing registers, and OMAP3430/3630 syscon routing bits.

## Control Flow
There is no runtime control flow. Driver C files compose these offsets and masks with `isp_reg_readl()`, `isp_reg_writel()`, `isp_reg_set()`, `isp_reg_clr()`, and `isp_reg_clr_set()` to program hardware.

## State And Persistence
The header has no state; it describes volatile hardware state. Correctness depends on these constants matching the SoC TRM and silicon revision behavior. Many modules cache desired state elsewhere and use this header to restore registers after reset or stream start.

## Dependencies And Integration Points
Every OMAP3 ISP block implementation depends on this file. It integrates with `isp.h` register access abstractions and with platform-specific syscon routing in `ispcsiphy.c`. It also encodes hardware revision differences referenced by CCP2, CSI2, and preview code.

## Risks And Edge Cases
- A typo in a shift or mask silently corrupts hardware programming; examples worth scrutiny include macros where mask definitions reuse a count shift for skip fields or where a sync-pattern mask references a non-shift macro name.
- Some macros are revision-specific, especially CSI2C and OMAP3630 PHY/control fields; using them on the wrong silicon can be invalid.
- Large groups of coefficient macros are repetitive and easy to update inconsistently.
- Because this file is included broadly, macro name collisions or semantic changes have wide blast radius.

## Test Signals
Most validation is integration-level: stream start register traces, IRQ decoding, format/crop hardware programming, histogram/H3A stats operation, PHY route/power tests, and suspend/resume context restore. Static checks comparing macros to TRM tables and targeted unit-style tests for register value composition would catch many regressions.
