# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso32.lds.S

## Purpose
Defines the linker script for the 32-bit PowerPC vDSO ELF shared object, including segment layout, exported symbols, feature-fixup sections, and trampoline offset symbols.

## Important APIs, Types, And Functions
Sets `OUTPUT_FORMAT` to `elf32-powerpc` or `elf32-powerpcle`, `OUTPUT_ARCH(powerpc:common)`, emits `VDSO_VVAR_SYMS`, defines fixup range symbols such as `VDSO_ftr_fixup_start/end`, and exports the vDSO versioned symbols. It defines `VDSO_sigtramp32` and `VDSO_sigtramp_rt32`.

## Control Flow
The linker lays out ELF headers, hash/dynamic symbol tables, notes, text, feature fixups, rodata, unwind data, dynamic sections, GOT/PLT, relocations, debug details, and discards writable/BSS/unsupported sections. PHDRS force a single read-execute PT_LOAD plus read-only dynamic, note, and EH frame headers.

## State And Persistence
Produces the static 32-bit vDSO image that is embedded into the kernel and mapped into userspace. No runtime state is defined here.

## Dependencies And Integration Points
Depends on generic linker macros, vDSO data-page symbols, build objects listed in the vDSO Makefile, and `gen_vdso32_offsets.sh` consuming `VDSO_*` symbols.

## Risks And Edge Cases
Exported symbols are user ABI. Section discard rules must prevent writable data in the vDSO. Fixup section boundaries must align with `vdso_fixup_features`. Program headers must remain compatible with dynamic loaders and vDSO validators.

## Test Signals
Build and inspect `vdso32.so.dbg` with `readelf -h -l -s -S`, validate one PT_LOAD with RX flags, confirm exported symbol versioning, generated offsets, and absence of writable alloc sections.
