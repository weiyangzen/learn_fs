# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_opp.c

## Purpose
This file implements the DCE output pixel processor formatter path. It programs bit-depth reduction, truncation, spatial dithering, temporal/frame-modulation dithering, clamp ranges, pixel encoding, dynamic expansion, and YCbCr 4:2:0 formatter memory/phase handling.

## Important APIs and Functions
Public functions include `dce110_opp_construct()`, optional `dce60_opp_construct()`, `dce110_opp_destroy()`, `dce110_opp_program_bit_depth_reduction()`, `dce110_opp_program_clamping_and_pixel_encoding()`, `dce110_opp_set_dyn_expansion()`, `dce110_opp_program_fmt()`, and `dce110_opp_set_clamping()`. Internal helpers implement generation-specific truncation (`set_truncation()`, `dce60_set_truncation()`), spatial dither, temporal dither, DCE6 and common clamping/pixel encoding, 4:2:0 formatter memory setup, and formatter resync FIFO reset.

## Control Flow
`dce110_opp_program_fmt()` optionally powers and selects 4:2:0 formatter memory, programs bit-depth reduction, programs clamping and pixel encoding, then resets/polls 4:2:0 phase lock when needed. Bit-depth reduction first disables previous truncation/dither state, then conditionally enables truncation, spatial dither seeds/modes, and temporal dither parameters. Clamping first disables clamp, then selects full, limited 8/10/12 bpc, or programmable range; common DCE writes programmable lower/upper RGB defaults while DCE6 lacks component clamp writes. Dynamic expansion is enabled for HDMI/DP/MST at 8, 10, and 12 bpc modes.

## State and Persistence
Software state is minimal: `struct dce110_opp` stores the embedded base object and register metadata. Hardware state persists in FMT dynamic expansion, bit depth, control, seed, temporal pattern, 4:2:0 memory, and clamp registers. The destructor frees the enclosing object and nulls the caller's pointer.

## Dependencies and Integration Points
The file depends on `dm_services.h`, fixed-point conversion helpers, `dce_opp.h`, `reg_helper.h`, and DC formatter parameter types from the OPP interface. It integrates downstream of timing/stream color decisions and upstream of stream encoder/link encoder output formatting.

## Risks and Test Signals
Risk areas include generation-specific missing fields, 4:2:0 paths using `FMT_CBCR_BIT_REDUCTION_BYPASS` and phase-lock polling, unsupported 10 bpc temporal dither being intentionally disabled, and stale formatter state if callers bypass `opp_program_fmt()`. DCE6 differences are substantial enough to require separate compile and display tests. Useful tests include RGB and YCbCr422/420 modes, limited/full range clamp validation, 6/8/10/12 bpc output checks, spatial and temporal dithering enable/disable tests, and suspend/resume formatter state restoration.
