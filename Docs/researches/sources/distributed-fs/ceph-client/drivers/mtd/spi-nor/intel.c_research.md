# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/intel.c

## Purpose

`intel.c` registers a small set of Intel S33B SPI NOR parts. The table is focused on device identity, size, lock support, and volatile software protection.

## Important APIs, types, and functions

The file defines `intel_nor_parts[]` for `160s33b`, `320s33b`, and `640s33b`, then exports `spi_nor_intel`. Each entry uses JEDEC-like IDs, sets size, and sets `SPI_NOR_HAS_LOCK | SPI_NOR_SWP_IS_VOLATILE`.

## Control flow

The common detection path matches IDs through `spi_nor_match_id()`. During late init, `spi_nor_init_flags()` turns table flags into runtime lock and volatile-protection flags, and the core may install default locking operations.

## State and persistence behavior

No local mutable state exists. The table tells the core that software protection bits exist and are volatile, affecting unlock-at-init behavior depending on kernel configuration.

## Dependencies and integration points

It integrates with the generic SPI NOR manufacturer registry, lock support, and MTD protection callbacks. It has no custom fixups.

## Risks

The main risk is protection semantics. Wrong volatile-protection flags can cause unexpected unlock or missing unlock after reset. There are no `no_sfdp_flags`, so behavior depends on defaults and/or SFDP availability for more advanced parameters.

## Test signals

Probe all listed parts, verify MTD size, confirm lock/unlock/is_locked behavior, and test power-cycle protection defaults with relevant `CONFIG_MTD_SPI_NOR_SWP_DISABLE*` settings.
