# sources/distributed-fs/ceph-client/arch/arc/lib/strlen.S

Purpose: optimized ARC `strlen()`.

Important APIs/functions: exports `strlen`.

Control flow: aligns the effective scan window around the input address, performs early detection across the first two loaded words with masks adjusted for the starting offset, then loops loading pairs of words until a zero byte is detected. Endian-specific logic converts the zero-byte mask into the byte count returned in `r0`.

State and persistence: no persistent state.

Dependencies and integration: always built in ARC lib. Uses word-at-a-time zero-byte detection, `norm`, `ror`, endian-specific masking, and ARC load scheduling.

Risks: initial unaligned address handling is subtle and may read before/around the string's first byte depending on aligned base computation. Length calculation must account for endian and early-end paths. Normal C string preconditions still apply.

Test signals: lengths 0 through multiple word boundaries, all pointer alignments, page-boundary strings where accessible padding matters, and endian coverage.
