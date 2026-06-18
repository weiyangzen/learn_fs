# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/spansion.c

## Purpose
Implements Spansion/Cypress SPI NOR manufacturer support for the generic SPI NOR core. It supplies device table entries, manufacturer-level late initialization, and Cypress-specific fixups for address mode discovery, volatile quad enable, octal DTR transitions, page-size correction, die erase, ECC write granularity, SFDP quirks, and program/erase failure handling.

## Important APIs, Types, and Functions
The exported integration point is `const struct spi_nor_manufacturer spi_nor_spansion`, backed by `spansion_nor_parts[]` and `spansion_nor_fixups`. `struct spansion_nor_params` stores the proprietary clear-status opcode selected from `USE_CLSR` or `USE_CLPEF`. Status/error paths are handled by `spansion_nor_clear_sr()`, `spansion_nor_sr_ready_and_clear()`, and `cypress_nor_sr_ready_and_clear()`. Cypress register access is expressed through `CYPRESS_NOR_RD_ANY_REG_OP`, `CYPRESS_NOR_WR_ANY_REG_OP`, and helpers including `cypress_nor_quad_enable_volatile()`, `cypress_nor_set_addr_mode_nbytes()`, `cypress_nor_get_page_size()`, and `cypress_nor_set_octal_dtr()`. Part-family fixup groups include `s25fs256t_fixups`, `s25hx_t_fixups`, `s28hx_t_fixups`, and `s25fs_s_nor_fixups`.

## Control Flow
The core matches a JEDEC ID against `spansion_nor_parts[]`, parses SFDP where available, then invokes family fixups. BFPT/post-SFDP hooks correct missing or misleading SFDP data such as 4-byte address mode methods, opcode tables, volatile register offsets, page program opcodes, erase opcodes, xSPI read opcode, dummy cycles, and page size. Late init installs ready callbacks and ECC/write-size policy. During I/O polling, the ready callback reads status from one die or all Cypress dice, clears sticky error flags, disables writes after failures, and returns ready/not-ready/error to the SPI NOR core.

## State and Persistence
Most state is volatile runtime parameter mutation in `nor->params`: `addr_nbytes`, `addr_mode_nbytes`, `page_size`, `read_dummy`, `writesize`, `ready`, `quad_enable`, `set_4byte_addr_mode`, `set_octal_dtr`, and die metadata. The code deliberately prefers volatile register updates for Cypress quad and octal mode setup to reduce risk from interrupted non-volatile register writes. It allocates `params->vreg_offset` for S25FS256T and private clear-status parameters with devm-managed memory.

## Dependencies and Integration Points
This file depends on the SPI NOR core (`core.h`), `spi_mem` operation execution, SFDP fixup callbacks, status register conventions, and MTD geometry exposed through `nor->mtd`. It integrates with manufacturer registration consumed by the SPI NOR core and with multi-die Cypress register maps.

## Risks
Incorrect SFDP fixups can create wrong capacity, page size, erase opcode, or address mode behavior. Octal DTR transitions are risky because the bus protocol changes mid-operation and are validated only by JEDEC ID readback. Program/erase failures must clear status and disable writes; missing this can leave WEL set and increase corruption risk. Multi-die status polling depends on accurate `n_dice` and `vreg_offset` data.

## Test Signals
Useful signals include successful probe of listed Spansion/Cypress parts, SFDP parse logs around fixups, MTD erase/write/read tests on affected devices, failure injection that sets `SR_E_ERR` or `SR_P_ERR`, and explicit validation of 3-byte/4-byte and 8D-8D-8D transitions.
