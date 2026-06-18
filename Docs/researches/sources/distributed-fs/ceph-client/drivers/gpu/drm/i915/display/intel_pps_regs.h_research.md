# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps_regs.h

## Purpose
`intel_pps_regs.h` defines the MMIO register addresses and bitfields for Intel panel power sequencing. It is a pure register contract used by `intel_pps.c` and related display code to read status, control panel power/VDD/backlight, program on/off delays, and configure power-cycle delay.

## Important Registers And Fields
`PPS_BASE`, `VLV_PPS_BASE`, and `PCH_PPS_BASE` describe the possible MMIO base addresses. `_MMIO_PPS(display, pps_idx, reg)` maps a PPS register offset through `display->pps.mmio_base` and the sequencer index.

`PP_STATUS(display, pps_idx)` exposes `PP_ON`, `PP_READY`, sequence type fields, cycle-delay-active state, and detailed sequence state values such as off-idle, on-idle, power-up substates, power-down substates, and reset.

`PP_CONTROL(display, pps_idx)` exposes legacy register unlock bits, BXT/CNP+ power-cycle delay field, `EDP_FORCE_VDD`, `EDP_BLC_ENABLE`, `PANEL_POWER_RESET`, and `PANEL_POWER_ON`.

`PP_ON_DELAYS` carries panel port selection, panel power-up delay, and backlight-on delay. `PP_OFF_DELAYS` carries panel power-down and backlight-off delays. `PP_DIVISOR` carries the older reference divider and panel power-cycle delay fields.

## Control Flow And Integration
The register macros are consumed by `intel_pps_get_registers()`, `wait_panel_status()`, VDD/panel on/off functions, delay readout, and register initialization in `intel_pps.c`. Platform code chooses the correct base through `intel_pps_setup()` and the correct `pps_idx` or VLV pipe before applying these macros.

## State, Dependencies, Risks, And Test Signals
This header stores no runtime state, but it defines the bit meanings that gate PPS state machines. Incorrect masks or field definitions would produce severe panel power sequencing failures: stuck waits, wrong delay programming, VDD not forced, backlight left disabled, or locked legacy registers.

Tests should indirectly validate these definitions through eDP power-cycle tests, PP_STATUS wait behavior, delay readback/debugfs output, and platform coverage for old PP_DIVISOR versus newer PP_CONTROL power-cycle programming.
