# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/gigadevice.c

## Purpose

`gigadevice.c` registers GigaDevice GD25Q/GD25LQ SPI NOR parts and provides a targeted SFDP fixup for `gd25q256`.

## Important APIs, types, and functions

`gd25q256_post_bfpt()` inspects BFPT version. For first-generation JESD216 data on GD25Q256C, it overrides `params->quad_enable` to `spi_nor_sr1_bit6_quad_enable()` because early SFDP does not define Quad Enable requirements. `gd25q256_fixups` attaches that hook.

`gigadevice_nor_parts[]` lists supported JEDEC IDs, sizes for non-SFDP parts, lock/top-bottom flags, 4K sector and dual/quad read hints, and `SPI_NOR_4B_OPCODES` for `gd25q256`.

## Control flow

The core detects a GigaDevice ID, applies default parameter setup, parses SFDP when required, calls the part `post_bfpt` fixup for `gd25q256`, and later converts flash flags into runtime lock and addressing behavior.

## State and persistence behavior

No local mutable state exists. Table flags influence persistent protection handling. The quad-enable fixup writes status register bit 6 at runtime when quad I/O is selected.

## Dependencies and integration points

The file depends on `sfdp.h` BFPT revision constants through `core.h`, quad-enable helpers from `core.c`, and common lock/addressing setup.

## Risks

The GD25Q256 ID spans multiple generations with different SFDP quality. The fixup must be narrowly version-gated so newer parts keep their SFDP-defined behavior. Incorrect lock/top-bottom flags can expose wrong protection ranges. Missing 4-byte opcode handling can break accesses above 16 MiB.

## Test signals

Probe GD25Q16/32/64/128 and GD25Q256 generations, verify debugfs quad-enable method effects, test lock/unlock regions, run reads and writes above 16 MiB on GD25Q256, and compare selected capabilities against SFDP dumps.
