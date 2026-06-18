# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc_coefs.c

## Purpose

`dispc_coefs.c` supplies the hard-coded DISPC FIR scaler coefficient tables used by overlay scaling. The complete 314-line source was read. It defines 3-tap and 5-tap coefficient arrays for multiple M ranges and exposes a lookup helper.

## Important APIs, Types, and Functions

The file defines `static const struct dispc_coef` arrays `coef3_M8` through `coef3_M32` and `coef5_M8` through `coef5_M32`, each with eight phases. The only function is `dispc_ovl_get_scale_coef(int inc, int five_taps)`, which maps a FIR increment bucket to either the 3-tap or 5-tap table.

## Control Flow

Lookup divides `inc` by 128, walks a descending table of `{Mmin, Mmax, coef_3, coef_5}`, and returns the matching table pointer. Upscaling stronger than 2x intentionally maps to M11, M16, or M19 tables instead of M8 to reduce visible blockiness and outlines. If no bucket matches, it returns `NULL`.

## State and Persistence Behavior

All coefficient data is static read-only kernel data. There is no mutable state or persistence outside the compiled image.

## Dependencies and Integration Points

The file depends on `struct dispc_coef` from `dispc.h` and is consumed by `dispc_ovl_set_scale_coef()` in `dispc.c` when programming horizontal, vertical, and chroma FIR registers.

## Risks and Edge Cases

Returned `NULL` is not checked by `dispc_ovl_set_scale_coef()`, so scaling calculations must keep `inc` in supported ranges. Coefficients are hardware- and quality-sensitive; accidental edits can introduce image artifacts. The table uses signed 8-bit fields, so values must stay within the expected hardware format.

## Test Signals

Signals include lookup tests for every M bucket boundary, upscaling buckets 0-3, both 3-tap and 5-tap paths, display scaling visual tests, and static checks that callers do not request out-of-range increments.
