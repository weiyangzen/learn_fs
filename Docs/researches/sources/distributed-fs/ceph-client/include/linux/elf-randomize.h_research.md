# sources/distributed-fs/ceph-client/include/linux/elf-randomize.h

Purpose: abstracts architecture support for ELF mmap and brk randomization.

Important APIs/types/functions: `arch_mmap_rnd()`, `arch_randomize_brk()`, and `compat_brk_randomized` feature macro.

Control flow: ELF binary loading asks the arch hooks for random offsets. If `CONFIG_ARCH_HAS_ELF_RANDOMIZE` is absent, mmap randomization returns zero and `arch_randomize_brk(mm)` defaults to `mm->brk` unless overridden.

State/persistence: no persistent state; randomization affects per-process virtual memory layout during exec.

Dependencies/integration: process `mm_struct`, ELF binfmt, ASLR configuration, and arch-specific overrides.

Risks/test signals: risks are silently disabling ASLR on unsupported architectures, compatibility brk behavior changes, and arch macro conflicts. Test PIE and non-PIE exec layouts, `CONFIG_COMPAT_BRK`, `randomize_va_space`, and architecture-specific brk alignment/range behavior.
