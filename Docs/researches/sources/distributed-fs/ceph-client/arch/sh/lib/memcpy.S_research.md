# sources/distributed-fs/ceph-client/arch/sh/lib/memcpy.S

Purpose: generic SH implementation of `memcpy`.

Important symbols: `ENTRY(memcpy)`, `jmptable`, and alignment case labels `case0` through `case3`.

Control flow: selects copy strategy from alignment, copies longword chunks where possible, then copies trailing bytes.

State and persistence: mutates destination memory only and returns the original destination pointer.

Dependencies and integration: linked when SH4 specialized implementation is not selected or size optimization is preferred.

Risks: overlapping buffers are not supported; use `memmove` for overlap. Alignment table mistakes can corrupt unaligned copies.

Test signals: string/memory selftests for all alignments and small/large sizes.
