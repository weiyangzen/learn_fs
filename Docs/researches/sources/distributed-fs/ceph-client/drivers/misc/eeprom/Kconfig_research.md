# sources/distributed-fs/ceph-client/drivers/misc/eeprom/Kconfig

Purpose: declares Linux Kconfig options for EEPROM and EEPROM-like memory drivers under `drivers/misc/eeprom`.

Important APIs, types, and functions: relevant options for this subset are `EEPROM_AT24`, `EEPROM_AT25`, `EEPROM_93CX6`, `EEPROM_DIGSY_MTC_CFG`, and `EEPROM_EE1004`. The menu also declares options for MAX6875, 93XX46, IDT 89HPESX, and M24LR drivers that are built by the same directory but not part of this source subset. Options select dependencies such as NVMEM, NVMEM_SYSFS, REGMAP, REGMAP_I2C, and SPI_MEM as needed.

Control flow: Kconfig selections determine which EEPROM drivers are compiled. AT24 depends on I2C and SYSFS and selects NVMEM/regmap; AT25 depends on SPI and SYSFS and selects SPI_MEM/NVMEM; EE1004 depends on I2C and SYSFS; DIGSY_MTC_CFG is a board-specific bool depending on GPIO_MPC5200 and SPI_GPIO.

State and persistence: no runtime state; this file controls compile-time availability and dependency selection for drivers that expose persistent EEPROM/FRAM/SPD contents at runtime.

Dependencies and integration points: integrated with the top-level kernel configuration. Help text documents user-visible module names and cautions, especially AT24 misconfiguration risks and SPD handling.

Risks: users can select generic EEPROM geometry that does not match hardware, which can lead to data loss in writable devices. Board-specific DIGSY_MTC_CFG exists as a legacy static device-registration path and should eventually be replaced by device tree.

Test signals: configuration build matrix for each option as built-in/module/disabled where applicable, dependency resolution for I2C/SPI/NVMEM/regmap, and module names matching Makefile output.
