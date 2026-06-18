# sources/distributed-fs/ceph-client/arch/sparc/lib/strncmp_32.S

Purpose: hand-optimized SPARC32 assembly implementation of `strncmp`, derived from GCC output of the generic GNU libc routine.

Important APIs/functions: `ENTRY(strncmp)` compares `%o0` and `%o1` for at most `%o2` bytes and returns signed byte difference or zero. `EXPORT_SYMBOL(strncmp)` exports the implementation.

Control flow: for lengths greater than three, it processes four byte comparisons per loop iteration using repeated inline blocks, stops on NUL or mismatch, and then handles the final remainder bytes. For short counts, it jumps directly to the tail loop. Return paths subtract unsigned byte values to preserve C `strncmp` ordering.

State and persistence: no persistent state and no writes. It advances local copies of string pointers and count registers.

Dependencies/integration: includes `linux/export.h` and `linux/linkage.h`. Provides the architecture symbol used by common kernel string users on 32-bit SPARC.

Risks: length handling is subtle: the code preloads bytes and decrements block/remainder counters while also stopping on NUL. The final return path uses `%o3`/`%g2`, so short-count and zero-count paths must avoid stale values. It does not use exception fixups; invalid user pointers are not supported.

Test signals: compare against generic `strncmp` for counts 0-8, long equal prefixes, NUL before `n`, mismatch before/at/after 4-byte boundaries, signed high-bit byte values, and all source alignments.
