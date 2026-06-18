# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.c

## Purpose
`dcn401_dpp.c` defines the DCN 4.0.1 DPP constructor, function table, basic state readback, CNVC plane setup, and 64-partition line-buffer calculators. It reuses much of DCN30/DCN35 color and cursor behavior while replacing scaler programming with the DCN401 DSCL implementation.

## Important APIs, types, and functions
- `dpp401_construct()` initializes `struct dcn401_dpp` with DCN401 register tables, function table, and caps.
- `dpp401_read_state()` currently reports only `DPP_CLOCK_ENABLE` and leaves DCN4 detailed state as TODO.
- `dpp401_dpp_setup()` programs CNVC format, alpha, 2-bit alpha LUT, pre-dealpha/re-alpha, and post-CSC selection.
- `dscl401_calc_lb_num_partitions()` and `dscl401_spl_calc_lb_num_partitions()` compute line-buffer partitions for classic and SPL scaler data, capped at 64.
- `dcn401_dpp_funcs` wires DCN401 to `dpp401_dscl_set_scaler_manual_scale()`, DCN401 cursor callbacks, DCN35 bias/scale, DCN30 GAMCOR/pre-degamma/CM bias, and cursor matrix setup.

## Control flow
Plane setup mirrors DCN30: reset format conversion defaults, map `surface_pixel_format` to hardware pixel format IDs, derive default color space and ICSC select for video formats, optionally write 2-bit alpha LUT, program alpha/dealpha/re-alpha controls, and invoke `dpp3_program_post_csc()` with either provided adjustment matrix or default matrix. Unlike DCN30, it does not force-disable cursor for YCrCb 4:2:0 formats.

Construction stores context, instance, function/cap pointers, and register table pointers. Line-buffer partition calculators use the same memory constants as DCN32 but cap luma/chroma partitions to 64, reflecting larger DCN401 capacity. The function table intentionally leaves gamut remap, full bypass, BLNDGAM, shaper, and 3D LUT callbacks NULL, while adding cursor matrix support.

## State and persistence behavior
State is runtime-only in `struct dcn401_dpp`, inherited `struct dpp` fields, cached scaler data, and hardware registers. The line-buffer calculators are stateless. Detailed DPP state readback is incomplete for DCN4, so software cannot currently persist or reconstruct the full color/scaler state through `dpp401_read_state()`.

## Dependencies and integration points
The file depends on DC core types, `dcn401_dpp.h`, DCN30 color helpers, DCN32 partition patterns, and DCN35 bias/scale helpers. It integrates with DC resource construction via `dpp401_construct()`, with scaler programming via `dcn401_dpp_dscl.c`, and with cursor matrix/attributes via `dcn401_dpp_cm.c`.

## Risks and edge cases
The DCN4 read-state TODO reduces diagnostics and may break tooling expecting parity with DCN30 readback. `dpp401_dpp_setup()` calls DCN30 post-CSC helper with DCN401 register tables, so field compatibility is critical. NULL callbacks for gamut remap/full bypass/color LUTs require higher-level code to check capability before calling. The partition cap checks use `> 64` despite caps advertising `max_lb_partitions = 63`, preserving hardware convention but creating off-by-one maintenance risk.

## Test signals
Key signals include DCN401 build and display bring-up, format coverage for RGB/YUV/FP16/RGBE, post-CSC adjustment tests, cursor matrix path tests, scaler partition/tap tests for 64-partition cases, NULL callback tolerance in DC color-management paths, and debug readback coverage demonstrating the current limited state read.
