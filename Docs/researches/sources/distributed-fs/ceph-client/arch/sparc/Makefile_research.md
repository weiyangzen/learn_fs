<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/Makefile

## Purpose
This architecture Makefile sets SPARC build flags, default defconfigs, linked libraries, boot targets, install hooks, generated headers, vDSO installation, packaged image path, and help text.

## Important APIs, Types, and Functions
It selects `sparc64_defconfig` or `sparc32_defconfig`, sets `CHECKFLAGS`, `KBUILD_LDFLAGS`, `BITS`, `UTS_MACHINE`, `KBUILD_CFLAGS`, and `KBUILD_AFLAGS`, and defines targets `image`, `zImage`, `uImage`, `tftpboot.img`, `vmlinux.aout`, `install`, and `archheaders`. It also defines `KBUILD_IMAGE := arch/sparc/boot/zImage`.

## Control Flow
Before configuration it keys off `ARCH`; after configuration it branches on `CONFIG_SPARC32`. SPARC32 builds use 32-bit v8, no-FPU, and assembler v8 flags. SPARC64 builds use 64-bit UltraSPARC, medlow code model, fixed global registers, undeclared-reg handling, optional mcount profiling, and UltraSPARC3 tuning when available. Boot targets delegate to `arch/sparc/boot`.

## State and Persistence Behavior
No runtime state exists. The file controls compiler/linker state and generated boot artifacts.

## Dependencies and Integration Points
It depends on Kbuild infrastructure, compiler option probing, `arch/sparc/prom`, `arch/sparc/lib`, optional power/video drivers, boot make rules, syscall header generation, and vDSO debug objects.

## Risks
SPARC ABI depends heavily on fixed global registers, no-FPU flags, linker emulation, and bitness. Wrong flags can produce unbootable kernels or corrupt register conventions. Boot target delegation assumes `vmlinux` is already linked.

## Test Signals
Build SPARC32 and SPARC64 defconfigs, inspect compiler/linker command lines, build each advertised image target, and run `make ARCH=sparc archheaders` plus vDSO install on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Makefile -->
