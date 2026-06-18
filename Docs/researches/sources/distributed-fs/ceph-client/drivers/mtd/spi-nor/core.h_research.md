# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/core.h

## Purpose

`core.h` is the internal contract for the SPI NOR subsystem. It defines standard SPI memory operation templates, internal flags, command descriptors, erase-map structures, OTP structures, flash identification records, manufacturer registration objects, SFDP cache structures, and prototypes shared by the core, SFDP, OTP, locking, debugfs, and manufacturer files.

## Important APIs, types, and functions

The header defines `SPI_NOR_*_OP` macros for read ID, write enable/disable, status/configuration register access, 4-byte mode entry/exit, bank register write, global block unlock, die/sector erase, read, page program, and software reset. These macros produce `struct spi_mem_op` templates consumed by `core.c`, `sfdp.c`, `otp.c`, and manufacturer octal-DTR code.

Key types include `spi_nor_flash_parameter`, `spi_nor_fixups`, `flash_info`, `spi_nor_manufacturer`, `spi_nor_erase_map`, `spi_nor_erase_region`, `spi_nor_erase_type`, `spi_nor_otp_organization`, and `spi_nor_otp_ops`. The `SNOR_ID()` and `SNOR_OTP()` macros create inline static descriptors for manufacturer tables.

The prototype list exposes the internal helper surface: register I/O, data I/O, write-enable, readiness, quad-enable methods, 4-byte mode methods, erase helpers, OTP helpers, SFDP parser entry points, locking and OTP MTD setup, and debugfs registration.

## Control flow

`core.h` does not execute runtime control flow, but it shapes the runtime pipeline. `flash_info` entries feed `spi_nor_get_flash_info()` and `spi_nor_init_params()`. `spi_nor_fixups` hooks are invoked in default, BFPT, SMPT, post-SFDP, and late phases. `spi_nor_flash_parameter` becomes the state object consumed by setup, MTD callbacks, debugfs, and manufacturer fixups.

## State and persistence behavior

The header distinguishes transient driver flags (`SNOR_F_*`) from flash capabilities and flash-specific metadata (`SPI_NOR_*` flags in `flash_info`). Some flags represent persistent or semi-persistent hardware state, such as software protection volatility, 4-byte opcode support, volatile I/O mode enable, soft reset support, ECC behavior, and RWW support.

OTP metadata records physical OTP layout but does not itself persist data; persistence is implemented by the flash and surfaced through `otp.c`.

## Dependencies and integration points

It includes `sfdp.h` and depends on public SPI NOR, MTD, SPI-mem, list, and kernel bit macros through the included translation units. Manufacturer modules export `const struct spi_nor_manufacturer` objects declared here, while the core consumes them through `manufacturers[]`.

## Risks

This header is a high-blast-radius ABI inside the driver. Any mismatch between `SNOR_F_*` names and `debugfs.c` display tables produces bad diagnostics. Incorrect `SPI_MEM_OP` templates can corrupt operation direction, bus width, or address length across all users. Flag overloading can also lead to confusion: `flash_info.flags`, `no_sfdp_flags`, `fixup_flags`, and runtime `nor->flags` have different meanings.

## Test signals

Build coverage should include all SPI NOR translation units. Runtime validation should check debugfs flag names, SFDP and non-SFDP probes, OTP user-prot registration, quad-enable methods, 4-byte mode selection, and manufacturer fixup paths that call these prototypes.
