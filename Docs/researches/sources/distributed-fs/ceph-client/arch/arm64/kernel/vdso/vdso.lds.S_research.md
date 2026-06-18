## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vdso.lds.S

### Purpose
`vdso.lds.S` is the linker script for the native AArch64 VDSO ELF image, defining section layout, program headers, discarded sections, exported symbol versions, and VVAR symbols.

### Important APIs, Types, And Functions
It emits `OUTPUT_FORMAT/OUTPUT_ARCH`, `VDSO_VVAR_SYMS`, text/dynamic/note PHDRs, exported `LINUX_2.6.39` symbols, and `VDSO_sigtramp = __kernel_rt_sigreturn`.

### Control Flow
The linker places ELF headers, hash/dynamic symbol tables, notes, executable text, alternatives, dynamic relocation metadata, rodata/GOT/PLT-like sections, debug details, and discards data/BSS/eh_frame. Program headers produce one read-exec PT_LOAD plus read-only PT_DYNAMIC and PT_NOTE.

### State, Persistence, And Dependencies
The output is the immutable VDSO ELF layout. No runtime state is created directly by the script.

### Integration Points
Used by `vdso/Makefile`, `vdso.c`, generic VDSO data-page macros, and userspace dynamic loader symbol lookup.

### Risks
Exported symbol names and version nodes are ABI. Accidentally retaining writable data, BSS, unsupported notes, or extra load segments breaks VDSO safety or loader assumptions. Text fill and BTI/property handling must remain compatible.

### Test Signals
Run `readelf -lSWsV`, generic VDSO checks, symbol-version tests, and runtime calls to `clock_gettime`, `gettimeofday`, `clock_getres`, `getrandom`, and signal return.
