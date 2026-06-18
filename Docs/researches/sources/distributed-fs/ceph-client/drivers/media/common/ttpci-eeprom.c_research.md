<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.c

## Purpose
`ttpci-eeprom.c` reads and decodes encoded MAC addresses from 24C16-style EEPROMs on Siemens/Technotrend/Hauppauge PCI DVB cards so dvb_net can use a stable Ethernet address.

## Important APIs, Types, and Functions
Exported functions are `ttpci_eeprom_decode_mac()` and `ttpci_eeprom_parse_mac()`. Internal helpers are `check_mac_tt()`, `getmac_tt()`, and `ttpci_eeprom_read_encodedMAC()`. The decode algorithm uses a fixed 20-byte XOR mask, bit shifts derived from encoded bytes, and a checksum over the decoded intermediate data.

## Control Flow
`ttpci_eeprom_parse_mac()` reads 20 encoded bytes from I2C EEPROM address `0x50`, starting at offset `0xcc`, using a two-message `i2c_transfer()`. On read failure it zeroes the proposed MAC and returns the error. On successful read it decodes with `getmac_tt()`, validates the signature checksum, copies six decoded bytes into the caller's buffer, and logs the MAC.

`ttpci_eeprom_decode_mac()` exposes the same decode/validate logic for callers that already have the 20 encoded bytes.

## State and Persistence Behavior
The EEPROM provides persistent hardware state, but this file only reads it. It does not cache decoded addresses. On failure, caller-provided MAC storage is explicitly zeroed in the parse path.

## Dependencies and Integration Points
The file depends on Linux I2C, module infrastructure, string helpers, and `eth_zero_addr()`. It exports symbols for DVB PCI card drivers. The companion header declares the two public helpers.

## Risks and Test Signals
The debug macro is hardwired on via `#if 1`, so parse operations can print more than expected. The decode algorithm is format-specific; invalid EEPROM data returns `-ENODEV` and zeros the output in `parse_mac()`. The header parameter name typo does not affect ABI but is visible to readers.

Test signals include I2C transfer returning exactly two messages, known encoded vectors decoding to expected MACs, checksum failure paths zeroing output, and downstream dvb_net receiving nonzero valid MAC addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.c -->
