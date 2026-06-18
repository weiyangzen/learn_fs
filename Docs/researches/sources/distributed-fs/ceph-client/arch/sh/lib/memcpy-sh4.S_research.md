# sources/distributed-fs/ceph-client/arch/sh/lib/memcpy-sh4.S

Purpose: SH4-optimized implementation of `memcpy`.

Important symbols: `ENTRY(memcpy)` and multiple alignment/size case labels such as `.Lcase00`, `.Lcase0`, `.Lcase2`, and `.Lcase3`.

Control flow: dispatches on source/destination alignment and size, uses SH4-friendly burst/load-store sequences for large regions, and falls back to byte/word cleanup for tails.

State and persistence: copies bytes from source to destination and returns the destination pointer; no internal state.

Dependencies and integration: selected by `Makefile` for SH4 when not optimizing for size and backs generic kernel `memcpy`.

Risks: assumes non-overlapping buffers as `memcpy` requires. Alignment case errors cause data corruption that is hard to localize.

Test signals: memory selftests across alignments, lengths around dispatch thresholds, and comparison with generic `memcpy`.
