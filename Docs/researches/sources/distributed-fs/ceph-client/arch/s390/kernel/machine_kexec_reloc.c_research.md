# sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_reloc.c

Purpose: applies s390 ELF relocation records used while relocating kexec purgatory code.

Important API: `arch_kexec_do_relocs(int r_type, void *loc, unsigned long val, unsigned long addr)` supports direct 8/12/16/20/32/64 relocations, GOT/JMP slot absolute 64-bit writes, PC-relative 16/32/64 forms with optional halfword shifting, and `R_390_RELATIVE`.

Control flow and state: stateless switch over relocation type writes directly into the temporary purgatory buffer. Unsupported types return 1 so callers report an invalid relocation.

Dependencies and integration: called by `arch_kexec_apply_relocations_add()` in `machine_kexec_file.c`; relocation constants come from ELF/s390 ABI headers.

Risks and test signals: relocation truncation is not range-checked here, so callers and generated purgatory must only use supported safe forms. Test purgatory link changes, `R_390_PLT32DBL` remapping in caller, and byte layout of 12/20-bit split fields.
