# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/special.c

Purpose: LoongArch special-section support for alternatives and switch/jump-table discovery.

Important APIs/types/functions: `arch_support_alt_relocation()` currently rejects PC-relative relocations in alternatives. `arch_find_switch_table()` locates switch tables via `.discard.tablejump_annotate` or the C jump table section. Helpers include `get_rodata_table_size_by_table_annotate()`, `find_reloc_by_table_annotate()`, and `find_reloc_of_rodata_c_jump_table()`. `arch_cpu_feature_name()` returns no names.

Control flow: annotated jump table relocations are scanned in pairs, grouped by text section, sorted by rodata offset to infer table size, then resolved to the first rodata relocation. C jump tables are found through relocations into `C_JUMP_TABLE_SECTION`.

State and persistence behavior: no ELF writes. It returns relocation pointers and table sizes used by shared `check.c` to mark jump-table heads and add alternative branch destinations.

Dependencies and integration points: depends on generic special parsing, relocation lookup, section rodata marking, and the common jump-table walker in `check.c`.

Risks: manual list allocation is not freed and `list_del_init(&table_list)` is suspicious for a list head; as a short-lived objtool process the leak is minor, but malformed annotations could confuse table sizing. The code increments `reloc` inside `for_each_reloc`, assuming paired entries. No CPU feature names means disassembly of alternatives shows feature numbers only.

Test signals: LoongArch switch statements and annotated C jump tables should not report "can't find switch jump table"; alternative sections with relocations should be rejected when unsupported.
