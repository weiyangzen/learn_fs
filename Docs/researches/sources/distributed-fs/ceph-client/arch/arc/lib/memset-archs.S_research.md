# sources/distributed-fs/ceph-client/arch/arc/lib/memset-archs.S

Purpose: ARCv2 optimized `memset()` and `memzero()`.

Important APIs/functions: exports `memset` and `memzero`. Optional `PREALLOC_INSTR`/`PREFETCHW_INSTR` macros emit cache preallocation/prefetch only for 64-byte L1 cache line configurations. LL64 controls 64-bit stores.

Control flow: zero-length returns immediately. Short lengths use byte stores. Longer ranges prefetch, byte-fill until destination alignment, replicate the byte into a word, then write 64-byte and 32-byte unrolled chunks before byte tail. `memzero()` remaps arguments and tail-calls `memset`.

State and persistence: no persistent state; returns original destination.

Dependencies and integration: selected for ARCv2. Depends on `L1_CACHE_SHIFT`, optional `CONFIG_ARC_HAS_LL64`, and safe use of prefetch/prealloc within the target range.

Risks: preallocation is only valid for line sizes explicitly handled; emitting it for other line sizes could touch outside the memset range. Tail and alignment logic must preserve return value and avoid overstore.

Test signals: memset tests over lengths 0-128+, all destination alignments, values beyond 0x7f, LL64/non-LL64 builds, cache-line-size variants, and `memzero()` equivalence tests.
