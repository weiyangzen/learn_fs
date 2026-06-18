# sources/distributed-fs/ceph-client/drivers/net/usb/smsc95xx.h

Purpose: Hardware register and bitfield definitions for SMSC/Microchip LAN95xx USB Ethernet devices. It defines TX command words, RX status fields, SCSR/MAC/PHY registers, WOL registers, checksum offload controls, vendor-specific PHY registers, USB vendor request IDs, and interrupt endpoint bits used by `smsc95xx.c`.

Important APIs and types: The header is macro-only. Key groups include `TX_CMD_A/B_*`, `RX_STS_*`, `ID_REV_*` chip IDs, `INT_STS`, `RX_CFG`, `TX_CFG`, `HW_CFG`, `PM_CTRL`, `LED_GPIO_CFG`, `AFC_CFG`, `E2P_CMD/E2P_DATA`, `BURST_CAP`, `STRAP_STATUS`, `INT_EP_CTL`, `MAC_CR`, `ADDRH/ADDRL`, `HASHH/HASHL`, `MII_ADDR/MII_DATA`, `FLOW`, `VLAN1/2`, `WUFF/WUCSR`, `COE_CR`, PHY EDPD/mode/interrupt/special registers, and `INT_ENP_*`.

Control flow: No executable flow. The definitions drive the C driver's reset sequence, MDIO bus access, EEPROM access, packet descriptor parsing, checksum offload programming, PHY interrupt bridging, and WOL filter packing.

State and persistence: No direct state. EEPROM and WOL constants influence persistent EEPROM access and suspend wake behavior, while chip-ID constants select feature availability at runtime.

Dependencies and integration points: Included by `smsc95xx.c`; relies on kernel USB direction/type and `BIT()` macros. Its chip-ID list is paired with the USB product table and revision detection in the C file.

Risks: LAN95xx has several revisions with different wake-filter and remote-wakeup capabilities, so incorrect chip-ID or feature masks can enable unsupported behavior. RX/TX field width errors would corrupt packet framing. PM and WOL bit names are close to LAN75xx but not identical, so sharing assumptions across headers would be risky.

Test signals: Build all `smsc95xx.c` users, verify reset and register dumps on multiple chip revisions, test checksum offload bits, MDIO/PHY interrupt delivery, EEPROM commands, WOL filter programming on 4-filter and 8-filter parts, and RX/TX descriptor parsing.
