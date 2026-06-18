# sources/distributed-fs/ceph-client/arch/parisc/include/asm/Kbuild

Purpose: declares PA-RISC architecture headers that should be generated or exported through Kbuild's UAPI/header-install machinery.

Important APIs/types/functions: the file contains Kbuild directives rather than C symbols. It names generic or generated header relationships for the `arch/parisc/include/asm` tree.

Control flow: during header generation and install, Kbuild reads these declarations to decide which asm headers are produced or forwarded to generic implementations.

State and persistence: no runtime state; persistent outputs are generated header files in build/install directories. Dependencies and integration: part of the kernel header build pipeline and consumed by userspace header installation.

Risks and test signals: missing or stale entries can break external builds or generated-offset inclusion. Test with `make headers_install`, allmodconfig compile coverage, and checks that `generated/asm-offsets.h` remains reachable.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
