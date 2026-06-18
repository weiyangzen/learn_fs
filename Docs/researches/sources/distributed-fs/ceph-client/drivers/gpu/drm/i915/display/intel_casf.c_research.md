# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.c

## Purpose

`intel_casf.c` implements Content Adaptive Sharpness Filter support for display hardware starting with Lunar Lake style display version 20+. CASF sharpens the image through the second pipe scaler, so the file computes the CRTC CASF state, programs the sharpness LUT and scaler coefficients, enables or disables the sharpness control register, and supports strength-only updates.

## Important APIs, Types, And Functions

The public entry points are `intel_casf_compute_config()`, `intel_casf_update_strength()`, `intel_casf_sharpness_get_config()`, `intel_casf_needs_scaler()`, `intel_casf_scaler_compute_config()`, `intel_casf_enable()`, and `intel_casf_disable()`. The code uses `crtc_state->uapi.sharpness_strength` as the user input and stores hardware-ready values in `crtc_state->hw.casf_params`: `casf_enable`, `strength`, `win_size`, and scaler filter `coeff[]`.

Internal helpers include `intel_casf_compute_win_size()` for selecting 3x3, 5x5, or 7x7 filter size from adjusted-mode pixel count, `intel_casf_filter_lut_load()` for loading the default 32-entry sharpness LUT, `convert_sharpness_coef_binary()` for converting percent-style coefficients to scaler mantissa/exponent format, and `intel_casf_write_coeff()` for programming 17 phases of 7-tap coefficients into scaler coefficient registers for scaler id 1.

## Control Flow

Atomic check calls `intel_casf_compute_config()`. If the platform lacks CASF, the function leaves state unchanged and succeeds. If user sharpness is zero, it disables CASF in CRTC state. If sharpness is nonzero, it rejects joiner configurations because the hardware does not support CASF with joiner pipes. Otherwise it enables CASF, clamps user strength to 0xef, adds 0x10 to convert to the hardware `(1.0 + strength)` 4.4 fixed-point encoding, chooses a filter size based on resolution, and calculates scaler coefficients.

`intel_casf_scaler_compute_config()` chooses one of three 7-tap coefficient templates according to `win_size`, normalizes the weights to percentages, and converts each tap to the scaler coefficient binary representation. At enable time, `intel_casf_enable()` loads the LUT, writes scaler coefficients, programs `SHARPNESS_CTL` with `FILTER_EN`, strength, and filter size, then calls `skl_scaler_setup_casf()` to configure the second pipe scaler. `intel_casf_disable()` clears scaler 1 control/window registers and sharpness control. `intel_casf_update_strength()` changes only the strength field and rewrites the scaler window size to latch the update.

## State And Persistence

CASF state is stored per CRTC in the atomic CRTC state, not in a separate global object. Hardware persistence consists of per-pipe `SHARPNESS_CTL`, `SHRPLUT_INDEX/DATA`, and scaler 1 coefficient/window/control registers. `intel_casf_sharpness_get_config()` reads `SHARPNESS_CTL` during state readout and reconstructs enable, strength, and window size when the filter is active.

## Dependencies And Integration Points

The file depends on CASF register definitions from `intel_casf_regs.h`, display register accessors from `intel_de.h`, CRTC/display state types, and scaler support in `skl_scaler.h`. It integrates with the DRM CRTC sharpness property created elsewhere, with scaler allocation logic that reserves scaler id 1 for CASF, with pipe config state dumping/checking, and with modeset logic that detects CASF enable/disable and strength changes.

## Risks

CASF consumes the second pipe scaler, so conflicts with pipe scaling or other scaler users are a primary risk. The joiner rejection must remain aligned with hardware capability. The coefficient writer warns and returns if scaler id is not 1; if scaler allocation changes, CASF may silently fail to program coefficients beyond that warning. Strength uses two encodings: user 0..255 and hardware fixed point with +0x10 offset and 0xef clamp. Readout warns if hardware strength is below 16, because such values cannot be represented as valid enabled user strength.

## Test Signals

Test signals include property tests that set sharpness 0, low, high, and over-clamp values; modesets at <=1080p, <=4K, and above 4K to exercise all filter sizes; joiner configurations that must fail with `-EINVAL`; scaler allocation tests proving scaler id 1 is reserved; and readout/state-check tests comparing `casf_enable`, `win_size`, and `strength`. Hardware traces should show writes to `SHRPLUT_*`, scaler coefficient registers, `SHARPNESS_CTL`, and scaler 1 window/control registers.
