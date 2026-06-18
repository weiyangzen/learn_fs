## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetrandom-chacha.S

Purpose: stackless SSE2 ChaCha20 block generator used by the 64-bit vDSO getrandom implementation.

Important API/function: `__arch_chacha20_blocks_nostack(output, key, counter, nblocks)`. Inputs are output buffer in RDI, 32-byte key in RSI, 8-byte counter in RDX, and number of 64-byte blocks in RCX.

Control flow: loads the ChaCha constant, key, and counter into XMM registers, runs 10 double-round iterations per block using SSE2 vector arithmetic/rotates, writes 64 bytes, increments the counter, loops for `nblocks`, stores the final counter, clears sensitive vector registers, and returns without stack spills.

State/persistence: updates the caller-provided counter in memory and output buffer. It intentionally avoids stack state and clears key/state-bearing XMM registers at exit.

Integration points: generic `lib/vdso/getrandom.c`, vdso64 Makefile, SSE2 baseline x86-64 ABI, and user-facing `__vdso_getrandom`.

Risks: cryptographic correctness, counter handling, and register clearing are security-sensitive. The routine assumes positive block count and caller-managed buffer sizes. Test signals include vDSO getrandom selftests, ChaCha20 known-answer tests, register/stack audit, objtool/unwind sanity, and sanitizer-style memory bounds tests outside vDSO where possible.
