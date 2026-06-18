# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/check.h

Purpose: Defines objtool instruction-analysis data structures shared by the checker, ORC generator, disassembler, tracing, and warning paths.

Important APIs/types/functions: `is_static_jump`, `is_dynamic_jump`, `is_jump`, `pv_ops_idx_off`, `_CHECK_H`, `INSN_CHUNK_BITS`, `INSN_CHUNK_SIZE`, `INSN_CHUNK_MAX`, `VISITED_BRANCH`, `VISITED_BRANCH_UACCESS`, `VISITED_BRANCH_MASK`, `VISITED_UNRET`.

Control flow: The checker populates `struct instruction` records, links alternatives/jump sources/call targets, tracks `struct insn_state` CFI and uaccess/noinstr flags, and exposes lookup/iteration helpers consumed by validation and ORC emission.

State and persistence behavior: Per-object in-memory analysis state lives in instruction records and alternative groups; no disk persistence except downstream ELF updates.

Dependencies and integration points: Depends on CFI, ELF sections/symbols/relocs, arch instruction types, Linux list/hlist helpers, and the optional disassembly context.

Risks: Bitfield limits (`INSN_CHUNK_BITS`), alternative-group CFI arrays, and unioned call/jump-table fields must stay consistent with checker allocation and traversal code.

Test signals: Objtool check tests should cover direct and dynamic jumps, alternatives, exception tables, static calls, uaccess/noinstr paths, and ORC output.

Source coverage: researched from the complete local file (165 lines, 3678 bytes).
