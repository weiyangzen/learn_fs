# sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.c

Purpose: Builds canonical Huffman decode tables for inflate from code-length arrays. It handles code-length tables, literal/length tables, and distance tables.

Important APIs/functions:
- `zlib_inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)` builds one decode table set.

Control flow:
- Counts code lengths, finds min/max length, clamps the requested root-table bits, and validates over-subscribed or incomplete code sets.
- Sorts symbols by code length into the caller-provided `work` array.
- Selects base/extra tables for CODES, LENS, or DISTS.
- Fills root table entries and allocates subtables when codes exceed root bits, tracking `used` against `ENOUGH`.
- Adds invalid-code markers for incomplete table slots and returns updated table pointer/root bits.

State and persistence:
- Stateless across calls. All storage is caller-provided via `table` and `work`.
- Uses static const base/extra arrays for length and distance symbols.

Dependencies and integration:
- Includes `<linux/zutil.h>` and `inftrees.h`.
- Called from `inflate.c` while parsing dynamic blocks.

Risks:
- Table construction is a core corruption boundary. Incorrect validation can accept malformed streams or overrun `state->codes`.
- `ENOUGH` is assumed sufficient; return `+1` signals insufficient table space.
- The backwards Huffman increment is format-specific and easy to break.

Test signals:
- Fuzz dynamic Huffman headers.
- Boundary tests for no symbols, single-symbol tables, incomplete/oversubscribed tables, max table usage, and invalid repeats from `inflate.c`.
