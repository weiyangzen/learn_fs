<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/Makefile

### Purpose
This Makefile builds the 64-bit PA-RISC vDSO shared object, wrapper, and generated symbol-offset header.

### Important APIs, Types, And Functions
It defines `obj-vdso64`, `obj-cvdso64`, instrumentation-disabling flags, `VDSO_LIBGCC` from `$(CC)`, wrapper dependency, linker/assembler/compiler commands, and `include/generated/vdso64-offsets.h`.

### Control Flow
Kbuild assembles note/sigtramp/restart objects, compiles `vdso64_generic.c`, links `vdso64.so` with `vdso64.lds`, builds the incbin wrapper, and extracts sorted offsets for `__kernel_*` symbols.

### State, Persistence, And Dependencies
Generated artifacts persist in the build tree. Dependencies include the native 64-bit compiler, linker script, `lib/vdso/Makefile.include`, and `gen_vdso_offsets.sh`.

### Integration Points
The wrapper supplies `vdso64_start/end` to `vdso.c`; generated offsets support native signal/restart trampoline lookup.

### Risks
Instrumentation must stay disabled for vDSO code. `CPPFLAGS_vdso64.lds` undefines `$(ARCH)`, so preprocessing assumptions matter. Offset generation depends on symbol naming.

### Test Signals
Native 64-bit builds should verify `vdso64.so`, offsets header contents, exported symbol versions, and absence of ftrace/sanitizer instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/Makefile -->
