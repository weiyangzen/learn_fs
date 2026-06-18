# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.c

## Purpose

`led.c` provides optional Linux LED class integration for `rtw88`. When a chip supplies a `led_set` operation and `CONFIG_RTW88_LEDS` is enabled, it registers a device LED named from the Realtek device and attaches mac80211's throughput trigger so LED blink rate tracks radio traffic.

## Important APIs, Types, and Functions

`rtw_led_init()` initializes `rtwdev->led_cdev`, assigns `brightness_set_blocking`, fills a stable LED name, creates a throughput LED trigger with `ieee80211_create_tpt_led_trigger()`, and registers the LED class device. `rtw_led_deinit()` turns the LED off through the chip operation and unregisters it if registration succeeded. The internal `rtw_led_set()` callback maps LED brightness changes to `rtwdev->chip->ops->led_set()` under `rtwdev->mutex`.

## Control Flow

Initialization exits early when the chip has no LED operation. Otherwise it builds a static throughput-to-blink-time table, configures the LED classdev, registers it, and records `rtwdev->led_registered` only on success. Runtime brightness changes are serialized by the device mutex. Deinit checks `led_registered`, forces `LED_OFF`, then unregisters.

## State and Persistence

LED state lives in `rtwdev->led_cdev`, `rtwdev->led_name`, and `rtwdev->led_registered`. Hardware LED state persists until changed by the chip `led_set` operation; deinit explicitly turns it off.

## Dependencies and Integration Points

This file depends on Linux LED classdev support, mac80211 throughput LED triggers, the chip-specific `led_set` callback, and driver logging. It integrates with device initialization and teardown through the prototypes in `led.h`.

## Risks

The chip `led_set` callback is called with the driver mutex held; chip implementations must not take locks in an order that deadlocks with other driver paths. `rtw_led_deinit()` calls `chip->ops->led_set()` without checking the callback again, relying on `led_registered` only being true when the callback existed at init. Registration failures leave LED integration disabled but should not block device operation.

## Test Signals

Tests should cover chips with and without `led_set`, LED class registration failure handling, throughput-trigger name creation, brightness changes under traffic, suspend/remove deinit turning the LED off, and lockdep behavior in chip LED callbacks.
