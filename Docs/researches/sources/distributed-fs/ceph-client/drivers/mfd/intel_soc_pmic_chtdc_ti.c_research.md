# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtdc_ti.c

Purpose: I2C MFD driver for Cherry Trail Dollar Cove TI PMIC. It creates a byte regmap, maps level1 PMIC interrupts through regmap-irq, and registers functional child devices.

Important APIs/types/functions: `chtdc_ti_probe()`, `chtdc_ti_shutdown()`, simple suspend/resume PM ops, `chtdc_ti_regmap_config`, `chtdc_ti_irq_chip`, and child cells for power button, ADC, thermal, power source, battery, and region.

Control flow: probe allocates `intel_soc_pmic`, initializes an I2C regmap with single-register reads, stores the IRQ, registers the regmap IRQ chip with `IRQF_ONESHOT`, and adds MFD children using the IRQ domain produced by regmap-irq. Shutdown and suspend disable the PMIC IRQ; resume re-enables it.

State and persistence: per-device state is limited to regmap, IRQ, and irq-chip data. Hardware interrupt mask/status registers hold volatile PMIC state.

Dependencies and integration: matches ACPI `INT33F5`; depends on I2C, regmap, regmap-irq, MFD core, and child drivers named `chtdc_ti_*`.

Risks: hardware cannot read multiple registers, so regmap configuration must keep single reads. Missing or bad IRQ prevents child interrupt routing. Level1 bit definitions drive child resource numbering.

Test signals: ACPI/I2C binding, regmap single-read behavior, child IRQ delivery, battery/power-source events, suspend/resume IRQ behavior, and MFD child enumeration.
