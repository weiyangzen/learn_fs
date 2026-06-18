# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_crc.c

Purpose: Crystal Cove PMIC I2C MFD driver for Bay Trail and Cherry Trail Intel SoCs. It chooses platform-specific child sets, registers a regmap IRQ domain, and adds a PWM lookup for backlight use by Intel graphics.

Important APIs/types/functions: `crystal_cove_i2c_probe()`, `crystal_cove_i2c_remove()`, `crystal_cove_irq_chip`, BYT/CHT `crystal_cove_config` records, `crc_pwm_lookup`, and child cell arrays for power, thermal, BCU, ADC, charger, GPIO, PMIC region, and PWM.

Control flow: probe selects BYT or CHT config using `soc_intel_is_byt()`, creates I2C regmap, registers regmap IRQ chip, enables IRQ wake, adds the PWM lookup table, updates IRQ-domain bus token, then registers configured MFD children. Remove deletes PWM lookup and children.

State and persistence: per-device state stores regmap and IRQ chip data. Wake-enable state is requested for the parent IRQ. PWM lookup is global while the device is bound.

Dependencies and integration: ACPI `INT33FD`, I2C ID `intel_soc_pmic_crc`, platform-data SoC detection, PWM lookup table, regmap-irq, and child PMIC/GPIO/PWM drivers.

Risks: global PWM lookup must be removed on failure/remove. BYT and CHT expose different child sets. IRQ wake enabling may fail non-fatally. Domain token update avoids conflicts with child domains.

Test signals: BYT versus CHT child enumeration, IRQ wake warning path, PWM backlight lookup by graphics, GPIO/charger IRQ domain behavior, and bind/unbind cleanup.
