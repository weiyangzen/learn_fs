<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/Makefile

### Purpose
This Makefile builds the 32-bit PA-RISC vDSO shared object, wrapper, and generated symbol-offset header.

### Important APIs, Types, And Functions
It defines `obj-vdso32`, `obj-cvdso32`, `VDSO_CFLAGS_REMOVE`, 32-bit compiler/linker flags, `VDSO_LIBGCC`, wrapper dependency on `vdso32.so`, and `include/generated/vdso32-offsets.h`.

### Control Flow
Kbuild assembles note/sigtramp/restart files, compiles `vdso32_generic.c` with VDSO-safe flags, links `vdso32.so` through `CROSS32CC` and `vdso32.lds`, builds `vdso32_wrapper.o` that incbins the shared object, and extracts `__kernel_*` offsets via `gen_vdso_offsets.sh`.

### State, Persistence, And Dependencies
Generated artifacts persist in the build tree. Dependencies include `lib/vdso/Makefile.include`, a working 32-bit cross compiler, libgcc, linker script, and Kbuild generated offsets.

### Integration Points
The wrapper contributes `vdso32_start/end` for `vdso.c`, and generated offsets feed signal code macros.

### Risks
Toolchain flags must avoid instrumentation and unsupported call models. Missing `CROSS32CC` breaks compat VDSO builds. Offset extraction only captures matching `__kernel_` symbols.

### Test Signals
Build with compat enabled, inspect exported symbol versions, verify offsets header, run VDSO signal/restart paths, and ensure no sanitizer/ftrace instrumentation appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/Makefile -->
