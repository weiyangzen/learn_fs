# sources/distributed-fs/ceph-client/lib/zlib_inflate/inffixed.h

Purpose: Provides precomputed fixed-Huffman decode tables for DEFLATE block type 1.

Important APIs/types:
- Defines `static const code lenfix[512]` and `static const code distfix[32]`.
- Entries use `struct code` from `inftrees.h`, with op/bits/val describing literals, lengths, distances, end-of-block, or invalid codes.

Control flow:
- Included inside `zlib_fixedtables()` in `inflate.c`. The include creates function-local static tables and assigns them to `state->lencode` and `state->distcode`.

State and persistence:
- Static read-only tables persist for the translation unit/function scope.
- No mutable state.

Dependencies and integration:
- Requires `code` to be defined before inclusion.
- Avoids rebuilding fixed Huffman tables at runtime.

Risks:
- Table contents must exactly match RFC1951 fixed-code definitions. Manual edits are high risk.
- Inclusion style is unusual; moving it to normal header scope changes linkage/visibility.

Test signals:
- Inflate streams containing fixed-Huffman blocks.
- Compare fixed-block decode with dynamic-table decode of equivalent data.
