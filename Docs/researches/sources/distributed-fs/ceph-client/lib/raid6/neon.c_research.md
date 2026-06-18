# sources/distributed-fs/ceph-client/lib/raid6/neon.c

Purpose: wraps generated ARM NEON RAID6 syndrome functions in safe kernel SIMD sections.

Important APIs and flow: `RAID6_NEON_WRAPPER(n)` creates generation and xor-syndrome wrappers for `n` equal to 1, 2, 4, and 8. Each wrapper calls generated `raid6_neonN_*_real()` inside `scoped_ksimd()` and publishes `raid6_neonxN` with `raid6_have_neon()`.

State and persistence: no persistence; wrappers protect SIMD state while real implementations mutate P/Q.

Dependencies and integration: generated `neonN.c` files from `neon.uc`, ARM SIMD helpers, and `raid6_algos[]`.

Risks and test signals: separation prevents NEON instructions outside the critical section. Signals include ARM/arm64 NEON builds, boot algorithm selection, and RAID6 parity tests.
