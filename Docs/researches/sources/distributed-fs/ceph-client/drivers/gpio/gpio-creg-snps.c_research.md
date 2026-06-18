
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-creg-snps.c

Purpose: exposes selected Synopsys CREG control-register bitfields as output-only GPIOs, mainly chip-select control lines on ARC boards.

Important APIs/types/functions: `struct creg_layout` describes per-GPIO shift, on/off values, and bit width; `struct creg_gpio` stores the gpiochip, MMIO register, spinlock, and layout. Key functions are `creg_gpio_set()`, `creg_gpio_dir_out()`, `creg_gpio_validate_pg()`, `creg_gpio_validate()`, and `creg_gpio_probe()`.

Control flow: probe maps one register, selects a layout from OF match data, reads `ngpios`, validates that all bitfield definitions fit in a 32-bit register and have distinct on/off values, initializes the spinlock, and registers a dynamic-base gpiochip with only set and direction-output callbacks. `creg_gpio_set()` computes cumulative bit shifts for the target field, masks that field, writes either layout `on` or `off`, and updates the register under lock.

State and persistence behavior: the only software state is layout and spinlock; output state persists in the shared CREG register. There is no input, IRQ, or PM context. Because all GPIOs share one register, every set is a read-modify-write.

Dependencies and integration points: depends on OF match data for `snps,creg-gpio-axs10x` and `snps,creg-gpio-hsdk`, MMIO, platform bus, and gpiolib. It is built in via `builtin_platform_driver()`.

Risks: `creg_gpio_set()` uses `layout->bit_per_gpio[i]` after a loop where `i == offset`; this relies on offset being in range and is correct only if gpiolib enforces bounds. Shared-register RMW races with non-driver writers are not prevented. It cannot report input state or high-impedance.

Test signals: probe validation failures for impossible layouts, correct register field packing for HSDK and AXS10x layouts, output-only GPIO behavior, and concurrent set operations preserving neighboring fields.
