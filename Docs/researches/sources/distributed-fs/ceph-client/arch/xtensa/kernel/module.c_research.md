<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/module.c

Purpose: applies Xtensa ELF relocations for loadable modules. Important functions are `decode_calln_opcode`, `decode_l32r_opcode`, and `apply_relocate_add`.

Control flow iterates relocation entries, computes symbol plus addend, and handles no-op/diff/asm-expand relocations, absolute `R_XTENSA_32`/PLT relocations, and `R_XTENSA_SLOT0_OP` for calln and L32R instruction fields with endian-specific byte patching and range validation. FLIX and ALT slot relocations, unknown relocations, and out-of-range operands fail with `-ENOEXEC`. Persistent state is patched module text/data in memory. Dependencies include ELF relocation constants, module loader, endianness, and Xtensa instruction encoding. Integration points are kernel module loading, vermagic, exported symbols, and instruction literal/call range constraints. Risks include silently ignoring unexpected SLOT0 opcodes due to assembler relaxation assumptions, range failures for far calls/literals, unaligned patch writes, and endian bugs. Test signals include loading modules with calls/literals, relocation failure tests, big/little endian builds, and modpost/objdump verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/module.c -->
