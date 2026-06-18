<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps6586x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps6586x.c

Purpose: exposes four TPS6586x PMIC GPIO-like outputs and maps them to parent PMIC interrupt virtual IRQs.

Important APIs, types, and functions: `struct tps6586x_gpio` stores the gpiochip and parent device. GPIO callbacks are get, set, direction_output, and `to_irq()`. Register helpers are parent MFD functions `tps6586x_read()`, `tps6586x_update()`, and `tps6586x_irq_get_virq()`.

Control flow: subsys init registers the platform driver. Probe inherits the parent's firmware node, reads optional platform data for static GPIO base, configures a four-line sleeping gpiochip, and registers it. Direction_output first sets the output value in `TPS6586X_GPIOSET2`, then programs function/direction bits in `TPS6586X_GPIOSET1`.

State and persistence behavior: no driver cache. PMIC registers store output values and mode. Input direction is not implemented; a FIXME notes missing dedicated-input handling.

Dependencies and integration points: depends on TPS6586x MFD services, parent IRQ mapping, platform data or dynamic GPIO base, and gpiolib.

Risks and test signals: missing input support limits use cases. `to_irq()` assumes a direct offset from `TPS6586X_INT_PLDO_0`. Test output programming, readback, platform-data base selection, firmware-node inheritance, IRQ mapping for all four lines, and behavior if parent MFD operations fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps6586x.c -->
