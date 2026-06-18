<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.lds.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.lds.S

### Purpose
`vdso.lds.S` is the linker script and symbol version map for the LoongArch vDSO.

### Important APIs, Types, And Functions
It sets `OUTPUT_ARCH(loongarch)`, emits `VDSO_VVAR_SYMS`, defines ELF sections and PHDRs, exports version `LINUX_5.10`, and defines `VDSO_sigreturn = __vdso_rt_sigreturn`.

### Control Flow
At link time, sections are laid out after ELF headers; hash, dynamic symbol, note, text, unwind, dynamic, and rodata sections are assigned to read/execute or read-only program headers. Data/bss/GNU-stack attributes are discarded. The version block exposes selected vDSO symbols and hides all others.

### State, Persistence, And Dependencies
Output is the linked vDSO ELF layout and symbol table. Dependencies include generated asm offsets, vDSO datapage definitions, and config-gated gettimeofday symbols.

### Integration Points
The Makefile uses this script to link `vdso.so.dbg`; `gen_vdso_offsets.sh` consumes `VDSO_*` symbols from the resulting ELF.

### Risks
Incorrect exported symbol list breaks userspace ABI. Discarding or PHDR mistakes can make the ELF invalid or writable. Version-name changes affect dynamic linker expectations.

### Test Signals
Run vDSO link checks, `readelf -l -s -V`, userspace calls to exported functions, and ABI comparison against expected LoongArch vDSO symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.lds.S -->
