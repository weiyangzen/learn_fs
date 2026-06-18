# sources/distributed-fs/ceph-client/drivers/net/usb/smsc75xx.h

Purpose: Hardware register and bitfield map for SMSC/Microchip LAN75xx USB Gigabit Ethernet devices. It defines TX/RX command word fields, system control/status registers, MAC registers, MII access registers, WOL filter registers, PHY vendor registers, USB vendor request IDs, and interrupt endpoint status bits consumed by `smsc75xx.c`.

Important APIs and types: The header exposes macros rather than functions. Important groups include `TX_CMD_A/B_*` and `RX_CMD_A/B_*` descriptor fields, `HW_CFG`, `PMT_CTL`, `INT_STS`, `DP_SEL/DP_CMD/DP_ADDR/DP_DATA`, `BURST_CAP`, `INT_EP_CTL`, `E2P_CMD/E2P_DATA`, `RFE_CTL`, FIFO/flow registers, `MAC_CR/MAC_RX/MAC_TX/FLOW`, address/filter registers, `WUCSR/WUF_CFGX/WUF_MASKX`, optional offload registers, PHY interrupt/mode/special registers, and `USB_VENDOR_REQUEST_*`.

Control flow: No executable flow exists. The constants define how the C driver sequences reset, configures FIFOs and receive filtering, accesses EEPROM/PHY/dataport RAM, parses RX command words, emits TX command words, and programs wake filters.

State and persistence: No direct state. It encodes hardware ABI values; incorrect constants persist as bad runtime device programming. EEPROM-related constants gate persistent EEPROM access from the driver.

Dependencies and integration points: Included only by `smsc75xx.c`. It relies on kernel USB request direction/type macros and `BIT()` for interrupt endpoint fields.

Risks: Bit mask mistakes affect hardware control directly. Some similarly named interrupt bits use trailing underscores in hardware names, so call sites must match the exact macro set. RX/TX command length and checksum fields must align with packet fixup code. WOL filter address spacing is encoded by macros that suspend code uses for repeated writes.

Test signals: Compile coverage of all register users, reset/init traffic on real LAN75xx hardware, EEPROM read/write, multicast hash programming, RX/TX descriptor parsing, WOL filter programming, and PHY interrupt handling.
