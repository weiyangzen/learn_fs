# sources/distributed-fs/ceph-client/drivers/gpio/gpio-adnp.c

## Purpose
This I2C driver supports Avionic Design N-bit GPIO expanders. It exposes configurable GPIO lines over SMBus byte registers and can emulate nested GPIO IRQs using the expander's interrupt status, enable, and sampled level registers.

## Important APIs, types, and functions
`struct adnp` stores the I2C client, GPIO chip, register shift, I2C and IRQ locks, and six per-register IRQ state arrays. GPIO operations include `adnp_gpio_get()`, `adnp_gpio_set()`, `adnp_gpio_direction_input()`, `adnp_gpio_direction_output()`, and optional `adnp_gpio_dbg_show()`. IRQ support is implemented by `adnp_irq()`, `adnp_irq_mask()`, `adnp_irq_unmask()`, `adnp_irq_set_type()`, bus-lock callbacks, and `adnp_irq_setup()`.

## Control flow
Probe reads `nr-gpios`, allocates state, initializes the I2C lock, computes register layout from GPIO count, fills the GPIO chip, optionally initializes IRQ state when `interrupt-controller` is present, and registers the GPIO chip. GPIO direction and value operations perform locked SMBus reads and writes. The threaded IRQ reads level/status/enable registers, computes edge and level pending bits from cached trigger configuration, and invokes nested child IRQs.

## State and persistence behavior
Direction, level, IRQ enable, and status live on the expander. Runtime IRQ policy is mirrored in `irq_enable`, `irq_level`, `irq_rise`, `irq_fall`, `irq_high`, and `irq_low`; these arrays are synchronized to hardware during IRQ bus unlock. No nonvolatile state is written.

## Dependencies and integration points
The driver depends on I2C SMBus byte access, gpiolib, threaded IRQs, firmware properties, debugfs sequence output, and nested IRQ handling. It integrates as an I2C driver with ID `gpio-adnp` and OF compatible `ad,gpio-adnp`.

## Risks and edge cases
I2C failures are propagated and can make GPIO reads or IRQ processing incomplete. Edge detection depends on the initial and later cached levels, but the handler as written computes `changed` against `irq_level` without updating it in the loop, so maintainers should verify whether repeated edges are expected to refresh cached state elsewhere. Direction changes read back DDR bits and return `-EPERM` if hardware refuses the change.

## Test signals
Test GPIO direction/value over I2C, debugfs register display, invalid `nr-gpios`, interrupt-controller setup with edge and level trigger types, nested IRQ delivery, and IER writes after mask/unmask bus synchronization.
