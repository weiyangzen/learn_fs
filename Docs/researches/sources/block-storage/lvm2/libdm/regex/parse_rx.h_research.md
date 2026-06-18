# File Research: sources/block-storage/lvm2/libdm/regex/parse_rx.h

Purpose: declares the internal regex parse-tree representation and parser entry points used by the libdm matcher.

Read coverage: complete file read, 57 lines.

Key contents:
- Defines regex node types: `CAT`, `STAR`, `PLUS`, `OR`, `QUEST`, and `CHARSET`.
- Defines internal sentinel characters `HAT_CHAR`, `DOLLAR_CHAR`, and `TARGET_TRANS`.
- Declares `struct rx_node` with tree links, charset bitsets, DFA construction fields, and computed first/last/follow position bitsets.
- Declares `rx_parse_str()` and `rx_parse_tok()`.

Dependencies:
- Includes `libdm/misc/dmlib.h` for `dm_bitset_t`, pools, and related helpers.

Risk and edge cases:
- `TARGET_TRANS` is `'\0'`, so parser/matcher callers must respect explicit begin/end token parsing when NUL markers are embedded.
- The parse tree carries both AST and DFA-construction state, so the matcher mutates parser-produced nodes during compilation.
