# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/elf.h

This header defines Alpha ELF ABI constants for the kernel. It lists Alpha relocation types, symbol `st_other` values, section flags, e_flags, register set sizes/types, executable page size, ET_DYN base, architecture checks, platform initialization, core-dump register copy hooks, hardware capability reporting, platform string selection, and auxiliary vector cache-shape entries.

Important APIs/macros are `elf_check_arch`, `ELF_CLASS/DATA/ARCH`, `ELF_EXEC_PAGESIZE`, `ELF_ET_DYN_BASE`, `ELF_PLAT_INIT`, `ELF_CORE_COPY_REGS`, `ELF_CORE_COPY_TASK_REGS`, `ELF_HWCAP`, `ELF_PLATFORM`, and `ARCH_DLINFO`. It depends on Alpha special instructions `amask` and `implver`, current thread info, and external cache-shape variables.

State is process exec/core-dump metadata and auxv entries. Risks are ABI-visible: relocation constants, rejecting `EF_ALPHA_32BIT`, register ordering for core files, and platform string/hwcap values consumed by dynamic loaders. Test signals are ELF exec, core dumps, dynamic loader behavior, auxv inspection, and binfmt_elf build coverage.
