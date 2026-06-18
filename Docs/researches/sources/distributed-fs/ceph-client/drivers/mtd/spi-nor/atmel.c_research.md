# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/atmel.c

Purpose: Atmel/Adesto SPI NOR manufacturer table and vendor-specific locking fixups.

Important APIs/types/functions: `atmel_nor_parts[]` lists supported JEDEC IDs, names, sizes, flags, no-SFDP capabilities, and fixups. `spi_nor_atmel` exports the manufacturer descriptor. `at25fs_nor_locking_ops` supports legacy whole-chip unlock for AT25FS parts. `atmel_nor_global_protection_ops` implements whole-chip global protect/unprotect for parts using Atmel global BP bits.

Control flow: late init fixups replace `nor->params->locking_ops`. AT25FS only allows whole-flash unlock by writing status register 0 and returns unsupported for lock/is_locked. Global protection reads SR, clears SRWD if needed, sets or clears BP bits 5:2, sets SRWD when protecting, and writes SR using `spi_nor_write_sr()` because the command is effectively a protect/unprotect pseudo-command. `is_locked` verifies range and checks all global BP bits.

State and persistence: persistent state is SPI NOR status-register protection bits. Runtime state is manufacturer/part metadata and selected locking ops. These operations can change flash write-protection state.

Dependencies and integration: depends on SPI NOR core helpers, `core.h`, status register definitions, and Kconfig SWP policy. Risks include whole-chip-only locking returning `-EINVAL` for partial ranges, WP# preventing SRWD changes, table entries without explicit size relying on SFDP, and legacy unlock behavior that may reduce protection unexpectedly. Test signals include JEDEC ID matching, late fixup invocation, whole-chip lock/unlock/is_locked, partial range rejection, SRWD asserted failure, and SWP policy boot behavior.
