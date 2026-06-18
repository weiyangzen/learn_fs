# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.c

Purpose: reads identification data from a 24LC02 EEPROM on NetUP Dual DVB-S2 CI cards, specifically the board revision and two six-byte MAC addresses.

Important APIs and functions: `netup_eeprom_read(struct i2c_adapter *i2c_adap, u8 addr)` performs a combined one-byte address write and one-byte data read from EEPROM I2C address `0x50`. `netup_get_card_info(struct i2c_adapter *i2c_adap, struct netup_card_info *cinfo)` reads revision byte 63, MAC bytes 64-69 for port 0, and MAC bytes 70-75 for port 1.

Control flow: `netup_eeprom_read` builds two `i2c_msg` entries, initializes the target offset, calls `i2c_transfer`, logs an error if two messages are not completed, and returns either the byte value or `-1`. `netup_get_card_info` performs sequential single-byte reads and stores results directly into the output structure.

State and persistence: the only persistent state is on the EEPROM device. The driver does not cache contents, validate MAC address format, or preserve partial-read error state. Failed reads become `0xff` when assigned to `u8` MAC/revision fields because the helper returns `-1` as an `int`.

Dependencies and integration points: depends on Linux I2C APIs, `cx23885.h`, and structure declarations in `netup-eeprom.h`. It is consumed by cx23885 NetUP board setup paths that need card revision and per-port MAC addresses.

Risks: the file contains a stray line with just `#` before includes, which is accepted as an empty preprocessing directive but is unusual. Error handling is weak for multi-byte card info reads because individual failures are not propagated. The EEPROM layout offsets are hard-coded. It assumes a one-byte EEPROM address and 7-bit I2C address `0x50`.

Test signals: useful validation includes I2C transfer failure injection, real NetUP EEPROM reads confirming revision/MAC offsets, and build coverage for the cx23885 NetUP configuration. No local tests are present in this subset.
