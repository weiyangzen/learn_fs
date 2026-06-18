## sources/distributed-fs/ceph-client/arch/arm64/Makefile

### Purpose
Defines ARM64 architecture compiler, assembler, linker, Rust, image, vDSO, install, and help rules for the kernel build.

### Important APIs, Types, And Functions
Sets `LDFLAGS_vmlinux`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_RUSTFLAGS`, endian flags, branch protection flags, stack protector sysreg flags, KASAN shadow defines, `KBUILD_IMAGE`, `BOOT_TARGETS`, `archprepare`, `vdso_prepare`, `virtconfig`, and `archhelp`.

### Control Flow
The Makefile detects toolchain features, appends flags according to config, selects assembler architecture, sets endian and linker targets, defines image targets that recurse into `arch/arm64/boot`, generates tools during `archprepare`, and builds vDSO artifacts after `prepare0`.

### State, Persistence, And Dependencies
Build state is generated flags and artifacts. Dependencies include compiler/linker feature tests, `asm-offsets.h`, vDSO build directories, EFI libstub, Kconfig symbols, and compression/install scripts.

### Integration Points
This file is included by the global top-level Makefile and controls how every ARM64 object and final boot image is produced.

### Risks
Toolchain flag selection is fragile: wrong PAC/BTI, SCS, FPU, unwind, KASAN, endian, or relocation flags can break boot or ABI. vDSO generation depends on prepare ordering.

### Test Signals
Build with GCC and Clang/LLVM, LLD and GNU ld, little/big endian, relocatable/KASLR, PAC/BTI/SCS, KASAN modes, Rust enabled, EFI zboot, and compat vDSO.
