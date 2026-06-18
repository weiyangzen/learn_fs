# sources/distributed-fs/ceph-client/drivers/video/backlight/gpio_backlight.c

## Purpose
This simple platform driver turns one GPIO into a binary backlight device.

## Important APIs, Types, and Functions
`struct gpio_backlight` stores an optional controlled display device and the GPIO descriptor. `gpio_backlight_update_status()` sets the GPIO to the effective backlight brightness. `gpio_backlight_controls_device()` filters global blank notifications to the matching display device when platform data supplies one.

## Control Flow
Probe reads optional legacy platform data, checks the `default-on` property, obtains the unnamed GPIO, registers a raw max-brightness-1 backlight, determines initial power from firmware phandle/current GPIO state or legacy default, sets brightness to one, and drives the GPIO direction/output to the effective brightness. The driver binds to `gpio-backlight`.

## State and Persistence
No mutable driver state exists beyond the GPIO descriptor and optional display-device pointer. Hardware state is just the output level; there is no cached brightness field.

## Dependencies and Integration Points
It depends on GPIO descriptors, device properties, optional `gpio_backlight_platform_data`, Open Firmware match data, and `BL_CORE_SUSPENDRESUME`. It integrates with display blanking through `controls_device`.

## Risks
This is a binary device: all nonzero brightness values collapse to on. Initial power semantics differ between DT phandle-linked devices and non-DT/legacy devices. An active-low GPIO is handled by gpiolib, so board descriptions must encode polarity correctly.

## Test Signals
Test DT and platform-data probe, missing GPIO, active-low GPIOs, default-on behavior, reading existing GPIO state for phandle-linked DT nodes, display-specific blank filtering, and suspend/resume blanking.
