# sources/distributed-fs/ceph-client/arch/arm/plat-orion/gpio.c

Purpose: Implements Marvell Orion GPIO controller support, gpiolib operations, GPIO-specific LED blink control, and chained GPIO interrupt handling.

Important APIs/types/functions: `struct orion_gpio_chip` wraps `gpio_chip`, a spinlock, MMIO base, valid input/output bitmaps, mask offset, secondary IRQ base, and IRQ domain. Public functions are `orion_gpio_set_unused`, `orion_gpio_set_blink`, `orion_gpio_led_blink_set`, `orion_gpio_set_valid`, and `orion_gpio_init`. Gpiolib callbacks include request, direction input/output, get, set, and to_irq. IRQ support uses `gpio_irq_set_type`, `gpio_irq_handler`, custom mask/unmask helpers, and generic irq chips.

Control flow: `orion_gpio_init()` configures one of two static chips, registers it with gpiolib, clears/masks edge and level interrupts, installs up to four chained parent handlers, allocates a two-type generic irq chip for level and edge modes, and creates a legacy IRQ domain. GPIO operations read/write `GPIO_OUT`, `GPIO_IO_CONF`, `GPIO_BLINK_EN`, `GPIO_IN_POL`, `GPIO_DATA_IN`, `GPIO_EDGE_CAUSE`, `GPIO_EDGE_MASK`, and `GPIO_LEVEL_MASK`. IRQ handling ORs level and edge causes, toggles polarity for both-edge emulation, then dispatches mapped child IRQs.

State and persistence: Static `orion_gpio_chips[2]` and `orion_gpio_chip_count` persist. Valid input/output masks are changed by `orion_gpio_set_valid()` from MPP setup. Hardware direction/output/blink/polarity/mask registers are persistent SoC state. Spinlocks serialize GPIO direction/output/blink changes and irq generic-chip locks serialize mask writes.

Dependencies and integration: Depends on gpiolib, IRQ generic-chip/domain APIs, OF headers, LED GPIO blink states, and `plat/orion-gpio.h`. `mpp.c` calls `orion_gpio_set_valid()` to expose only MPP pins configured as GPIO-capable. Board code passes parent IRQs grouped by eight GPIO lines.

Risks: Both-edge interrupts are implemented by polarity flipping and explicitly documented as racy. `orion_gpio_set_blink()` uses `pin & 31` after finding the chip rather than subtracting `chip.base`; this is correct only for 32-wide chips aligned on 32-pin bases. `kstrdup()` and `gpiochip_add_data()` errors are not checked. Tests should exercise direction validity, LED blink default delays, GPIO-to-IRQ mapping, edge/level interrupt masking, both-edge stress, and two-chip configurations.
