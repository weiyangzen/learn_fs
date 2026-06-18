<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/elf.h

Purpose: Defines PowerPC ELF relocation numbers, register-set types, core-dump register counts, ELF class/data selection, and vector register layouts.

Important APIs/types/functions: `R_PPC_*`, TLS relocations, `R_PPC64_*`, `ELF_N*` register counts, `elf_gregset_t32/64`, `elf_fpregset_t`, `elf_vrregset_t`, `ELF_ARCH`, `ELF_CLASS`, and `ELF_DATA`.

Control flow: Linkers/loaders use relocation numbers; kernel core dump and ptrace paths use register-set typedefs; userspace debuggers interpret note layouts from these ABI definitions.

State and persistence: No runtime state, but it fixes persistent ELF object and core-file ABI formats.

Dependencies and integration points: Depends on Linux types, PowerPC ptrace/cputable/auxvec headers, and `__vector128`. Integrated by binfmt_elf, core dumping, ptrace, GDB, loaders, and toolchains.

Risks: Relocation values and register layouts are immutable ABI. VMX/VSX layout must stay compatible with ptrace and signal contexts.

Test signals: Toolchain relocation tests, ELF loader smoke tests, core dump register-note validation, ptrace tests, and ppc32/ppc64 endian variants.

Source read size: 298 lines, 13415 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/elf.h -->
