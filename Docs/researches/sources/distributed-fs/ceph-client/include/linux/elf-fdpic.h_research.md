# sources/distributed-fs/ceph-client/include/linux/elf-fdpic.h

Purpose: FDPIC ELF loader state for NOMMU/MMU architectures where executable segments can be independently placed and described by a load map.

Important APIs/types/functions: ELF class aliases for `elf_fdpic_loadseg`, `elf_fdpic_loadmap`, `ELF_FDPIC_LOADMAP_VERSION`, `struct elf_fdpic_params`, arrangement flags such as `ELF_FDPIC_FLAG_HONOURVADDR`, `CONSTDISP`, `CONTIGUOUS`, stack flags, and `elf_fdpic_arch_lay_out_mm()` under MMU.

Control flow: binfmt FDPIC parses ELF headers/program headers into `elf_fdpic_params`, computes load maps for executable and interpreter, maps headers/segments/stack/dynamic areas, and optionally lets architecture layout code select addresses.

State/persistence: no persistent state; per-exec transient state holds copied headers, loadmap pointers, mapped addresses, flags, and stack requirements.

Dependencies/integration: `uapi/linux/elf-fdpic.h`, generic ELF types, binfmt loader, architecture ELF class and optional MMU layout policy.

Risks/test signals: risks are wrong ELF32/ELF64 aliases, loadmap size/version mismatch, honoring incompatible virtual addresses, stack exec/noexec policy, and interpreter/executable address collisions. Test FDPIC binaries with and without interpreters, varied PT_LOAD arrangements, PT_GNU_STACK, and MMU/NOMMU configurations.
