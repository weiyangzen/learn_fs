
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cs5535.c

Purpose: supports AMD CS5535/CS5536 GPIOs, exposing a gpiochip plus exported helper functions for hardware-specific GPIO event and register manipulation.

Important APIs/types/functions: `struct cs5535_gpio_chip` stores gpiochip, I/O base, platform device, and spinlock. Exported symbols include `cs5535_gpio_set()`, `cs5535_gpio_clear()`, `cs5535_gpio_isset()`, `cs5535_gpio_set_irq()`, and `cs5535_gpio_setup_event()`. Gpiolib callbacks are `chip_gpio_request()`, `chip_gpio_get()`, `chip_gpio_set()`, `chip_direction_input()`, and `chip_direction_output()`.

Control flow: probe requests the I/O resource, initializes a 32-line gpiochip with named pins, masks out reserved pins and the power button from the module `mask`, and registers the chip. GPIO request validates availability and clears auxiliary functions. Set/clear operations write lower-bank or high-bank registers, with `errata_outl()` applying the CS5536 high-bank read-modify-write workaround. Direction-output enables both input and output and sets output value.

State and persistence behavior: hardware registers hold all GPIO state. The global module `mask` is modified at probe to remove unsafe pins. A spinlock serializes exported and gpiochip register access. There is no PM callback; the erratum helper specifically accounts for post-suspend high-bank behavior.

Dependencies and integration points: depends on platform I/O resources, `include/linux/cs5535.h` register definitions, x86 MSR access for IRQ routing, and external drivers that may call the exported CS5535 helper symbols.

Risks: global state and exported helpers imply only one effective controller instance. The mask parameter is security/safety critical because some pins are reserved or power-management-related. Direct I/O port and MSR access make this architecture/platform specific.

Test signals: detection of reserved pin rejection, GPIO value/direction operations on low and high banks, errata path after suspend scenarios, exported event/IRQ helper behavior, and module parameter mask adjustment logging.
