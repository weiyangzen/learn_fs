# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dpp.h

## Purpose

`dpp.h` defines the Display Pipe and Plane processing abstraction for DCN. DPP performs per-plane conversion, cursor composition, scaling, color management, LUT/3D LUT programming, gamut remap, HDR multiplier, alpha/keying, histogram, and DPP clock control.

## Important APIs, Types, And Functions

Important types include `defer_reg_writes`, `dpp`, static `dpp_input_csc_matrix`, `dpp_grph_csc_adjustment`, `cnv_color_keyer_params`, `cnv_alpha_2bit_lut`, `dcn_dpp_state`, `dcn_dpp_reg_state`, `CM_bias_params`, and `dpp_funcs`. The vtable covers GAMCOR/pre-degamma/dealpha/bias, state readback, reset, scaler setup, pixel storage depth, optimal taps, gamut remap, CSC default/adjustment, regamma/degamma LUTs, setup/full bypass, cursor attributes/position/matrix/disable, HDR multiplier, DPP clock control, deferred update, blend/shaper/3D LUTs, alpha keyer, histogram control/read, and gamut readback.

## Control Flow

Plane programming sets DPP setup from pixel format, expansion, input CSC, color space, and alpha LUT; then scaler, pixel depth, color pipeline, cursor state, and optional LUTs are programmed. Deferred updates can batch disabling color blocks. Readback functions support debug and color-state logging. Cursor updates use both DPP and HUBP programming.

## State And Persistence Behavior

`dpp` persists per DPP instance in the resource pool. It caches regamma/degamma/shaper params, cursor attributes, deferred-register flags, color-management bypass mode, cursor-offload flag, and cursor register mirrors. Hardware persists DPP registers and LUT RAM until reprogrammed or reset.

## Dependencies And Integration Points

It includes `transform.h` and cursor register cache. It integrates with `plane_resource`, HWSS plane enable/update paths, color management, SPL/scaler data, OPP/MPC blending, HUBP cursor fetch, and DML scaler/timing outputs.

## Risks And Edge Cases

Color pipeline ordering is complex; disabling LUTs or bypassing CM in the wrong order can cause visible color shifts. Static CSC matrices must match hardware coefficient format. Cursor state is split across DPP and HUBP. LUT bank selection, deferred writes, and 3D LUT programming require careful synchronization. Scaler tap selection must obey DPP caps.

## Test Signals

Tests should cover RGB/YUV formats, scaling ratios/taps, rotations via upstream HUBP, degamma/regamma/shaper/blend/3D LUTs, gamut remap, HDR multiplier, cursor movement/offload, alpha keying, histogram, and reset/power transitions. Visual color errors, cursor corruption, and scaler artifacts are primary signals.
