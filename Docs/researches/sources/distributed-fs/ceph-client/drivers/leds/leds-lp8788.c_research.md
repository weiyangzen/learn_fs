# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8788.c

Purpose: keyboard backlight LED driver for the TI LP8788 MFD current-sink block.

Important APIs/types/functions: `struct lp8788_led` stores parent MFD pointer, mutex, LED class device, selected ISINK, and on/off state. `lp8788_led_init_device()` configures ISINK scale and current code; `lp8788_brightness_set()` writes PWM and toggles sink enable; `lp8788_led_probe()` registers one LED class device.

Control flow: the platform child gets the parent `struct lp8788`, selects platform data or defaults, initializes ISINK registers, then registers `keyboard-backlight` or the platform-provided name. Brightness writes update PWM for ISINK 1-3 and only change enable state when zero/nonzero state changes.

State and persistence: `led->on` caches enable state to avoid redundant writes. Brightness/current values are stored in parent hardware registers and are not persisted by this driver across MFD reset.

Dependencies and integration: depends on LP8788 MFD helpers, `lp8788-isink` register tables, platform data, LED class, and mutex serialization.

Risks: only ISINK 1-3 are accepted in brightness path; bad platform data returns `-EINVAL`. The default config mutates a static object when platform data is present, which is safe only because devices are expected to be singular or identical. No OF parsing is present in this file.

Test signals: platform probe under LP8788 MFD, PWM writes at min/max brightness, enable transition at zero/nonzero, platform current/scale overrides, and invalid ISINK configuration.
