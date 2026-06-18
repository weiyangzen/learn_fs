# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc.h

## Purpose
`dispc.h` is the DISPC register-address contract shared by the DISPC implementation and scaling coefficient provider. It defines common register offsets, overlay register address macros, the FIR coefficient structure, the coefficient lookup prototype, and inline helpers that map logical OMAP channels/planes to the register offsets used by different generations of the OMAP display controller.

## Important APIs, Types, And Data
- Common register constants cover revision, sysconfig/status, IRQ status/enable, control/config registers, global alpha, multiple LCD manager controls/configs, clock divisor, global FIFO/MFLAG control, and gamma table registers.
- Overlay register macros such as `DISPC_OVL_BA0(n)`, `DISPC_OVL_ATTRIBUTES(n)`, `DISPC_OVL_FIR(n)`, `DISPC_OVL_CONV_COEF(n, i)`, `DISPC_OVL_PRELOAD(n)`, and `DISPC_OVL_MFLAG_THRESHOLD(n)` compose a plane base address with a plane-specific offset helper.
- `struct dispc_coef` contains five signed/unsigned coefficient fields used by the scaler writer in `dispc.c`; `dispc_ovl_get_scale_coef()` is implemented in `dispc_coefs.c`.
- Manager helpers include `DISPC_DEFAULT_COLOR()`, `DISPC_TRANS_COLOR()`, `DISPC_TIMING_H/V()`, `DISPC_POL_FREQ()`, `DISPC_DIVISORo()`, `DISPC_SIZE_MGR()`, `DISPC_DATA_CYCLE1/2/3()`, and `DISPC_CPR_COEF_R/G/B()`.
- Overlay helpers include `DISPC_OVL_BASE()` and per-plane offsets for base addresses, UV addresses, position, size, attributes, FIFO threshold/status, row/pixel increments, GFX CLUT/window skip, FIR/FIR2, picture size, accumulator registers, FIR coefficient arrays, color conversion coefficients, preload, and MFLAG thresholds.

## Control Flow
This header has no runtime control flow beyond inline switch dispatch. The caller supplies `enum omap_channel` or `enum omap_plane_id`; the helper returns the hardware offset for that logical resource. Unsupported combinations call `BUG()` and return zero only to satisfy control-flow analysis. `dispc.c` uses these helpers in register read/write macros, context save/restore, debugfs dumping, overlay setup, timing programming, FIFO initialization, gamma restore, and errata workarounds.

## State And Persistence Behavior
`dispc.h` stores no mutable state. Its constants are compile-time mappings from logical DSS resources to hardware register offsets. The only persistent contract is ABI-like within the driver: if a helper maps a plane/channel incorrectly, every user of that macro writes the wrong MMIO address.

## Dependencies And Integration Points
The header depends on local enum definitions from `omapdss.h` being visible before use, kernel integer types, and `BUG()`. It is included by `dispc.c` and `dispc_coefs.c`. It encodes hardware layout knowledge from OMAP2 through OMAP5/DRA7 DISPC generations, including special offsets for VIDEO3 and writeback, which differ from earlier GFX/VIDEO1/VIDEO2 layouts.

## Risks And Edge Cases
- The helper functions intentionally crash on invalid channels/planes. This is appropriate for internal invariants but makes caller-side validation important.
- Some helpers are only valid for LCD managers and reject DIGIT; others are invalid for GFX or writeback. Misusing generic-looking macros can hit `BUG()` or write nonsensical offsets.
- `DISPC_OVL_MFLAG_THRESHOLD(n)` expands directly to an absolute offset helper, unlike most overlay macros that add `DISPC_OVL_BASE(n)`. This is correct for the global MFLAG threshold register layout but easy to misuse if assumed to follow the base-plus-offset pattern.
- Offset differences for VIDEO3/WB and second UV/scaler registers are subtle. Adding a new plane or SoC generation requires a full audit of every switch.

## Test Signals
Compile coverage is the first signal because many helpers are inline. Additional validation can assert known offsets for every manager and plane, exercise debugfs register dump address coverage, and run plane setup paths for each plane type to ensure no valid caller path reaches a `BUG()`. Hardware bring-up should compare dumped register addresses against the TRM for OMAP2/3/4/5/DRA7 and verify VIDEO3/WB/NV12 paths specifically.
