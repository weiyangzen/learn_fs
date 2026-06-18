# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.h

Purpose: defines the NetUP EEPROM card-info structure and declares the EEPROM read helpers.

Important APIs and types: `struct netup_port_info` contains one six-byte MAC address. `struct netup_card_info` contains two ports and an 8-bit revision. Exported functions are `netup_eeprom_read` and `netup_get_card_info`.

Control flow: consumers allocate or embed `struct netup_card_info`, pass an `i2c_adapter` to `netup_get_card_info`, and then read populated revision/MAC fields. Single-address reads can use `netup_eeprom_read` directly.

State and persistence: the header stores no state. It documents the shape of data copied from EEPROM into transient caller-owned structures.

Dependencies and integration points: relies on Linux integer aliases (`u8`) and `struct i2c_adapter` from included kernel headers in consumers. It is the public boundary for `netup-eeprom.c` inside the cx23885 driver.

Risks: the API has no explicit error-returning version of `netup_get_card_info`, so callers cannot distinguish valid `0xff` EEPROM bytes from read failures without changing the implementation. Structure fields are fixed to exactly two ports.

Test signals: compile coverage and board-level EEPROM read tests validate this header. Static checks should ensure callers have included I2C type definitions before this header.
