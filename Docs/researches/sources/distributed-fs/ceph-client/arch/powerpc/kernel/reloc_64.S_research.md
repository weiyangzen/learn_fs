# sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_64.S

## Purpose
`reloc_64.S` applies dynamic relocations for a relocatable 64-bit PowerPC kernel image.

## Important APIs, Types, And Functions
It exports `_GLOBAL(relocate)`, with final kernel address in `r3`. It parses RELA dynamic tags and supports `R_PPC64_RELATIVE` and `R_PPC64_UADDR64`. Embedded pointers reference `__dynamic_start`, `__rela_dyn_start`, `__dynamic_symtab`, and `_stext`.

## Control Flow
The function computes runtime addresses via link-register self-reference, scans `.dynamic` for RELA pointer, size, and entry size, calculates the current offset and final relocation offset, divides size by entry size to get a loop count, and then processes each RELA entry. Relative relocations use addend plus final offset; `UADDR64` also resolves the dynamic symbol value before storing. Unsupported relocation types are skipped.

## State And Persistence
The routine patches 64-bit words in the kernel image. It keeps no external state.

## Dependencies And Integration Points
It is used by relocatable PowerPC64 boot paths and by secure guest setup in `prom_init.c` when the kernel image must be restored and re-relocated.

## Risks
Only two relocation types are handled, so toolchain changes that emit other relocation kinds can leave stale addresses. Unlike the PPC32 version, no explicit cache flush appears here, so it relies on usage/context not requiring instruction-cache invalidation for handled relocations.

## Test Signals
Boot relocated PPC64 kernels at varied bases, inspect `.rela.dyn` for only supported relocations, run secure guest relocation paths, and validate symbols requiring `R_PPC64_UADDR64`.
