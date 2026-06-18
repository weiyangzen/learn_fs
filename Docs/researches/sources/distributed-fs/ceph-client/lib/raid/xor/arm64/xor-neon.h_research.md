# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.h

Purpose: declares the two arm64 SIMD inner XOR generator functions shared between implementation and glue units.

Important APIs and flow: exposes `xor_gen_neon_inner()` and `xor_gen_eor3_inner()` with the standard XOR generator signature: destination, source pointer array, source count, and byte length.

State and persistence: no state; this is an interface header.

Dependencies and integration: included by `arm64/xor-neon.c` and `arm64/xor-neon-glue.c` to keep SIMD instruction bodies separate from SIMD state wrappers.

Risks and test signals: prototype mismatch would be caught by compiler diagnostics. Runtime signals are the same as the arm64 NEON/EOR3 implementation and glue paths.
