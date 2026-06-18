# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/elf.h

Purpose: defines the Nios II user ABI surface for `elf.h`, exported to userspace through headers_install.

Important APIs/types/functions: typedefs: `elf_greg_t`, `elf_fpregset_t`; macros: `_UAPI_ASM_NIOS2_ELF_H`, `R_NIOS2_NONE`,
`R_NIOS2_S16`, `R_NIOS2_U16`, `R_NIOS2_PCREL16`, `R_NIOS2_CALL26`, `R_NIOS2_IMM5`,
`R_NIOS2_CACHE_OPX`, `R_NIOS2_IMM6`, `R_NIOS2_IMM8`, `R_NIOS2_HI16`, `R_NIOS2_LO16`, and 16 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file freezes user-visible ABI constants and structures; changes persist through compiled
userspace, ptrace tools, signal frame layouts, ELF loaders, and syscall numbering.

Dependencies and integration points: Dependencies include `linux/ptrace.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks are ABI breaks: changed constants, register order, signal context layout, byte order,
relocation numbers, or syscall numbering can break existing userspace and tooling.

Test signals: Test signals are headers_install, libc/toolchain builds, ptrace/core-dump inspection, signal ABI
tests, ELF relocation/module loader tests, and syscall table generation checks.
