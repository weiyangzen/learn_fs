# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/micron-st.c

## Purpose

`micron-st.c` registers Micron and ST SPI NOR parts and implements shared Micron/ST behavior: flag-status-register readiness, octal-DTR entry/exit, multi-die erase setup, and several part-specific SFDP fixups.

## Important APIs, types, and functions

The file defines Micron opcodes and FSR bits, `micron_st_nor_octal_dtr_en/dis()`, `micron_st_nor_ready()`, multi-die late init helpers, `mt35xu512aba_post_sfdp_fixup()`, `mt25qu512a_post_bfpt_fixup()`, and exported manufacturers `spi_nor_micron` and `spi_nor_st`.

`micron_st_nor_ready()` combines normal status-register readiness with FSR reads, reports erase/program/protection errors, clears FSR, and sends write-disable on program/erase errors to avoid accidental later writes.

## Control flow

Probe matches Micron or ST entries, applies manufacturer default init to set lock support, clear 16-bit status default, and disable quad enable. SFDP and part fixups add octal-DTR settings, multi-die metadata, or status quirks. Late init installs FSR readiness for entries with `USE_FSR`, defaults 4-byte mode to WREN+EN4B/EX4B when absent, and installs octal-DTR switching.

## State and persistence behavior

The file writes volatile configuration registers to enter/exit octal-DTR mode. Multi-die late init sets die erase opcode and `n_dice`, and enters 4-byte address mode so die erase can work. FSR error bits are cleared after detection. Protection state and data persistence remain in flash hardware.

## Dependencies and integration points

It depends on core register and spi-mem helpers, `spi_nor_set_read_settings()`, `spi_nor_set_pp_settings()`, 4-byte address helpers, and readiness polling in `core.c`. The ST and Micron tables share the same manufacturer fixups.

## Risks

FSR handling changes error reporting and write-latch cleanup; if unsupported by a controller, fallback to status-only readiness is intentional only for `-EOPNOTSUPP`. Octal-DTR mode writes must be reversible or shutdown/resume can leave the flash in an unexpected protocol. Multi-die late init enters 4-byte mode during parameter initialization, which is persistent until restored and can affect boot safety. Large legacy tables have many IDs where size, lock flags, and FSR flags must remain exact.

## Test signals

Run program/erase failure injection or protected-sector tests to verify FSR error handling and write-disable. Test octal-DTR read/write on MT35XU parts, multi-die chip erase on N25Q/MT25Q large parts, 4-byte access above 16 MiB, suspend/resume, and controller paths that do not support RDFSR.
