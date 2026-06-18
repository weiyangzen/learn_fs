# sources/compression/zlib/contrib/infback9/inftree9.c

Purpose: builds canonical Huffman decoding tables for the deflate64 inflater.

Important APIs/types/functions: exported `inflate_table9(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)` and copyright string `inflate9_copyright`. Static base/extra tables describe deflate64 length and distance code semantics.

Control flow: the function counts code lengths, finds min/max lengths, validates over-subscribed or incomplete trees, sorts symbols into `work`, then fills root and sub-tables by reversed Huffman code order. It emits literal, table-link, length/distance, end-of-block, and invalid entries. It advances `*table` by used entries and returns the actual root bit count.

State and persistence: no persistent mutable state. It writes into caller-provided work/table buffers in `inflate_state`.

Dependencies/integration: depends on `zutil.h`, `inftree9.h`, `MAXBITS`, `ENOUGH_LENS`, and `ENOUGH_DISTS`. `infback9.c` calls it for code-length, literal/length, and distance tables.

Risks: callers must guarantee all `lens[]` values are in range. If root bit constants change, `ENOUGH_*` values must be recalculated. Return `1` indicates table space exhaustion, which calling code treats as invalid data.

Test signals: dynamic deflate64 block decoding exercises this heavily; targeted tests should include empty, incomplete, over-subscribed, and maximum-table cases.
