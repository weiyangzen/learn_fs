# sources/distributed-fs/ceph-client/arch/powerpc/boot/dcr.h

## Purpose
Boot-wrapper DCR access and register-definition header for IBM/AMCC 4xx support code.

## Important APIs, Types, And Control Flow
Macros `mfdcr`, `mtdcr`, `mfdcrx`, and `mtdcrx` wrap inline assembly for device-control-register reads/writes. The header defines SDRAM, EBC, CPC, MAL, CPR, and SDR register numbers plus helper macros such as `SDRAM0_READ`, `SDRAM_CONFIG_BANK_SIZE`, `EBC_BXCR_BANK_SIZE`, `CPC0_SYS0_*` divider extraction, `SDR0_READ`, and `CPR0_READ`. There is no function-level control flow; callers sequence register writes/reads in 4xx board code.

## State, Dependencies, Risks, And Tests
State is hardware DCR state read or written by callers. Dependencies include 4xx CPU support for DCR instructions and exact controller register encodings. Risks include inline asm constraints accepting only immediate DCR numbers for `mfdcr/mtdcr`, wrong divider masks, static `sdram_bxcr` in a header creating per-translation-unit copies, and destructive writes through helper macros. Test by compiling 405/440 targets, validating decoded memory/clock sizes against hardware docs, and booting board wrappers that use each macro family.
