# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/transform.h

## Purpose

`transform.h` defines the transform/DPP-side abstraction for scaling, line-buffer setup, gamut/CSC adjustment, regamma/degamma, input LUTs, cursor attributes, and scaler filter selection. It bridges older transform naming with newer DPP capabilities.

## Important APIs, Types, And Functions

The file defines `struct transform`, colorimetry and AVI infoframe-related enums, graphics gamut adjustment type, CSC adjustment, overscan, scaling ratios, sharpness, line-buffer parameters, scaler initialization, and `scaler_data`. `transform_funcs` includes reset, scaler programming, pixel-storage depth, optimal tap calculation, gamut remap, OPP CSC default/adjustment, regamma LUT power/config/programming, regamma mode, IPP degamma/input LUT/setup/bypass, and cursor attributes.

It also declares scaler filter selectors such as `get_filter_2tap_16p`, `get_filter_4tap_64p`, and higher-tap 64-phase filters. `dpp_caps` exposes scaler processing format, line-buffer partition limits, and an ASIC-specific partition calculator.

## Control Flow

Plane programming computes scaler ratios/taps and line-buffer settings, asks the transform implementation for optimal taps, programs scaler/filter state, sets pixel storage depth, and applies color transforms/LUTs. Bypass hooks are used when no transform work is required.

## State And Persistence Behavior

Transform object state is minimal, but programmed scaler, line buffer, LUT, CSC, degamma, and cursor state persists in DPP/transform hardware until reprogrammed. Filter tables are read-only data selected by ratio and tap count.

## Dependencies And Integration Points

The header depends on `dc_hw_types.h`, fixed-point math, cursor/gamma types, and shared color enums. It integrates with resource scaling validation, DPP construction, MPC/OPP color management, cursor programming, and infoframe colorimetry decisions.

## Risks And Test Signals

Risks include wrong tap selection, line-buffer partition miscalculation, color-space mismatch, LUT bank errors, and cursor attribute regressions. Test signals include scaled planes, rotation/viewport cases, cursor on scaled surfaces, color-management tests, scaler filter visual quality, and underflow checks with high-bandwidth scaling.
