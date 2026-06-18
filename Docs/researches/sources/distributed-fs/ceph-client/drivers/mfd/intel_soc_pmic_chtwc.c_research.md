# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtwc.c

Purpose: MFD core for Cherry Trail Whiskey Cove PMIC on I2C. It handles multi-address PMIC register access, model quirks via DMI, level1 regmap IRQs, and child device registration.

Important APIs/types/functions: `cht_wc_probe()`, `cht_wc_byte_reg_read()`, `cht_wc_byte_reg_write()`, `cht_wc_regmap_cfg`, `cht_wc_regmap_irq_chip`, DMI model table, and child cells for power source, external charger, region, and LEDs.

Control flow: probe checks ACPI `_HRV` equals `CHT_WC_HRV`, validates IRQ, allocates `intel_soc_pmic`, records model from DMI, initializes a custom 16-bit-address regmap that temporarily switches `client->addr`, registers a shared oneshot regmap IRQ chip, and adds child devices with the IRQ domain.

State and persistence: stores detected model in `pmic->cht_wc_model` for child behavior. Register access mutates the I2C client's address around each SMBus operation and restores it immediately.

Dependencies and integration: ACPI ID `INT34D3`, I2C SMBus byte access, regmap-irq, DMI board quirks, and shared PMIC child drivers.

Risks: changing `client->addr` requires serialized regmap access; callers must include high address bits or receive `-EINVAL`. `_HRV` separates Whiskey Cove variants sharing ACPI IDs. DMI matches affect device-specific behavior.

Test signals: `_HRV` rejection/acceptance, multi-address regmap reads/writes, interrupt mapping to children, DMI-specific model paths, LED/charger child probing, and suspend/resume IRQ handling.
