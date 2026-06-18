# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.h

## Purpose

`dispc.h` is the DISPC register map and inline register-address helper header. The complete 907-line file was read. It defines common, manager, overlay, FIR, writeback, preload, and MFLAG register offsets plus helper functions mapping `enum omap_channel` and `enum omap_plane` to SoC register addresses used by `dispc.c`.

## Important APIs, Types, and Functions

The public data type is `struct dispc_coef`, used by `dispc_coefs.c` and scaler programming. It declares `dispc_ovl_get_scale_coef()`. Macros include `DISPC_REVISION`, `DISPC_IRQSTATUS`, `DISPC_CONTROL`, `DISPC_CONFIG`, `DISPC_OVL_*`, and `DISPC_*` register constructors. Inline helpers include manager helpers such as `DISPC_DEFAULT_COLOR()`, `DISPC_TIMING_H()`, `DISPC_DIVISORo()`, and overlay helpers such as `DISPC_OVL_BASE()`, `DISPC_BA0_OFFSET()`, `DISPC_FIR_COEF_*_OFFSET()`, `DISPC_PRELOAD_OFFSET()`, and `DISPC_MFLAG_THRESHOLD_OFFSET()`.

## Control Flow

The header has no independent runtime flow, but its inline switches execute whenever `dispc.c` computes MMIO addresses. Unsupported channel/plane combinations intentionally call `BUG()` and return 0.

## State and Persistence Behavior

No runtime state is owned by the header. It defines compile-time register constants and offset calculations for DISPC hardware state.

## Dependencies and Integration Points

It depends on OMAP DSS enum definitions from the include graph. `dispc.c` uses it for every register access, and `dispc_coefs.c` uses `struct dispc_coef` plus the coefficient lookup declaration.

## Risks and Edge Cases

The offset helpers encode hardware layout assumptions for different overlays, managers, and writeback. Several helpers deliberately reject GFX or DIGIT combinations. Any register offset error can silently program the wrong hardware register. The header mixes base macros and inline offsets, so callers must choose the right constructor for plane/manager type.

## Test Signals

Signals include compile coverage for all helpers, register dump comparison against TRM offsets, exercising GFX/video/writeback code paths, OMAP4+ LCD2/LCD3 coverage, and avoiding unsupported enum combinations in callers.
