<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio-pxa.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio-pxa.h

Purpose: Declares PXA platform GPIO helper macros and platform data for legacy PXA GPIO controllers.

Important APIs/types/functions: `GPIO_bit(x)` selects a bit within a 32-line bank. `gpio_to_bank(gpio)` maps a GPIO number to a bank. `pxa_last_gpio` exposes the last implemented GPIO number. `pxa_irq_to_gpio()` maps IRQs back to GPIOs. `pxa_gpio_platform_data` carries IRQ base and optional `gpio_set_wake()` callback.

Control flow: PXA GPIO drivers and platform setup code use macros for register bit/bank calculations and platform data to configure IRQ/wakeup behavior.

State and persistence behavior: `pxa_last_gpio` is global runtime/platform state; wake configuration persists in hardware/controller state.

Dependencies and integration points: Integrates with PXA board files, GPIO controller drivers, and IRQ wake management.

Risks: Some PXA SoCs have holes in GPIO numbering, so callers must not assume contiguous valid lines up to a fixed architectural maximum. IRQ-to-GPIO mappings are platform-specific.

Test signals: PXA GPIO driver build tests, bank/bit mapping tests around 31/32 boundaries, IRQ-to-GPIO mapping checks, wake callback tests, and platform data validation for SoC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio-pxa.h -->
