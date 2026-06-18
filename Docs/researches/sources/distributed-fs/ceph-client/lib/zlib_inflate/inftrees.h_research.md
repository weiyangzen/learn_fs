# sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.h

Purpose: Defines inflate decode table entries, table size constants, code-table type enum, and the `zlib_inflate_table()` prototype.

Important APIs/types:
- `typedef struct code { unsigned char op; unsigned char bits; unsigned short val; } code`.
- `ENOUGH` is the max dynamic table size reserved in `inflate_state`.
- `MAXD` reserves worst-case distance table space.
- `codetype` distinguishes CODES, LENS, and DISTS table generation.
- Declares `zlib_inflate_table()`.

Control flow: No executable logic. The comments define how `op`, `bits`, and `val` are interpreted by `inflate.c` and `inffast.c`.

State and persistence: No state. Constants influence `struct inflate_state` allocation.

Dependencies and integration:
- Used by `inflate.h`, `inflate.c`, `inffast.c`, `inffixed.h`, and `inftrees.c`.

Risks:
- `code` layout is assumed to be four bytes for compact decode tables.
- Changing op-bit encoding requires coordinated decoder changes.
- Reducing `ENOUGH` or `MAXD` can make valid streams fail.

Test signals:
- Static size/layout checks if added.
- Dynamic-Huffman inflate tests near maximum table usage.
