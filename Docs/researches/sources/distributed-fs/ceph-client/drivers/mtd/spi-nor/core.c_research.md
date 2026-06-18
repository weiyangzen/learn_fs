# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.c

## Purpose

`core.c` is the central Linux MTD SPI NOR framework implementation. It binds as a `spi_mem_driver`, detects or matches a flash device, derives `spi_nor_flash_parameter` data from defaults, manufacturer fixups, SFDP, and late fixups, negotiates supported read/program/erase protocols with the controller, registers an `mtd_info`, and implements the MTD read, write, erase, suspend, resume, remove, and shutdown paths. It also exports `spi_nor_scan()` for controller-specific users.

## Important APIs, types, and functions

The main public entry point is `spi_nor_scan()`, exported with `EXPORT_SYMBOL_GPL`, which validates `struct spi_nor`, allocates a bounce buffer, hardware-resets the part when a reset GPIO exists, resolves `flash_info`, initializes parameters, optionally initializes RWW wait queues, selects controller-compatible operations, initializes the chip, and fills MTD callbacks.

Key helper families include register access (`spi_nor_read_id`, `spi_nor_read_sr`, `spi_nor_read_cr`, `spi_nor_write_sr`, `spi_nor_write_sr_and_check`), write-enable and readiness (`spi_nor_write_enable`, `spi_nor_write_disable`, `spi_nor_wait_till_ready`), protocol helpers (`spi_nor_spimem_setup_op`, `spi_nor_read_data`, `spi_nor_write_data`, `spi_nor_read_any_reg`, `spi_nor_write_any_volatile_reg`), quad/4-byte/octal mode setup, erase map execution, and MTD operation callbacks.

`manufacturers[]` integrates manufacturer modules by referencing `spi_nor_eon`, `spi_nor_esmt`, `spi_nor_everspin`, `spi_nor_gigadevice`, `spi_nor_intel`, `spi_nor_issi`, `spi_nor_macronix`, `spi_nor_micron`, `spi_nor_st`, and others outside this group.

## Control flow

Probe begins in `spi_nor_probe()`: it enables the `vcc` regulator, allocates and initializes `struct spi_nor`, chooses a flash name from platform data or modalias, calls `spi_nor_scan()`, registers debugfs, creates read/write direct maps, and finally calls `mtd_device_register()`.

`spi_nor_scan()` resets protocols to 1-1-1, allocates an early bounce buffer, optionally toggles hardware reset, detects or matches flash info, initializes `nor->params`, optionally initializes RWW wait queues, calls `spi_nor_setup()` to select the actual read/program/erase path, runs `spi_nor_init()` to enter octal/quad/4-byte modes and optional unlock-all behavior, and installs MTD callbacks.

Read/write/erase MTD flows wrap controller preparation and locking. Reads call `spi_nor_prep_and_lock_rd()` and loop through `spi_nor_read_data()` or the octal-DTR alignment helper. Writes split by page boundaries, issue WREN, program one page fragment, wait ready, and advance `retlen`. Erases choose chip/die erase, uniform sector erase, or non-uniform erase-command lists built from the erase map.

## State and persistence behavior

Persistent device state includes volatile and non-volatile flash modes and registers: quad enable bits, 4-byte address mode, status/configuration registers, software protection bits, octal-DTR mode bits, and erase/program effects on the flash array. Driver state is held in `struct spi_nor`: opcodes, protocols, address byte count, `params`, cached JEDEC ID, cached SFDP pointer, bounce buffer, direct-map descriptors, `mtd_info`, flags, and RWW lock state.

Shutdown and remove call `spi_nor_restore()` to exit 4-byte mode when needed and issue a soft reset if SFDP advertised reset support. Suspend disables volatile octal-DTR mode; resume calls `spi_nor_init()` again.

## Dependencies and integration points

The file depends on Linux MTD, SPI, SPI-mem, GPIO descriptor reset, regulator, OF properties (`broken-flash-reset`, `no-wp`, `m25p,fast-read`), debugfs/sysfs hooks, SFDP parsing, OTP and locking helpers, and manufacturer `flash_info` tables. It supports both modern `spi_mem` paths and legacy `controller_ops`, with DTR register operations rejected for legacy controller ops.

## Risks

Capability selection is safety-critical: wrong SFDP parsing or fixups can select unsupported opcodes, bus widths, dummy cycles, address widths, or erase sizes. Stateful mode transitions are especially risky on systems with broken reset lines because a crash can leave flash in 4-byte or octal-DTR mode for boot firmware. RWW locking is complex and bank-based; mistakes can allow reads during program/erase of the same bank or over-serialize otherwise safe access. Octal-DTR odd-address alignment uses temporary buffers and 0xff padding, so partial transfer accounting must remain exact. Non-uniform erase planning must avoid erasing outside requested ranges, especially for overlaid regions.

## Test signals

Useful tests include JEDEC/SFDP probe on known parts, spi-mem operation support filtering, MTD read/write/erase with unaligned and page-boundary ranges, large erase ranges across uniform and non-uniform maps, suspend/resume and remove/shutdown restoration, RWW concurrent read/program tests on multi-bank parts, debugfs parameter inspection, and boot-cycle tests for `broken-flash-reset` platforms.
