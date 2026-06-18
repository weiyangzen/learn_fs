# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Kconfig

Purpose: Defines Kconfig options for the Marvell 8897 NFC NCI core and USB, UART, I2C, and SPI transports.

Important APIs, types, and functions: `NFC_MRVL` is the hidden core symbol. `NFC_MRVL_USB` depends on `NFC_NCI && USB`; `NFC_MRVL_UART` depends on `NFC_NCI && NFC_NCI_UART`; `NFC_MRVL_I2C` depends on `NFC_MRVL && I2C`; `NFC_MRVL_SPI` depends on `NFC_MRVL && NFC_NCI_SPI`. Transport selections pull in the core where needed.

Control flow: Build-time only. Users select a bus transport; Kconfig includes or selects the common Marvell core.

State and persistence behavior: Only kernel configuration state persists. Runtime state belongs to the Marvell source files outside this work item.

Dependencies and integration points: Connects Marvell NFC support to NFC NCI core and bus-specific helper subsystems.

Risks: Dependency asymmetry matters: USB/UART select the core directly, while I2C/SPI depend on the core. This can affect menu visibility and build selection. Descriptions should remain aligned with actual device IDs and transport support.

Test signals: Kconfig resolution for each transport, all-modules build, dependency-disabled builds without USB/UART/I2C/SPI helpers, and expected module selection of `nfcmrvl`.
