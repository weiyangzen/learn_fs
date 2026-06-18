<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/Makefile -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/Makefile

### Purpose
This Makefile builds the LoongArch vDSO shared object, embeds it into the kernel, and generates symbol-offset headers.

### Important APIs, Types, And Functions
It defines `obj-vdso-y`, optional `vgettimeofday.o`, `ccflags-vdso`, `cflags-vdso`, `aflags-vdso`, linker flags, `gen-vdsosym`, targets for `vdso.lds`, `vdso.so.dbg`, `vdso.so`, and final `vdso.o`.

### Control Flow
Kbuild compiles vDSO objects with restricted C/ASM flags and `-D__VDSO__`, links `vdso.so.dbg` with `vdso.lds`, runs generic vDSO checks, strips to `vdso.so`, generates `include/generated/vdso-offsets.h` from `NM` plus `gen_vdso_offsets.sh`, and builds `vdso.o` that incbins the shared object.

### State, Persistence, And Dependencies
Build outputs are generated vDSO ELF files and offset headers. Dependencies include generic `lib/vdso/Makefile.include`, compiler support flags, `NM`, `OBJCOPY`, `CONFIG_GENERIC_GETTIMEOFDAY`, and generated C-vDSO include selections.

### Integration Points
`vdso.S` embeds the generated `vdso.so`; kernel ELF/vDSO setup uses generated offsets to expose vDSO entry points to userspace.

### Risks
Compiler flags must avoid kernel instrumentation and unsupported ABI options. Linker script/version exports must match actual objects. Offset generation relies on `VDSO_*` symbols in `vdso.lds.S`.

### Test Signals
Cross-build 32/64-bit LoongArch vDSO, run vDSO check, inspect exported symbols, and run userspace gettime/getcpu/getrandom/sigreturn tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/Makefile -->
