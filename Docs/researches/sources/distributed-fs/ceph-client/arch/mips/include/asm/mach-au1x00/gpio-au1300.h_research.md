# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1300.h

**Purpose:** Defines inline GPIO helpers for the Au1300 GPIC-backed GPIO controller.

**Important APIs/types/functions:** Exports `AU1300_GPIO_BASE`, `AU1300_GPIO_NUM`, `AU1300_GPIO_MAX`, `AU1300_GPIC_ADDR`, and inline helpers `au1300_gpio_get_value()`, `au1300_gpio_direction_input()`, `au1300_gpio_set_value()`, `au1300_gpio_direction_output()`, `au1300_gpio_to_irq()`, `au1300_irq_to_gpio()`, `au1300_gpio_is_valid()`, and `au1300_gpio_getinitlvl()`.

**Control flow:** Helpers compute the GPIC bank offset and bit mask from a GPIO number, then read or write GPIC pin-value, pin-clear, device-clear, and reset-value registers. IRQ mapping is direct from GPIO number to `AU1300_FIRST_INT`.

**State and persistence behavior:** No software state. Hardware state includes GPIC pin levels, device/GPIO ownership, and reset-captured initial levels for GPIO 0-63.

**Dependencies and integration points:** Depends on `au1000.h`, `addrspace.h`, `io.h`, GPIC macros, and `alchemy_get_cputype()`. Integrated with Au1300 gpiolib, interrupt controller, pinmux, and board setup.

**Risks:** `au1300_gpio_is_valid()` only accepts Au1300 CPU type; using helpers on older Alchemy chips is invalid. Range checking is minimal in value/direction helpers. GPIOs above 63 have no reset-level support. Hardware automatically switches output state on value writes.

**Test signals:** Boot Au1300, test all exposed GPIOs 0-74, verify GPIO-to-IRQ direct mapping, initial level readback for 0-63, device-to-GPIO ownership transition, and gpiolib integration.
