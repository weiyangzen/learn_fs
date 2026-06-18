# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/swp.c

## Purpose
Implements default SPI NOR software write protection using status-register block-protection bits. It maps MTD lock/unlock/is_locked calls to BP/TB/SRWD status register updates and supplies backward-compatible full-chip unlock at probe.

## Important APIs, Types, and Functions
Public integration functions are `spi_nor_init_default_locking_ops()`, `spi_nor_try_unlock_all()`, and `spi_nor_set_mtd_locking_ops()`. Core helpers include `spi_nor_get_sr_bp_mask()`, `spi_nor_get_sr_tb_mask()`, `spi_nor_get_min_prot_length_sr()`, `spi_nor_get_locked_range_sr()`, `spi_nor_sr_lock()`, `spi_nor_sr_unlock()`, and `spi_nor_sr_is_locked()`. `spi_nor_sr_locking_ops` is the default `struct spi_nor_locking_ops`.

## Control Flow
The lock path reads the status register, derives the currently protected range, checks whether requested protection can be represented without unlocking other regions, calculates the BP/TB encoding, optionally sets `SR_SRWD`, and writes back with verification. Unlock performs the inverse: it only shrinks protection if the requested region can be unlocked without locking unrelated areas. MTD wrappers prepare/lock the NOR, call the selected locking op, then unlock/unprepare.

## State and Persistence
Protection state persists in status register BP bits, optional BP3 encodings, top/bottom selector bits, and SRWD. The code supports volatile-locking devices through flags supplied by part tables, but the actual persistence depends on the flash status register implementation.

## Dependencies and Integration Points
The implementation depends on `struct spi_nor` flags set by manufacturer tables and core parsing, including `SNOR_F_HAS_LOCK`, `SNOR_F_HAS_4BIT_BP`, `SNOR_F_HAS_SR_BP3_BIT6`, `SNOR_F_HAS_SR_TB`, `SNOR_F_HAS_SR_TB_BIT6`, and `SNOR_F_NO_WP`. It plugs into the MTD lock API by assigning `_lock`, `_unlock`, and `_is_locked`.

## Risks
Only contiguous top or bottom ranges can be represented; arbitrary ranges fail with `-EINVAL`. Size calculations depend on erase-sector assumptions and power-of-two BP encodings. Mis-set flags can protect the wrong end of flash or use the wrong BP3/TB bit. `spi_nor_try_unlock_all()` intentionally ignores errors, so hardware write protection may only be visible via debug logs.

## Test Signals
Exercise lock/unlock/is_locked across top, bottom, full, empty, and unrepresentable ranges. Confirm status register values after operations and run MTD write attempts against locked regions.
