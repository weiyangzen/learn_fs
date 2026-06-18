# sources/distributed-fs/ceph-client/arch/m68k/coldfire/gpio.c

Purpose: generic ColdFire GPIO support, providing both legacy exported helpers and an optional gpiolib `gpio_chip`.

Important APIs and functions: exported `__mcfgpio_get_value()`, `__mcfgpio_set_value()`, `__mcfgpio_direction_input()`, `__mcfgpio_direction_output()`, `__mcfgpio_request()`, and `__mcfgpio_free()`. With `CONFIG_GPIOLIB`, wrappers populate `mcfgpio_chip` with direction, get/set, request/free, and `to_irq` callbacks, registered by `core_initcall(mcfgpio_sysinit)`.

Control flow and state: get reads the pin data register. Set and direction operations update MMIO registers under `local_irq_save()` for read-modify-write ports. GPIOs at or after `MCFGPIO_SCR_START` use set/clear registers instead of output data RMW. Request is a no-op; free returns the line to input. State is hardware direction/output latch state only.

Dependencies and integration: `asm/mcfgpio.h` supplies port address/bit mapping macros; Linux gpiolib consumers can request GPIOs and map selected pins to IRQs via `MCFGPIO_IRQ_VECBASE`. Board and SoC pinmux files must place pads in GPIO mode.

Risks and test signals: no ownership enforcement in `__mcfgpio_request()` means conflicts are possible. RMW locking only blocks local interrupts, not external bus masters. `to_irq` depends on compile-time min/max definitions. Test with gpiolib line toggles, input reads, set/clear register GPIOs, IRQ mapping boundaries, and concurrent users on the same port.
