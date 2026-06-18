# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon-glue.c

Purpose: creates arm64 SIMD-safe `xor_block_template` wrappers for NEON and SHA3 `eor3` XOR implementations.

Important APIs and flow: `XOR_TEMPLATE(neon)` and `XOR_TEMPLATE(eor3)` generate `xor_gen_neon()` and `xor_gen_eor3()`. Each wrapper executes the corresponding `_inner` function inside `scoped_ksimd()` and publishes `xor_block_neon` or `xor_block_eor3`.

State and persistence: no durable state; it protects live kernel SIMD state while mutating parity buffers.

Dependencies and integration: depends on `<asm/simd.h>`, `xor-neon.h`, and `arm64/xor_arch.h`, which registers one of these templates when NEON is present.

Risks and test signals: risks include SIMD use outside a valid kernel SIMD section and mismatched inner function declarations. Signals include arm64 build coverage, KUnit XOR tests, and boot logs selecting `neon` or `eor3`.
