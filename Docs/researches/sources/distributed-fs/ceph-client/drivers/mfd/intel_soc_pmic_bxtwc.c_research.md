# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_bxtwc.c

Purpose: MFD core for Broxton Whiskey Cove PMIC accessed through Intel SCU IPC. It provides an IPC-backed regmap, multi-level regmap IRQ domains, sysfs register access, and PMIC child devices.

Important APIs/types/functions: `bxtwc_probe()`, `regmap_ipc_byte_reg_read()`, `regmap_ipc_byte_reg_write()`, `bxtwc_add_chained_irq_chip()`, `bxtwc_add_chained_devices()`, regmap IRQ chips for level1, power button, TMU, BCU, ADC, charger, and critical events.

Control flow: probe validates ACPI `_HRV`, obtains IRQ and SCU IPC handle, initializes custom regmap, registers the level1 IRQ chip, chains secondary chips off virtual level1 IRQs, adds child MFD devices with the relevant IRQ domains, and applies the charger level1 unmask workaround.

State and persistence: `struct intel_soc_pmic` holds regmap, IRQ chip data, and SCU handle. Global sysfs `addr` chooses the PMIC register for privileged `val` reads/writes. Suspend/shutdown disable the parent IRQ.

Dependencies and integration: depends on ACPI `INT34D3`, SCU IPC PMIC access command, regmap IRQ, MFD children for thermal/GPIO/region/TMU/BCU/GPADC/USBC/charger, and `intel_soc_pmic` shared data.

Risks: nested IRQ domain setup must use the right parent vIRQ and domain. The global debug register address is shared across devices. IPC register addressing encodes I2C address in high bits and defaults to device1 when absent.

Test signals: `_HRV` filtering, interrupt delivery through each chained domain, charger IRQ unmask workaround, sysfs admin register access, suspend/resume IRQ disable/enable, and child driver probing.
