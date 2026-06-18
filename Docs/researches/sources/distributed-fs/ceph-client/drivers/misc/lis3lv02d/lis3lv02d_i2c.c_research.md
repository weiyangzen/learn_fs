# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d_i2c.c

## Purpose
`lis3lv02d_i2c.c` is the I2C transport for the LIS3 accelerometer core. It supplies SMBus read/write/block-read callbacks, regulator control, OF/platform-data setup, IRQ and PM integration, and calls the common core initializer.

## Important APIs, types, and functions
Transport callbacks are `lis3_i2c_write`, `lis3_i2c_read`, `lis3_i2c_blockread`, `lis3_i2c_init`, and `lis3_reg_ctrl`. Driver entry points are `lis3lv02d_i2c_probe` and `lis3lv02d_i2c_remove`. PM callbacks are `lis3lv02d_i2c_suspend`, `lis3lv02d_i2c_resume`, `lis3_i2c_runtime_suspend`, and `lis3_i2c_runtime_resume`. The OF match table recognizes `st,lis3lv02d`.

## Control flow
Probe optionally parses OF into core platform data, applies platform-data axis maps and block-read feature selection, calls platform resource setup, obtains `Vdd` and `Vdd_IO` regulators, fills the global `lis3_dev`, powers regulators for initialization, calls `lis3lv02d_init_device`, and turns regulators back off so runtime PM owns later power. Remove releases platform resources, disables joystick, removes core sysfs, and frees regulators. System sleep keeps wakeup-configured devices powered as needed, while runtime PM calls common poweroff/poweron.

## State and persistence
The file stores no per-client allocation of its own; it mutates global `lis3_dev`. Regulator descriptors are kept in that global. Platform resource setup may create board-specific state outside this file and is released through platform callbacks.

## Dependencies and integration points
The driver depends on I2C SMBus byte and optional I2C block functionality, regulator bulk APIs, runtime/system PM, OF matching, platform data, and the shared LIS3 core. It publishes I2C IDs `lis3lv02d` and `lis331dlh`.

## Risks
`lis3_i2c_read` assigns a possibly negative SMBus return to `u8` and returns 0, which can mask read errors. The global `lis3_dev` means two I2C devices conflict. Regulator state is toggled around core init and again by runtime PM, so failed init paths must keep regulator cleanup correct. OF-allocated platform data is not explicitly freed in this transport path.

## Test signals
Tests should verify probe with and without platform data, OF parsing, block read selection only when adapter supports it, regulator enable/disable sequencing, IRQ propagation from `client->irq`, runtime PM transitions, system sleep wakeup behavior, and remove cleanup.
