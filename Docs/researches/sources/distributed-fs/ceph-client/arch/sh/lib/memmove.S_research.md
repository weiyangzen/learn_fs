# sources/distributed-fs/ceph-client/arch/sh/lib/memmove.S

Purpose: implements overlap-safe memory move for SH.

Important symbols: `ENTRY(memmove)`, `jmptable`, `case_none`, and alignment cases.

Control flow: detects source/destination ordering and overlap, chooses forward or backward copying as appropriate, and uses alignment-aware chunks plus tail cleanup.

State and persistence: mutates destination memory and returns destination pointer.

Dependencies and integration: core kernel memory primitive used wherever ranges may overlap.

Risks: incorrect overlap detection is the primary hazard and can self-corrupt copies. Backward-copy tail logic is alignment-sensitive.

Test signals: memory tests with identical pointers, non-overlap, forward overlap, backward overlap, and varied alignments.
