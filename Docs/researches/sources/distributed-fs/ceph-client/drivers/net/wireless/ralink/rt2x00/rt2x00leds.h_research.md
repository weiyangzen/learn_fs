# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00leds.h

## Purpose
Defines the small rt2x00 LED data model shared by LED implementation and chip-specific initializers.

## Important APIs, Types, And Functions
`enum led_type` identifies radio, association, activity, and quality LEDs. `struct rt2x00_led` contains the parent `rt2x00_dev`, embedded `led_classdev`, type, and flags. Flags are `LED_INITIALIZED` and `LED_REGISTERED`.

## Control Flow
Chip code initializes `struct rt2x00_led` fields and sets `LED_INITIALIZED`; `rt2x00leds_register()` registers initialized LEDs and sets `LED_REGISTERED`. Runtime helpers check type and registered flag before calling brightness callbacks.

## State And Persistence
The structures are embedded in `rt2x00_dev` and persist for the device lifetime. Registration flags track LED class ownership; brightness state lives inside the embedded class device.

## Dependencies And Integration Points
Depends on Linux LED class and `struct rt2x00_dev`. Used by `rt2x00.h` and `rt2x00leds.c`, with optional compilation through `CONFIG_RT2X00_LIB_LEDS`.

## Risks
Flags are plain integers, not atomic; LED registration should remain in lifecycle paths. A chip initializer must provide valid `brightness_set` callbacks before marking initialized.

## Test Signals
Compile with and without LED support, verify chip LED initialization, registration/unregistration flag transitions, and safe brightness changes during radio/link state changes.
