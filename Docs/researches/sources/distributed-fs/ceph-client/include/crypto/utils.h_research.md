# sources/distributed-fs/ceph-client/include/crypto/utils.h

Purpose: provides small shared crypto utility helpers for XOR operations and constant-time memory comparison.

Important APIs, types, and flow: `__crypto_xor()` is the external implementation for XORing two sources into a destination. `crypto_xor()` XORs a buffer in place, using word-sized operations when possible and falling back to byte operations. `crypto_xor_cpy()` XORs two input buffers into an output buffer. `crypto_memneq()` delegates to `__crypto_memneq()` to compare buffers without early-exit timing leakage.

State and persistence: stateless; all operations are caller-buffer based.

Dependencies and integration: used broadly by block modes, MACs, and verification code. Depends on unaligned access helpers and constant-time comparison implementation.

Risks and test signals: overlapping buffers, alignment, and size-zero behavior matter for XOR; comparison must remain constant-time. Signals include XOR unit tests for aligned/unaligned/overlapping buffers, KMSAN/KASAN tests, and timing-sensitive review of `crypto_memneq()` call sites.
