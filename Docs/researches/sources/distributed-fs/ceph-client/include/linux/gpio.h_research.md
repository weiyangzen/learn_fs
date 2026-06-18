<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio.h

Purpose: Legacy bulk GPIO include that exposes old global-number GPIO APIs while warning new code to use driver or consumer-specific headers.

Important APIs/types/functions: Legacy flags include `GPIOF_IN`, `GPIOF_OUT_INIT_LOW`, and `GPIOF_OUT_INIT_HIGH`. With legacy gpiolib, APIs include `gpio_is_valid()`, `gpio_request()`, `gpio_free()`, direction setters, value get/set raw wrappers, cansleep variants, `gpio_to_irq()`, `gpio_request_one()`, and `devm_gpio_request_one()`. When gpiolib is enabled, most operations bridge through descriptor APIs such as `gpio_to_desc()` and `gpiod_*`. Disabled stubs return `-ENOSYS`/`-EINVAL`, warn, or no-op.

Control flow: Legacy consumers request a global GPIO number, set direction, read/write values, optionally map to IRQ, then free. The header adapts these calls to descriptor-based gpiolib when available.

State and persistence behavior: No state in the header; requested GPIO state lives in gpiolib and hardware. Global numbering is a legacy namespace.

Dependencies and integration points: Depends on `linux/gpio/consumer.h` when `CONFIG_GPIOLIB` is set, and on legacy gpiolib config. Bridges old drivers/platform data to modern descriptor infrastructure.

Risks: New code should avoid this header. Global GPIO numbers are ambiguous and platform-dependent. Disabled stubs may warn if code calls GPIO operations without gpiolib. Raw value APIs bypass active-low semantics.

Test signals: Legacy driver builds, request/direction/value/IRQ tests through descriptor backend, disabled gpiolib build warnings, and migration tests comparing legacy and descriptor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio.h -->
