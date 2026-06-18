# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-regs.h

## Purpose
`ccs-regs.h` is a generated register definition header for MIPI CCS/SMIA camera sensors. It assigns CCI register descriptors, field masks, shifts, enumerated values, and generated array bounds for identity, mode, timing, PLL, crop/output, CSI/PHY, binning/scaling, test pattern, correction, flash, PDAF, and bracketing registers.

## Important APIs, Types, and Functions
Important macros include `CCS_R_*` register descriptors, `CCS_FL_FLOAT_IREAL`, `CCS_FL_IREAL`, and `CCS_BUILD_BUG`. Register descriptors use V4L2 CCI width macros such as `CCI_REG8`, `CCI_REG16`, and `CCI_REG32`, with private CCS flags for real-number conversion. Field macros follow `*_SHIFT`, `*_MASK`, and symbolic value patterns. Arrayed registers include descriptor arrays, lane bitrate arrays, binning subtype arrays, lane seed values, data-transfer page data, and bracketing LUT entries.

## Control Flow
There is no executable control flow. Core and register-access code use the macros to build CCI reads/writes, parse field values, calculate limits, and program sensor state. `CCS_BUILD_BUG` verifies that CCS private flags fit inside CCI private mask space.

## State and Persistence Behavior
The file stores no runtime state. It describes volatile hardware register state and generated constants. Some registers represent read-only capabilities, some are controls, and some are streaming-time state with side effects.

## Dependencies and Integration Points
It depends on Linux bit macros and `media/v4l2-cci.h`. It is consumed by `ccs-limits.c`, `ccs-core.c`, `ccs-reg-access.c`, quirks, and any code using `ccs_read()`/`ccs_write()`. Real-number flags integrate with `ccs_reg_conv()`.

## Risks and Edge Cases
Because the file is generated, manual edits risk mismatching the CCS specification. Register aliases and overlapping addresses, such as some PHY/USL definitions, require consumers to use the correct symbolic context. Private conversion flags must not be stripped before reads that need converted MHz/Mbps values. Array bounds macros must agree with generated limit sizes.

## Test Signals
Build with `CCS_BUILD_BUG`, probe hardware covering CCS 1.0/1.1 and SMIA compatibility, validate field decoding for identity/capabilities, confirm PLL/PHY timing writes use the correct widths, and compare generated register values against the CCS specification or known sensor traces.
