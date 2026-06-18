# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx512vl-x86_64.S

Purpose: AVX-512VL/BW ChaCha block XOR functions for x86_64, optimized variants for 2, 4, and 8 blocks.

Important APIs/types/functions: exports `chacha_2block_xor_avx512vl()`, `chacha_4block_xor_avx512vl()`, and `chacha_8block_xor_avx512vl()`. It uses counter constants `CTR2BL`, `CTR4BL`, and `CTR8BL`.

Control flow: like the AVX2 file, functions broadcast/load ChaCha state, add counter lanes, run repeated double rounds, add original state, XOR source, and store output. AVX-512VL paths use `vprold` rotate instructions instead of byte-shuffle or shift/or sequences. Wider register availability lets the 8-block path keep original state in `ymm16`-`ymm31`. Partial final writes use mask registers and masked loads/stores where applicable, reducing scratch handling.

State and persistence: no persistent state. Uses AVX-512 register state and `vzeroupper`; caller must bracket FPU use.

Dependencies: AVX, AVX2, AVX512VL, AVX512BW (`kmovq` use), OS xfeature support as checked by `chacha.h`, and x86_64 ABI.

Integration points: highest-priority SIMD path in `chacha_dosimd()` when the static key is enabled.

Risks: AVX-512 state usage must be gated correctly or the kernel can fault/corrupt state. Masked tail handling must preserve exact byte counts. Counter advancement remains split between assembly lane constants and C dispatcher state mutation.

Test signals: same ChaCha known-answer and partial-length tests as AVX2, plus CPU-feature-specific runtime coverage for AVX-512VL/BW systems.
