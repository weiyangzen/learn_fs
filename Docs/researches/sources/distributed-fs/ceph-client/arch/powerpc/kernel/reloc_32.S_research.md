# sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_32.S

## Purpose
`reloc_32.S` applies dynamic relocations for a relocatable PPC32 kernel image at early boot or secure-guest transitions.

## Important APIs, Types, And Functions
It exports `_GLOBAL(relocate)`, taking the desired final address in `r3`. It parses dynamic tags `DT_RELA`, `DT_RELASZ`, and `DT_RELAENT`, handles relocation types `R_PPC_RELATIVE`, `R_PPC_ADDR16_HI`, `R_PPC_ADDR16_HA`, and `R_PPC_ADDR16_LO`, and references linker-provided offsets for `__dynamic_start`, `__rela_dyn_start`, `__dynamic_symtab`, and `_stext`.

## Control Flow
The routine obtains its runtime address with a branch-and-link trick, computes runtime addresses for dynamic, rela, symbol, and text sections, scans `.dynamic` for RELA metadata, computes current and final relocation offsets, then iterates each relocation. Relative relocations store addend plus final offset; halfword relocations compute symbol/addend/final-offset high, high-adjusted, or low halves. Modified locations are flushed from data cache and invalidated from instruction cache before returning.

## State And Persistence
It mutates the loaded kernel image in place. There is no global data beyond embedded PC-relative pointers.

## Dependencies And Integration Points
It is called by early boot/relocation code such as secure guest setup in `prom_init.c`. It depends on the linker script producing dynamic relocation metadata and on PowerPC cache-management instructions.

## Risks
Incorrect offset calculation corrupts code/data before the kernel runs. Unknown relocation types are skipped, so new relocation forms must be added deliberately. Cache synchronization is mandatory for modified instructions.

## Test Signals
Build and boot relocatable PPC32 kernels, inspect relocation sections for supported types, test nonzero final bases, and validate instruction patching after relocation through early boot execution.
