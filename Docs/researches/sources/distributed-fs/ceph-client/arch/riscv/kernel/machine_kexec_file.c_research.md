# sources/distributed-fs/ceph-client/arch/riscv/kernel/machine_kexec_file.c

Purpose: Supplies RISC-V `kexec_file_load` support for crash extras, purgatory relocations, and DTB/initrd/cmdline segments.

Important APIs/types/functions: Defines `kexec_file_loaders[]`, `arch_kimage_file_post_load_cleanup()`, `prepare_elf_headers()`, `setup_kdump_cmdline()`, `arch_kexec_apply_relocations_add()`, and `load_extra_segments()`.

Control flow: For crash kernels it counts RAM ranges, builds ELF core headers, rewrites crashkernel command-line arguments, applies purgatory relocations for RISC-V relocation types, and places extra segments. Relocation handling encodes branch, JAL, PC-relative high/low, compressed branch/jump, ADD/SUB, and 64-bit relocations while ignoring relax/alignment where appropriate.

State and persistence: Populates `struct kimage` with elfcorehdr, FDT, initrd, command line, and purgatory relocation results. Temporary crash memory arrays and FDT buffers are freed during cleanup.

Dependencies and integration points: Depends on kexec file core, libfdt, crash memory iteration, RISC-V relocation encoders, ELF constants, and both ELF/raw image loaders.

Risks and test signals: Purgatory relocation bugs cause silent boot failure; FDT/cmdline edits affect crash dump usability. Test signed `kexec_file_load`, crash kernel with elfcorehdr, relocation type coverage, FDT validation, and command-line crashkernel stripping.
