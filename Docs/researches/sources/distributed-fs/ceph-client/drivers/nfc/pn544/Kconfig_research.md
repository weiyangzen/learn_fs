# sources/distributed-fs/ceph-client/drivers/nfc/pn544/Kconfig

Purpose: Declares build configuration for the PN544 HCI core and its I2C and MEI transports.

Important entries: `NFC_PN544` is the hidden core tristate and selects `CRC_CCITT`. `NFC_PN544_I2C` depends on `NFC_HCI && I2C && NFC_SHDLC` and selects the core. `NFC_PN544_MEI` depends on `NFC_HCI && NFC_MEI_PHY` and selects the core.

Control flow: No runtime flow; it gates module build and dependency availability.

State and persistence: Build configuration only.

Dependencies and integration points: Ties PN544 to the NFC HCI stack, SHDLC LLC for I2C, MEI NFC PHY for Intel MEI transport, and CRC-CCITT for I2C framing/firmware checks.

Risks: The hidden core is selected only by transports. I2C depends on SHDLC because its LLC framing uses that layer; MEI uses LLC NOP from its transport. Test signals include dependency-disabled builds, module builds for `pn544_i2c` and `pn544_mei`, and CRC dependency presence.
