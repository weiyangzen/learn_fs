# sources/distributed-fs/ceph-client/drivers/gpio/gpio-104-idi-48.c

## Purpose
This ISA driver supports ACCES 104-IDI-48 input boards. It exposes 48 input-only GPIO lines through `gpio-regmap` and maps the board interrupt/status register into per-line IRQs.

## Important APIs, types, and functions
The module parameters `base[]` and `irq[]` define ISA instances. `idi_48_reg_mask_xlate()` maps logical GPIO offsets to sparse hardware port registers. `idi48_regmap_config` defines an 8-bit I/O-port regmap with read-only data ranges and precious IRQ status. `idi48_regmap_irqs[]` maps all 48 lines to six status bits by byte group. Probe uses `devm_regmap_add_irq_chip()` and `devm_gpio_regmap_register()`.

## Control flow
Probe reserves an 8-port ISA range, maps it, initializes regmap access, allocates a regmap IRQ chip with status/unmask at register `0x7`, registers the shared IRQ, then creates a `gpio_regmap_config` with `reg_dat_base = 0`, 8 GPIOs per register, custom mask translation, line names, and the regmap IRQ domain.

## State and persistence behavior
The driver keeps no private mutable state beyond devres-managed objects. GPIO values and interrupt status are read from hardware. The regmap is raw-spinlocked and treats the IRQ status register as precious to avoid accidental destructive reads.

## Dependencies and integration points
It depends on ISA, I/O port resources, regmap, regmap-irq, and `gpio-regmap`. It integrates with gpiolib as a sleeping-safe regmap GPIO provider and with the IRQ subsystem through a regmap IRQ domain.

## Risks and edge cases
The hardware is input-only, so write access is explicitly denied for data registers. The IRQ model groups lines behind byte-level status bits; wrong mask translation would report the wrong line or miss an edge. `IRQF_SHARED` is used, so shared interrupt behavior should be considered during board bring-up.

## Test signals
Expected signals are a 48-line GPIO chip with names for groups A and B, correct reads across the sparse register layout, no output direction support, and edge-both IRQ delivery for all lines when the configured ISA IRQ is asserted.
