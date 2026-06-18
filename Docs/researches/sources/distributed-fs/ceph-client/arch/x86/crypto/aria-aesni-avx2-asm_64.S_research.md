# sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx2-asm_64.S

Purpose: Implements ARIA 32-block parallel encryption, decryption, and CTR keystream XOR for x86_64 with AVX2/AES-NI, plus alternate GFNI S-box paths when the C glue selects them. It is the AVX2 backend behind `aria_aesni_avx2_glue.c` and consumes `struct aria_ctx` layout offsets from `asm-offsets.h`.

Important APIs/functions: exported typed symbols are `aria_aesni_avx2_encrypt_32way`, `aria_aesni_avx2_decrypt_32way`, `aria_aesni_avx2_ctr_crypt_32way`, `aria_aesni_avx2_gfni_encrypt_32way`, `aria_aesni_avx2_gfni_decrypt_32way`, and `aria_aesni_avx2_gfni_ctr_crypt_32way`. Internal workers include `__aria_aesni_avx2_crypt_32way`, `__aria_aesni_avx2_ctr_gen_keystream_32way`, and `__aria_aesni_avx2_gfni_crypt_32way`.

Control flow: public ECB entry points load either `ARIA_CTX_enc_key` or `ARIA_CTX_dec_key`, load 32 input blocks into YMM registers, byteslice the state, run alternating ARIA FO/FE rounds, branch on `ARIA_CTX_rounds` for 128/192/256-bit key schedules, perform the final round, debyteslice, and write blocks back. CTR paths first build 32 consecutive counter blocks from a big-endian 128-bit IV, encrypt those counters with the encryption key schedule, XOR the encrypted keystream with source blocks, store output, and update the IV by 32 blocks.

State and persistence: no persistent state is stored in this assembly file. It mutates caller-provided output, temporary keystream storage, and the in-request IV pointer. Correctness depends on the C caller entering FPU context with `kernel_fpu_begin()` and only calling this path for full 32-block batches.

Dependencies and integration points: depends on Linux linkage/CFI macros, `FRAME_BEGIN/END`, YMM state availability, AES-NI for AES S-box based transforms, optional GFNI transforms, and exact `aria_ctx` offsets. The glue layer registers this implementation as part of `ecb(aria)` and `ctr(aria)` at AVX2 priority and falls back to AVX or scalar code for smaller tails.

Risks: high risk is in counter carry handling, byteslice/debyteslice ordering, and key-length branch alignment with generic ARIA. The assembly uses destination memory as temporary storage in ECB-style workers, so overlap assumptions must continue to match the skcipher walk helpers. GFNI and non-GFNI paths must remain bit-identical.

Test signals: crypto selftests should cover ARIA ECB and CTR for 128/192/256-bit keys, in-place and out-of-place buffers, non-multiple CTR lengths in the glue fallback, IV low-word overflow near `2^64`, and CPU feature combinations with AVX2 only versus AVX2+GFNI.
