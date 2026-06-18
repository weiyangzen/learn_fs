<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.c

## Purpose
`gpio-idio-16.c` is a reusable gpio-regmap and regmap-irq library for ACCES IDIO-16 family devices. It maps 16 fixed outputs and 16 isolated inputs into a 32-line gpiochip and wires input interrupts through regmap-irq.

## Important APIs, types, and functions
The exported API is `devm_idio_16_regmap_register()`. `struct idio_16_data` stores the regmap and last IRQ mask. `idio_16_handle_mask_sync()` toggles device-level IRQ enable when all child IRQs are masked or unmasked. `idio_16_reg_mask_xlate()` maps offsets to output or input register banks. `idio_16_names` defines stable line names.

## Control flow
Registration validates parent, map, and IRQ descriptors, disables device IRQs, installs a regmap IRQ chip, optionally deactivates input filters, configures gpio-regmap data/set bases and fixed output bitmap for GPIO 0-15, and registers the chip.

## State and persistence behavior
Line state is in device registers and regmap cache. The only software state is `irq_mask`, used to avoid redundant enable/disable transitions. Outputs are fixed-direction; inputs are fixed-direction and interrupt-capable.

## Dependencies and integration points
The helper exports namespace `GPIO_IDIO_16`, depends on regmap, regmap-irq, and gpio-regmap, and is intended for bus-specific IDIO-16 wrapper drivers.

## Risks and edge cases
The whole device IRQ is enabled only when transitioning away from all-masked and disabled when returning to all-masked; incorrect regmap-irq defaults can leave interrupts stuck. Devices without status registers use the `no_status` flag, shifting responsibility to regmap-irq semantics.

## Test signals
Wrapper tests should cover fixed output/input direction, interrupt masking transitions, filter deactivation, no-status variants, line names, and regmap register/mask translation for all 32 offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-idio-16.c -->
