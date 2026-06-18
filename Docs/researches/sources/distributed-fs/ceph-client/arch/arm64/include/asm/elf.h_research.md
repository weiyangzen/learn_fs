## sources/distributed-fs/ceph-client/arch/arm64/include/asm/elf.h

Purpose: defines arm64 ELF ABI, relocation constants, core register sets, aux vector entries, personality setup, compat ELF handling, and GNU property parsing.

Important APIs/types/functions: exports AArch64 relocation IDs, `ELF_CLASS/DATA/ARCH/PLATFORM`, `elf_check_arch`, `ELF_ET_DYN_BASE`, `ELF_NGREG`, `ELF_CORE_COPY_REGS`, `elf_gregset_t`, `elf_fpregset_t`, `ELF_PLAT_INIT`, `SET_PERSONALITY`, `ARCH_DLINFO`, stack randomization masks, compat ELF constants, `struct arch_elf_state`, `ARM64_ELF_BTI`, `arch_parse_elf_property`, and `arch_elf_adjust_prot`.

Control flow: exec setup validates ELF machine type, resets personality, emits vDSO/minsigstksz aux entries, parses BTI properties, and adjusts mmap protections when required.

State and persistence: affects process personality, thread flags, mm context/vDSO exposure, executable mapping protections, and core dump format.

Dependencies and integration: integrates binfmt_elf, signal ABI, ptrace/user register layout, HWCAP, compat mode, BTI, and vDSO.

Risks: ABI changes break loaders, core dumps, ASLR, BTI enforcement, or 32-bit compat exec. Test signals are ELF loader tests, auxv inspection, core dump/gdb tests, BTI property tests, ASLR checks, and compat userspace bootstraps.
