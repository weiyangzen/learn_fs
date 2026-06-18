# sources/distributed-fs/ceph-client/drivers/mfd/menf21bmc.c

Purpose: I2C MFD core for the MEN 14F021P00 Board Management Controller. It verifies SMBus support, reads firmware revision fields, exits watchdog production mode if needed, and registers watchdog, LED, and hwmon child devices.

Important APIs, types, and functions: `menf21bmc_cell[]` lists `menf21bmc_wdt`, `menf21bmc_led`, and `menf21bmc_hwmon`. `menf21bmc_wdt_exit_prod_mode()` reads production status and sends the exit command if active. `menf21bmc_probe()` checks adapter functionality, reads major/minor/main revision words, logs firmware version, exits production mode, and calls `devm_mfd_add_devices()`.

Control flow: probe performs all hardware checks before child registration. Because devm MFD add is used, child devices are removed automatically on parent teardown. There is no custom remove path.

State and persistence: the driver keeps no private runtime state. Exiting production mode changes BMC persistent or semi-persistent watchdog behavior. Firmware revision is only logged.

Dependencies and integration points: depends on I2C SMBus byte/word operations, MFD core, and child drivers with matching names. Binding is by I2C ID `menf21bmc`.

Risks: revision fields are read as SMBus words but printed as decimal two-digit values, which may not match firmware encoding if it is BCD or endian-sensitive. Exiting production mode is performed automatically at probe and may have operational effects. Test signals include functionality-mask failure, revision read errors, production-mode exit success/failure, and devm child registration.
