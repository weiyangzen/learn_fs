<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom-chacha.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom-chacha.S

### Purpose
`vgetrandom-chacha.S` implements a LoongArch ChaCha20 block generator for vDSO getrandom without spilling sensitive key material to the stack.

### Important APIs, Types, And Functions
The exported function is `__arch_chacha20_blocks_nostack(output, key, counter, nblocks)`. Internal macros map state registers and define `OP_4REG` for four parallel operations.

### Control Flow
The function saves callee-saved registers, loads ChaCha constants, key words, and a 64-bit counter, then loops over 64-byte blocks. Each block performs 10 double rounds using add/xor/rotate sequences for column and diagonal rounds, adds the original state, stores 16 words to output, increments the counter with carry, advances output, and repeats. At the end it stores the updated counter, clears sensitive temporary state registers, restores saved registers, and returns.

### State, Persistence, And Dependencies
Persistent output is generated random bytes and updated counter memory. Sensitive key/state remain in registers; only ABI callee-saved registers are spilled and later restored. Dependencies include LoongArch integer instructions, ABI register conventions, and vDSO getrandom generic code.

### Integration Points
`vgetrandom.c` calls generic `__cvdso_getrandom()`, which can use this arch ChaCha helper for userspace random generation.

### Risks
ChaCha round constants, rotation counts, counter update, and little-endian word stores must be exact. The no-sensitive-stack property depends on not spilling state/key registers beyond the saved ABI registers. Register aliasing is dense and review-sensitive.

### Test Signals
Run known-answer ChaCha20 vectors through the vDSO helper, getrandom vDSO selftests, counter wrap tests, and inspect assembly for unintended stack spills of key/state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetrandom-chacha.S -->
