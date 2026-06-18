# sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8008.c

## Purpose
`qcom-pm8008.c` is the Qualcomm PM8008 I2C MFD core. It claims the PMIC's two I2C addresses, provides primary and secondary regmaps, configures a per-peripheral regmap IRQ chip, and registers regulator, temperature alarm, and GPIO children.

## Important APIs, Types, And Functions
`pm8008_irqs[]` maps misc, temp-alarm, and GPIO interrupts. `pm8008_get_irq_reg()` converts logical regmap-irq offsets into peripheral-based addresses. `pm8008_set_type_config()` programs edge/level and polarity configuration buffers. `pm8008_irq_chip` defines main status, mask/unmask, ack, config, and register addressing. `pm8008_probe()` wires the full device.

## Control Flow
Probe creates a dummy client at `addr + 1`, initializes and attaches the secondary regmap, initializes the primary regmap last as the default, optionally drives reset GPIO low, waits briefly, creates a named IRQ-domain fwnode, registers the regmap IRQ chip on the physical IRQ, stores the IRQ domain for the GPIO child, and adds `pm8008-regulator`, `qpnp-temp-alarm`, and `pm8008-gpio` MFD children.

## State And Persistence
State is devm-managed: dummy I2C client, two regmaps, IRQ fwnode, regmap IRQ data, reset GPIO descriptor, and child devices. Hardware state includes interrupt mask, ack, and type/polarity registers. There is no persistent storage outside the PMIC registers.

## Dependencies And Integration Points
It depends on I2C, regmap, regmap-irq fwnodes, GPIO descriptors, MFD core, IRQ domains, OF compatible `qcom,pm8008`, and child drivers using the regmap and IRQ domain.

## Risks
The secondary regmap is initialized with `qcom_mfd_regmap_cfg` and then attached with `pm8008_regmap_cfg_2`; ordering is intentional because the default regmap must be attached last. IRQ register address calculation depends on `PM8008_NUM_PERIPHS` and the base table staying aligned. The reset GPIO is requested as `GPIOD_OUT_LOW`, so board polarity must match bindings.

## Test Signals
Probe with both I2C addresses present, regmap name visibility, interrupt type programming for temp/GPIO edge and level modes, temp alarm resource IRQ, GPIO child access to the stored IRQ domain, reset-GPIO boards, and cleanup of allocated fwnodes.
