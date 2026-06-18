# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_gpio.h

**Purpose:** Declares BCM63xx GPIO initialization and per-CPU GPIO line counts.

**Important APIs/types/functions:** Exports `bcm63xx_gpio_init()`, inline `bcm63xx_gpio_count()`, and direction constants `BCM63XX_GPIO_DIR_OUT`/`BCM63XX_GPIO_DIR_IN`. GPIO count returns 32 for BCM6328, 40 for BCM3368, 8 for BCM6338, 16 for BCM6345, 38 for BCM6358/6368, 48 for BCM6362, and 37 for BCM6348/default.

**Control flow:** GPIO init registers the controller, and consumers use the count helper to size chips or validate GPIO numbers based on current CPU ID.

**State and persistence behavior:** No local state. Runtime state is in GPIO controller registers and gpiolib objects created by the implementation.

**Dependencies and integration points:** Depends on `bcm63xx_cpu.h` CPU detection. Integrated by board LEDs/buttons, PCI/PCMCIA ready lines, USB, Ethernet PHY reset, and gpiolib.

**Risks:** GPIO count defaults to 37 for unknown/default path, so CPU detection errors can expose invalid lines. Direction constants are hardware convention-specific and may be confused with gpiolib logical direction values.

**Test signals:** Boot every SoC family, verify registered GPIO count, exercise boundary GPIOs, direction/value operations, interrupt-capable lines, and board LEDs/buttons.
