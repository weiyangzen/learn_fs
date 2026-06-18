# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/esmt.c

## Purpose

`esmt.c` registers ESMT F25L/F25Q SPI NOR parts. It provides static `flash_info` entries for a small set of devices, including software protection capabilities.

## Important APIs, types, and functions

The file defines `esmt_nor_parts[]` and exports `spi_nor_esmt`. Entries identify devices with `SNOR_ID()`, set `.size`, set `SECT_4K`, and mark lock support with `SPI_NOR_HAS_LOCK`; `f25l32pa` also uses `SPI_NOR_SWP_IS_VOLATILE`.

## Control flow

The core matches JEDEC IDs to this manufacturer table. Runtime behavior then follows common core paths: `spi_nor_init_flags()` converts table flags into runtime lock and volatile-protection flags, `spi_nor_init_default_locking_ops()` can be selected during late init, and non-SFDP flags seed erase settings.

## State and persistence behavior

No local mutable state exists. The table affects persistent flash protection behavior by telling the core that block protection bits exist and may be volatile after power-on.

## Dependencies and integration points

It depends on `core.h` definitions and integrates with the generic lock setup in the SPI NOR core and locking helper files.

## Risks

Protection flags have direct user-visible effects. If `SPI_NOR_HAS_LOCK` or `SPI_NOR_SWP_IS_VOLATILE` is wrong, the core may expose invalid lock operations or unlock a device unexpectedly under `CONFIG_MTD_SPI_NOR_SWP_DISABLE*`. Size or erase hints must match hardware.

## Test signals

Probe each ESMT ID, verify `mtd->_lock/_unlock/_is_locked` behavior where exposed, confirm volatile protection behavior after reset, and run erase/write tests with 4K sector alignment.
