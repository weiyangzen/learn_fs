# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_backlight.h

## Purpose
`intel_backlight.h` declares the i915 display backlight API used by panel setup, modeset, ACPI/native brightness controls, and optional Linux backlight class registration.

## Important APIs, Types, and Functions
The API exposes function-table initialization, setup/destroy, enable/update/disable, ACPI and raw PWM setters, brightness inversion/scaling helpers, and conditional `intel_backlight_device_register/unregister()` wrappers. It forward-declares display, connector, panel, encoder, atomic, and CRTC state types.

## Control Flow
Panel code calls `intel_backlight_init_funcs()` before `intel_backlight_setup()`. Modeset paths call enable/update/disable around panel power transitions. User/firmware brightness updates enter through class device callbacks or `intel_backlight_set_acpi()`. Cleanup calls destroy and unregister functions.

## State and Persistence
The header stores no state. Implementations mutate `intel_panel.backlight` fields and hardware PWM state.

## Dependencies and Integration Points
It depends only on `linux/types.h` plus forward declarations, making it a stable interface for display code. `CONFIG_BACKLIGHT_CLASS_DEVICE` controls whether registration functions are real or no-op inline stubs.

## Risks
Callers must ensure `intel_panel` has initialized backlight function pointers before setup. The header exposes low-level PWM conversion helpers, so misuse outside established locking or range contracts can bypass normal clamping.

## Test Signals
Compile tests cover configuration with and without `CONFIG_BACKLIGHT_CLASS_DEVICE`. Runtime signals come from panel initialization, modeset backlight enable/disable, ACPI brightness updates, and class-device registration behavior.
