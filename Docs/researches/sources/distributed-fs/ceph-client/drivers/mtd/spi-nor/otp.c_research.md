# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/otp.c

## Purpose

`otp.c` implements user OTP support for SPI NOR flashes. It maps vendor security-register operations into the MTD user protection register API, handles contiguous logical OTP offsets, enforces region alignment for erase/lock, checks lock status before destructive operations, and installs MTD OTP callbacks when a flash supplies OTP ops.

## Important APIs, types, and functions

Generic security-register helpers are `spi_nor_otp_read_secr()`, `spi_nor_otp_write_secr()`, `spi_nor_otp_erase_secr()`, `spi_nor_otp_lock_sr2()`, and `spi_nor_otp_is_locked_sr2()`. These are used by flash entries that represent OTP as Winbond/GigaDevice-style security registers.

MTD callbacks include `spi_nor_mtd_otp_info()`, `spi_nor_mtd_otp_read()`, `spi_nor_mtd_otp_write()`, `spi_nor_mtd_otp_erase()`, and `spi_nor_mtd_otp_lock()`. `spi_nor_set_mtd_otp_ops()` installs those callbacks on `mtd_info`.

## Control flow

The core calls `spi_nor_set_mtd_otp_ops()` while filling MTD info. If `params->otp.ops` is absent, nothing is exposed. Reads and writes validate/logically clamp offsets, lock the device, translate logical MTD offsets into physical OTP region addresses, and call the supplied OTP ops one region at a time. Writes first check whether any affected region is locked. Erase and lock require whole-region aligned ranges.

## State and persistence behavior

OTP data, erase state, and lock bits persist in flash hardware. The code temporarily overrides `nor->read_opcode`, `program_opcode`, protocols, address bytes, and direct-map descriptors to issue security-register commands, then restores previous state. Locking uses status/configuration register bits via SR2/CR helpers.

## Dependencies and integration points

It depends on `core.h` SPI NOR helpers, MTD OTP callback contracts, `spi_nor_prep_and_lock()`, write-enable and readiness helpers, and flash-supplied `spi_nor_otp_ops`/organization metadata.

## Risks

Temporary mutation of `struct spi_nor` opcodes and direct-map descriptors must always be restored on error. OTP writes are one-way on many devices, and lock operations are irreversible, so range validation and lock checks are critical. Logical-to-physical offset translation assumes region length is a power of two; `spi_nor_set_mtd_otp_ops()` warns and refuses otherwise. Reads and writes must not span unsupported physical security registers except through the per-region loop.

## Test signals

Test `_get_user_prot_info`, read/write, lock, and erase on a flash with OTP ops. Verify locked writes and erases return `-EROFS`, partial logical reads across regions split correctly, unaligned erase/lock returns `-EINVAL`, and normal flash read/write opcodes still work after OTP errors.
