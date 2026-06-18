# sources/distributed-fs/ceph-client/arch/arc/lib/memset.S

Purpose: ARCompact/ARC700 `memset()` and `memzero()`.

Important APIs/functions: exports `memset` and `memzero`; `SMALL` controls the bytewise tiny path threshold.

Control flow: computes alignment from destination and length. Aligned path expands the byte to a word and stores words in a zero-overhead loop. Unaligned larger ranges fix up the start/end using byte/halfword stores, then enter the aligned loop. Tiny ranges byte-store directly. `memzero()` converts `(mem, size)` to `memset(mem, 0, size)` and branches.

State and persistence: no persistent state; returns the original destination pointer.

Dependencies and integration: selected for `CONFIG_ISA_ARCOMPACT`. Uses ARC short instructions, auto-increment stores, zero-overhead loops, and CFI linkage.

Risks: alignment fixups write around range edges and must not overrun. `SMALL` must remain large enough for the alignment strategy. Endian-independent byte replication must keep only low byte of value.

Test signals: every small length around the threshold, all destination alignments, nonzero byte values, large lengths, and `memzero()` call sites.
