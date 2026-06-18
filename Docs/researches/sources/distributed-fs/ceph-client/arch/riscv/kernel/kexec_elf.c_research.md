# sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_elf.c

Purpose: Loads ELF-format RISC-V kernels for the `kexec_file_load` syscall.

Important APIs/types/functions: Defines `riscv_kexec_elf_load()`, `elf_find_pbase()`, `elf_kexec_load()`, and `elf_kexec_ops`.

Control flow: The loader parses ELF headers, finds the lowest physical and virtual load addresses, locates a suitably aligned memory hole, computes the new entry address, adds each PT_LOAD segment to the kexec image, and appends DTB/initrd/cmdline extra segments.

State and persistence: Mutates `struct kimage` segment list and `image->start`. ELF info is transient and freed after loading.

Dependencies and integration points: Depends on generic kexec ELF parsing, memblock/kexec buffer placement, RISC-V boot alignment, and `load_extra_segments()` in machine kexec file code.

Risks and test signals: Wrong base translation or alignment makes the second kernel unbootable. Test ELF vmlinux kexec, large segment layouts, initrd/cmdline handling, crash kernels, and invalid ELF rejection.
