# sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.h

## Purpose
`lan78xx.h` is the LAN78xx hardware definition layer. It defines USB vendor requests, interrupt endpoint bits, TX/RX command fields, system registers, MAC/PHY datapath registers, filter RAM layout, wake registers, and OTP/EEPROM control constants used by `lan78xx.c`.

## Important APIs, Types, And Constants
The file has no functions or exported data structures. Its API is a register and bitfield namespace. USB requests are `USB_VENDOR_REQUEST_WRITE_REGISTER`, `USB_VENDOR_REQUEST_READ_REGISTER`, and `USB_VENDOR_REQUEST_GET_STATS`. TX and RX metadata is described by `TX_CMD_A_*`, `TX_CMD_B_*`, `RX_CMD_A_*`, `RX_CMD_B_*`, and `RX_CMD_C_*`, covering length, checksum, TSO, VLAN, error, and wake fields.

Register groups cover identity/reset (`ID_REV`, `HW_CFG`, `PMT_CTL`), GPIO/wake, dataport RAM (`DP_SEL`, `DP_CMD`, `DP_ADDR`, `DP_DATA`), EEPROM (`E2P_CMD`, `E2P_DATA`), USB configuration and LPM/LTM (`USB_CFG0..3`, `USB_STATUS`, latency registers), interrupt endpoint control, receive filtering (`RFE_CTL`, `VLAN_TYPE`, `MAF_*`), FIFO/flow control, MAC control, MII access, EEE timing, wake filters (`WUCSR`, `WUCSR2`, `WK_SRC`, `WUF_CFG`, `WUF_MASK*`), protocol offload registers, RGMII DLL tuning, and OTP programming registers.

## Control Flow
`lan78xx.c` uses these constants in all hardware read-modify-write paths. TX fills command words from `TX_CMD_*`; RX parses `RX_CMD_*`; reset/probe programs USB, FIFO, RFE, MAC, PMT, and LTM registers; MDIO uses `MII_ACC_*`; suspend/WoL programs wake filter constants.

## State And Persistence Behavior
The header itself has no runtime state, but it defines persistent and volatile hardware state: EEPROM/OTP bytes, MAC address registers, filter RAM, VLAN/hash tables, USB LPM settings, PHY/MAC control, wake filters, and counters. Mask accuracy is critical because incorrect bit definitions can corrupt unrelated hardware state.

## Dependencies And Integration Points
The header is tightly coupled to Microchip LAN7800/LAN7850/LAN7801 hardware documentation and the implementation in `lan78xx.c`. It relies on common Linux bit and integer macros from surrounding includes.

## Risks And Test Signals
The file contains duplicate identical definitions for `GPIO_CFG1_GPIOD6_` and `PHY_DEV_ID_REV_SHIFT_`, a low-risk maintenance smell. Test coverage should exercise register dumps, TX/RX offloads, EEPROM/OTP reads and writes, wake filter programming, MDIO, USB LPM/LTM, and MAC/PHY mode transitions.
