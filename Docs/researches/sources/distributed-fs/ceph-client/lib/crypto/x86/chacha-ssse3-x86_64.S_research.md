# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-ssse3-x86_64.S

Purpose: SSSE3 ChaCha and HChaCha primitives for x86_64, including one-block and four-block encryption paths.

Important APIs/types/functions: local `chacha_permute` implements one-block permutation. Exports `chacha_block_xor_ssse3()`, `hchacha_block_ssse3()`, and `chacha_4block_xor_ssse3()`.

Control flow: `chacha_permute` operates on a state matrix in XMM registers, performing double rounds with SSSE3 byte shuffles for 8/16-bit rotates and shift/or for 7/12-bit rotates, with row shuffles between column and diagonal phases. The one-block XOR path saves original state, permutes, adds state back, XORs source, and handles partial tails via stack scratch copy. HChaCha permutes and stores words 0..3 and 12..15. The four-block path broadcasts state words across lanes, adds counter increments, performs parallel rounds without per-round word shuffles, then transposes for output.

State and persistence: no global state; only caller buffers and stack scratch are mutated. Uses XMM registers under caller-managed FPU context.

Dependencies: SSSE3, x86_64 calling conventions, `linux/linkage.h`, frame macros, and dispatcher in `chacha.h`.

Integration points: baseline SIMD implementation once SSSE3 is available; also used for HChaCha even when AVX2/AVX512 accelerate bulk ChaCha.

Risks: partial-block code must avoid overread/overwrite. HChaCha output word selection must match XChaCha construction. Round-count loop assumes even `nrounds`.

Test signals: ChaCha, HChaCha/XChaCha known-answer vectors and guard-buffer partial-length tests are key.
