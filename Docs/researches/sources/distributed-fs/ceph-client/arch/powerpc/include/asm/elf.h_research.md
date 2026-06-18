## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/elf.h

Purpose: defines PowerPC ELF loading, core dump, aux vector, personality, HWCAP, vDSO, and relocation contracts.

Important APIs/types/functions: `elf_check_arch()`, `compat_elf_check_arch()`, `ELF_ET_DYN_BASE`, `ELF_CORE_EFLAGS`, `PPC_ELF_CORE_COPY_REGS`, `ppc_elf_core_copy_regs()`, `ELF_HWCAP`, `ELF_HWCAP2`, `ELF_PLATFORM`, `ELF_BASE_PLATFORM`, `SET_PERSONALITY`, `elf_read_implies_exec()`, `ARCH_DLINFO`, `COMPAT_ARCH_DLINFO`, `arch_setup_additional_pages()`, `relocate()`, and `struct func_desc`.

Control flow: ELF exec validates machine type, sets ABI/thread flags, chooses PIE base, emits aux vector cache/vDSO/min-sigstack entries, and copies registers for core dumps. PPC64 initializes r2 for ELFv1 TOC semantics and distinguishes ELFv2 via e_flags.

State and persistence: reads `cur_cpu_spec`, `current->mm->context.vdso`, task personality/thread flags, cache geometry globals, and base platform string. Core dump register data persists in ELF notes.

Dependencies and integration: depends on UAPI ELF definitions, page/task helpers, vDSO setup, signal frame sizing, CPU feature tables, and cache discovery.

Risks and test signals: ABI personality and aux vector mistakes break dynamic loaders and 32-bit compat. Core register copying must truncate correctly for 32-bit tasks. Test signals include native and compat ELF exec, PIE ASLR, glibc auxv checks, core dump inspection, ELFv1/ELFv2 binaries, vDSO mapping, and 32-bit toolchain executable-stack behavior.
