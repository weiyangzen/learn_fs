# sources/distributed-fs/ceph-client/drivers/leds/leds-adp5520.c

## Purpose
Provides LED support for Analog Devices ADP5520/ADP5501 MFD PMICs using platform data. It registers up to three LED class devices and programs current, enable, timing, and fade registers through the parent MFD API.

## Important APIs, Types, And Functions
`struct adp5520_led` embeds a classdev and stores the parent device, LED ID, and flags. Important functions are `adp5520_led_set`, `adp5520_led_setup`, `adp5520_led_prepare`, `adp5520_led_probe`, and `adp5520_led_remove`.

## Control Flow
Probe requires `adp5520_leds_platform_data`, validates LED count, allocates an array of private LEDs, clears LED currents, initializes timing/fade registers, then loops through `struct led_info` entries. Each LED inherits name/default trigger, sets a blocking brightness callback, derives flags/ID, registers the classdev, and enables the corresponding LED output/control bits.

Brightness writes the appropriate current register with `value >> 2`, converting LED-class brightness to the PMIC's coarser current scale. Remove clears all LED enable bits and unregisters classdevs.

## State And Persistence
State is mostly platform-data-derived and static after probe. Hardware state persists in PMIC LED current/time/fade/control registers. No lock is used in the LED callback, relying on parent MFD serialization or simple register writes.

## Dependencies And Integration Points
Depends on the ADP5520 MFD API, platform data, LED class, and platform driver binding `adp5520-led`. It does not parse device tree in this file.

## Risks
The driver ORs multiple setup writes into one `ret`, which can obscure the first failing operation. Platform data must provide valid LED counts, flags, names, and timing fields. Brightness resolution is reduced by shifting right two bits.

## Test Signals
Test platform-data registration for one to three LEDs, verify enable bits per ID, confirm current writes scale brightness correctly, validate fade/on/off timing programming, and ensure remove disables all LED outputs.
