# sources/distributed-fs/ceph-client/drivers/video/backlight/ili922x.c

## Purpose
This SPI LCD driver initializes Ilitek ILI9221/ILI9222 display controllers. Register access uses SPI, while pixel memory is refreshed over an RGB interface.

## Important APIs, Types, and Functions
`struct ili922x` stores SPI, LCD device, and power state. Module parameters `ili922x_id` and `tx_invert` alter start-byte ID and byte polarity. `ili922x_read_status()`, `ili922x_read()`, and `ili922x_write()` implement the controller's start-byte/index/data protocol with register-access speed limiting. `ili922x_poweron()`, `ili922x_poweroff()`, and `ili922x_display_init()` program power, display, gamma, GRAM window, and RGB-interface registers. `ili922x_lcd_power()` backs the LCD `set_power` callback.

## Control Flow
Probe allocates state, reads `REG_DRIVER_CODE_READ`, verifies the masked device ID, reads status for debug, runs display initialization, registers `ili922xlcd`, and powers on. Runtime power transitions call the power-on/off register sequences only when crossing the `POWER_IS_ON()` boundary. Remove powers the panel off.

## State and Persistence
Power state is volatile in `ili->power`. The panel retains programmed register state until reset or power loss. There is no persistent software storage.

## Dependencies and Integration Points
The driver depends on SPI, OF headers, the LCD class, and module parameters for legacy board quirks. It caps register access speed to 4 MHz while allowing higher-speed GRAM access outside this driver.

## Risks
Several initialization writes ignore return values because `ili922x_display_init()` is `void`; failures can leave partially initialized hardware. Power-on/off accumulate return codes with addition rather than preserving the first negative error cleanly. `tx_invert` and `ili922x_id` are global module settings, not per-device properties.

## Test Signals
Test ID read success/failure, register speed capping, byte inversion mode, init sequence execution, power off/on via sysfs LCD power, remove cleanup, and SPI transfer failures during read/write.
