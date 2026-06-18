## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/vgetrandom-chacha.S

### Purpose
`vgetrandom-chacha.S` implements a stackless NEON ChaCha20 block function for the ARM64 VDSO getrandom fast path.

### Important APIs, Types, And Functions
It defines `__arch_chacha20_blocks_nostack(uint8_t *dst, const uint8_t *key, uint32_t *counter, size_t nblocks)`. The routine uses vector registers `v0`-`v7` and `v16`-`v18`, deliberately avoiding callee-saved `d8`-`d15`.

### Control Flow
The function loads the ChaCha constant, 256-bit key, and 64-bit counter with zero nonce, runs 20 rounds per 64-byte block using NEON add/xor/rotate/shuffle operations, adds the original state, stores one block to the destination, increments the counter, loops for all blocks, writes back the counter, zeroes sensitive vector registers, and returns without stack spills.

### State, Persistence, And Dependencies
State is caller-provided output, key, and counter memory plus transient SIMD registers. There is no kernel global state or stack state.

### Integration Points
Called by the generic VDSO getrandom implementation when ARM64 FPSIMD is available. It is built into the native VDSO and paired with `vgetrandom.c`.

### Risks
Cryptographic correctness, counter update, register clobbering, and stackless behavior are critical. Using callee-saved SIMD registers or failing to clear sensitive registers would violate userspace ABI or leak material.

### Test Signals
Compare against ChaCha20 test vectors, run VDSO getrandom stress tests, inspect disassembly for no stack access and no `d8`-`d15` clobbering, and test FPSIMD and non-FPSIMD fallback behavior.
