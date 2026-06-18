# sources/distributed-fs/ceph-client/arch/arc/lib/strcpy-700.S

Purpose: ARC700 optimized `strcpy()`.

Important APIs/functions: exports `strcpy`, preserving the original destination in `r0`.

Control flow: aligned source/destination uses word-at-a-time copy with NUL detection. It handles source 4-byte versus 8-byte alignment to allow limited read-ahead without crossing unwanted cache lines. Once a word containing NUL is found, it stores bytes until the terminator. Unaligned cases use a byte loop.

State and persistence: no persistent state.

Dependencies and integration: always built in ARC lib. Depends on ARC zero-byte detection, endian-specific byte extraction, auto-increment stores, and ABI return convention.

Risks: `strcpy()` requires sufficient destination space and non-overlap. Word-at-a-time read-ahead must not access invalid memory in corner cases. Byte termination handling must store the NUL exactly once.

Test signals: empty strings, strings of every length around word boundaries, all source/destination alignments, endian builds, and destination content checks immediately after NUL.
