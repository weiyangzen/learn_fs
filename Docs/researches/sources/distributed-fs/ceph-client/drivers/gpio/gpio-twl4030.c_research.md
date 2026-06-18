<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl4030.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl4030.c

Purpose: implements GPIO and optional LED-as-GPIO support for TWL4030/TPS659x0 MFD chips, including pull/debounce configuration, module power gating by usage, GPIO IRQ setup, and an OMAP3 WLAN power quirk.

Important APIs, types, and functions: `struct gpio_twl4030_priv` stores gpiochip, mutex, IRQ base, usage bitmask, direction cache, and output-state cache. GPIO callbacks are request, free, direction_input, direction_output, get_direction, get, set, and `to_irq()`. Helpers program TWL GPIO registers, LED PWM/output registers, pullups/pulldowns, debounce, and OF platform data.

Control flow: probe allocates state, creates legacy IRQ descriptors and a simple domain when built-in, calls `twl4030_sih_setup()`, parses OF properties, configures pulls and debounce, optionally adds two LED output GPIOs, registers the chip, and applies a Compulab OMAP3 WLAN power hog/export quirk. Request powers the GPIO module on for first GPIO use and initializes LED outputs when requested. Free powers the module off after last GPIO use.

State and persistence behavior: driver caches usage, direction, output state, and LEDEN. Hardware registers hold actual values, pulls, debounce, and module power. No suspend/resume is in this file.

Dependencies and integration points: depends on TWL MFD I2C helpers, SIH IRQ setup, OF properties `ti,use-leds`, `ti,debounce`, `ti,mmc-cd`, `ti,pullups`, `ti,pulldowns`, and gpiolib descriptors.

Risks and test signals: IRQ dispatch is refused for loadable module builds because genirq setup needs built-in availability. `twl_get()` rejects unrequested lines. LED GPIOs invert drive semantics through open-drain LED registers. Test module power usage counts, OF pull/debounce programming, LED request/free, IRQ mapping, OMAP3 quirk cleanup, and I2C failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-twl4030.c -->
