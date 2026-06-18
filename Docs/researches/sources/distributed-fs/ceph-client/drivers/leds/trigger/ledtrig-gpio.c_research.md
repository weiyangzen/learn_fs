<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-gpio.c

Purpose: The GPIO trigger drives an LED from a GPIO input, typically described by the LED device's `trigger-sources` property.

Important APIs and state: `struct gpio_trig_data` stores the LED pointer, desired on brightness, and GPIO descriptor. Sysfs exposes `desired_brightness`. `gpio_trig_irq()` reads the GPIO value and sets LED brightness full/desired or off.

Control flow: Activation allocates state, obtains an optional GPIO named `trigger-sources` as input, names it `led-trigger`, requests a shared threaded IRQ on both rising and falling edges, and calls the IRQ handler once for initial state. Deactivation frees the IRQ, releases the GPIO, and frees state.

State and persistence: Per-LED trigger state lives until deactivation. Brightness follows the current GPIO level and requested brightness value; no state persists across trigger changes.

Dependencies and integration: It depends on GPIOLIB, LED trigger core, IRQ support, and firmware properties for trigger source mapping.

Risks and test signals: `gpiod_get_value_cansleep()` is used in a threaded IRQ, which is appropriate for sleeping GPIO providers. Missing GPIO returns `-EINVAL`. Test firmware property resolution, IRQ edge handling, desired brightness sysfs, and teardown while interrupts fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-gpio.c -->
