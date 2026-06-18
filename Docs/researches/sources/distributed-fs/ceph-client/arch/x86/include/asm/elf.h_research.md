
# sources/distributed-fs/ceph-client/arch/x86/include/asm/elf.h

Purpose: x86 ELF ABI constants, register dump layout, process personality setup, vDSO aux vector setup, and mmap layout hooks.

Important APIs and control flow: defines ELF register sets, relocation constants for i386/x86-64, ELF class/data/arch, architecture checks, platform init macros, and core-register copy macros for 32-bit and 64-bit. Compat paths validate IA32/x32 binaries, start compat threads, and set IA32 personality. `ELF_ET_DYN_BASE`, `ELF_HWCAP`, `ELF_HWCAP2`, `elf_read_implies_exec()`, `ARCH_DLINFO*`, `mmap_is_ia32()`, stack randomization masks, and vDSO setup declarations integrate exec with mm and auxv.

State, dependencies, and risks: state is current thread registers, fs/gs bases, personality flags, mm vDSO context, CPU capabilities, and VA alignment settings. Dependencies include ptrace/user ABI, vdso, fsgsbase, ia32/x32 support, and binfmt_elf. Risks include ABI-incompatible register ordering, wrong exec-stack policy for compat processes, vDSO auxv errors, and mmap base regressions. Test signals are ELF exec tests, core dump validation, compat/x32 tests, ASLR tests, and vDSO signal-return checks.
