# sources/distributed-fs/ceph-client/drivers/nfc/pn533/Kconfig

Purpose: Declares build configuration for the PN533/PN532 NFC core and USB, I2C, and UART transports.

Important entries: `NFC_PN533` is the hidden core tristate. `NFC_PN533_USB` depends on USB and selects the core. `NFC_PN533_I2C` depends on I2C and selects the core. `NFC_PN532_UART` depends on `SERIAL_DEV_BUS` and selects the core.

Control flow: No runtime flow; configuration determines which modules are built and which transport frontends expose menus.

State and persistence: Build configuration only.

Dependencies and integration points: Integrates with USB, I2C, serdev, and the common NFC device stack. The UART option is named PN532 because it targets PN532-style UART transport while sharing PN533 core.

Risks: The core has no prompt, so it is enabled only by selected transports. Missing NFC core dependency may be inherited from parent menu; build tests should catch invalid standalone selections. Test signals include module and built-in builds for each transport, dependency hiding without USB/I2C/SERIAL_DEV_BUS, and module names `pn533_usb`, `pn533_i2c`, and `pn532_uart`.
