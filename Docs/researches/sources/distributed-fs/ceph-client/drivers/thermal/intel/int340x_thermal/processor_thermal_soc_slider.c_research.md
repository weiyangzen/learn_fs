# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_soc_slider.c

## Purpose

`processor_thermal_soc_slider.c` integrates the Processor Thermal Device SoC efficiency slider with Linux platform profiles, translating performance/balanced/low-power profiles into a firmware slider register.

## Important APIs, Types, and Functions

Exports are `proc_thermal_soc_power_slider_add()`, `proc_thermal_soc_power_slider_suspend()`, and `proc_thermal_soc_power_slider_resume()`. Module parameters `slider_balance` and `slider_offset` tune the balanced slider value and firmware offset. `set_soc_power_profile()` programs the 64-bit register at offset `0x5B38`. Platform profile callbacks convert between `enum platform_profile_option` and slider values.

## Control Flow

Add programs the default balanced profile and registers a platform profile provider named `SoC Power Slider` with low-power, balanced, and performance choices. Profile set locks parameter state, applies the latest balanced parameter, converts the requested profile, sets slider bits, sets enable bit, and optionally sets offset. Profile get reads the current register and maps it back to a supported profile.

## State and Persistence Behavior

Static globals hold slider value policy, offset, and one saved register image for suspend. Hardware slider state persists in the MMIO register and is restored on resume.

## Dependencies and Integration Points

It depends on PCI MMIO, `platform_profile`, bitfield helpers, and common processor thermal feature detection. The newer PCI driver enables it on PTL/WCL/NVL feature masks.

## Risks and Test Signals

Risks include static saved state across devices, possible mismatch between module parameter get and pending balanced parameter, unsupported firmware slider values causing profile_get failure, and offset rules tied to exact min/max slider values. Test signals include platform profile registration, profile get/set round trips, module parameter validation, suspend/resume restore, and feature-mask probe on supported IDs.
