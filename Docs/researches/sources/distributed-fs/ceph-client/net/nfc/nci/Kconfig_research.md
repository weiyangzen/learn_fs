# sources/distributed-fs/ceph-client/net/nfc/nci/Kconfig

Purpose: Defines kernel configuration options for NFC Controller Interface support and optional NCI transports over SPI and UART.

Important APIs and symbols: `CONFIG_NFC_NCI` enables the core NCI protocol module, depending on `NFC`. `CONFIG_NFC_NCI_SPI` depends on `NFC_NCI && SPI` and selects `CRC_CCITT`. `CONFIG_NFC_NCI_UART` depends on `NFC_NCI && TTY`.

Control flow: Kconfig controls whether objects in `net/nfc/nci/Makefile` are built into the kernel or as modules. The SPI and UART options compile transport wrappers that sit under the NCI core.

State and persistence: No runtime state. The selected symbols persist in the kernel build configuration and determine module availability.

Dependencies and integration points: Integrates with the NFC subsystem menu, SPI framework, TTY framework, and CRC support for SPI transport.

Risks: Drivers depending on SPI or UART NCI support must select or depend on these symbols. Misconfiguration can build a controller driver without the needed NCI transport module.

Test signals: Build matrix coverage for `NFC_NCI=y/m`, SPI enabled/disabled, UART enabled/disabled, and module autoload expectations for NCI transports.
