# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.h

## Purpose

`led.h` declares the optional LED integration API for `rtw88` and provides no-op stubs when LED support is disabled.

## Important APIs, Types, and Functions

With `CONFIG_RTW88_LEDS`, it declares `rtw_led_init()` and `rtw_led_deinit()`. Without that config, both functions are static inline empty functions so callers can invoke them unconditionally.

## Control Flow

There is no runtime flow in the header other than compile-time Kconfig selection between real functions and stubs.

## State and Persistence

No state is owned by the header. Real LED state is stored in `struct rtw_dev` fields used by `led.c`.

## Dependencies and Integration Points

The header is included by core initialization and teardown code that should not need to know whether LED support is compiled in. It depends on `struct rtw_dev` being declared by included driver headers.

## Risks

The main risk is build coverage: both LED-enabled and LED-disabled configurations need to compile. Callers should not assume LED side effects occur when the config is disabled or the chip lacks `led_set`.

## Test Signals

Compile tests should cover `CONFIG_RTW88_LEDS=y` and disabled builds. Runtime tests should verify init/deinit calls are harmless on chips without LEDs.
