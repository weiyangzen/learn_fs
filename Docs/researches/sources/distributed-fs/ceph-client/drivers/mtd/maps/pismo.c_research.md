<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pismo.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pismo.c

Purpose: I2C EEPROM discovery driver for PISMO memory modules. It does not map flash directly; it creates `physmap-flash` or `mtd-ram` platform devices based on EEPROM chip-select descriptors.

Important APIs, types, and functions: packed EEPROM formats are `struct pismo_cs_block` and `struct pismo_eeprom`. Runtime structs are `struct pismo_mem` and `struct pismo_data`. Key functions include `pismo_eeprom_read()`, `pismo_add_device()`, `pismo_add_nor()`, `pismo_add_sram()`, `pismo_add_one()`, `pismo_probe()`, and `pismo_remove()`.

Control flow: probe verifies I2C functionality, allocates driver state, reads the 256-byte EEPROM, logs board name, iterates up to five chip selects, converts width encoding, uses platform-provided base addresses, and adds child platform devices for static NOR or SRAM. Child devices carry resources and platform data for physmap or plat-ram. Remove unregisters all child devices and frees state.

State and persistence: persistent state is module EEPROM content and memory devices. Runtime state is child platform-device pointers and optional VPP callback data from platform data.

Dependencies and integration points: I2C core, PISMO platform data, physmap-flash, mtd-ram/plat-ram, and optional VPP forwarding.

Risks: `pismo_probe()` dereferences `pdata->cs_addrs[i]` without a visible null check after optional VPP extraction, so platform data appears required despite being treated partly optional. EEPROM checksum field is not validated. Test signals are EEPROM read size, child device creation for type 2/3 entries, width rejection, VPP forwarding, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pismo.c -->
