
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-davinci.c

Purpose: implements TI DaVinci/Keystone GPIO with MMIO GPIO operations, direct or banked IRQ modes, runtime clock acquisition, and system suspend/resume context preservation.

Important APIs/types/functions: `struct davinci_gpio_controller` stores the gpiochip, IRQ domain, lock, register-bank pointers, direct IRQ count, parent IRQs, register contexts, and `BINTEN` context. Key functions are `davinci_gpio_probe()`, `__davinci_direction()`, `davinci_gpio_irq_setup()`, `gpio_irq_handler()`, `gpio_irq_type_unbanked()`, `davinci_gpio_save_context()`, and `davinci_gpio_restore_context()`.

Control flow: probe reads `ti,ngpio` and `ti,davinci-gpio-unbanked`, maps registers, collects parent IRQs, initializes callbacks, and registers the gpiochip before IRQ setup. Banked mode allocates a legacy IRQ domain and chains each 16-GPIO bank parent to `gpio_irq_handler()`. Unbanked mode reuses existing parent IRQ chips and changes only trigger programming. GPIO set uses dedicated set/clear registers; direction uses the `dir` bitmap where set means input.

State and persistence behavior: register state is protected by a spinlock for direction reads/writes. Suspend saves direction, set-data, rising/falling trigger, and `BINTEN`; resume restores changed values. The global `gpio_base` points at the mapped controller base and is used for `BINTEN`.

Dependencies and integration points: depends on platform properties, clk framework, gpiolib, irqdomain/chained IRQs, OF match data selecting DaVinci versus Keystone irq-chip copying, and postcore initcall ordering for board code.

Risks: maximum register-bank assumptions are fixed by `MAX_REGS_BANKS` and `offset_array`. Unbanked mode mutates copied parent irq-chip structures, which is sensitive to irqchip internals. The context save clears only the last bank's `intstat` after the loop, which is a possible maintenance hazard.

Test signals: DT property validation, banked and unbanked IRQ paths, rising/falling-only trigger rejection, direct IRQ type programming, GPIO suspend/resume restoration, and early-boot GPIO availability.
