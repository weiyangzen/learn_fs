# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.c

Purpose: provides arm64 NEON and SHA3 EOR3 accelerated XOR inner loops.

Important APIs and flow: `__xor_neon_{2,3,4,5}` load four `uint64x2_t` vectors per iteration, XOR each requested source into destination, and store back. `eor3()` emits the SHA3 `eor3` instruction. `__xor_eor3_{3,4,5}` use three-input XOR where profitable, while the 2-source case reuses NEON. `__DO_XOR_BLOCKS()` emits `xor_gen_neon_inner()` and `xor_gen_eor3_inner()`.

State and persistence: no persistent state; destination pages are modified in place. The caller must already own SIMD state.

Dependencies and integration: depends on `<asm/neon-intrinsics.h>`, ARM64 SHA3 feature support, `xor-neon.h`, and glue wrappers.

Risks and test signals: risks include alignment assumptions, SHA3 feature gating, and inline assembly constraints for `eor3`. Signals include KUnit randomized XOR testing, feature-gated boot selection, and parity verification on NEON-only and SHA3-capable arm64 CPUs.
