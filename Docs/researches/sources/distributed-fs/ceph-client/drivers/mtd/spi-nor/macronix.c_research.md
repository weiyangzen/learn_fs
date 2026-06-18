# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/macronix.c

## Purpose

`macronix.c` registers Macronix SPI NOR parts and implements Macronix-specific fixups for quad page program, quad enable, 4-byte address mode defaults, and octal-DTR mode transitions.

## Important APIs, types, and functions

`mx25l25635_post_bfpt_fixups()` distinguishes ID-reused MX25L25635 variants by checking BFPT 4-4-4 fast read support and sets `SNOR_F_4B_OPCODES` for the newer variant. `macronix_qpp4b_post_sfdp_fixups()` adds missing 1-1-4 page program support with a 4-byte opcode. `mx25l3255e_late_init_fixups()` supplies missing quad-enable and 1-4-4 page program settings for older SFDP.

The octal-DTR helpers write CR2 dummy-cycle and mode registers, verify mode switches by reading JEDEC ID, and support both enable and disable paths. Manufacturer late init supplies default 4-byte mode entry and `set_octal_dtr`.

## Control flow

After matching a Macronix part, the core applies manufacturer default init, SFDP parsing, part post-BFPT/post-SFDP fixups, manufacturer late init, and then capability selection. If the selected read/write protocols are 8D-8D-8D and the volatile I/O-mode flag is set, `spi_nor_set_octal_dtr()` calls the Macronix mode switch helper.

## State and persistence behavior

Static tables have no mutable state, but mode helpers write volatile CR2 registers on the flash. The driver verifies transitions by reading IDs in the expected protocol. Shutdown and suspend can disable volatile octal mode through the core. Quad enable may persist depending on part register behavior.

## Dependencies and integration points

The file uses `spi_nor_write_any_volatile_reg()`, `spi_nor_read_id()`, `spi_nor_set_pp_settings()`, `spi_nor_set_4byte_addr_mode_en4b_ex4b()`, and SFDP BFPT macros. It integrates heavily with core mode setup and SFDP fixup hooks.

## Risks

Macronix has ID reuse and incomplete SFDP on several parts, so fixup scope matters. Octal-DTR mode switching is stateful; failed disable can leave the device inaccessible to boot firmware. Dummy-cycle conversion through `MXIC_NOR_REG_DC()` must match hardware encoding. ID verification assumes duplicated bytes in 8D reads, so controller byte ordering and `SNOR_F_SWAP16` interactions need coverage.

## Test signals

Test MX25L25635E/F differentiation, MX25L3255E quad and 1-4-4 page program, 4-byte reads/writes/erases on large parts, octal-DTR entry/exit on MX25UW51245G, suspend/resume restoration, and debugfs protocol/opcode output.
