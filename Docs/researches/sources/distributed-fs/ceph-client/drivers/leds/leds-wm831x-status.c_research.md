# sources/distributed-fs/ceph-client/drivers/leds/leds-wm831x-status.c

Purpose: LED class driver for WM831x status LEDs. It controls status LED mode, blink timing, duty cycle, and source selection through WM831x control registers.

Important APIs, types, and functions: `struct wm831x_status` caches class device, WM831x pointer, locks, register address/value, blink parameters, source, and brightness. `wm831x_status_set()` rebuilds and writes the control register. `wm831x_status_brightness_set()` updates brightness and clears blink on off. `wm831x_status_blink_set()` maps supported on/off timings to hardware duration and duty fields. The `src` sysfs attribute reads/writes one of `otp`, `power`, `charger`, or `soft`.

Control flow: probe gets a register resource, merges optional platform data, initializes locks, reads the current hardware register, derives startup brightness and source, sets LED class callbacks/groups, and registers the LED. Brightness/blink/src updates mutate cached fields under spinlock or mutex and call `wm831x_status_set()`.

State and persistence: `reg_val` mirrors the control register and preserves unspecified bits across updates. Hardware startup state can be preserved for source when platform data requests it. Remove unregisters the LED but does not reset hardware.

Dependencies and integration points: WM831x MFD core/status definitions, platform resources/data, LED class, sysfs attribute groups, and platform device ids.

Risks and test signals: supported blink timing is narrow and ratio-based; test invalid timings, 62/63 ms handling, source sysfs parsing, platform-data preserve/default behavior, concurrent brightness/src writes, and register read/write failures.
