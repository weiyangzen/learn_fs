# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.c

## Purpose
`dcn42_dpp.c` adapts DCN401 DPP behavior for DCN 4.2 and adds CM histogram control/readback support. It also updates DPP setup for DCN42 alpha LUT register layout and color-space CSC selection.

## Important APIs, types, and functions
- `dpp42_construct()` initializes `struct dcn42_dpp` with DCN42 register tables, function table, and caps.
- `dpp42_dpp_cm_hist_control()` programs CM histogram tap point, channel enables, source selections, channel crossbars, format, read channel mask, and RGB-to-luma coefficients.
- `dpp42_dpp_cm_hist_read()` locks ready histogram buffers, reads 256 bins for enabled channels, accumulates into `struct cm_hist`, and unlocks.
- `dpp42_dpp_setup()` programs CNVC format/alpha and post-CSC similar to DCN401, but writes split `ALPHA_2BIT_LUT01/23` registers and only uses ICSC for YCbCr or higher color-space values.
- `get_hist_rgb_luma_coefs()` chooses BT.709 or BT.2020 fixed-point luma coefficients.
- `dcn42_dpp_funcs` combines DCN401 scaler/cursor functions, DCN35 clock/bias-scale functions, DCN30 GAMCOR/CM helpers, and new histogram callbacks.

## Control flow
Histogram control writes ten fields in `CM_HIST_CNTL`. If source 2 is RGB-to-luma, it writes BT.2020 luma coefficients for 2020 RGB color spaces and BT.709 coefficients otherwise; if not, it writes pass-through green/Y coefficients. Histogram read validates the output pointer, reads the configured channel mask, checks buffer A/B ready status, locks the histogram block, resets index to zero, iterates 256 bins, reads one register per enabled channel per bin, accumulates into the caller's histogram arrays, unlocks, and returns whether data was read.

DPP setup follows the standard CNVC path: reset format controls, map surface format to pixel format/alpha defaults, derive color space, program split 2-bit alpha LUT registers for 10-bit formats, set pixel format and alpha, clear pre-dealpha/re-alpha, and call `dpp3_program_post_csc()` with caller matrix or defaults. Its adjustment path bypasses CSC for RGB-like color spaces and selects ICSC for YCbCr color spaces.

Construction stores context, instance, function/cap pointers, and DCN42 register tables. Caps advertise floating DSCL processing, 63 max line-buffer partitions, and the DCN401 partition calculator.

## State and persistence behavior
Histogram output accumulates into caller-owned `struct cm_hist`; the function does not clear bins before adding. Hardware histogram buffers, lock state, and ready status are register-backed. DPP setup and scaler/cursor state remains runtime-only in `struct dcn42_dpp`, inherited DPP shadows, and hardware registers.

## Dependencies and integration points
The file depends on `dcn42_dpp.h`, DCN401 DPP and scaler functions, DCN35 clock/bias-scale functions, DCN30 CM helpers, register helpers, and DC color/histogram structures. It integrates upward through histogram callbacks in `struct dpp_funcs` and downward through DCN42-specific histogram registers.

## Risks and edge cases
Histogram read uses logical OR of ready statuses and does not distinguish which hardware buffer is ready. It accumulates rather than assigns, so callers must clear `cm_hist` when they need per-read samples. Lock/unlock sequencing is critical to avoid reading changing bins. `dpp42_dpp_setup()` casts the base DPP to `struct dcn401_dpp` even though construction uses `struct dcn42_dpp`; this relies on identical leading layout for base/register pointers and is a maintenance hazard. The split alpha LUT registers differ from DCN401, so wrong register tables will corrupt alpha programming.

## Test signals
Validation should include DCN42 bring-up, histogram enable/read for each channel mask and tap point, RGB-to-luma coefficients for BT.709 versus BT.2020, repeated histogram reads with known accumulation behavior, CNVC format coverage including 2-bit alpha formats, post-CSC adjustment for RGB and YCbCr inputs, inherited scaler/cursor tests, and register-table layout tests for the DCN401 cast assumption.
