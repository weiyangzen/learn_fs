# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/debugfs.c

## Purpose

`debugfs.c` exposes runtime SPI NOR configuration through debugfs. It creates a global `spi-nor` root and per-device directories containing `params` and `capabilities` files. These files let developers inspect detected flash identity, selected opcodes, protocols, flags, erase commands, sector map, and supported read/program modes.

## Important APIs, types, and functions

`spi_nor_debugfs_register()` creates the per-device directory and files. `spi_nor_debugfs_shutdown()` removes the root directory at module exit. `spi_nor_debugfs_unregister()` is registered as a devm action to remove a device directory on detach.

`spi_nor_params_show()` prints selected live state from `struct spi_nor` and `struct spi_nor_flash_parameter`. `spi_nor_capabilities_show()` walks `params->hwcaps.mask`, converts each bit to read/program command indexes through `spi_nor_hwcaps_read2cmd()` and `spi_nor_hwcaps_pp2cmd()`, and prints command details.

## Control flow

The core calls `spi_nor_debugfs_register(nor)` after a successful scan in `spi_nor_probe()`. On first registration, the file creates the root directory. It then registers a devm cleanup callback, creates a device-named subdirectory, and creates read-only seq files. The seq show functions run when users read the debugfs files and access live driver state.

## State and persistence behavior

The file does not persist state. It exposes current in-memory state, including opcodes/protocols that may have been changed by SFDP parsing, fixups, controller capability filtering, and octal-DTR setup. The static `rootdir` pointer tracks global debugfs root lifetime.

## Dependencies and integration points

It depends on debugfs, seq_file show helpers, SPI NOR internals from `core.h`, public SPI NOR protocol enums, and SPI/SPI-mem types. The `snor_f_names[]` array must remain in sync with `enum spi_nor_option_flags` in `core.h`.

## Risks

The file is diagnostic, not data-path critical, but stale or incorrect output can mislead debugging of flash bring-up. `rootdir` creation is lazy and global; cleanup relies on module exit and devm per-device removal. If flag names fall out of sync, debugfs will show wrong flags. Reading live state assumes the device remains valid through debugfs lifetime, which is mitigated by devm removal.

## Test signals

Mount debugfs and verify `/sys/kernel/debug/spi-nor/<device>/params` and `capabilities` after probing several devices. Check that selected opcodes, protocols, erase map, and flags match SFDP dumps and expected manufacturer fixups.
