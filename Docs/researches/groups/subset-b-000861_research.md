# subset-b-000861 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx2-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx2-asm_64.S

Purpose: Implements ARIA 32-block parallel encryption, decryption, and CTR keystream XOR for x86_64 with AVX2/AES-NI, plus alternate GFNI S-box paths when the C glue selects them. It is the AVX2 backend behind `aria_aesni_avx2_glue.c` and consumes `struct aria_ctx` layout offsets from `asm-offsets.h`.

Important APIs/functions: exported typed symbols are `aria_aesni_avx2_encrypt_32way`, `aria_aesni_avx2_decrypt_32way`, `aria_aesni_avx2_ctr_crypt_32way`, `aria_aesni_avx2_gfni_encrypt_32way`, `aria_aesni_avx2_gfni_decrypt_32way`, and `aria_aesni_avx2_gfni_ctr_crypt_32way`. Internal workers include `__aria_aesni_avx2_crypt_32way`, `__aria_aesni_avx2_ctr_gen_keystream_32way`, and `__aria_aesni_avx2_gfni_crypt_32way`.

Control flow: public ECB entry points load either `ARIA_CTX_enc_key` or `ARIA_CTX_dec_key`, load 32 input blocks into YMM registers, byteslice the state, run alternating ARIA FO/FE rounds, branch on `ARIA_CTX_rounds` for 128/192/256-bit key schedules, perform the final round, debyteslice, and write blocks back. CTR paths first build 32 consecutive counter blocks from a big-endian 128-bit IV, encrypt those counters with the encryption key schedule, XOR the encrypted keystream with source blocks, store output, and update the IV by 32 blocks.

State and persistence: no persistent state is stored in this assembly file. It mutates caller-provided output, temporary keystream storage, and the in-request IV pointer. Correctness depends on the C caller entering FPU context with `kernel_fpu_begin()` and only calling this path for full 32-block batches.

Dependencies and integration points: depends on Linux linkage/CFI macros, `FRAME_BEGIN/END`, YMM state availability, AES-NI for AES S-box based transforms, optional GFNI transforms, and exact `aria_ctx` offsets. The glue layer registers this implementation as part of `ecb(aria)` and `ctr(aria)` at AVX2 priority and falls back to AVX or scalar code for smaller tails.

Risks: high risk is in counter carry handling, byteslice/debyteslice ordering, and key-length branch alignment with generic ARIA. The assembly uses destination memory as temporary storage in ECB-style workers, so overlap assumptions must continue to match the skcipher walk helpers. GFNI and non-GFNI paths must remain bit-identical.

Test signals: crypto selftests should cover ARIA ECB and CTR for 128/192/256-bit keys, in-place and out-of-place buffers, non-multiple CTR lengths in the glue fallback, IV low-word overflow near `2^64`, and CPU feature combinations with AVX2 only versus AVX2+GFNI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-aesni-avx2-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-avx.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aria-avx.h

Purpose: Shared header for x86 ARIA vector backends. It centralizes block-count constants, exported assembler prototypes, and the runtime dispatch table used by AVX, AVX2, and AVX512 glue files.

Important APIs/types/functions: defines `ARIA_AESNI_PARALLEL_BLOCKS`/`_SIZE` for 16-way AVX, `ARIA_AESNI_AVX2_PARALLEL_BLOCKS`/`_SIZE` for 32-way AVX2, and `ARIA_GFNI_AVX512_PARALLEL_BLOCKS`/`_SIZE` for 64-way AVX512. Declares all 16-way and 32-way AES-NI/GFNI assembler entry points. Defines `struct aria_avx_ops` with function pointers for 16/32/64-way encrypt, decrypt, and CTR operations.

Control flow: this file has no executable control flow. It shapes the dispatch flow in glue files: module init validates CPU features, fills `aria_avx_ops` with the best available implementation, and request handlers call through those pointers for bulk processing.

State and persistence: no runtime state is stored here. `struct aria_avx_ops` instances are static globals in glue modules, not in the header. The constants determine request-context keystream buffer sizes and skcipher walk thresholds.

Dependencies and integration points: includes `linux/types.h` and assumes `ARIA_BLOCK_SIZE` is visible before size constants are used by C files that also include `crypto/aria.h`. The prototypes bind C glue to architecture-specific symbols in `aria-aesni-avx-asm_64.S`, `aria-aesni-avx2-asm_64.S`, and `aria-gfni-avx512-asm_64.S`.

Risks: any mismatch between constants and assembly batch widths causes buffer overrun or missed fast paths. Prototype drift would be especially dangerous for CTR because the argument order includes both a scratch keystream pointer and mutable IV pointer.

Test signals: compile coverage across AVX, AVX2, and AVX512 configs catches declaration mismatches. Runtime crypto tests should verify that each driver consumes exactly its advertised block batch and that request context sizes are adequate for CTR scratch buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-avx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-gfni-avx512-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aria-gfni-avx512-asm_64.S

Purpose: Provides the 64-block parallel ARIA backend for x86_64 AVX512/GFNI. It is the highest-priority ARIA implementation in this subset and implements ECB-style encrypt/decrypt plus CTR bulk processing over ZMM registers.

Important APIs/functions: public symbols are `aria_gfni_avx512_encrypt_64way`, `aria_gfni_avx512_decrypt_64way`, and `aria_gfni_avx512_ctr_crypt_64way`. Internal helpers include `__aria_gfni_avx512_crypt_64way` and `__aria_gfni_avx512_ctr_gen_keystream_64way`. Macros implement byteslicing, ARIA add-round-key, GFNI S-box transforms, diffusion layers, and final round operations.

Control flow: entry points load key schedule pointers for encryption or decryption, prepare 64 input blocks as sixteen ZMM lanes, run ARIA rounds with branches for 12, 14, or 16 rounds, then debyteslice and write output. CTR builds 64 sequential counter blocks, using a fast add path unless the low 64-bit counter may overflow; the carry path uses AVX512 mask registers to propagate high-word increments. The encrypted counters are XORed with source blocks before output.

State and persistence: persistent key state lives in `struct aria_ctx`, supplied by the glue. This file updates caller memory only: output blocks, scratch keystream blocks, and the 128-bit IV. No global data is mutable; lookup/bitmatrix constants are read-only.

Dependencies and integration points: requires AVX512F, AVX512VL, GFNI, OSXSAVE-enabled ZMM state, Linux frame/linkage macros, and generated `ARIA_CTX_*` offsets. `aria_gfni_avx512_glue.c` registers these routines and reuses lower-width GFNI AVX/AVX2 routines for tails.

Risks: the AVX512 counter-generation path has subtle carry and byte-swap logic. Mask-register behavior, ZMM temporary use, and output lane order must remain synchronized with the write macros. Incorrect OS xfeature gating would corrupt task FPU state.

Test signals: compare against generic ARIA for all key sizes and both ECB/CTR; exercise in-place CTR, exactly 64-block requests, 64+tail requests, and IV values near `0xffffffffffffffff` in the low half. Boot/module tests on CPUs with AVX512 but missing GFNI should reject registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria-gfni-avx512-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx2_glue.c

Purpose: Registers the AVX2/AES-NI ARIA skcipher implementations for ECB and CTR and dispatches bulk work to 32-way assembly, optionally choosing GFNI variants at module init.

Important APIs/types/functions: declares and exports 32-way AVX2 and 32-way GFNI assembly functions. Uses `static struct aria_avx_ops aria_ops` as the selected dispatch table and `struct aria_avx2_request_ctx` for CTR scratch keystream storage. Main callbacks are `aria_avx2_ecb_encrypt`, `aria_avx2_ecb_decrypt`, `aria_avx2_ctr_encrypt`, `aria_avx2_set_key`, and `aria_avx2_init_tfm`.

Control flow: ECB walkers process 32-block chunks, then 16-block chunks, then scalar single blocks. CTR walks virtual skcipher segments, processes 32-block and 16-block full batches inside `kernel_fpu_begin/end`, then scalar ARIA blocks, and finally a partial tail only when the current walk segment covers the request end. Module init checks AVX, AVX2, AES, OSXSAVE, and YMM xfeatures, selects GFNI or AES-NI function pointers, and registers two skcipher algorithms at priority 500.

State and persistence: key material is stored in each `struct aria_ctx`. The request context holds only temporary keystream bytes. CTR mutates `walk.iv` as the counter advances. Module-global state is limited to `aria_ops` and registered algorithm metadata.

Dependencies and integration points: depends on `crypto/aria.h`, `ecb_cbc_helpers.h`, `aria-avx.h`, x86 CPU feature helpers, skcipher walk APIs, FPU ownership helpers, and lower-level AVX 16-way symbols for tails. It integrates with the Linux crypto API as `ecb-aria-avx2` and `ctr-aria-avx2`.

Risks: `ECB_WALK_START` is passed the 16-way threshold while 32-way blocks are attempted first; changes to helper semantics could affect fast-path batching. The CTR partial-tail condition must avoid generating a partial keystream before a later walk segment. Missing `CRYPTO_ALG_SKCIPHER_REQSIZE_LARGE` would be risky because the request context stores a 512-byte keystream.

Test signals: crypto manager selftests should select this driver on AVX2 hardware and verify ECB/CTR vectors, tail lengths below 16 blocks, requests spanning walk segments, in-place operation, GFNI and non-GFNI dispatch, and module unload registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx2_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx_glue.c

Purpose: Registers the 16-way AVX/AES-NI ARIA skcipher backend for ECB and CTR, with optional GFNI routines when available.

Important APIs/types/functions: declares and exports 16-way AES-NI and GFNI assembly symbols. Uses `struct aria_avx_ops` for runtime-selected pointers and `struct aria_avx_request_ctx` for one 16-block CTR keystream buffer. Provides `aria_avx_ecb_encrypt`, `aria_avx_ecb_decrypt`, `aria_avx_ctr_encrypt`, `aria_avx_set_key`, and `aria_avx_init_tfm`.

Control flow: module init validates AVX, AES, OSXSAVE, and SSE/YMM xfeatures; then it selects GFNI 16-way routines or regular AES-NI routines and registers `ecb(aria)` plus `ctr(aria)` at priority 400. ECB uses helper macros to process 16-block chunks and scalar tails. CTR walks request segments, runs 16-block chunks in FPU context, then scalar full blocks, then a final partial tail.

State and persistence: per-transform state is `struct aria_ctx`; per-request state is the keystream scratch array. The CTR IV is the only mutable protocol state and is incremented as blocks are consumed. The static dispatch table is set once at module init.

Dependencies and integration points: depends on generic ARIA `aria_set_key`, `aria_encrypt`, `aria_decrypt`, crypto walk helpers, x86 feature probing, and the assembly file `aria-aesni-avx-asm_64.S` for the actual 16-way operations. It is a lower-priority fallback beneath AVX2/AVX512 drivers.

Risks: the assembly routines require FPU ownership, so all vector calls must remain wrapped. Partial CTR handling must only happen on the final segment or the IV/ciphertext stream can diverge. Exported 16-way symbols are also used by AVX2 and AVX512 glue for tail processing, so ABI drift affects multiple modules.

Test signals: validate driver priority selection, generic fallback for short buffers, in-place CTR, sub-block CTR lengths, CPU feature rejection on missing YMM state, and GFNI selection when `X86_FEATURE_GFNI` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria_aesni_avx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria_gfni_avx512_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aria_gfni_avx512_glue.c

Purpose: Registers the AVX512/GFNI ARIA skcipher backend and composes it with lower-width GFNI AVX and AVX2 routines for tail processing.

Important APIs/types/functions: declares 64-way assembly functions, uses `struct aria_avx_ops aria_ops`, and defines `struct aria_avx512_request_ctx` with a 64-block keystream buffer. Main callbacks are `aria_avx512_ecb_encrypt`, `aria_avx512_ecb_decrypt`, `aria_avx512_ctr_encrypt`, `aria_avx512_set_key`, and `aria_avx512_init_tfm`.

Control flow: ECB processing attempts 64-way, then 32-way, then 16-way, then scalar blocks. CTR mirrors that ordering inside skcipher walks, wrapping each vector call with FPU begin/end. Module init requires AVX, AVX2, AVX512F, AVX512VL, GFNI, OSXSAVE, and SSE/YMM/AVX512 xfeatures; then it wires 16-way and 32-way GFNI functions plus 64-way AVX512 functions and registers priority-600 algorithms.

State and persistence: no persistent state beyond registered algorithms and the initialized static dispatch table. Key schedule lives in `struct aria_ctx`; request scratch contains the large keystream buffer; IV state is updated in place.

Dependencies and integration points: depends on `aria-avx.h` declarations for lower-width GFNI functions, the AVX512 assembly symbols in `aria-gfni-avx512-asm_64.S`, skcipher helpers, and x86 FPU/xfeature checks. It supersedes AVX2 when available through crypto API priority.

Risks: the request context is 1024 bytes, so the `CRYPTO_ALG_SKCIPHER_REQSIZE_LARGE` flag is necessary. Correct operation depends on both CPU instruction bits and OS-managed ZMM state. Tail dispatch to lower-width functions assumes those modules/symbols are linked in the same build configuration.

Test signals: boot and module-load tests should confirm registration only on full AVX512/GFNI systems. Crypto tests should cover 64-, 32-, 16-, scalar-, and partial-tail paths, IV carry behavior, and priority selection over AVX2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aria_gfni_avx512_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish-x86_64-asm_64.S

Purpose: Implements x86_64 assembly Blowfish single-block encryption/decryption and 4-block parallel encryption/decryption used by the Blowfish glue module.

Important APIs/functions: exported symbols are `blowfish_enc_blk`, `blowfish_dec_blk`, `blowfish_enc_blk_4way`, and `__blowfish_dec_blk_4way`. Macros define the context layout (`p`, `s0`-`s3`), Blowfish F-function table lookups, endian block packing, and 4-way round-key preloading.

Control flow: single-block functions load an 8-byte block, transform endian/layout, run 16 Feistel rounds through `round_enc` or `round_dec`, apply final P-array whitening, and write the block. The 4-way encryption path loads four blocks, preloads round keys, applies the F-function across four independent registers per round, then writes four blocks. The 4-way decrypt routine accepts a `cbc` flag; after decryption it optionally XORs with previous ciphertext blocks before output.

State and persistence: all persistent state is in `struct bf_ctx`, specifically P-array and S-box tables prepared by generic Blowfish key setup. This assembly mutates only caller-provided output and register temporaries. The CBC 4-way path reads the source ciphertext as chaining input.

Dependencies and integration points: called by `blowfish_glue.c` through the crypto cipher and skcipher APIs. Depends on exact `struct bf_ctx` table layout from `crypto/blowfish.h` and Linux `SYM_FUNC` linkage macros.

Risks: register preservation is manual, including `%r12` and `%rbx`; mistakes can corrupt callers. CBC decryption relies on source blocks still being available for XOR. Endian conversion and 64-bit rotates are performance-sensitive and are why the glue blacklists Pentium 4 by default.

Test signals: use Blowfish known-answer tests for cipher, ECB, and CBC; test 1-, 4-, and non-multiple-of-4 block counts; in-place CBC decrypt; and module behavior with the `force` parameter on blacklisted CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish-x86_64-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish_glue.c

Purpose: Linux crypto API glue for the x86_64 optimized Blowfish implementation. It registers the base cipher and ECB/CBC skcipher variants and routes bulk work to scalar or 4-way assembly.

Important APIs/types/functions: declares assembly entry points, wraps 4-way decrypt into `blowfish_dec_ecb_4way` and `blowfish_dec_cbc_4way`, implements `blowfish_encrypt`, `blowfish_decrypt`, `blowfish_setkey_skcipher`, ECB/CBC request handlers, `is_blacklisted_cpu`, and module init/exit. Registers `blowfish-asm`, `ecb-blowfish-asm`, and `cbc-blowfish-asm`.

Control flow: ECB encrypt/decrypt walkers use 4-way blocks where possible and scalar blocks for tails. CBC encrypt is inherently serial and uses scalar encryption. CBC decrypt can process 4 blocks in parallel because each plaintext block is the decrypted ciphertext XORed with the previous ciphertext block. Module init rejects Pentium 4 unless `force` is set, then registers the cipher algorithm first and skciphers second, rolling back on failure.

State and persistence: key schedule state lives per transform in `struct bf_ctx`. Module-global state is the `force` parameter and registered algorithm metadata. No on-disk or cross-request persistence exists.

Dependencies and integration points: depends on generic `blowfish_setkey`, crypto alg/skcipher registration, and `ecb_cbc_helpers.h`. It provides higher-priority skcipher drivers than generic implementations and a base cipher driver for users of `crypto_cipher`.

Risks: registration rollback unregisters the base cipher if skcipher registration fails, but exit unregisters both unconditionally in normal loaded state. Performance blacklist must be kept architecture-specific. CBC decrypt correctness depends on helper macro ordering and the assembly `cbc` flag.

Test signals: crypto selftests for Blowfish key sizes, ECB/CBC encrypt/decrypt, odd block counts, in-place operation, registration failure injection if available, and blacklisted CPU path with and without `force`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx-asm_64.S

Purpose: Implements 16-block parallel Camellia ECB encryption/decryption and CBC decryption using AVX plus AES-NI-assisted S-box transforms.

Important APIs/functions: public symbols are `camellia_ecb_enc_16way`, `camellia_ecb_dec_16way`, and `camellia_cbc_dec_16way`. Internal helpers `__camellia_enc_blk16` and `__camellia_dec_blk16` perform the core round schedule. Macro groups implement AES-assisted S-box transforms, byteslicing, FL/FLINV layers, key-dependent round loops, and output packing.

Control flow: entry points load 16 blocks, pre-whiten with `key_table`, byteslice into XMM registers, run Camellia round groups and FL layers, branch on `key_length` to include the extra 256/192-bit-key round group, unpack, and write output. CBC decryption uses stack temporary storage to protect in-place operation, then XORs decrypted blocks with previous ciphertext blocks before final output.

State and persistence: persistent state is the `struct camellia_ctx` key table generated in C. This assembly mutates output and stack/destination scratch only. It does not retain state after return.

Dependencies and integration points: called by `camellia_aesni_avx_glue.c` and exported for reuse by AVX2 glue as a 16-way tail. Depends on `camellia_ctx` layout (`key_table`, `key_length`), Linux frame/linkage macros, AVX, AES-NI, and SSE/YMM state management by the caller.

Risks: the transformed S-box tables and lane order are hard to audit and must match scalar Camellia exactly. CBC decrypt has in-place overlap concerns and manually arranged XOR order. Any key table layout change must update both C and assembly.

Test signals: Camellia known-answer tests for 128/192/256-bit keys, ECB and CBC decrypt, exactly 16-block requests, 16+tail requests through glue, and in-place CBC decrypt should exercise this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx2-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx2-asm_64.S

Purpose: Implements 32-block parallel Camellia ECB encryption/decryption and CBC decryption using AVX2 and AES-NI.

Important APIs/functions: exports `camellia_ecb_enc_32way`, `camellia_ecb_dec_32way`, and `camellia_cbc_dec_32way`. Internal functions `__camellia_enc_blk32` and `__camellia_dec_blk32` hold the core round flow. Macros provide 32-way byteslicing, AES-assisted S-box transforms, FL layers, round scheduling, and writeback.

Control flow: public functions call `vzeroupper`, load and byte-swap 32 input blocks into YMM registers, select encryption or decryption key start, use destination or stack as scratch depending on overlap, and call the core crypt helper. The helper runs base round groups, inserts FL layers, branches on `key_length` to process the larger-key rounds, unpacks lanes, and returns for writeback. CBC decrypt XORs decrypted output with previous ciphertext blocks after preserving the first decrypted block as needed.

State and persistence: uses only caller-owned `struct camellia_ctx`, destination memory, and stack scratch. No global mutable state. The use of `vzeroupper` manages architectural vector state hygiene rather than persistent data.

Dependencies and integration points: called by `camellia_aesni_avx2_glue.c`, which gates AVX2/AES-NI/OSXSAVE support and falls back to 16-way/scalar tails. Depends on exact key table offsets and on helper C key schedule behavior.

Risks: AVX2 lane ordering and output transposition are fragile. CBC decrypt has special in-place handling with a 512-byte stack allocation. Missing `vzeroupper` or incorrect FPU wrapping in callers can cause performance or state issues.

Test signals: run Camellia ECB/CBC vectors for all key sizes, exactly 32-block CBC decrypt, in-place and out-of-place decrypt, 32+16+2+1 fallback mixes, and module tests on CPUs with AVX but no AVX2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx2-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-x86_64-asm_64.S

Purpose: Provides scalar and 2-way x86_64 assembly Camellia block operations used by the baseline Camellia asm module and by wider AES-NI modules for tails.

Important APIs/functions: exports `__camellia_enc_blk`, `camellia_dec_blk`, `__camellia_enc_blk_2way`, and `camellia_dec_blk_2way`. Macros reference the eight Camellia S-box tables exported from `camellia_glue.c`, define key table offsets, implement F-function rounds, FL/FLINV layers, endian packing, optional XOR output for CBC encryption helpers, and two-block parallel variants.

Control flow: scalar encryption loads one 16-byte block, pre-whitens, runs three or four groups of six rounds depending on key length, applies FL layers, and writes or XORs output. Scalar decryption starts from the selected terminal whitening key, conditionally includes the higher-key round group, then reverses round order. Two-way routines perform the same logic over two blocks interleaved in registers.

State and persistence: all key state is read from `struct camellia_ctx`. Output is written directly or XORed with existing destination when the caller requests the XOR variant. No persistent mutable state is kept by the assembly.

Dependencies and integration points: depends on S-box globals from `camellia_glue.c`, `camellia_ctx` layout from `camellia.h`, and Linux CFI/linkage macros. It is used by `camellia_glue.c`, `camellia_aesni_avx_glue.c`, and `camellia_aesni_avx2_glue.c`.

Risks: because the S-box tables live in C, link visibility and symbol names are part of the ABI. The boolean XOR mode in encryption must remain aligned with `camellia_enc_blk_xor` wrappers. Manual preservation of callee-saved registers and endian rotations are correctness-sensitive.

Test signals: scalar and 2-way paths are exercised by short ECB/CBC requests below vector batch sizes, CBC encryption, CBC decryption tails, all key lengths, and in-place requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-x86_64-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia.h

Purpose: Architecture-local Camellia interface header defining the context layout and assembler/glue contracts shared across scalar, AVX, and AVX2 implementations.

Important APIs/types/functions: defines key/block sizes, `CAMELLIA_TABLE_BYTE_LEN`, `CAMELLIA_PARALLEL_BLOCKS`, and `struct camellia_ctx` containing `u64 key_table[34]` plus `u32 key_length`. Declares `__camellia_setkey`, scalar block functions, 2-way functions, 16-way AVX/AES-NI functions, and `camellia_decrypt_cbc_2way`. Provides inline wrappers that hide the boolean XOR parameter for encryption.

Control flow: no standalone execution. The inline wrappers route normal encrypt calls to `__camellia_enc_blk(..., false)` and CBC/XOR helpers to `__camellia_enc_blk(..., true)`, and similarly for 2-way operation.

State and persistence: establishes the persistent transform state layout. The key table stores expanded subkeys; `key_length` controls whether 24- or 32-round schedules are used by both C and assembly.

Dependencies and integration points: included by Camellia glue and assembly-coupled C code in this directory. Includes `crypto/b128ops.h`, Linux crypto/kernel headers, and exposes symbols used across separate modules through `EXPORT_SYMBOL_GPL` in `camellia_glue.c` and AVX glue.

Risks: this header is an ABI contract with hand-written assembly. Changing `CAMELLIA_TABLE_BYTE_LEN`, field order, prototypes, or wrapper semantics requires synchronized assembly offset changes. The header declares 16-way functions but the AVX2 glue also declares 32-way functions locally.

Test signals: build tests catch prototype drift; runtime vectors for scalar, 2-way, 16-way, and 32-way paths catch layout or key-length mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx2_glue.c

Purpose: Registers the AVX2/AES-NI Camellia ECB and CBC skcipher implementations at higher priority than the AVX and scalar asm variants.

Important APIs/functions: declares `camellia_ecb_enc_32way`, `camellia_ecb_dec_32way`, and `camellia_cbc_dec_32way`. Uses `camellia_setkey`, `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, `cbc_decrypt`, and module init/exit callbacks. Registers `ecb-camellia-aesni-avx2` and `cbc-camellia-aesni-avx2` at priority 500.

Control flow: module init checks AVX, AVX2, AES, OSXSAVE, and SSE/YMM xfeatures before registering skciphers. ECB handlers process 32-way chunks, then 16-way chunks, then 2-way and scalar tails. CBC encrypt remains scalar because encryption is chaining-dependent. CBC decrypt processes 32-way, 16-way, 2-way, and scalar chunks.

State and persistence: per-transform state is `struct camellia_ctx`; no request-specific context is needed. Module state is limited to registered algorithm descriptors.

Dependencies and integration points: depends on `camellia.h`, `ecb_cbc_helpers.h`, x86 feature helpers, AVX2 assembly, AVX 16-way exported symbols, and scalar/2-way exports from `camellia_glue.c`.

Risks: feature gating must reject unsupported OS YMM state. The fallback chain spans symbols from multiple compilation units, so Kconfig/linkage changes can break tails. CBC decrypt correctness depends on helper macro walking order matching assembly assumptions about previous ciphertext.

Test signals: verify driver priority selection, 32-block and mixed-size ECB/CBC requests, all key sizes, in-place CBC decrypt, scalar tails, and module load failure on missing AVX2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx2_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx_glue.c

Purpose: Registers the 16-way AVX/AES-NI Camellia ECB and CBC skcipher backend.

Important APIs/functions: declares and exports `camellia_ecb_enc_16way`, `camellia_ecb_dec_16way`, and `camellia_cbc_dec_16way`. Implements `camellia_setkey`, ECB/CBC callbacks, and module init/exit. Registers priority-400 `ecb-camellia-aesni` and `cbc-camellia-aesni`.

Control flow: module init validates AVX, AES, OSXSAVE, and YMM xfeatures, then registers algorithms. ECB encrypt/decrypt use 16-way vector blocks, then 2-way scalar asm, then single-block asm. CBC encrypt uses scalar encryption only. CBC decrypt uses 16-way vector decrypt, then 2-way CBC helper, then scalar decrypt.

State and persistence: transform state is `struct camellia_ctx` produced by `__camellia_setkey`; no per-request scratch is allocated by the glue. Module state is only registration metadata.

Dependencies and integration points: depends on exported scalar/2-way functions from `camellia_glue.c`, vector assembly from `camellia-aesni-avx-asm_64.S`, x86 CPU feature checks, and `ecb_cbc_helpers.h`. It also exports the 16-way routines so AVX2 glue can reuse them for tails.

Risks: all vector calls depend on crypto helper/FPU handling in the broader x86 crypto framework. Exported symbol ABI must remain stable for AVX2 tail use. CBC decrypt must preserve source ciphertext for chaining when buffers overlap.

Test signals: crypto selftests should cover 16-block boundaries, all key sizes, CBC decrypt in-place, fallback to 2-way/single tails, and module rejection on CPUs lacking AES-NI or OSXSAVE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_glue.c

Purpose: Baseline x86_64 Camellia glue and key schedule implementation. It exports scalar/2-way assembly symbols, S-box tables, key expansion, CBC helper logic, and crypto API registrations.

Important APIs/types/functions: exports `__camellia_enc_blk`, `camellia_dec_blk`, `__camellia_enc_blk_2way`, `camellia_dec_blk_2way`, `__camellia_setkey`, and `camellia_decrypt_cbc_2way`. Contains eight 256-entry S-box tables, sigma constants, `camellia_setup128`, `camellia_setup192`, `camellia_setup256`, `camellia_setup_tail`, and crypto callbacks for cipher/ECB/CBC registration.

Control flow: key setup validates 16/24/32-byte keys, records `key_length`, builds KL/KR/KA/KB-derived subkeys with rotations and Camellia F-functions, and reshapes subkeys for assembly consumption. Request handlers use 2-way blocks for ECB and CBC decrypt where possible, scalar for tails, and scalar CBC encryption. Module init blacklists Pentium 4 unless `force` is set, registers the base cipher, then skciphers with rollback on failure.

State and persistence: per-transform persistent state is `struct camellia_ctx` containing expanded key material and key length. S-box tables are read-only globals visible to assembly. Module-global mutable state is the `force` parameter and registration state only.

Dependencies and integration points: uses Linux unaligned big-endian loads, crypto registration APIs, `ecb_cbc_helpers.h`, and the scalar assembly file. Exports are reused by AVX and AVX2 modules for tails and shared key setup.

Risks: key expansion is dense and feeds hand-written assembly; subkey ordering bugs affect every optimized Camellia driver. `camellia_decrypt_cbc_2way` has explicit in-place handling by copying the IV block when needed. Blacklist logic is performance-driven and should not hide functional regressions.

Test signals: known-answer tests for all key sizes, raw cipher API, ECB/CBC skcipher API, invalid key lengths, 2-way CBC decrypt in-place, module registration rollback, and AVX/AVX2 tail reuse all exercise this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast5-avx-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/cast5-avx-x86_64-asm_64.S

Purpose: Implements 16-block parallel CAST5 ECB encryption/decryption and CBC decryption using x86_64 AVX/SSE registers. It is the assembly backend used by `cast5_avx_glue.c`.

Important APIs/functions: public symbols are `cast5_ecb_enc_16way`, `cast5_ecb_dec_16way`, and `cast5_cbc_dec_16way`; internal helpers are `__cast5_enc_blk16` and `__cast5_dec_blk16`. The file references external S-box tables `cast_s1` through `cast_s4` and expects `struct cast5_ctx` layout fields `Km`, `Kr`, and round count.

Control flow: ECB entry points load 16 64-bit blocks into XMM pairs, call the encrypt or decrypt helper, then write swapped left/right halves. Round macros broadcast masking subkeys, derive rotation counts, perform CAST5 F1/F2/F3 S-box lookups through scalar GPRs for two lanes at a time, and XOR results into Feistel halves. Decryption reverses key order and checks the context round count for reduced-round keys. CBC decrypt decrypts 16 blocks, then XORs each plaintext with the prior ciphertext block before writing.

State and persistence: key schedule and round count live in `struct cast5_ctx`; S-boxes are read-only external data. The assembly mutates only output buffers and registers. CBC decrypt reads source ciphertext as chaining state.

Dependencies and integration points: depends on `cast5_avx_glue.c` for CPU xfeature gating, crypto registration, and scalar fallback. Requires Linux linkage/frame macros, AVX/SSE register state, and generic CAST5 symbols/tables.

Risks: the implementation mixes vector lanes with scalar S-box table loads, so register allocation and callee-saved preservation are delicate. CBC decrypt assumes source remains intact while output is produced. Round count handling must match CAST5 reduced-round behavior for short keys.

Test signals: CAST5 ECB/CBC vectors with minimum and maximum key sizes, reduced-round keys, exactly 16-block decrypt, in-place CBC decrypt, non-16-block fallback through glue, and CPU xfeature rejection should cover the integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast5-avx-x86_64-asm_64.S -->
