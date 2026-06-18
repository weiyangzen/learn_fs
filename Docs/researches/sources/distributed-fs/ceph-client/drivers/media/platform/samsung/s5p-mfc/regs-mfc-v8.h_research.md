# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v8.h

## Purpose
This header defines the v8 extension to the v7/v6 MFC register map. It repositions or adds decoder DPB, stride, scratch, CPB, display, decoded-frame, returned-tag, and SEI registers; it also updates selected encoder rate-control and aspect/H.264 option registers and v8 memory sizing formulas.

## Important APIs, Types, and Constants
Important exports include v8 decoder registers for minimum scratch size, first/second/third-plane DPB sizes and strides, DPB address arrays, MV buffer, scratch buffer, CPB buffer, available DPB flags, display and decoded first/second/third plane addresses, frame types, crop info, picture profile, returned tags, and MVC/SEI state. Encoder updates include fixed QP, RC config/bounds/params, padding, MV range, VBV, min scratch, aspect ratio, and H.264 options. Constants set v8 context sizes, TMV/ME/scratch formulas, 64-byte plane alignment, firmware size, CPB size, version, and port count.

## Control Flow and State
The header has no functions. It changes what state the operation layer reads after firmware commands and where it writes buffer addresses before commands. The default decoder format in `s5p_mfc_dec_init()` switches to `NV12M` for v8+ hardware, reflecting the plane-address changes declared here.

## Dependencies and Integration Points
It includes `regs-mfc-v7.h` and therefore inherits v6/v7 semantics. The core variant table maps `samsung,mfc-v8` and `samsung,exynos5433-mfc` to this version, with Exynos5433 using a three-clock setup. Decoder and encoder operation files use the v8 offsets under `IS_MFCV8_PLUS()` style predicates.

## Risks
Several v8 offsets overlap conceptually with v6 names but not addresses, so operation dispatch must select the correct register table. Plane alignment changed and v8 supports layouts different from older tiled defaults; incorrect size or stride programming can produce corrupted frames without immediate command failure.

## Test Signals
Signals include v8 probe on both compatible variants, `NV12M` decode output, three-plane decode where supported by later variants, scratch-size queries, DPB reconfiguration on resolution change, and encoder rate-control/aspect controls.
