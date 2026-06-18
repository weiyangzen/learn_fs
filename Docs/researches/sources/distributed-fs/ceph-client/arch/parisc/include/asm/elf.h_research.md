# sources/distributed-fs/ceph-client/arch/parisc/include/asm/elf.h

Purpose: defines PA-RISC ELF ABI constants, relocation behavior, register sets, core-dump layout, auxiliary vector handling, and personality selection.

Important APIs/types/functions: exports `ELF_ARCH`, `ELF_CLASS`, `ELF_DATA`, `ELF_PLAT_INIT`, `ELF_HWCAP`, `elf_check_arch`, `elf_greg_t`, `elf_gregset_t`, `ELF_NGREG`, `ELF_CORE_COPY_REGS`, and compat-related definitions.

Control flow: binfmt_elf validates PA-RISC binaries, initializes registers and stack ABI state, emits core dumps, and selects 32-bit or 64-bit behavior from ELF class/personality.

State and persistence: defines user-visible process and core-file ABI state. Dependencies and integration: works with `processor.h`, `ptrace.h`, uapi ELF definitions, and signal/syscall paths.

Risks and test signals: ABI drift breaks program startup, dynamic linking, or core analysis. Test with native and compat ELF execution, core dumps, auxv inspection, and ptrace register validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
