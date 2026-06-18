# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Kconfig

## Purpose
This Kconfig fragment defines the STMicroelectronics NCI-family core and its I2C/SPI physical-layer options.

## Important symbols
- `NFC_ST_NCI` is a hidden tristate core selected by transports and contains chipset NCI logic.
- `NFC_ST_NCI_I2C` depends on `NFC_NCI && I2C`, selects the core, and builds `st-nci_i2c`.
- `NFC_ST_NCI_SPI` depends on `NFC_NCI && SPI`, selects the core, and builds `st-nci_spi`.

## Control flow and integration
The build layout separates the common NCI/HCI/SE/vendor implementation from physical links. Runtime transport registration flows through `ndlc_probe()` into `st_nci_probe()`.

## State, dependencies, and risks
Kconfig state is compile-time only. Correct dependency expression is important because both transports need the NCI stack and the shared NDLC/core code. The help text identifies the family-level nature of these drivers, so compatible strings in I2C/SPI source determine exact chip coverage.

## Test signals
Configuration tests should cover built-in/module combinations, disabling `NFC_NCI`, disabling individual buses, and verifying each transport selects the core.
