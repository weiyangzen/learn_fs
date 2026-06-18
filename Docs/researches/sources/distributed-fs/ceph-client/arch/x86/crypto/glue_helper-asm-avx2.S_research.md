<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx2.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx2.S

Purpose: This include file provides YMM load/store helper macros for 16-way AVX2 block-cipher wrappers. It is the AVX2 counterpart of the 8-way helper and is used by 16-block Serpent and similar assembly code.

Important APIs/types/functions: `load_16way(src, x0..x7)` loads sixteen 16-byte blocks as eight 32-byte YMM vectors. `store_16way(dst, x0..x7)` stores those eight YMM vectors. `store_cbc_16way(src, dst, x0..x7, t0)` handles CBC decryption output by XORing decrypted plaintext candidates with the previous IV/ciphertext chain, using a temporary register to bridge lanes.

Control flow: A consumer loads sixteen blocks, transposes/crypts them, and writes either direct ECB output or CBC-decrypted output. CBC store logic must account for the fact that one YMM register contains two adjacent blocks, so it uses permutation/alignment operations and a temporary register to form the correct chain.

State and persistence: It has no persistent state. Runtime state is the caller's vector register set and source/destination memory. Output mutation is limited to the destination range and, indirectly, caller-managed IV state in higher-level glue.

Dependencies and integration points: It assumes AVX2/YMM state ownership and a 16-byte block size. It integrates with `serpent-avx2-asm_64.S` and any other 16-way block-cipher assembly using the same register ordering.

Risks and test signals: The CBC helper is sensitive to lane order and source/destination overlap. A missing `vzeroupper` in caller code can also hurt mixed SSE/AVX transitions. Tests should compare 16-block CBC decrypt against scalar reference, include overlapping in-place buffers, and run with tails that force glue fallback after one 16-block group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx2.S -->
