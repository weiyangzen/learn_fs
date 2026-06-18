<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/elf.h

Purpose: Defines RISC-V ELF UAPI constants, relocation flags, register-set notes, and HWCAP exposure.

Important APIs/types/functions: Defines `ELF_NGREG`, `ELF_NFPREG`, RISC-V relocation/flag constants, `R_RISCV_*` values, and arch ELF metadata consumed by tools.

Control flow: No kernel runtime flow in the header; ELF loader, core dump, ptrace, and toolchains consume constants.

State and persistence: ELF files/core notes persist these ABI values.

Dependencies and integration points: Used by binutils, glibc, loaders, ptrace/core dump, and module/toolchain flows.

Risks: ABI number changes break binaries, debuggers, and core files.

Test signals: Toolchain relocation tests, core dump regset tests, headers_install, and dynamic loader smoke tests.

Source read size: 101 lines, 2916 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/elf.h -->
