## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32/Makefile

### Purpose
`vdso32/Makefile` builds the AArch32 compat VDSO using a 32-bit compiler/linker toolchain from the ARM64 tree.

### Important APIs, Types, And Functions
It defines `CC_COMPAT`, `LD_COMPAT`, `cc32-option`, VDSO CPP/C/assembly/linker flags, objects `note.o` and `vgettimeofday.o`, optional generated gettimeofday include flags, `vdso.so.raw`, `vdso32.so.dbg`, stripped `vdso.so`, and the borrowed ARM `vdsomunge` host tool.

### Control Flow
Kbuild selects a compat compiler target, builds freestanding 32-bit objects with ARM ABI, soft-float, endian, ARM/Thumb2 options, links a raw shared object with the compat linker script and VDSO checks, runs `vdsomunge`, then strips the final `vdso.so` embedded by `vdso32-wrap.S`.

### State, Persistence, And Dependencies
State is build artifacts and generated dependency files. There is no runtime state.

### Integration Points
It uses generic VDSO build checks, top-level include paths, ARM vDSO munge tooling, compat cross-compile variables, and `vdso.c` mapping support.

### Risks
A missing or incompatible 32-bit toolchain breaks compat VDSO builds. Global ARM64 flags cannot be reused blindly. Thumb2 unwinding limitations require frame-pointer handling choices. Linker orphan behavior and symbol versions are ABI-sensitive.

### Test Signals
Cross-build with GCC/Clang and BFD/LLD, little/big endian and Thumb2 options, inspect `readelf` output, and run 32-bit libc time calls on ARM64 compat kernels.
