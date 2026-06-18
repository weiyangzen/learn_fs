# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.h

## Purpose

This header declares the Vega10 thermal and fan-control interface used by the hwmgr function table and related PowerPlay code.

## Important APIs, Types, and Functions

`struct vega10_temperature` groups edge, hotspot, HBM, VR, liquid, and PLX temperature channels, although the paired C file only exposes a single current temperature read in this subset. Macros define thermal alert masks, min/max raw reading ranges, min/max alert temperatures, and static PWM/RPM mode constants. Exported functions cover temperature readout, thermal controller start/stop/uninitialize, alert disable, fan speed capability query, PWM/RPM fan get/set, static/default mode switching, SMC fan-control start/stop, reset-to-default, and mGPU fan boost.

## Control Flow, State, and Persistence

The header owns no state. Its functions operate on `struct pp_hwmgr`, especially `hwmgr->thermal_controller`, fan default-mode cache fields, platform caps, and Vega10 backend SMC feature flags. Startup requires a `struct PP_TemperatureRange` supplied by the caller.

## Dependencies and Integration Points

It includes `hwmgr.h` and is consumed by `vega10_hwmgr.c` to populate thermal and fan callbacks. The C implementation depends on fan tables and PowerTune limits parsed from BIOS tables before these APIs are invoked.

## Risks and Test Signals

The declared surface mixes low-level register mode control with high-level SMC fan control. Tests should verify callback registration, no-fan board behavior, RPM/PWM support flags, thermal startup with null and valid ranges, and that all declared exports have matching definitions in the linked build.
