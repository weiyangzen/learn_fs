# sources/compression/zlib/inftrees.c

## Purpose
`inftrees.c` builds canonical Huffman decode tables for deflate code-length, literal/length, and distance alphabets. It also provides fixed-code table selection or generation.

## Important APIs, Types, and Functions
The main internal API is `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)`. It also defines `inflate_fixed(struct inflate_state *state)`, optional `buildtables()` under `BUILDFIXED`, and a `MAKEFIXED` generator main. Static base/extra arrays encode deflate length and distance semantics.

## Control Flow, State, and Persistence
`inflate_table()` counts code lengths, finds min/max/root widths, rejects over-subscribed or invalid incomplete codes, sorts symbols by length, fills root and sub-tables with replicated entries, links sub-tables, and advances the caller's table pointer. `inflate_fixed()` either points at generated `inffixed.h` tables or builds them once through `z_once()`.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, and `inflate.h`. `inflate.c` and `infback.c` call it while decoding dynamic blocks, and fixed-block decoding depends on its fixed-table setup.

## Risks and Test Signals
Risks include table-space overflow if root bits or `ENOUGH_*` constants drift, accepting invalid code sets, and thread-safety caveats with `BUILDFIXED` when atomics are unavailable. Tests should cover over-subscribed tables, missing end-of-block codes, incomplete distance sets, all fixed blocks, and dynamic-code fuzzing.
