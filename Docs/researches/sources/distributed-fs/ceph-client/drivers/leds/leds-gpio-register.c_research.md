# sources/distributed-fs/ceph-client/drivers/leds/leds-gpio-register.c

Purpose: early-init helper for board files to register a `"leds-gpio"` platform device while keeping original platform data in init memory.

Important APIs/types/functions: `gpio_led_register_device()` copies `struct gpio_led_platform_data`, duplicates its `leds` array with `kmemdup()`, and calls `platform_device_register_resndata()` using the copied platform data.

Control flow: the helper rejects zero LEDs, duplicates the LED descriptors, registers a new platform device named `"leds-gpio"` with caller-provided id, and frees the duplicated LED array if device registration fails. On success, ownership is transferred to platform-device resources.

State and persistence: no module-level state. The created platform device persists until platform-device teardown. The copied platform data avoids references to discarded `__init` memory.

Dependencies/integration: integrates legacy board code with the generic GPIO LED driver in `leds-gpio.c`. Uses platform-device resource-data registration and GPIO LED platform-data definitions.

Risks: only the `leds` array is deep-copied; any strings or nested pointers inside LED descriptors must remain valid. Invalid `num_leds` returns `-EINVAL`. This is an `__init` helper, so it is for boot-time board setup rather than hotplug.

Test signals: call from board init with valid/empty data, confirm platform device binds to `leds-gpio`, verify copied array survives after init memory discard, and test registration failure cleanup.
