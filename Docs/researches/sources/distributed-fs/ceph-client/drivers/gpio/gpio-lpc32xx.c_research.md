<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc32xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc32xx.c

## Purpose
`gpio-lpc32xx.c` exposes the LPC32xx SoC's mixed GPIO/GPI/GPO banks as six separate gpiochips with legacy fixed numbering and bank-specific register mappings.

## Important APIs, types, and functions
`struct gpio_regs` describes per-bank register offsets. `struct lpc32xx_gpio_chip` combines gpiochip, register mapping, and MMIO base. Static gpiochip entries cover `gpio_p0`, `gpio_p1`, `gpio_p2`, `gpio_p3`, `gpi_p3`, and `gpo_p3`. Bank-specific helpers handle direction, level set, and input state mapping.

## Control flow
Probe maps the shared GPIO register resource, assigns the base to each static chip, installs OF xlate for three-cell GPIO specifiers, and registers all six chips. P0/P1/P2 use contiguous bit mappings; P3 GPIO uses non-contiguous input bits; GPI and GPO P3 are input-only and output-only banks.

## State and persistence behavior
All state is in SoC registers. The static `lpc32xx_gpiochip[]` array is process-wide driver state and each entry persists for module lifetime. No software output cache is kept except hardware outp_state readback for GPO.

## Dependencies and integration points
It binds to `nxp,lpc3220-gpio`, uses raw MMIO accessors, fixed gpio bases matching historical numbering, OF three-cell translation, and gpiolib.

## Risks and edge cases
The probe ignores return values from each `devm_gpiochip_add_data()` call, so partial registration failures are not propagated. Static chip objects mean only one controller instance is supported. Several `to_irq` callbacks return `-ENXIO`, explicitly documenting no IRQ mapping.

## Test signals
Test all six banks, fixed base numbering, P3 non-contiguous input mapping including GPIO5, OF xlate bank validation, input-only/output-only behavior, and failure injection around per-chip registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lpc32xx.c -->
