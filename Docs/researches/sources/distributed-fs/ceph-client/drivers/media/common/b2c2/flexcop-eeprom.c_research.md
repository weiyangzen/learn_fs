# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-eeprom.c

## Purpose
This file implements FlexCop EEPROM access currently used for MAC address reading. It reads an LRC-protected MAC record from the card EEPROM through the common I2C request callback.

## Important APIs, Types, and Functions
`calc_lrc` computes XOR LRC. `flexcop_eeprom_request` retries EEPROM reads/writes against chip address `0x50 | ((addr >> 8) & 3)` using `fc->fc_i2c_adap[1]`. `flexcop_eeprom_lrc_read` validates LRC. The exported API is `flexcop_eeprom_check_mac_addr`.

## Control Flow
The MAC check reads eight bytes from EEPROM address `0x3f8`, validates the LRC over the first seven bytes, and copies the first six bytes into `fc->dvb_adapter.proposed_mac` for normal MAC mode. Extended EUI64 mode is recognized but rejected with `-EINVAL`.

## State and Persistence
The active code only reads EEPROM. Disabled `#if 0` code documents possible write/unlock helpers but is not compiled. Successful reads update the in-memory proposed MAC.

## Dependencies and Integration Points
It depends on `flexcop.h` and the bus-specific `i2c_request` callback. The PCI part uses this common path; USB has its own MAC retrieval path according to the header comment.

## Risks and Test Signals
Retries stop on `ret == 0`; nonzero bus errors are returned after all attempts. LRC failure returns `-EINVAL`. Test valid MAC, bad LRC, I2C retry success/failure, and extended-mode rejection. Ensure I2C adapter index 1 is initialized before calling.
