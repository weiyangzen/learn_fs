# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/include/arch/elf.h

Purpose: maps PowerPC ELF relocation types to objtool's generic relocation aliases.

Important APIs/types/functions: defines `R_NONE`, `R_ABS64`, `R_ABS32`, `R_DATA32`, `R_DATA64`, `R_TEXT32`, and `R_TEXT64` using PPC/PPC64 relocation constants.

Control flow: none.

State and persistence behavior: determines relocation types in generated metadata sections if those features are used.

Dependencies and integration points: used by shared ELF writers and PowerPC decoder relocation sizing.

Risks: mixed PPC32/PPC64 relocation aliases must match object class and linker expectations. Some aliases use relative relocations, so consumers must interpret them consistently.

Test signals: generated metadata relocations in PPC objects should pass `relocs_check.sh` and linker validation.
