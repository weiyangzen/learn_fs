# sources/distributed-fs/ceph-client/drivers/leds/leds-bd2802.c

## Purpose
Implements the ROHM BD2802GU RGB LED controller. It exposes six legacy LED class devices, one for each RGB component of two LEDs, plus driver-specific sysfs attributes for waveform/current and an advanced direct-register configuration mode.

## Important APIs, Types, And Functions
`struct bd2802_led` stores platform data, client, reset GPIO, rwsem, software state for two RGB LEDs, six classdevs, advanced-configuration flag, selected LED/color/state, wave pattern, and RGB current. Macros generate per-color brightness/blink callbacks and direct register sysfs stores. Key helpers include `bd2802_set_on`, `bd2802_set_blink`, `bd2802_turn_off`, `bd2802_enable_adv_conf`, `bd2802_register_led_classdev`, suspend/resume helpers, and probe/remove.

## Control Flow
Probe allocates state, requests reset GPIO, detects the chip by writing clock setup, resets the chip to save power, initializes defaults, creates device attributes, and registers all six classdevs. Brightness callbacks map nonzero to steady-on and zero to off. Blink callbacks reject zero on/off delays and set hardware blink using the current `wave_pattern`.

When the first channel turns on, reset is deasserted and common timing is configured. Turning off a component clears current registers, updates cached RGB state, and if all outputs are off and advanced mode is disabled, asserts reset. Advanced mode dynamically exposes raw register sysfs files and keeps the chip out of reset.

## State And Persistence
Software tracks two-bit state for each color of each LED, default wave/current settings, and whether advanced mode owns direct register access. Suspend asserts reset; resume reinitializes and restores cached LED states or advanced mode.

## Dependencies And Integration Points
Depends on I2C SMBus, reset GPIO, platform data `leds-bd2802.h`, LED class, PM sleep, and custom device sysfs attributes. It does not use modern fwnode LED naming.

## Risks
The driver has a broad custom sysfs ABI and direct register access that can conflict with LED class operations. Many hardware writes ignore errors after logging through `bd2802_write_byte`. Six separate classdev fields avoid `container_of` arrays but create repetitive error paths. Advanced mode changes reset behavior and persistence assumptions.

## Test Signals
Test registration/unregistration of all six LEDs, steady and blink modes, reset assertion when all LEDs off, advanced configuration on/off and raw register files, wave/current attributes, suspend/resume state restoration, and cleanup if classdev registration fails mid-sequence.
