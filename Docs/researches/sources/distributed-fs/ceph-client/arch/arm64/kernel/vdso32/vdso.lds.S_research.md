## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/vdso.lds.S

### Purpose
`vdso32/vdso.lds.S` is the linker script for the AArch32 compat VDSO image.

### Important APIs, Types, And Functions
It defines ELF32 ARM output format, VVAR symbols, section layout, text/dynamic/note PHDRs, and the `LINUX_2.6` symbol version exporting `__vdso_clock_gettime`, `__vdso_gettimeofday`, `__vdso_clock_getres`, `__vdso_clock_gettime64`, and `__vdso_clock_getres_time64`.

### Control Flow
The linker places hash/dynsym/dynstr/version sections, notes, dynamic metadata, rodata/GOT/PLT-like inputs, ARM/Thumb text and veneers, relocations, ARM unwind index, debug details, and attributes, while discarding writable data, BSS, and GNU stack notes. Program headers describe one read-exec load segment plus dynamic and note segments.

### State, Persistence, And Dependencies
The script creates static ELF layout only.

### Integration Points
Used by `vdso32/Makefile`, generic VDSO data-page macros, vdsomunge, and compat VDSO mapping in `vdso.c`.

### Risks
Exported symbols and versions are compat ABI. Incorrect relocation, ARM veneer, or unwind section handling can break 32-bit loaders and unwinders. Writable sections must not enter the runtime VDSO.

### Test Signals
Run `readelf -lSWsV`, generic VDSO checks, 32-bit time ABI tests, and linker orphan warning builds.
