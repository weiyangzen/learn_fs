# sources/distributed-fs/ceph-client/tools/objtool/orc_gen.c

Purpose: Declares or implements ORC unwind table creation and dumping for objtool-generated stack unwind metadata.

Important APIs/types/functions: `orc_list_add`, `orc_create`, `orc_list_entry`.

Control flow: `orc_gen.c` walks analyzed text instructions, deduplicates ORC entries, handles alternative-group byte CFI, appends section terminators, creates `.orc_unwind`/`.orc_unwind_ip` sections, and writes relocatable IP entries. `orc_dump.c` reads those sections and prints resolved symbol/section offsets or absolute IP deltas.

State and persistence behavior: Builds transient ORC list entries, then persists generated unwind sections in the target ELF.

Dependencies and integration points: Depends on checker CFI state, `asm/orc_types.h`, objtool ELF section creation, relocation lookup, and libelf for dumping.

Risks: Alternative flattening, deduplication, and terminator entries must align with unwinder expectations; malformed ORC section sizes or missing rela entries break dumps.

Test signals: Objtool ORC generation on normal text, alternatives, empty text, duplicate states, and `orc_dump` on relocatable and non-relocatable files.

Source coverage: researched from the complete local file (151 lines, 3496 bytes).
