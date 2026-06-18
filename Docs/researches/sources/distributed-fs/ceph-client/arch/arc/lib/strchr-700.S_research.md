# sources/distributed-fs/ceph-client/arch/arc/lib/strchr-700.S

Purpose: ARC700 optimized `strchr()`.

Important APIs/functions: exports `strchr`, taking string pointer in `r0` and target char in `r1`, returning pointer or NULL in `r0`.

Control flow: normalizes the target byte into a repeated word, handles initial unaligned bytes, then scans words using branch-light zero-byte and matching-byte detection. When either NUL or target is found, endian-specific logic computes the first relevant byte offset and returns either its address or NULL if NUL came first.

State and persistence: no persistent state.

Dependencies and integration: always included by the ARC lib Makefile. Uses ARC word operations, `norm`, `ror`, endian-specific bit math, and careful code alignment for branch prediction.

Risks: simultaneous target/NUL detection must choose the earliest byte. Endian-specific bit tricks are easy to break. It can read aligned words containing bytes beyond the terminating NUL, so it relies on normal architecture tolerance for word-at-a-time string scanning.

Test signals: searches for present/absent characters at every offset, target `'\0'`, unaligned string starts, strings shorter than one word, and endian coverage.
