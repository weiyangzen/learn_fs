# sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs.S

Purpose: ARCv2 `memcpy()` for configurations that cannot rely on unaligned memory access.

Important APIs/functions: exports `memcpy`; defines endian-specific shift/merge/extract macros and LL64-aware `LOADX`/`STOREX`.

Control flow: handles zero and small sizes, byte-copies until destination is word-aligned, then chooses source-aligned fast copy or one of three source-unaligned reconstruction paths. Unaligned source offsets 1, 2, and 3 are rebuilt with shifted adjacent words; tails are copied bytewise.

State and persistence: no persistent state; uses scratch registers to hold merged source words and returns destination in `r0`.

Dependencies and integration: selected for ARCv2 when unaligned access is not enabled. Depends on endian macros, optional LL64, zero-overhead loops, and kernel lib symbol linkage.

Risks: byte reconstruction is high-risk for endian and off-by-one errors, especially around small lengths after alignment prologue. Source/destination overlap is not supported. Incorrect tail handling can undercopy or overcopy.

Test signals: exhaustive small-size copy tests, all source alignment offsets, destination alignment transitions, endian builds, LL64 builds, and randomized buffer comparisons against a reference implementation.
