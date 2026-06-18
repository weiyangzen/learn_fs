# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c

## Purpose
`dcn30_dpp.c` implements the DCN 3.0 display pipe processor behavior for AMD Display Core. It wires the DPP function table to register-programming routines for format conversion, post-CSC, pre-degamma ROM selection, cursor attributes, scaler tap selection, blend/shaper/3D LUT programming, deferred memory power-down, state readback, and DPP construction.

## Important APIs, types, and functions
- `dpp3_construct()` initializes `struct dcn3_dpp` with DC context, instance, register tables, function table, and caps.
- `dpp30_read_state()` and `dpp30_read_reg_state()` read live DPP enable, color pipeline, scaler, MPC, and control registers into debug state structures.
- `dpp3_cnv_setup()` maps `enum surface_pixel_format` and expansion/CSC inputs into CNVC format, alpha, 2-bit alpha LUT, dealpha/re-alpha, and post-CSC registers.
- `dpp3_program_post_csc()` programs either the ICSC or COMA post-CSC matrix bank, using local hardcoded color-space matrices or caller-provided matrix entries.
- `dpp3_set_pre_degam()`, `dpp3_set_cursor_attributes()`, and `dpp3_get_optimal_number_of_taps()` cover pre-degamma ROM mode, cursor format/degamma state, and adaptive scaler tap selection.
- Local helpers program double-buffered blend gamma LUTs, shaper LUTs, and tetrahedral 3D LUTs while managing CM memory low-power state.
- `dcn30_dpp_funcs` is the integration surface consumed by DC resource construction and hardware sequencing.

## Control flow
Construction is straightforward: `dpp3_construct()` stores register descriptors and exposes `dcn30_dpp_funcs` plus `dcn30_dpp_cap`. Runtime programming usually starts through function-table callbacks. Plane setup enters `dpp3_cnv_setup()`, which resets format-control defaults, selects a hardware pixel format code, programs alpha behavior, optionally writes 2-bit alpha LUT values, disables pre-dealpha/re-alpha, and then calls `dpp3_program_post_csc()` with bypass or ICSC selection.

Post-CSC uses double-buffering. If bypass is requested it clears `CM_POST_CSC_MODE`; otherwise it chooses built-in matrix coefficients or caller coefficients, reads `CM_POST_CSC_MODE_CURRENT`, selects the alternate ICSC/COMA register bank, programs matrix registers through `cm_helper_program_color_matrices()`, and switches `CM_POST_CSC_MODE`.

The color LUT paths follow the same pattern. `dpp3_program_blnd_lut()`, `dpp3_program_shaper()`, and `dpp3_program_3dlut()` bypass and schedule memory power-down on NULL parameters. With valid parameters, they power the target memory, choose the alternate RAM bank, program region/control registers plus LUT data, and update mode/select registers so hardware latches the new bank. `dpp3_deferred_update()` later completes power-down requests only after hardware reports the bypass state on vupdate.

Scaler tap selection in `dpp3_get_optimal_number_of_taps()` derives defaults from scaling ratios, clamps chroma horizontal taps to supported values, checks debug max-downscale limits, calculates line-buffer partitions through DPP caps, clamps vertical taps to partition-derived limits, and collapses identity axes to one tap unless `always_scale` is set.

## State and persistence behavior
This file maintains only runtime software and hardware state. Software state lives in `struct dpp` and `struct dcn3_dpp`: cached function/cap pointers, register tables, cursor attribute snapshots, deferred low-power bits, scaler cache fields, and LUT/filter pointers. Persistent effects are register writes to DPP/CNVC/CM/DSCL blocks; there is no disk or cross-boot persistence. Low-power behavior is stateful across frames through `deferred_reg_writes` and `ctx->dc->optimized_required`, because memory shutdown is postponed until the bypass mode has latched.

## Dependencies and integration points
The implementation depends on Display Core base types, `reg_helper` register macros, `dcn30_dpp.h` register tables, `dcn30_cm_common.h` matrix/gamma helpers, fixed-point helpers, DC debug/cap flags, and common DPP functions from DCN1/DCN2. It integrates upward through `struct dpp_funcs`, and downward through ASIC-specific register offsets/masks supplied by resource construction.

## Risks and edge cases
The highest-risk areas are register bank selection and latch timing for post-CSC, blend LUT, shaper, and 3D LUT. Incorrect current-mode reads or select writes can update the bank currently scanned out. LUT data paths assume valid nonzero `params->hw_points_num` and correctly sized tetrahedral arrays. `dpp3_set3dlut_ram12()` writes entries in pairs and assumes an even entry count. Low-power paths rely on debug flags and mode-current checks; stale `deferred_reg_writes` can assert if a LUT is re-enabled before the bypass latch. Format setup has many hardware magic pixel codes, and YCrCb video formats disable cursors on DCN30 while related newer code does not. Tap selection must match line-buffer partition math or the scaler can underflow.

## Test signals
Useful signals include DC bring-up on DCN30 hardware, plane format tests across RGB, FP16, RGBE, and YUV 4:2:0 variants; CSC adjustment and color-space bypass tests; cursor format and degamma tests; identity/upscale/downscale scaler validation with debug `always_scale`; blend/shaper/3D LUT programming with RAM A/B flips; low-power memory enable/disable coverage; register readback through debug state; and visual CRC tests for gamma, CSC, cursor, and scaler output.
