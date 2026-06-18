# sources/distributed-fs/ceph-client/drivers/misc/eeprom/digsy_mtc_eeprom.c

Purpose: statically registers a bit-banged SPI bus and 93xx46 EEPROM device for display-configuration EEPROMs on the DigsyMTC board.

Important APIs, types, and functions: defines GPIO numbers for SPI clock, chip select, data in/out, and output enable; a `spi_gpio_platform_data`; a platform device named `spi_gpio`; a GPIO descriptor lookup table; one `spi_board_info` entry for `eeprom-93xx46`; and init function `digsy_mtc_eeprom_devices_init()`.

Control flow: at `device_initcall`, the driver adds the GPIO lookup table, registers SPI board info, attaches a software node with `"data-size" = 8` to the `spi_gpio` platform device, and registers that platform device. On software-node add failure it returns immediately; on platform-device registration failure it removes the software node.

State and persistence: no runtime private state beyond globally defined platform data/device/lookup structures. Persistent EEPROM contents are handled by the downstream `eeprom-93xx46` driver, not this file.

Dependencies and integration points: depends on `GPIO_MPC5200`, `SPI_GPIO`, GPIO machine lookup tables, SPI board-info registration, software nodes, and the `eeprom-93xx46` SPI driver. It is explicitly a board-specific legacy registration shim.

Risks: the file comment states this should be replaced by device-tree-defined SPI/EEPROM devices. Hard-coded GPIO numbers and bus number can collide with platform changes. There is no cleanup path for the device_initcall registration, which is typical for board setup but not hotplug-friendly.

Test signals: DigsyMTC boot should show `spi_gpio.1` registration, correct GPIO lookup resolution, creation of the `eeprom-93xx46` SPI device, and usable EEPROM sysfs/NVMEM access through the downstream driver.
