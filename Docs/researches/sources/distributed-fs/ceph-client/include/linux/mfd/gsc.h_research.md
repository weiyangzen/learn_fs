# sources/distributed-fs/ceph-client/include/linux/mfd/gsc.h

Purpose: This header defines the Gateworks System Controller MFD register interface and parent state. It maps the GSC I2C subaddresses, core registers, control and IRQ bit positions, and common regmap read/write callbacks.

Important APIs, types, and functions: Device-address macros identify miscellaneous control, update, GPIO, HWMON, EEPROM banks, and RTC I2C targets. The register enum defines control, time, IRQ status/enable, firmware CRC/version, and write-protect offsets. Bit constants define pushbutton actions, sleep/watchdog/switch-boot controls, and IRQ sources. `gsc_read` and `gsc_write` are regmap bus callbacks. `struct gsc_dev` stores the parent device, primary and HWMON I2C clients, regmap, firmware version, and CRC.

Control flow, state, and persistence: The parent driver instantiates multiple logical functions behind the controller's I2C addresses, provides regmap access to the misc block, and exposes child functionality for RTC, HWMON, GPIO, watchdog, or update paths. State persists in controller firmware registers, EEPROM, RTC, IRQ latches, and watchdog/sleep configuration.

Dependencies and integration points: It depends on regmap and I2C client users. It integrates with MFD children for hardware monitoring, RTC, GPIO, EEPROM/NVMEM, watchdog, and firmware update support.

Risks and test signals: Risks include bit-position macros being used as masks without `BIT()`, incorrect I2C subaddress routing, write-protect mistakes, and watchdog/sleep settings surviving reboot unexpectedly. Test signals include regmap read/write callback tests, IRQ source/mask tests, firmware version/CRC readback, HWMON child probe, RTC operation, and watchdog timeout behavior.
