# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.h

## Purpose
`gsc-regs.h` defines the G-Scaler MMIO register offsets and bitfield construction macros used by `gsc-regs.c`. It is the hardware contract for enable/reset/IRQ, input and output formats, scaling ratios, image sizes, offsets, and DMA base-address slots.

## Important APIs, Types, and Functions
The header exports constants for `GSC_ENABLE`, `GSC_SW_RESET`, `GSC_IRQ`, `GSC_IN_CON`, `GSC_SRCIMG_SIZE`, `GSC_SRCIMG_OFFSET`, `GSC_CROPPED_SIZE`, `GSC_OUT_CON`, `GSC_SCALED_SIZE`, prescaler/main-scaler ratio registers, destination size/offset registers, and Y/Cb/Cr input/output address mask/base registers. It provides field macros such as `GSC_SRCIMG_WIDTH(x)`, `GSC_CROPPED_HEIGHT(x)`, `GSC_OUT_GLOBAL_ALPHA(x)`, `GSC_PRESC_H_RATIO(x)`, and indexed address macros like `GSC_IN_BASE_ADDR_Y(n)`.

## Control Flow
There is no executable control flow. The macros are composed by the register helper layer before `writel()` calls.

## State and Persistence
No software state is stored here. The values describe volatile hardware registers.

## Dependencies and Integration Points
This header is included indirectly through `gsc-core.h` and directly supports `gsc-regs.c`. Its field names mirror the G-Scaler hardware block and must remain synchronized with format and scaler logic in the GSC core.

## Risks and Edge Cases
Several macros shift caller-provided values without range checking, so callers must clamp dimensions, offsets, ratios, and alpha before composing register fields. The indexed DMA base macros encode fixed slot spacing; using an index beyond the hardware buffer count would address unintended registers. Typographical names such as `OEDER` are part of the internal API and should be changed only with all users.

## Test Signals
Compile-time coverage comes from all helper call sites resolving these macros. Runtime validation is register trace or hardware behavior for every supported format/path: enable, reset, frame-done IRQ, crop/scale sizes, input/output path selection, buffer masks, and indexed Y/Cb/Cr address programming.
