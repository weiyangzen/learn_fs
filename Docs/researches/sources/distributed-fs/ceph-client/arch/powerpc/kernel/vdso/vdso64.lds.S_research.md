# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso64.lds.S

## Purpose
Defines the linker script for the 64-bit PowerPC vDSO ELF shared object, including exported ABI symbols, feature-fixup sections, read-only segment layout, and signal trampoline offset symbol.

## Important APIs, Types, And Functions
Sets `OUTPUT_FORMAT` to `elf64-powerpc` or `elf64-powerpcle`, `OUTPUT_ARCH(powerpc:common64)`, declares fixup range symbols, exports vDSO functions under `VDSO_VERSION_STRING`, and defines `VDSO_sigtramp_rt64 = __kernel_start_sigtramp_rt64`.

## Control Flow
The linker places ELF metadata, notes, text including `.sfpr`, feature/MMU/lwsync/firmware fixup sections, rodata, dynamic data, unwind sections, relocations, GOT/TOC, debug details, and discards writable data, BSS, OPD, PLT/glink, and unsupported metadata. PHDRS force read-execute load and read-only dynamic/note/EH frame segments.

## State And Persistence
Produces the static 64-bit vDSO image embedded in the kernel and mapped into each 64-bit process.

## Dependencies And Integration Points
Depends on the vDSO Makefile, generic linker macros, `vdso.c` feature fixup ranges, 64-bit ABI TOC/GOT needs, and the offset generator for `VDSO_*` symbols.

## Risks And Edge Cases
The symbol export list and trampoline symbol are ABI-sensitive. Discarding OPD/PLT/glink must match the selected ABI and compiler output. Relocation and TOC placement must remain valid for the freestanding vDSO.

## Test Signals
Use `readelf` on `vdso64.so.dbg` to verify symbol versions, program headers, dynamic section, absence of writable alloc sections, and expected `VDSO_sigtramp_rt64` offset generation.
