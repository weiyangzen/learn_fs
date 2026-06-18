# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/include/arch/elf.h

Purpose: x86 generic relocation aliases for objtool metadata and instruction analysis.

Important APIs/types/functions: maps `R_NONE`, `R_ABS64`, `R_ABS32`, `R_DATA32`, `R_DATA64`, `R_TEXT32`, and `R_TEXT64` to x86-64 relocation types.

Control flow: none.

State and persistence behavior: controls relocation types for generated objtool sections and architecture-specific relocation classification.

Dependencies and integration points: used by x86 decoder, shared ELF helpers, and metadata writers in `check.c`/ORC code.

Risks: objtool mostly targets x86-64 here; using these aliases with 32-bit objects requires care. Incorrect aliasing can break linker relocation application or runtime metadata interpretation.

Test signals: generated `.orc_unwind_ip`, call-site, retpoline, return, static-call, and mcount sections should contain expected x86 relocation types.
