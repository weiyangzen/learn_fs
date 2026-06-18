## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vgetrandom-chacha.S

Purpose: Provides a no-stack s390 vector implementation of ChaCha20 blocks for the vDSO getrandom fast path.

Important symbol: `__arch_chacha20_blocks_nostack(uint8_t *dst_bytes, const uint8_t *key, uint32_t *counter, size_t nblocks)`.

Control flow: Loads ChaCha constants and byte-permutation data, loads the key, builds the counter/zero nonce state, runs ten double rounds per block with vector add/xor/rotate/shuffle operations, adds original state, stores little-endian output using a facility-148 alternative path, increments and stores the counter, advances output, loops by block count, then zeroes sensitive vector registers before returning.

State and persistence: Reads key and counter from caller memory, writes output and updated counter, and avoids stack spills. Sensitive vector state is explicitly cleared before return.

Dependencies and integration: Depends on s390 vector/facility instructions, alternatives, DWARF CFI, and generic vDSO getrandom code that calls the architecture ChaCha provider.

Risks and test signals: Risks are endian conversion errors, counter carry handling, facility alternative mismatch, and register clobber/secret leakage. Test signals include ChaCha20 known-answer tests through vDSO getrandom, facility-148 and non-148 paths, multi-block counter rollover behavior, and objtool/CFI sanity where applicable.
