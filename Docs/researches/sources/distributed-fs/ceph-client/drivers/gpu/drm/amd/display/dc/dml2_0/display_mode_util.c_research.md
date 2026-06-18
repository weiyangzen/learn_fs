# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.c

## Purpose
`display_mode_util.c` implements common DML math, format, mapping, and debug-print utilities. It is support code for formula implementation and for dumping DML inputs, support status, bounding boxes, clock policies, and generated register structures.

## Important APIs, types, and functions
Math helpers include `dml_ceil()`, `dml_floor()`, `dml_min*()`, `dml_max*()`, `dml_log()`, `dml_log2()`, `dml_round()`, `dml_pow()`, and `dml_round_to_multiple()`. Format and mapping helpers include `dml_util_is_420()`, `dml_is_vertical_rotation()`, `dml_get_cursor_bit_per_pixel()`, `dml_get_num_active_planes()`, `dml_get_num_active_pipes()`, `dml_get_plane_idx()`, `dml_get_pipe_idx()`, and `dml_calc_pipe_plane_mapping()`. Debug routines print RQ, DLG, TTU, policy, mode-support, display-config, SoC bounding-box, and clock-config structures.

## Control flow
The math functions are direct formula helpers. Debug functions walk fixed-size or caller-supplied plane counts and emit fields with `dml_print()`, with `fail_only` filtering in `dml_print_dml_mode_support_info()`. Mapping functions count active planes from nonzero viewport width, sum `DPPPerSurface` for active planes, and build `pipe_plane` by expanding each plane's DPP count.

## State and persistence behavior
The file has no persistent state. It reads caller-provided DML structures and may depend on `ASSERT()` for invalid formats or missing pipe mappings. It writes only to logging output and output arrays supplied by callers.

## Dependencies and integration points
It depends on `display_mode_util.h`, the DML core structures, `dml_print()`, and `ASSERT()`. Its outputs feed diagnostics and the pipe-plane mapping used by mode programming consumers.

## Risks and edge cases
The private `_log()` type-puns a `float` through `int *`, which is sensitive to aliasing and IEEE layout assumptions. `dml_util_is_420()` asserts on several source formats rather than returning false. `dml_get_num_active_planes()` treats a zero viewport width as inactive. `dml_calc_pipe_plane_mapping()` does not bounds-check the expanded DPP count against `__DML_NUM_PLANES__`. Debug dumps have many fields and can drift from structure changes.

## Test signals
Useful signals include formula regression vectors, NaN behavior for min/max, zero granularity handling, 420/rotation/cursor mappings, pipe-plane mapping with ODM/MPC multi-DPP cases, invalid enum assertion tests, and debug-output smoke tests for populated support and programming structures.
