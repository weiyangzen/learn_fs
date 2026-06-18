<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgetrandom-chacha.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgetrandom-chacha.S

Purpose: Provides a no-stack RISC-V assembly implementation of ChaCha20 blocks for vDSO getrandom.

Important APIs/types/functions: Defines `__arch_chacha20_blocks_nostack` and local macros for ChaCha quarter rounds, state registers, rotations, and output stores.

Control flow: Loads ChaCha constants/key/counter, loops over requested blocks, performs 20 rounds via register-only quarter-round operations, writes keystream blocks, increments the counter, and returns without using the stack.

State and persistence: Operates only on caller-provided output, key, counter, and block count. No global state.

Dependencies and integration points: Called by generic vDSO getrandom code; built only in vDSO context with strict ABI/register constraints.

Risks: Cryptographic correctness and register preservation are critical. No-stack constraint leaves little room for spills; counter increment and endian stores must match ChaCha20 spec.

Test signals: vDSO getrandom known-answer tests, randomized output comparison with generic ChaCha, objdump stack-use inspection, and RV32/RV64 build coverage.

Source read size: 252 lines, 5624 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vgetrandom-chacha.S -->
