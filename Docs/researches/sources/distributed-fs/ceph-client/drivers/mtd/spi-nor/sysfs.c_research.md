# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sysfs.c

## Purpose
Exposes SPI NOR identification and SFDP data through a `spi-nor` sysfs attribute group on the SPI device. This is diagnostic and introspection glue rather than flash I/O logic.

## Important APIs, Types, and Functions
Read-only text attributes are `manufacturer`, `partname`, and `jedec_id`, implemented by `manufacturer_show()`, `partname_show()`, and `jedec_id_show()`. A binary `sfdp` attribute is implemented by `sfdp_read()`. Visibility is controlled by `spi_nor_sysfs_is_visible()` and `spi_nor_sysfs_is_bin_visible()`. The exported group list is `spi_nor_sysfs_groups[]`.

## Control Flow
Sysfs show handlers recover `struct spi_nor` from `device -> spi_device -> spi_mem -> driver data` and format the requested field. `jedec_id_show()` prefers the part-table ID when present and falls back to the probed ID buffer. `sfdp_read()` uses `memory_read_from_buffer()` over `nor->sfdp->dwords`. Visibility callbacks hide missing manufacturer/name/ID/SFDP attributes.

## State and Persistence
The file does not mutate persistent state. It reflects runtime probe state stored in `nor->manufacturer`, `nor->info`, `nor->id`, and `nor->sfdp`.

## Dependencies and Integration Points
It depends on SPI, SPI MEM, sysfs, and SPI NOR core data ownership. The group is expected to be attached by the SPI NOR driver during device registration.

## Risks
The code assumes the SPI device driver data is a valid `spi_mem` and that `spi_mem` driver data is a valid `spi_nor`. Visibility checks prevent most null dereferences for optional fields, but `sfdp_read()` assumes `nor->sfdp` exists because the binary visibility callback hides it otherwise.

## Test Signals
After probing SPI NOR devices, verify `/sys/.../spi-nor/manufacturer`, `partname`, `jedec_id`, and optional `sfdp` contents and permissions. Test devices without SFDP or table IDs to confirm attributes are hidden or fall back correctly.
