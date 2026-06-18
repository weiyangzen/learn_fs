<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-timberdale.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-timberdale.c

Purpose: supports the Timberdale FPGA GPIO block as a built-in platform driver with legacy platform-data GPIO numbering and optional chained interrupt support.

Important APIs, types, and functions: `struct timbgpio` stores MMIO base, spinlock, gpiochip, legacy IRQ base, and cached interrupt enable register. GPIO callbacks are input/output direction, get, set, and `to_irq()`. IRQ callbacks are enable/disable, set_type, and chained `timbgpio_irq()`.

Control flow: probe requires platform data with `nr_pins <= 32`, maps MMIO, sets gpiochip callbacks and legacy base, registers the gpiochip, disables interrupts, and, if a parent IRQ plus positive IRQ base exist, manually installs per-line IRQ chips and a chained parent handler. The chained handler acknowledges the parent, reads and clears pending bits, temporarily disables IER to avoid hardware corruption with simultaneous IRQs, dispatches each mapped IRQ, and restores the cached enable mask.

State and persistence behavior: direction/value/IRQ mode live in FPGA registers. `last_ier` mirrors enabled IRQ lines to repair IER after the hardware erratum path. No dynamic IRQ domain or PM save exists.

Dependencies and integration points: depends on legacy `timb_gpio_platform_data`, raw I/O access, static IRQ descriptors, and built-in platform registration.

Risks and test signals: manual legacy IRQ setup is fragile compared with modern irqdomains. Direction-output ignores the requested initial value and only changes direction. Both-edge IRQs require hardware version greater than 2. Test platform-data validation, no-IRQ mode, version-dependent both-edge setup, IER erratum workaround, IRQ base mapping, and value behavior when switching to output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-timberdale.c -->
