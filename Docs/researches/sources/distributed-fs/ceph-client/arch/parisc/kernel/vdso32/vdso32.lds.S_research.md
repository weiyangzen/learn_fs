<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32.lds.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32.lds.S

### Purpose
`vdso32.lds.S` defines the ELF32 PA-RISC vDSO link layout, program headers, discarded sections, and exported symbol version set.

### Important APIs, Types, And Functions
It sets `OUTPUT_FORMAT("elf32-hppa-linux")`, `OUTPUT_ARCH(hppa)`, base address `VDSO_LBASE`, PT_LOAD/PT_NOTE/PT_DYNAMIC/PT_GNU_EH_FRAME program headers, and version exports for sigtramp, restart, gettimeofday, clock_gettime, and clock_gettime64.

### Control Flow
The linker places hash/dynamic symbol sections, note, text, rodata, unwind frames, dynamic/PLT/GOT, debug-only zero-address sections, and discards writable/bss/stack-note inputs.

### State, Persistence, And Dependencies
The linked shared object layout persists in `vdso32.so`. Dependencies include `asm/vdso.h`, page constants, Kbuild compile flags, and vDSO source symbol names.

### Integration Points
Used by the vDSO32 Makefile and consumed by the wrapper object and user dynamic linker.

### Risks
Export names include suffixed aliases expected by `VDSO32_SYMBOL()`/offset generation. Accidentally retaining writable data would violate vDSO mapping assumptions.

### Test Signals
Use `readelf -l -s -V` on `vdso32.so`, verify exported symbol versions and no writable load segment or bss/data payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32.lds.S -->
