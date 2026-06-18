# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.c

## Purpose

`sfdp.c` parses JEDEC Serial Flash Discoverable Parameters and turns flash-resident tables into SPI NOR runtime parameters. It discovers density, address width, read modes, erase types, page size, quad-enable requirements, 4-byte opcode support, non-uniform sector maps, xSPI Profile 1.0 octal-DTR settings, SCCR volatile register offsets, and soft-reset or byte-order flags.

## Important APIs, types, and functions

Public entry points are `spi_nor_check_sfdp_signature()` and `spi_nor_parse_sfdp()`. Internal parser stages include `spi_nor_parse_bfpt()`, `spi_nor_parse_smpt()`, `spi_nor_parse_4bait()`, `spi_nor_parse_profile1()`, `spi_nor_parse_sccr()`, `spi_nor_parse_sccr_mc()`, and post-SFDP fixup dispatch.

Important helpers include `spi_nor_read_sfdp()`, which temporarily forces the RDSFDP opcode, 3-byte address, and 8 dummy cycles; erase-type sorting and mask translation helpers; SMPT map-selection helpers that run detection commands; and 4BAIT conversion code that updates read/program/erase opcodes to 4-byte variants.

## Control flow

`spi_nor_parse_sfdp()` reads and validates the SFDP header, reads optional parameter headers once, caches a bounded complete SFDP dump in `nor->sfdp`, chooses the newest BFPT header, parses BFPT, then iterates optional tables. Optional parser failures are warned but do not discard already-parsed base parameters. Finally it runs manufacturer and part post-SFDP fixups.

BFPT parsing sets density, address bytes, fast-read capabilities, erase types, page size, quad-enable method, 4-byte mode method, soft-reset support, octal read instructions, command extension type, and 8D byte swap flag. SMPT can replace uniform erase maps with non-uniform regions. 4BAIT can force 4-byte opcodes. Profile 1 adds 8D-8D-8D read/program support and status-register dummy/address requirements.

## State and persistence behavior

The parser mainly mutates in-memory `nor->params` and `nor->flags`. It also temporarily mutates read opcode/address/dummy fields while reading SFDP or SMPT detection bytes, restoring them before return. The cached `nor->sfdp` is devm-managed for later sysfs/debug access.

## Dependencies and integration points

It depends on `core.h`, `sfdp.h`, bitfield helpers, sort, kmalloc/devm allocation, SPI NOR data I/O helpers, and manufacturer fixup hooks. Its outputs are consumed by core setup, debugfs, sysfs, manufacturer octal-DTR code, erase planning, and MTD geometry.

## Risks

SFDP is untrusted device data. Bad lengths, pointers, density encodings, or table IDs can cause wrong allocations or wrong geometry; the code bounds cached SFDP to one page but parser-specific reads still rely on header lengths. Optional table failures are intentionally non-fatal, so partially correct configuration is possible. SMPT detection temporarily changes read settings and executes vendor-defined reads, which can fail on controllers with limited command support. Incorrect 4BAIT handling can mask needed operations or select 4-byte opcodes without complete read/program/erase coverage.

## Test signals

Test SFDP signature fallback, BFPT-only devices, JESD216A/B/C/D differences, non-uniform erase maps, 4BAIT large flashes, xSPI Profile 1 octal-DTR flashes, malformed/truncated SFDP tables, optional table parse failures, and debugfs/sysfs SFDP cache visibility.
