# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/orc.c

Purpose: converts generic CFI states into LoongArch ORC unwind entries, writes ORC entries plus instruction-pointer relocations, and prints ORC dumps.

Important APIs/types/functions: `init_orc_entry()` maps `struct cfi_state` to `struct orc_entry`; `write_orc_entry()` stores entries and creates text relocations with `elf_init_reloc_text_sym()`; `orc_print_dump()` formats decoded entries.

Control flow: `init_orc_entry()` handles null CFI and undefined/end-of-stack hints early, then maps supported unwind hint types, CFA base (`CFI_SP`/`CFI_FP`), FP rule, RA rule, and signal flag. Unknown hint or base registers produce objtool errors.

State and persistence behavior: `write_orc_entry()` modifies the generated ORC section buffer and the paired IP relocation section. This persistent metadata is later written by `elf_write()`.

Dependencies and integration points: consumes LoongArch CFI register constants, `asm/orc_types.h`, and generic ORC creation. It must agree with kernel LoongArch ORC unwinder field semantics.

Risks: only SP and FP CFA bases are accepted, and only undefined/CFA/FP rules for FP and RA are serialized. New unwind forms need explicit mapping. Unlike x86 ORC writing, offsets are not byte-swapped here, so endian assumptions should be validated.

Test signals: `objtool --orc` followed by `--dump=orc` on LoongArch objects should show correct SP/FP/RA offsets for prologue, body, epilogue, undefined, and end-of-stack hints.
