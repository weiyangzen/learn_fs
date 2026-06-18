# sources/distributed-fs/ceph-client/drivers/misc/eeprom/m24lr.c

## Purpose
I2C driver for ST M24LR RFID/NFC EEPROM devices. It exposes EEPROM contents through nvmem and exposes the system parameter sector through sysfs attributes for UID, sector count, password update, unlock, and a binary `sss` area.

## Important APIs, Types, And Functions
`struct m24lr_chip` describes per-variant `sss_len`, `page_size`, and `eeprom_size`; `struct m24lr` holds UID, geometry, control and EEPROM regmaps, and a mutex. `m24lr_regmap_read()` and `m24lr_regmap_write()` retry transient failures until timeout. `m24lr_read()` and `m24lr_write()` dispatch to control or EEPROM regmap. `m24lr_nvmem_read()` and `m24lr_nvmem_write()` implement nvmem. Sysfs callbacks include `m24lr_ctl_sss_read/write()`, `new_pass_store()`, `unlock_store()`, `uid_show()`, and `total_sectors_show()`.

## Control Flow
Probe checks I2C capability, identifies chip data from OF/ID/ACPI, reads two `reg` cells, creates a dummy I2C client for EEPROM access, initializes one cached control regmap and one EEPROM regmap, registers nvmem, creates the `sss` binary sysfs file, then reads UID from register 2324 as a device sanity check. Reads and writes are serialized by `m24lr->lock`; writes are split at device page boundaries and retried to handle NACKs during internal write cycles.

## State, Persistence, And Dependencies
Persistent state includes EEPROM data, system security sector data, password state, lock state, and UID. Driver state is geometry, cached control regmap data, and global sysfs binary attribute configuration. Dependencies include I2C, regmap, nvmem-provider, device properties, OF matching, ACPI match data, and sysfs attribute groups.

## Integration Points
Compatible strings and I2C IDs cover `m24lr04e-r`, `m24lr16e-r`, and `m24lr64e-r`. Nvmem consumers bind to the EEPROM dummy client. Device sysfs attributes are attached through `dev_groups`; the `sss` binary file is created manually during probe and removed during remove.

## Risks
Control-sector and password writes are security-sensitive and only lightly validated. `m24lr_write()` uses `buf + offset` while also passing the device offset, which is suspicious for nonzero offsets because sysfs/nvmem buffers are normally relative to the request, not absolute device memory. The global `bin_attr_sss` is mutated per probe (`size` and `private`), making multiple devices risky. Timeout loops are fixed at 25 ms and may not match all parts.

## Test Signals
Exercise all variants, multiple instances, nonzero-offset nvmem writes, page-boundary writes, read/write timeout paths, sysfs `sss` bounds, UID read failure cleanup, password input parsing, dummy-client creation failure, and regmap cache behavior for volatile control registers.
