# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight_regs.h

## Purpose
`intel_backlight_regs.h` defines MMIO registers and bit masks for i915 native backlight PWM control across legacy CPU PWM, PCH split PWM, VLV/CHV pipe PWM, BXT/CNP PWM controllers, and utility-pin PWM output.

## Important APIs, Types, and Functions
The file is macro-only. Key definitions include `BLC_PWM_CTL2`, `BLC_PWM_CTL`, duty/frequency masks, legacy and polarity bits, PCH `BLC_PWM_PCH_CTL1/2`, CPU `BLC_PWM_CPU_CTL/2`, BXT `BXT_BLC_PWM_CTL/FREQ/DUTY`, VLV pipe-specific controls, histogram enable, and `UTIL_PIN_CTL` mode/polarity/pipe fields.

## Control Flow
The macros are consumed by `intel_backlight.c` platform callback tables. Setup paths read control/frequency/duty registers, enable paths program periods and enable bits, disable paths clear enable bits, and set paths update duty-cycle fields.

## State and Persistence
The header describes hardware state only. Register values persist until display power loss, BIOS/firmware changes, or driver writes. Software mirrors are in `panel->backlight`.

## Dependencies and Integration Points
It depends on `intel_display_reg_defs.h` and platform display base macros. It integrates with PCH/platform conditionals and register access helpers in the implementation.

## Risks
Many fields share similar names but differ by generation; for example PCH CTL1 is not layout-compatible with CTL2, while BXT controllers have separate duty/frequency registers. Incorrect mask selection can overwrite frequency while updating duty or enable the wrong pipe/controller. Utility pin programming affects controller 1 on BXT-style hardware.

## Test Signals
Coverage should include register dumps before/after enable/disable, brightness ramp tests, active-low panels, BXT controller 1 utility pin use, PCH override mode, VLV pipe A/B validation, and legacy combination mode behavior.
