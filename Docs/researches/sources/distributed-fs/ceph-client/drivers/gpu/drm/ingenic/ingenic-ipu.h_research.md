<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.h

## Purpose
Defines the private Ingenic IPU register map and bit fields used by `ingenic-ipu.c` to program control, status, DMA addresses, image geometry, strides, resize LUTs, and color-space conversion.

## Important APIs, types, and functions
This header exports macros only. Important groups are `JZ_REG_IPU_*` register offsets, `JZ_IPU_CTRL_*` control bits, input/output geometry shifts, stride shifts, input/output format encodings, RGB component order encodings, JZ4725B resize LUT fields, JZ4760 bicubic coefficient fields, and CSC offset shifts.

## Control flow
There is no executable flow. The implementation combines these constants into regmap writes during atomic modeset and IRQ handling.

## State and persistence
No C state is stored here. The macros describe persistent MMIO state in the IPU block: run/stop/reset/chip-enable state, DMA addresses, format configuration, resize coefficients, and CSC coefficients.

## Dependencies and integration points
Includes `linux/bitops.h` for `BIT()`. It is private to the Ingenic DRM IPU implementation and avoids exposing IPU registers through a public DRM ABI.

## Risks
Register-field aliases are hardware-specific: for example RGB and YUV input format encodings share bit positions, and incorrect output order bits produce swapped colors. Any shift or mask drift directly corrupts IPU programming.

## Test signals
Build coverage catches missing macros. Runtime signals are correct color ordering, correct YUV conversion, successful scaling, and stable frame IRQ behavior across JZ4725B and JZ4760 compatible devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-ipu.h -->
