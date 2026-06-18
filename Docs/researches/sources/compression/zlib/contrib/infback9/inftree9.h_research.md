# sources/compression/zlib/contrib/infback9/inftree9.h

Purpose: declares the decode-table representation and table builder for deflate64 inflation.

Important APIs/types/functions: `code` struct with `op`, `bits`, and `val`; constants `ENOUGH_LENS`, `ENOUGH_DISTS`, and `ENOUGH`; enum `codetype` with `CODES`, `LENS`, `DISTS`; prototype for `inflate_table9`.

Control flow: `infback9.c` allocates `code codes[ENOUGH]` in `inflate_state`, then asks `inflate_table9` to fill sections for code-length, literal/length, and distance decoding. The decoder interprets `op` bit patterns documented in this header.

State and persistence: header-only declarations and constants; no mutable state.

Dependencies/integration: must be included before `inflate9.h` needs `code` and `ENOUGH`. Uses zlib `FAR` in the prototype.

Risks: the `ENOUGH_*` constants are tied to root table bit choices in `infback9.c`; changing one side without the other can cause table overflow. This is explicitly internal implementation API.

Test signals: compile coverage plus dynamic Huffman decoding coverage; no standalone tests in this folder.
