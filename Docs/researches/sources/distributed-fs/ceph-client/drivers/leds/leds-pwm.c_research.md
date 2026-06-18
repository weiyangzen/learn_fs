# sources/distributed-fs/ceph-client/drivers/leds/leds-pwm.c

Purpose: generic platform driver for device-tree/firmware described single-color PWM LEDs. It creates one LED class device per child node of a `pwm-leds` device and drives brightness by scaling a PWM duty cycle over the PWM period, optionally inverting it for `active-low`.

Important APIs, types, and functions: `struct led_pwm` holds firmware-derived static configuration; `struct led_pwm_data` stores the runtime `led_classdev`, `pwm_device`, cached `pwm_state`, optional enable GPIO, and polarity; `struct led_pwm_priv` is a flexible-array container for all LEDs. `led_pwm_set()` is the LED core callback and applies the PWM state. `led_pwm_add()` acquires the PWM via `devm_fwnode_pwm_get()`, handles default state, registers with `devm_led_classdev_register_ext()`, and optionally sets the starting PWM value. `led_pwm_create_fwnode()` parses child node properties, and `led_pwm_probe()` allocates the per-device array.

Control flow: probe counts children, allocates enough slots, parses each child, and registers each LED. Brightness writes flow from LED sysfs/triggers to `led_pwm_set()`, which computes `period * brightness / max_brightness`, applies active-low inversion, mirrors nonzero brightness to the enable GPIO, and calls `pwm_apply_might_sleep()`.

State and persistence: state is entirely in memory plus the PWM hardware. `LEDS_DEFSTATE_KEEP` reads the current PWM state and derives brightness from the existing duty cycle; otherwise the driver initializes a new PWM state. It deliberately keeps the PWM enabled during normal off states because disabled PWMs may not drive an inactive level; suspend is handled through `LED_CORE_SUSPENDRESUME`.

Dependencies and integration points: depends on LED class, PWM framework, firmware-node property APIs, optional GPIO descriptors, and the `pwm-leds` OF compatible. LED naming and default state are delegated to LED core init data.

Risks and test signals: validate child-node error handling, default-state keep with zero period fallback, active-low duty inversion, enable GPIO optionality, and suspend behavior where `LED_SUSPENDED` disables PWM output. Runtime tests should check sysfs brightness, trigger operation, DT bindings for `max-brightness`, `default-brightness`, `active-low`, and that off LEDs actually turn off on target hardware.
