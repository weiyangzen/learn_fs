# sources/distributed-fs/ceph-client/drivers/nfc/microread/Kconfig

Purpose: Defines Kconfig options for the Inside Secure Microread HCI NFC core and its I2C and MEI transports.

Important APIs, types, and functions: `NFC_MICROREAD` is a hidden tristate core selecting `CRC_CCITT`. `NFC_MICROREAD_I2C` depends on `NFC_HCI && I2C && NFC_SHDLC` and selects the core. `NFC_MICROREAD_MEI` depends on `NFC_HCI && NFC_MEI_PHY` and also selects the core.

Control flow: Build-time only; choosing a transport selects the shared Microread HCI logic.

State and persistence behavior: Only kernel configuration state persists. Runtime state lives in the built modules.

Dependencies and integration points: Connects transport-specific code to NFC HCI, SHDLC LLC for I2C, and the shared MEI PHY helper for MEI transport.

Risks: Transport dependencies must match the LLC names passed at runtime (`LLC_SHDLC_NAME` for I2C, `LLC_NOP_NAME` for MEI). Missing `CRC_CCITT` would break Type 1 tag transceive CRC generation in core code.

Test signals: Build I2C and MEI transports independently and together, as modules and built-in, and verify selecting transports pulls in `microread.o`.
