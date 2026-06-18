# sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-archs-unaligned.S

Purpose: ARCv2 `memcpy()` optimized for CPUs/configurations where unaligned memory accesses are permitted.

Important APIs/functions: exports `memcpy`. Macro `LOADX`/`STOREX` selects 64-bit `ldd/std` when `CONFIG_ARC_HAS_LL64` is present, otherwise 32-bit loads/stores.

Control flow: copies 32 or 64 byte blocks in an unrolled zero-overhead loop, then copies the remaining bytes one at a time. It avoids alignment prologue because the selected configuration permits unaligned accesses.

State and persistence: no persistent state; `r0` remains destination return value and `r3` walks the destination.

Dependencies and integration: selected for ARCv2 when `CONFIG_ARC_USE_UNALIGNED_MEM_ACCESS` is enabled. Depends on ARCv2 load/store behavior, optional LL64, and kernel lib linkage.

Risks: illegal or slow unaligned hardware behavior would make this unsafe if selected for the wrong CPU. It is not overlap-safe. Large unrolled operations need correct block-size constants for LL64 and non-LL64 variants.

Test signals: unaligned source and destination copy tests, LL64 and non-LL64 builds, small tails 0-31 bytes, long copies, and hardware/platform smoke tests for unaligned access support.
