# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.c

## Purpose

`amdgpu_ras_eeprom_i2c.c` adapts rascore EEPROM persistence to AMDGPU I2C EEPROM hardware. It discovers the RAS table address from VBIOS or MP1 IP defaults and implements paged I2C transfers for RAS bad-page EEPROM records.

## Important APIs, Types, And Functions

The exported object is `amdgpu_ras_eeprom_i2c_sys_func`, with `.eeprom_i2c_xfer = ras_eeprom_i2c_xfer` and `.update_eeprom_i2c_config = ras_eeprom_i2c_config`. Constants describe EEPROM memory address regions `0x0` and `0x40000`, 19-bit address to 7-bit I2C address conversion, 256-byte page size, and two-byte EEPROM offsets.

## Control Flow, State, And Persistence

Configuration first asks atom firmware for a RAS ROM address, normalizes the wire-format address into a 19-bit memory address, or falls back to `0x40000` for selected MP1 13.0.x ASICs. Transfer code loops over the requested range, computes the I2C device address and two-byte offset, limits writes so they do not cross a page boundary, allows reads up to `U16_MAX`, issues a two-message `i2c_transfer`, and sleeps 10 ms after writes for EEPROM internal programming. Persistence is the EEPROM-backed RAS table.

## Dependencies And Integration Points

It depends on AMDGPU atom firmware helpers, `ras_eeprom` control, the configured I2C adapter from the RAS manager, Linux I2C APIs, and MP1 IP version detection. It is plugged into `ras_eeprom_config` by `amdgpu_ras_mgr_init_eeprom_config`.

## Risks And Test Signals

Risks include wrong EEPROM base address, I2C adapter quirks not honored beyond max lengths stored elsewhere, partial transfer accounting, page-boundary write errors, and fixed sleep latency. Test signals include VBIOS-address and fallback-address platforms, EEPROM read/write/reset table tests, bad-page persistence across reboot, I2C fault injection, and page-boundary transfer tests.
