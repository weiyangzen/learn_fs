# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Makefile

## Purpose
This Makefile maps S3FWRN5/S3FWRN82 Kconfig symbols to kernel objects.

## Important build objects
- `s3fwrn5-objs = core.o firmware.o nci.o phy_common.o` builds the shared NCI core, firmware-update protocol, proprietary NCI RF configuration, and GPIO mode helpers.
- `s3fwrn5_i2c-objs = i2c.o` builds the I2C transport module.
- `s3fwrn82_uart-objs = uart.o` builds the serdev UART transport module.

## Control flow and integration
`obj-$(CONFIG_NFC_S3FWRN5)` emits the shared module, while the I2C and UART objects are separate modules selected by their transport configs. Physical modules call exported symbols from the shared object.

## State, dependencies, and risks
There is no runtime state. The build is sensitive to symbol/module ordering because `i2c.o` and `uart.o` depend on exported `s3fwrn5_probe()`, `s3fwrn5_remove()`, common PHY helpers, and firmware/NCI receive paths from the core module.

## Test signals
Build tests should compile the shared core alone, each physical transport as a module, and all objects built-in to detect missing exports or module metadata regressions.
