# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_reg.h

## Purpose

`ni_reg.h` is a compact Northern Islands display-register definition header for DCE5-era Radeon hardware. It defines register offsets and bitfield helper macros for gamma, prescale, color-space conversion, degamma/regamma, DisplayPort MSE/MST scheduling, and digital front-end/back-end controls.

## Important Definitions

The header defines DCE5 register offsets such as `NI_INPUT_GAMMA_CONTROL`, `NI_PRESCALE_GRPH_CONTROL`, `NI_INPUT_CSC_CONTROL`, `NI_OUTPUT_CSC_CONTROL`, `NI_DEGAMMA_CONTROL`, `NI_REGAMMA_CONTROL`, `NI_DP_MSE_*`, `NI_DIG_BE_CNTL`, and `NI_DIG_FE_CNTL`.

Bitfield helpers include gamma/degamma/regamma mode encoders, CSC mode encoders, DP MSE rate and slot allocation fields, digital front-end source/mode/HPD selection, and digital front-end control fields for stereosync, dual-link, swap, and symbol clock.

## Control Flow and State

There is no executable control flow and no owned state. The macros are used by display programming code to compose values written through Radeon MMIO helpers. The persistent effect occurs only when another source file writes these register values to hardware.

## Dependencies and Integration Points

This header is included by NI/Cayman display and ASIC code that needs DCE5 register names without duplicating raw offsets. In this work item, `ni.c` includes it, though most heavy use of these display macros likely lives in other display files.

## Risks and Test Signals

- Bitfield macros assume caller-supplied `x` values fit the documented width; most mask locally before shifting, but semantic range validation is left to callers.
- A few DP MSE macros in this header reference `x` but are object-like macros rather than function-like macros, which is suspicious and would fail if expanded as constants. Existing callers may avoid those specific forms or define/use replacement macros elsewhere.
- Wrong offsets or shifts can break color management, DP MST/MSE timing, encoder routing, or link mode programming.

Build coverage catches malformed macro expansion when used. Runtime test signals include modeset success on NI DCE5 outputs, gamma/CSC programming behavior, DP MST stream allocation, HDMI/DVI/LVDS/DP encoder routing, and absence of display underruns or link-training regressions.
