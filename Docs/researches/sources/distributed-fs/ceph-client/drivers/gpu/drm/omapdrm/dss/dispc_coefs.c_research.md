# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dispc_coefs.c

## Purpose
`dispc_coefs.c` provides the scaler FIR coefficient tables used by DISPC overlay programming. It isolates the static 3-tap and 5-tap coefficient sets from the main controller code and exposes a single lookup function that maps a requested FIR increment to the closest supported hardware table.

## Important APIs, Types, And Data
- The file defines paired arrays `coef3_M*` and `coef5_M*`, each with eight `struct dispc_coef` entries for the eight FIR phases. The suffix represents the coefficient family selected by the normalized increment bucket.
- `dispc_ovl_get_scale_coef(int inc, int five_taps)` is the only function. It returns a pointer to one of the static coefficient arrays or `NULL` if the increment falls outside known buckets.
- The tables cover downscaling and upscaling buckets: direct buckets from `M8` through `M32`, plus special upscaling buckets for normalized increments 3, 2, and 0..1 that intentionally use `M11`, `M16`, and `M19` to avoid visible artifacts.

## Control Flow
The lookup divides the caller-supplied increment by 128, then scans a small ordered table of `{Mmin, Mmax, coef_3, coef_5}` descriptors. On the first inclusive range match it returns either the 5-tap or 3-tap coefficient pointer depending on `five_taps`. If no range matches, it returns `NULL`; `dispc.c` logs an error and skips coefficient programming in that case.

## State And Persistence Behavior
All coefficient tables are `static const`; the file has no mutable state, allocation, hardware access, or persistence. Returned pointers remain valid for the lifetime of the module and are read by `dispc_ovl_set_scale_coef()` when programming FIR registers.

## Dependencies And Integration Points
The file depends on `struct dispc_coef` and `dispc_ovl_get_scale_coef()` declared in `dispc.h`, local DSS definitions from `omapdss.h`, and `ARRAY_SIZE` from the kernel. Its only direct integration point is the scaler code in `dispc.c`, which separately requests horizontal coefficients and vertical coefficients, with vertical selection depending on whether five-tap mode is active.

## Risks And Edge Cases
- `inc` is integer-divided by 128 before matching, so boundary behavior depends on truncation. Incorrect increment calculation in the caller can select a neighboring coefficient family.
- The function accepts `int five_taps` rather than `bool`; any nonzero value selects 5-tap coefficients.
- Returning `NULL` leaves the caller unable to program coefficients. Current caller logs but does not fail the whole overlay setup at that exact point, so prior validation must keep increments inside supported ranges.
- Visual quality depends on these magic tables. Changes need image-quality and artifact testing, not just compile testing.

## Test Signals
Unit-level tests can cover bucket boundaries after `inc / 128`, special upscaling mappings for normalized increments 0..3, and 3-tap versus 5-tap selection. Integration tests should exercise scaling ratios around bucket edges, five-tap fallback behavior, and visual/hardware validation for upscaling beyond 2x where the special tables are used to reduce blockiness/outlines.
