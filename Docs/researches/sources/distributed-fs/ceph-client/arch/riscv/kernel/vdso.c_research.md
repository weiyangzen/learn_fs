<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso.c

Purpose: Maps the RISC-V vDSO and VVAR pages into new user address spaces and initializes native/compat vDSO metadata.

Important APIs/types/functions: Defines `struct __vdso_info`, `vdso_mremap()`, `__vdso_init()`, `vdso_init()`, `__setup_additional_pages()`, `compat_arch_setup_additional_pages()`, and `arch_setup_additional_pages()`.

Control flow: Boot init validates vDSO ELF images, records text/data page counts and offsets, and sets up special mappings. Exec-time setup maps VVAR then vDSO text at randomized addresses, records `mm->context.vdso`, and supports compat mapping when applicable.

State and persistence: Stores read-only vDSO metadata and per-mm vDSO base. VVAR/vDSO mappings persist in each process mm.

Dependencies and integration points: Depends on linker symbols from `vdso.S`/compat images, generic vDSO special mappings, signal code for `rt_sigreturn`, hwprobe vDSO data, and ELF exec.

Risks: Mapping order, offsets, and page permissions are ABI/security sensitive. Remap restrictions must prevent moving special mappings into invalid layouts.

Test signals: Process startup auxv/vDSO presence, `clock_gettime`, `getcpu`, `riscv_hwprobe`, `rt_sigreturn`, compat tasks, ASLR, and mremap rejection tests.

Source read size: 187 lines, 4344 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso.c -->
