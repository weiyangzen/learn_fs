<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raydium_i2c_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/raydium_i2c_ts.c

## Purpose
`raydium_i2c_ts.c` drives Raydium I2C capacitive touchscreen controllers, including `raydium_i2c`, `rm32380`, ACPI `RAYD0001`, and OF `raydium,rm32380`. It handles power sequencing, banked I2C register access, bootloader/main firmware mode discovery, firmware updates, sysfs maintenance commands, interrupt-driven multitouch reporting, and system sleep.

## Important APIs, Types, And Functions
`struct raydium_data` holds the `i2c_client`, input device, `avdd`/`vccio` regulators, optional reset GPIO, queried `struct raydium_info`, sysfs mutex, report buffer, bank address, packet sizes, and boot mode. `raydium_i2c_send()` and `raydium_i2c_read()` implement the key transport rule: if an address exceeds one byte, an `RM_CMD_BANK_SWITCH` message and the data transfer are issued in one `i2c_transfer()` to avoid other devices interleaving on the shared bus. Initialization flows through `raydium_i2c_check_fw_status()`, `raydium_i2c_query_ts_bootloader_info()`, and `raydium_i2c_query_ts_info()`. Firmware update is split across bootloader helpers such as `raydium_i2c_enter_bl()`, `raydium_i2c_fw_write_page()`, `raydium_i2c_write_checksum()`, and `raydium_i2c_do_update_firmware()`.

## Control Flow
Probe verifies raw I2C capability, acquires regulators and reset GPIO, powers on, checks an SMBus byte transaction reaches a device, initializes boot/main mode, allocates a report buffer sized from controller metadata, creates a ten-slot direct MT input device with X/Y resolution, registers sysfs attributes, and requests a threaded IRQ. On IRQ, `raydium_i2c_irq()` ignores events while in bootloader recovery, reads a full packet from `data_bank_addr`, validates the trailing checksum, and calls `raydium_mt_event()` to report each contact's slot state, X/Y, pressure, and major/minor width.

## State And Persistence
The driver keeps controller metadata and boot mode in RAM. Firmware update is user-triggered by sysfs `update_fw`; it loads `raydium_<hw_ver>.fw`, writes flash pages, and reinitializes metadata. Sysfs also exposes `fw_version`, `hw_version`, `boot_mode`, and `calibrate`. Hardware state persists in controller flash after updates, while input/report state is volatile.

## Dependencies And Integration Points
It depends on the I2C core, firmware loader, regulator and GPIO consumer APIs, input MT, wake IRQ/sleep PM, ACPI/OF matching, and sysfs device groups. `device_may_wakeup()` selects between sleep command and full power-off during suspend.

## Risks
Bank switching is fragile by design; any future refactor to regmap would violate the driver's stated bus atomicity requirement. Firmware update disables IRQs but still depends on controller acknowledgments and correct package size/checksum. `raydium_i2c_power_on()` is effectively a no-op without reset GPIO, so board descriptions without GPIO may leave regulator sequencing to external firmware. Suspend refuses bootloader mode with `-EBUSY`.

## Test Signals
Test probe on I2C adapters with `I2C_FUNC_I2C`, read sysfs version/mode files, verify checksum warnings are absent under touch load, trigger calibration, exercise firmware update with valid and invalid firmware sizes, and check suspend/resume both with and without wakeup enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raydium_i2c_ts.c -->
