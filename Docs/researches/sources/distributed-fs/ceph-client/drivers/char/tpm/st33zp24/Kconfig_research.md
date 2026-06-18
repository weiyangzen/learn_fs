<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Kconfig

## Purpose
Defines configuration symbols for the STMicroelectronics ST33ZP24 TPM 1.2 core and its I2C and SPI physical bus drivers.

## Important APIs, Types, And Functions
Symbols are `TCG_TIS_ST33ZP24`, `TCG_TIS_ST33ZP24_I2C`, and `TCG_TIS_ST33ZP24_SPI`. The bus options depend on `I2C` or `SPI` and select the common core symbol.

## Control Flow
Selecting either bus transport pulls in the shared ST33ZP24 core. Kbuild then builds the common `tpm_st33zp24` object and the chosen physical transport module.

## State And Persistence
The selected Kconfig symbols persist in `.config` and decide whether the ST33ZP24 platform can probe via I2C, SPI, or both.

## Dependencies And Integration Points
This sub-Kconfig is sourced from the main TPM Kconfig and integrates with the ST33ZP24 Makefile, Linux I2C/SPI device matching, ACPI IDs, and OF compatibles.

## Risks And Edge Cases
The core is hidden and only selected by transports, so direct user selection is avoided. Dependency mistakes could build a bus driver without its bus framework or omit the shared core.

## Test Signals
Build configurations for I2C-only, SPI-only, both transports, and module versus built-in variants. Runtime probe tests should bind `st33zp24-i2c` and `st33zp24-spi` devices and register TPM chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/Kconfig -->
