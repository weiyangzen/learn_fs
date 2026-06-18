# sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx-asm_64.S

### Purpose
`aria-aesni-avx-asm_64.S` implements 16-way parallel ARIA block cipher helpers for x86_64 using AVX and AES-NI, with optional GFNI variants. It is not an AES mode implementation; it uses AES instructions and affine transformations to accelerate ARIA S-boxes and provides ECB-style 16-block encrypt/decrypt helpers plus CTR keystream encryption helpers for ARIA glue code elsewhere in the kernel.

### Important APIs, Types, And Functions
Exported functions are `aria_aesni_avx_encrypt_16way()`, `aria_aesni_avx_decrypt_16way()`, `aria_aesni_avx_ctr_crypt_16way()`, `aria_aesni_avx_gfni_encrypt_16way()`, `aria_aesni_avx_gfni_decrypt_16way()`, and `aria_aesni_avx_gfni_ctr_crypt_16way()`. Internal functions are `__aria_aesni_avx_crypt_16way()`, `__aria_aesni_avx_ctr_gen_keystream_16way()`, and `__aria_aesni_avx_gfni_crypt_16way()`. The assembly relies on ARIA context offsets from `asm-offsets.h`, including `ARIA_CTX_rounds`, `ARIA_CTX_enc_key`, and `ARIA_CTX_dec_key`. Major macros handle byte slicing, de-byte-slicing, round-key addition, ARIA FO/FE/FF rounds, S-box implementations using AES-NI or GFNI, diffusion layers, CTR increment, and output writes.

### Control Flow
Encrypt and decrypt wrappers load 16 input blocks into XMM registers, select encryption or decryption round keys, byte-slice the blocks, run the shared 16-way crypt core, de-byte-slice, and write 16 blocks. The shared core performs alternating ARIA FO and FE rounds, checking `ARIA_CTX_rounds` to choose the 12-round, 14-round, or 16-round final sequence for 128/192/256-bit keys. AES-NI S-box macros isolate AES SubBytes via `vaesenclast`/`vaesdeclast` and apply affine tables; GFNI variants replace these table-filtered affine steps with `vgf2p8affine*` instructions. CTR generation loads the big-endian 128-bit IV, byte-swaps to little endian for increments, constructs 16 counter blocks, writes back the IV advanced by 16, encrypts the counters, XORs them with source, and writes output.

### State, Persistence, And Dependencies
Persistent state is the ARIA context supplied by the caller, including round count and expanded round keys. CTR mode mutates the caller-provided IV to the next counter after 16 blocks. Temporary byte-sliced state is held in XMM registers and, during the core, in scratch memory based on the destination pointer. Dependencies include x86_64, AVX VEX-encoded XMM operations, AES-NI for the base path, GFNI for the GFNI path, Linux typed linkage, frame macros, and generated ARIA structure offsets.

### Integration Points
This file is called by ARIA x86 glue code that batches full 16-block chunks and handles mode-level request walking and tail processing. It complements scalar or smaller parallel ARIA implementations by providing high throughput for large ECB/CTR-style workloads. The CTR helper's keystream buffer parameter lets the function build counter blocks, encrypt them through the same 16-way core, and avoid exposing byteslicing details to the caller.

### Risks
The round-count branches must match ARIA key schedule semantics exactly; using the wrong `ARIA_CTX_rounds` value corrupts all output. The byte-slice/de-byte-slice register ordering is subtle and must match `write_output()` ordering. CTR IV update is observable state and must stay consistent across batched calls. GFNI and non-GFNI paths must remain equivalent despite different S-box implementations. The scratch-memory use through the destination pointer assumes the caller provides writable output space for the full 16-block batch.

### Test Signals
Tests should compare AESNI-AVX and GFNI outputs against generic ARIA for 128/192/256-bit keys, both encryption and decryption, 16-block ECB batches, CTR batches with IV continuation across multiple calls, in-place CTR if supported by glue, CPU feature dispatch between GFNI and non-GFNI paths, and randomized multi-block differential tests around round-count boundaries.
