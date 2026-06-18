# sources/distributed-fs/ceph-client/arch/arc/lib/strcmp.S

Purpose: ARCompact/ARC700 optimized `strcmp()`.

Important APIs/functions: exports `strcmp`.

Control flow: unaligned pointers use a byte loop. Aligned pointers use word loads and a repeated `0x01010101` zero-detection trick to scan until either a NUL or mismatch. Little-endian and big-endian paths then mask or adjust the first significant byte and return ordering.

State and persistence: no persistent state.

Dependencies and integration: selected for `CONFIG_ISA_ARCOMPACT`. Uses ARC700 scheduling assumptions, `norm`, `ror`, byte masks, and endian macros.

Risks: the big-endian path compensates for zero-detection carry propagation; careless edits could misorder bytes around `0x00`/`0x01`. Word-at-a-time reads require valid accessible memory past short strings within normal alignment expectations.

Test signals: prefix/equal/different strings, mismatch before and after NUL, high-bit bytes, all alignments, and big-endian-specific zero/carry cases.
