<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-eeprom.c

Purpose: bit-level Microwire-style EEPROM access for SOLO6x10 cards, used by core sysfs EEPROM read/write handlers.

Important APIs, types, and functions: `solo_eeprom_ewen()` enables or disables EEPROM writes. `solo_eeprom_read()` clocks out a 16-bit big-endian word. `solo_eeprom_write()` clocks a 16-bit word and polls for completion. Helpers `solo_eeprom_cmd()`, `solo_eeprom_reg_read()`, and `solo_eeprom_reg_write()` drive `SOLO_EEPROM_CTRL` bits.

Control flow: commands enable EEPROM access/chip select, shift command/address bits, then read or write 16 data bits with delays. Writes require `solo_eeprom_ewen()` around the sysfs write loop and poll `EE_DATA_READ` for completion.

State and persistence: reads and writes persistent on-card EEPROM. Values are exposed as big-endian words to callers.

Dependencies and integration points: core sysfs `eeprom` attribute, `SOLO_EEPROM_CTRL` register, udelay timing.

Risks: EEPROM writes can permanently change device data; core limits default writes to 64 bytes but `full_eeprom` permits 128 bytes. `solo_eeprom_write()` returns `!retval`, which means zero on success if ready bit became set, matching kernel style only if callers treat nonzero as error carefully. Timing is fixed delay-based.

Test signals: read stable EEPROM contents, write guarded region and verify, write-disable prevents unintended writes, timeout behavior on absent EEPROM, and no corruption under repeated sysfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-eeprom.c -->
