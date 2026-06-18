# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Kconfig

## Purpose
This Kconfig fragment defines build options for the Samsung S3FWRN5 NFC core, its I2C physical layer, and the related S3FWRN82 UART physical layer.

## Important symbols
- `NFC_S3FWRN5` is a hidden tristate selected by physical-layer drivers. It selects `CRYPTO_LIB_SHA1` because firmware download hashes images with SHA1.
- `NFC_S3FWRN5_I2C` is user-visible, depends on `NFC_NCI && I2C`, selects the shared core, and builds `s3fwrn5_i2c.ko`.
- `NFC_S3FWRN82_UART` is user-visible, depends on `NFC_NCI && SERIAL_DEV_BUS`, selects the same core, and builds `s3fwrn82_uart.ko`.

## Control flow and integration
The build graph keeps common NCI/firmware logic in the core object while letting I2C and UART choose their transport dependencies. Runtime integration is through the Linux NCI stack, not the digital or HCI stacks.

## State, persistence, and dependencies
Kconfig state is compile-time only. The important dependency signal is that firmware update support is always present when the core is selected, and UART support is tied to serdev rather than tty line disciplines.

## Risks
The UART option is S3FWRN82-specific but selects the S3FWRN5 core; regressions in common mode/firmware code can affect both chips. Missing `NFC_NCI` or transport dependencies prevent physical-layer visibility.

## Test signals
Config tests should cover built-in and module combinations for core, I2C, and UART; dependency pruning when `I2C` or `SERIAL_DEV_BUS` is disabled; and that selecting either physical layer pulls in `CRYPTO_LIB_SHA1` through the core.
