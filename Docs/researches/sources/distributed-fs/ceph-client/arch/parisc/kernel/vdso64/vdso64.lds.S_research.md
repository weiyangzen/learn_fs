<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64.lds.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64.lds.S

### Purpose
`vdso64.lds.S` defines the ELF64 PA-RISC vDSO link layout, program headers, discarded sections, and symbol version exports.

### Important APIs, Types, And Functions
It sets `OUTPUT_FORMAT("elf64-hppa-linux")`, `OUTPUT_ARCH(hppa:hppa2.0w)`, VDSO base placement, PT_LOAD/PT_NOTE/PT_DYNAMIC/PT_GNU_EH_FRAME headers, and exports sigtramp, restart, gettimeofday, and clock_gettime symbols.

### Control Flow
The linker places dynamic symbol/hash sections, note, text, rodata, unwind frames, dynamic/PLT/GOT, debug sections, and discards writable data/BSS/stack notes.

### State, Persistence, And Dependencies
The resulting layout persists in `vdso64.so`. Dependencies include `asm/vdso.h`, vDSO source symbol names, and the 64-bit PA-RISC ABI.

### Integration Points
Used by the vDSO64 Makefile and user dynamic linking of the `[vdso]` image.

### Risks
Writable sections must remain discarded. Exported names with `64` suffixes must match offset generation and kernel lookup macros.

### Test Signals
Inspect program headers, symbol versions, exported symbols, and absence of writable LOAD data with `readelf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64.lds.S -->
