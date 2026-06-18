# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/panel_cntl.h

## Purpose

`panel_cntl.h` defines the panel-control abstraction used for embedded panels. It centralizes panel power, backlight, and panel-specific control hooks behind a small DC hardware object.

## Important APIs, Types, And Functions

The header defines `struct panel_cntl` with context, instance, stored state, and `panel_cntl_funcs`. The function table covers panel control destruction and panel/backlight operations such as hardware initialization, power control, backlight enabling, PWM/backlight level programming, and state reads depending on ASIC implementation.

## Control Flow

eDP enablement sequences typically power the panel, wait required T7/T9/T12 intervals in link/panel code, enable backlight PWM or AUX backlight, then set brightness. Disable paths reverse brightness/backlight/panel power ordering.

## State And Persistence Behavior

The object persists in the resource pool and may cache current panel/backlight state. Hardware state persists in panel power and PWM/backlight registers or firmware-controlled panel state.

## Dependencies And Integration Points

Panel control integrates with eDP link service functions, DMUB panel replay/PSR flows, backlight exports to DRM, and power sequencing in DPMS and suspend/resume.

## Risks And Test Signals

Risks include incorrect panel power sequencing, brightness scaling bugs, missing waits, and NULL hooks on unsupported ASICs. Test signals include eDP boot display, backlight sysfs/DRM brightness changes, suspend/resume, PSR/replay transitions, and panel power-off/on hot paths.
