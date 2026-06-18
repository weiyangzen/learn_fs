# sources/distributed-fs/ceph-client/drivers/mfd/mt6360-core.c

Purpose: I2C MFD driver for the MediaTek/Richtek MT6360 PMU. It presents four I2C slave address spaces as one 16-bit regmap, handles PMIC/LDO CRC framing, validates vendor info, registers a regmap IRQ chip, and creates ADC, charger, LED, regulator, and TCPC child devices.

Important APIs, types, and functions: `struct mt6360_ddata` stores four I2C clients, regmap, IRQ data, chip revision, and CRC table. `mt6360_irqs[]` and `mt6360_irq_chip` describe 16 IRQ registers. `mt6360_xlate_pmicldo_addr()` encodes PMIC/LDO address size fields. `mt6360_regmap_read()` and `mt6360_regmap_write()` implement custom banked regmap access with CRC for PMIC and LDO banks. `mt6360_check_vendor_info()` validates vendor nibble. `mt6360_probe()` creates dummy clients, initializes CRC/regmap/irqchip, and registers children with an IRQ domain.

Control flow: probe maps TCPC, PMIC, LDO, and PMU I2C slave IDs, with the real client used for PMU. Regmap register high byte selects the bank. Reads/writes choose the client, optionally translate address and verify/append CRC, then issue SMBus block transfers. After vendor validation, regmap-irq provides child IRQ mappings to `devm_mfd_add_devices()`.

State and persistence: `ddata` owns slave clients and CRC table. Hardware register state is not cached. `chip_rev` is stored after validation. Child drivers access all banks through the shared regmap.

Dependencies and integration points: depends on I2C dummy devices, custom regmap bus, CRC8, regmap-irq, MFD cell macros, and DT compatible `mediatek,mt6360`. Child IRQ resources are named for charger, ADC, LED, and regulator events.

Risks: custom read/write code uses pointer arithmetic on `void *`, which relies on compiler extensions. Write buffer lifetime is manually freed, unlike the read path's cleanup attribute. CRC framing and block-size assumptions are complex and easy to regress. Suspend/resume only toggles wake if the device is wake-capable but probe never sets wake capability. Test signals include all bank translations, CRC mismatch handling, short SMBus transfers, IRQ resource mapping, vendor rejection, and child driver access across PMU/TCPC/PMIC/LDO banks.
