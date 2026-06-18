<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.h

## Purpose
`ttpci-eeprom.h` declares the exported TTPCI EEPROM MAC helpers for DVB card drivers.

## Important APIs, Types, and Functions
It declares `ttpci_eeprom_decode_mac(u8 *decodedMAC, u8 *encodedMAC)` and `ttpci_eeprom_parse_mac(struct i2c_adapter *adapter, u8 *propsed_mac)`. The latter parameter name contains a spelling error but the type and function name are correct.

## Control Flow
Callers either pass raw encoded EEPROM bytes to the decode helper or pass an I2C adapter to have the implementation read and decode the EEPROM.

## State and Persistence Behavior
The header defines no state. The implementation reads persistent EEPROM contents and writes caller-supplied buffers.

## Dependencies and Integration Points
It includes Linux types and I2C declarations and pairs with `ttpci-eeprom.c`. It is intended for media/DVB board drivers that need a MAC address for network-over-DVB support.

## Risks and Test Signals
The misspelled `propsed_mac` parameter can cause confusion but not compile failure. Test signals are compile users including this header and successful link resolution of exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.h -->
