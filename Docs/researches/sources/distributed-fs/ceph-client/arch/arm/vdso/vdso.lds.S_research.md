## sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.lds.S

### Purpose
ARM vDSO linker script defining ELF format, sections, program headers, discarded data, and the public `LINUX_2.6` symbol version.

### Important APIs, Types, And Functions
Exports versioned symbols `__vdso_clock_gettime`, `__vdso_gettimeofday`, `__vdso_clock_getres`, `__vdso_clock_gettime64`, and `__vdso_clock_getres_time64`. It also expands `VDSO_VVAR_SYMS`.

### Control Flow
The linker lays out headers, dynamic symbol sections, notes, unwind metadata, dynamic data, rodata, executable text, GOT/relocation sections, and discards writable/bss sections. Program headers force one read-execute PT_LOAD plus PT_DYNAMIC, PT_NOTE, and EH frame headers.

### State, Persistence, And Dependencies
State is ELF layout metadata. Dependencies include `asm/vdso.h`, `vdso/datapage.h`, ARM ELF output formats, and vDSO object section names.

### Integration Points
Controls the ABI exposed to user loaders and libc. The exported version block is the contract by which user programs resolve vDSO functions.

### Risks
Writable sections are discarded intentionally; any vDSO C change needing writable storage will fail or mislink. Wrong program headers can make the image unmappable or fail generic vDSO checks.

### Test Signals
Run `readelf -l -S --version-info` on `vdso.so.dbg`, verify one PT_LOAD and expected global symbols, and run clock/gettimeofday ABI tests.
