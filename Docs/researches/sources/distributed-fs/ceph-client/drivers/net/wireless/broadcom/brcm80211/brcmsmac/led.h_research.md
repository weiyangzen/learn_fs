# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/led.h

## Purpose
`led.h` declares the optional LED support interface for `brcmsmac`. It defines the per-device radio LED state and provides real or stubbed registration functions depending on `CONFIG_BRCMSMAC_LEDS`.

## Important APIs, Types, and Functions
- `struct gpio_desc` is forward-declared to avoid forcing GPIO headers into every includer.
- `struct brcms_led` stores a fixed LED name buffer and the owned GPIO descriptor.
- With `CONFIG_BRCMSMAC_LEDS`, `brcms_led_register()` and `brcms_led_unregister()` are implemented by `led.c`.
- Without LED support, unregister is a no-op and register returns `-ENOTSUPP`.

## Control Flow
The header has only compile-time conditional flow. It lets the mac80211 probe/remove code call LED registration and unregister unconditionally, while disabled LED builds compile those calls to harmless stubs.

## State and Persistence
`struct brcms_led` is embedded in `struct brcms_info` and persists only for the lifetime of that device object. It stores runtime LED name and GPIO descriptor state only.

## Dependencies and Integration Points
The header is included by `mac80211_if.h` and `led.c`. It integrates with Kconfig symbol `CONFIG_BRCMSMAC_LEDS` and depends on includers having a visible `struct brcms_info` declaration for the prototypes.

## Risks and Edge Cases
- The disabled stub returns `-ENOTSUPP`; callers must treat LED support as optional.
- The no-op unregister path gives callers no runtime indication that LED support is absent.
- The fixed 32-byte name buffer requires bounded string operations in implementation code.

## Test Signals
Compile with LED support enabled and disabled. Confirm probe/remove builds in both configurations, callers tolerate optional registration failure, and `struct brcms_led` name handling remains bounded.
