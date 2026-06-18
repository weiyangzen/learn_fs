# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/leds.h

## Purpose
Declares b43legacy LED support data structures, SPROM behavior constants, behavior enum, lifecycle APIs, and disabled-build stubs.

## Important APIs, Types, and Functions
When LED support is enabled, `struct b43legacy_led` contains a device pointer, `struct led_classdev`, GPIO index, active-low flag, and name buffer. `B43legacy_LED_BEHAVIOUR` and `B43legacy_LED_ACTIVELOW` decode SPROM values. `enum b43legacy_led_behaviour` covers off/on/activity/radio/mode/transfer/weird/assoc/inactive behaviors. The public APIs are `b43legacy_leds_init` and `b43legacy_leds_exit`.

## Control Flow
Enabled builds expose real initialization and teardown implemented in `leds.c`. Disabled builds define an empty `struct b43legacy_led` and inline no-op lifecycle functions, allowing `struct b43legacy_wldev` to include LED fields unconditionally.

## State and Persistence
Enabled state is per-device LED class registration state and GPIO metadata. Disabled builds carry no LED state. Hardware GPIO persistence is controlled by the implementation, not the header.

## Dependencies and Integration Points
Depends on Linux LED class APIs when `CONFIG_B43LEGACY_LEDS` is set. It integrates with `b43legacy.h` device state and `main.c` core init/exit lifecycle, where LEDs are initialized after core init and removed during core exit.

## Risks
The name length constant must fit generated names using wiphy names. Behavior enum values reflect hardware/SPROM encodings, so reordering is not safe. Disabled stubs must stay source-compatible with enabled APIs.

## Test Signals
Build LED-enabled and disabled configurations, verify generated LED names fit, and inspect sysfs trigger registration on hardware with SPROM LED descriptors and fallback `0xFF` descriptors.
