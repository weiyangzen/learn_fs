# sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.h

Purpose: Defines the internal inflate parser modes and `struct inflate_state` used by `inflate.c`, `inffast.c`, and DFLTCC inflate glue.

Important APIs/types:
- `inflate_mode` enumerates every parser/decode/trailer/error state: header modes, block type modes, stored/dynamic/code decode modes, check/done/error modes.
- `struct inflate_state` stores wrapper flags, checksum, sliding window, bit accumulator, copy/match state, decode table pointers, dynamic table counts, temporary lengths/workspace, and fixed-size code table storage.
- `REVERSE(q)` byte-swaps 32-bit checksum words from the bit accumulator.

Control flow: The mode enum documents state transitions consumed by the `inflate.c` switch loop. No executable code except macros.

State and persistence:
- This header defines the persistent state for a streaming inflate call. The state lives inside `struct inflate_workspace` in `infutil.h`.
- `codes[ENOUGH]`, `lens[320]`, and `work[288]` avoid allocation while building dynamic Huffman tables.

Dependencies and integration:
- Includes `inftrees.h` for `code` and `ENOUGH`.
- DFLTCC computes extension placement from this struct size/alignment.

Risks:
- Changing enum or struct fields must be coordinated with `inflate.c`, `inffast.c`, and DFLTCC hooks.
- Fixed array sizes are format-derived. Reducing them risks table overflow.

Test signals:
- Compile with all consumers.
- Inflate dynamic-block stress cases that approach `ENOUGH` and length-array limits.
