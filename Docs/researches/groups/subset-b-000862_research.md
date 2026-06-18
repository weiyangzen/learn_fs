# subset-b-000862 research

Grouped research for x86 crypto vector implementations and 32-bit x86 entry code in the ceph-client source tree. Each section is wrapped with deterministic file markers so reconciliation can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast5_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/cast5_avx_glue.c

Purpose: This file is the Linux Crypto API glue for the AVX CAST5 skcipher implementation. It registers high-priority ECB and CBC variants that use 16-way assembly routines for bulk work and generic CAST5 block helpers for leftovers or serial CBC encryption.

Important APIs/types/functions: The exported-to-assembly prototypes are `cast5_ecb_enc_16way`, `cast5_ecb_dec_16way`, and `cast5_cbc_dec_16way`. `cast5_setkey_skcipher()` adapts `cast5_setkey()` to `struct crypto_skcipher`. The request handlers are `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt`. `cast5_algs[]` registers `ecb(cast5)` as `ecb-cast5-avx` and `cbc(cast5)` as `cbc-cast5-avx` with priority 200.

Control flow: Module init first checks that the CPU and OS expose SSE/YMM xstate through `cpu_has_xfeatures(XFEATURE_MASK_SSE | XFEATURE_MASK_YMM)`. If available, skcipher registration exposes the algorithms. ECB encrypt/decrypt walks the request with `ECB_WALK_START`, processes 16-block chunks under `kernel_fpu_begin()` with AVX assembly, then drops to one-block `__cast5_encrypt` or `__cast5_decrypt` for the tail. CBC encryption is intentionally serial because each block depends on the previous ciphertext. CBC decryption processes independent ciphertext blocks 16 at a time and XORs the decrypted first block with the incoming IV through the shared helper.

State and persistence: Persistent state is limited to per-transform `struct cast5_ctx` key schedule storage and the registered algorithm table. Request state is local to `skcipher_walk`, including source/destination pointers, residual byte count, and CBC IV updates. No file-backed state exists.

Dependencies and integration points: It depends on `crypto/cast5.h`, `crypto/algapi.h`, `crypto/internal/skcipher.h` through `ecb_cbc_helpers.h`, x86 FPU save/restore APIs, and the matching AVX assembly object that provides the 16-way symbols. It integrates with the Crypto API module loader through `MODULE_ALIAS_CRYPTO("cast5")`.

Risks and test signals: The FPU section must begin only for full vector chunks and must be closed before generic scalar fallbacks. CBC in-place decryption depends on the helper preserving the previous ciphertext before overwrite. Tests should include Crypto API CAST5 ECB/CBC vectors, in-place and out-of-place requests, unaligned scatterlists, non-multiple request tails, CPU feature refusal on missing YMM state, and module unload after active transform teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast5_avx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6-avx-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/cast6-avx-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements 8-way AVX CAST6 block transforms for ECB encryption, ECB decryption, and CBC decryption. It performs CAST6 rounds over two groups of four 128-bit blocks using XMM registers, table lookups, byte shuffles, and shared AVX load/store helpers.

Important APIs/types/functions: Public symbols are `cast6_ecb_enc_8way`, `cast6_ecb_dec_8way`, and `cast6_cbc_dec_8way`. Local worker symbols `__cast6_enc_blk8` and `__cast6_dec_blk8` run the vectorized round function on already-loaded registers. Important macros include `F1_2`, `F2_2`, `F3_2`, `Q`, `QBAR`, `get_round_keys`, `preload_rkr`, `transpose_4x4`, `inpack_blocks`, and `outunpack_blocks`. The code uses CAST S-box symbols `cast_s1` through `cast_s4` and key schedule offsets `km` and `kr`.

Control flow: The public ECB entry loads eight source blocks with `load_8way`, calls the encryption or decryption core, and stores eight output blocks. The encryption core byte-swaps and transposes blocks into SIMD lanes, preloads masking/rotation metadata, runs the twelve CAST6 quad-round groups in the encryption order, then transposes and byte-swaps output back. Decryption executes the same structural pipeline with reversed key order and inverse Q/QBAR sequence. CBC decryption preserves the source pointer, decrypts eight blocks, then `store_cbc_8way` XORs plaintext with the previous ciphertext chain and updates the output.

State and persistence: The routine is stateless apart from the caller-owned CAST6 context. It consumes the expanded key schedule at fixed offsets and uses volatile vector and general registers, saving the callee-saved registers it uses (`r15`, `rbx`, and for CBC `r12`). No persistent global state is modified.

Dependencies and integration points: It includes `linux/linkage.h`, `asm/frame.h`, and `glue_helper-asm-avx.S`. It is called by `cast6_avx_glue.c` under `kernel_fpu_begin()` after SSE/YMM xstate has been validated. Correct integration depends on the CAST6 generic key schedule layout and the shared `cast_s*` S-box tables.

Risks and test signals: Table lookup indexing and byte-lane transposition must exactly match the CAST6 big-endian block format. Any mismatch in key schedule offsets, Q/QBAR order, or CBC store order causes silent ciphertext divergence. Tests should use CAST6 known-answer vectors, ECB/CBC decrypt/encrypt round trips for exactly 8 blocks and mixed tails, in-place CBC decrypt, objtool/unwind validation, and CPU feature gating through the glue module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6-avx-x86_64-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/cast6_avx_glue.c

Purpose: This file registers AVX-accelerated CAST6 ECB and CBC skcipher algorithms. It connects Crypto API requests to the 8-way x86-64 AVX assembly implementation while retaining scalar generic CAST6 helpers for serial CBC encryption and residual blocks.

Important APIs/types/functions: Assembly entry points are `cast6_ecb_enc_8way`, `cast6_ecb_dec_8way`, and `cast6_cbc_dec_8way`. `cast6_setkey_skcipher()` wraps `cast6_setkey()`. Request handlers `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt` are registered in `cast6_algs[]` for `ecb(cast6)` and `cbc(cast6)` with driver names `ecb-cast6-avx` and `cbc-cast6-avx`.

Control flow: `cast6_init()` refuses registration unless SSE and YMM xstate are available. For ECB, the helper macro opens an skcipher walk, enters the kernel FPU for chunks of at least eight blocks, invokes the 8-way assembly routine, then exits the FPU before one-block scalar fallback. CBC encrypt walks one block at a time because chaining prevents parallel encryption. CBC decrypt uses 8-way assembly for bulk decryption and then scalar `__cast6_decrypt` for the tail.

State and persistence: Per-transform state is `struct cast6_ctx` stored in the Crypto API context. The CBC IV is updated in the walk object after each processed group. Registered algorithm state persists only while the module is loaded.

Dependencies and integration points: It depends on the generic CAST6 implementation, the shared `ecb_cbc_helpers.h` macro framework, x86 FPU/xstate support, and the assembly file in the same directory. It integrates with module autoloading through `MODULE_ALIAS_CRYPTO("cast6")`.

Risks and test signals: The vector path assumes callers never reach it without `kernel_fpu_begin()`. The helper threshold must match the 8-block assembly contract. Tests should cover CAST6 ECB/CBC known-answer vectors, request sizes below/at/above eight blocks, in-place CBC decrypt, fallback behavior for remainders, feature-gated module load failure, and comparison against the generic `cast6` driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/cast6_avx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/ecb_cbc_helpers.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/ecb_cbc_helpers.h

Purpose: This header provides macro templates for x86 block-cipher skcipher ECB and CBC request walking. It is designed for glue files that need direct calls to vector assembly and scalar fallbacks without indirect-call overhead.

Important APIs/types/functions: `ECB_WALK_START` and `CBC_WALK_START` declare local walk state, calculate whether the FPU/vector path should be active, and begin `kernel_fpu_begin()` when a segment has enough blocks. `ECB_BLOCK` calls a block function repeatedly for a fixed block count. `CBC_ENC_BLOCK` implements serial CBC encryption with `crypto_xor_cpy`. `CBC_DEC_BLOCK` handles parallel CBC decryption, preserving the last ciphertext block for IV update and in-place safety. `ECB_WALK_END` and `CBC_WALK_END` close the FPU section and call `skcipher_walk_done`.

Control flow: A glue handler expands `*_WALK_START`, one or more `*_BLOCK` invocations from largest to smallest block grouping, and `*_WALK_END`. The generated loop advances through each contiguous skcipher segment. When the code transitions from vector chunk size to smaller scalar chunks, the macro ends the kernel FPU section so scalar C helpers run outside vector state ownership.

State and persistence: All state is local macro-expanded stack state: `ctx`, `skcipher_walk`, `nbytes`, `src`, `dst`, `do_fpu`, and a small IV preservation buffer. The only persistent mutation is the caller-visible CBC IV in `walk.iv`, carried across segments.

Dependencies and integration points: It includes `crypto/internal/skcipher.h` and `asm/fpu/api.h`. Consumers must provide block functions with the signature `(ctx, dst, src)` and must pass accurate block sizes and vector block counts. It integrates many x86 CAST, Serpent, and Twofish glue files with the Crypto API walk model.

Risks and test signals: Because these are macros, variable names and control-flow structure are part of the contract; misuse can compile but corrupt data. `fpu_blocks == -1` disables FPU ownership for scalar-only paths. In-place CBC decrypt relies on the local buffer before overwrite. Tests should stress segmented scatterlists, zero-length and tail requests, transitions from vector to scalar fallback, IV continuity across walk segments, and lockdep/preemption-sensitive FPU usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/ecb_cbc_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx.S

Purpose: This small include file defines common XMM load/store helper macros for 8-way AVX block-cipher assembly wrappers. It keeps ECB and CBC I/O packing consistent across CAST6, Serpent, and Twofish AVX implementations.

Important APIs/types/functions: `load_8way(src, x0..x7)` loads eight 16-byte blocks from consecutive memory into XMM registers. `store_8way(dst, x0..x7)` stores eight XMM registers back to consecutive output blocks. `store_cbc_8way(src, dst, x0..x7)` XORs decrypted blocks with the previous CBC chain using ciphertext from `src`, then stores the resulting plaintext.

Control flow: Consumer assembly calls `load_8way`, runs its cipher core, and then calls either `store_8way` for ECB or `store_cbc_8way` for CBC decrypt. The CBC helper XORs block zero with the caller's current IV already carried in the first loaded chain register convention and subsequent blocks with previous ciphertext from memory.

State and persistence: The macros have no persistent state. They operate on caller-selected vector registers and memory pointers. Their effects are the loads from `src` and stores to `dst`.

Dependencies and integration points: The include is pulled into x86-64 AVX assembly files after register conventions are defined. It depends on 16-byte block ciphers and on callers arranging decrypted block registers in the order expected by the store macro.

Risks and test signals: A register-order mismatch in a consumer silently corrupts ECB output or CBC chaining. In-place CBC requires source memory still contain ciphertext when the store helper reads previous blocks. Tests should include exact 8-block ECB/CBC vectors, in-place CBC decrypt, and inspection of all users after register convention changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx2.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx2.S

Purpose: This include file provides YMM load/store helper macros for 16-way AVX2 block-cipher wrappers. It is the AVX2 counterpart of the 8-way helper and is used by 16-block Serpent and similar assembly code.

Important APIs/types/functions: `load_16way(src, x0..x7)` loads sixteen 16-byte blocks as eight 32-byte YMM vectors. `store_16way(dst, x0..x7)` stores those eight YMM vectors. `store_cbc_16way(src, dst, x0..x7, t0)` handles CBC decryption output by XORing decrypted plaintext candidates with the previous IV/ciphertext chain, using a temporary register to bridge lanes.

Control flow: A consumer loads sixteen blocks, transposes/crypts them, and writes either direct ECB output or CBC-decrypted output. CBC store logic must account for the fact that one YMM register contains two adjacent blocks, so it uses permutation/alignment operations and a temporary register to form the correct chain.

State and persistence: It has no persistent state. Runtime state is the caller's vector register set and source/destination memory. Output mutation is limited to the destination range and, indirectly, caller-managed IV state in higher-level glue.

Dependencies and integration points: It assumes AVX2/YMM state ownership and a 16-byte block size. It integrates with `serpent-avx2-asm_64.S` and any other 16-way block-cipher assembly using the same register ordering.

Risks and test signals: The CBC helper is sensitive to lane order and source/destination overlap. A missing `vzeroupper` in caller code can also hurt mixed SSE/AVX transitions. Tests should compare 16-block CBC decrypt against scalar reference, include overlapping in-place buffers, and run with tails that force glue fallback after one 16-block group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements 8-way AVX Serpent block encryption, block decryption, and CBC decryption. It processes two four-block groups in parallel with XMM registers and bit-sliced Serpent S-box macros.

Important APIs/types/functions: Public symbols are `serpent_ecb_enc_8way_avx`, `serpent_ecb_dec_8way_avx`, and `serpent_cbc_dec_8way_avx`; they are typed for CFI and exported by the glue file. Local cores `__serpent_enc_blk8_avx` and `__serpent_dec_blk8_avx` perform the 32-round cipher. Macro families `S0_1` through `S7_2`, `SI0_1` through `SI7_2`, `K2`, `LK2`, `KL2`, `S`, `SP`, `transpose_4x4`, `read_blocks`, and `write_blocks` express Serpent's S-box, linear transform, key mixing, and bit-sliced packing.

Control flow: The ECB wrappers load eight blocks, call the encrypt or decrypt core, then store reordered output registers. The encrypt core initializes an all-ones mask, transposes input blocks into bit-sliced lanes, applies key 0, runs 32 Serpent S-box/linear-transform rounds with keys 1 through 31, applies final key 32, and transposes back. Decryption reads blocks, applies key 32, walks inverse S-boxes and inverse linear transforms down to key 0, then writes plaintext. CBC decrypt decrypts eight ciphertext blocks and uses `store_cbc_8way` to XOR with the prior ciphertext chain.

State and persistence: The file owns no global state. It reads `struct serpent_ctx` round keys through the context pointer and uses volatile XMM registers. Public wrappers rely on the caller having enabled kernel FPU/vector usage.

Dependencies and integration points: It includes `linux/linkage.h`, `linux/cfi_types.h`, `asm/frame.h`, and `glue_helper-asm-avx.S`. It is used by `serpent_avx_glue.c` and by AVX2 glue as an 8-block fallback. The C header `serpent-avx.h` declares the ABI.

Risks and test signals: Bit-sliced Serpent is extremely register-order-sensitive: wrong transposition, inverse S-box ordering, or final store ordering changes every block. CBC chaining depends on ciphertext still being readable. Tests should include Serpent known-answer vectors, 8-block ECB/CBC bulk paths, AVX2 fallback users, in-place decrypt, objtool/CFI symbol validation, and mixed-size requests that leave scalar tails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx-x86_64-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx.h

Purpose: This header declares the AVX Serpent 8-way assembly ABI used by x86 Serpent glue modules.

Important APIs/types/functions: `SERPENT_PARALLEL_BLOCKS` is set to 8. The declared routines are `serpent_ecb_enc_8way_avx`, `serpent_ecb_dec_8way_avx`, and `serpent_cbc_dec_8way_avx`, each taking a cipher context, destination pointer, and source pointer. It forward-declares `struct crypto_skcipher` and includes Serpent and block operation headers.

Control flow: There is no runtime control flow in this header. C glue includes it to size walk thresholds and call the assembly entry points.

State and persistence: The header defines no storage. It describes use of caller-owned context and request buffers.

Dependencies and integration points: It depends on `crypto/serpent.h`, `crypto/b128ops.h`, and Linux integer types. It connects `serpent_avx_glue.c`, `serpent_avx2_glue.c`, and the AVX assembly implementation.

Risks and test signals: The constant must match the assembly's exact block count. A prototype mismatch would break the x86-64 calling convention at runtime. Build tests across AVX and AVX2 modules and Crypto API Serpent vectors are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx2-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx2-asm_64.S

Purpose: This assembly file implements the AVX2 16-way Serpent fast path for x86-64. It doubles the AVX 8-way structure by using YMM registers and AVX2 load/store helpers.

Important APIs/types/functions: Public functions are `serpent_ecb_enc_16way`, `serpent_ecb_dec_16way`, and `serpent_cbc_dec_16way`. Local cores `__serpent_enc_blk16` and `__serpent_dec_blk16` run the bit-sliced cipher. Macro families mirror the AVX file but use YMM registers: S-boxes `S0` through `S7`, inverse S-boxes `SI0` through `SI7`, key helpers `K2`, `LK2`, `KL2`, and block transposition helpers. `load_16way`, `store_16way`, and `store_cbc_16way` come from `glue_helper-asm-avx2.S`.

Control flow: ECB wrappers clear upper vector state with `vzeroupper`, load sixteen blocks, call the encrypt/decrypt core, store the results, clear upper state again, and return. The encrypt core transposes sixteen blocks into bit-sliced YMM lanes, applies all Serpent rounds in order, and transposes back. The decrypt core performs the inverse sequence from round key 32 down to 0. CBC decrypt decrypts sixteen blocks and uses the AVX2 CBC store helper to XOR with the input chain.

State and persistence: No persistent state is stored. The code reads Serpent round keys from the caller's context and mutates destination buffers. It uses YMM registers and therefore requires correct XSAVE/YMM ownership from the caller.

Dependencies and integration points: It includes `linux/linkage.h`, `asm/frame.h`, and `glue_helper-asm-avx2.S`. It is registered through `serpent_avx2_glue.c`, which also depends on the AVX 8-way functions for fallback.

Risks and test signals: AVX2 lane ordering, `vzeroupper`, and CBC chain construction are key integration risks. The glue's FPU threshold uses the 8-way constant, so the assembly must be safe when called only for 16-block chunks. Tests should cover exact 16-block requests, 16+8+tail decomposition, CBC in-place decryption, CPU gating for AVX2/OSXSAVE/YMM, and known-answer comparisons against generic Serpent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx2-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-i586-asm_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-i586-asm_32.S

Purpose: This i386 assembly file implements 4-way SSE2 Serpent encryption and decryption for 32-bit x86. It provides the low-level routines behind the shared SSE2 Serpent glue on CONFIG_X86_32 builds.

Important APIs/types/functions: Public symbols are `__serpent_enc_blk_4way` and `serpent_dec_blk_4way`. The encryption symbol accepts an extra `bool xor` argument that selects either normal write or XOR-with-existing-output behavior through the `xor_blocks` macro. Macro groups define key loading (`get_key`, `K`, `LK`, `KL`), Serpent S-boxes and inverse S-boxes (`S0` through `S7`, `SI0` through `SI7`), block transposition, and read/write/xor helpers.

Control flow: The encrypt routine reads four blocks from the source, transposes them into bit-sliced SSE registers, applies the Serpent round sequence with linear transforms, and writes or XORs output depending on the caller's flag. The decrypt routine reads four encrypted blocks, applies inverse rounds, and writes plaintext. The i386 calling convention uses stack argument offsets for context, destination, source, and the XOR flag.

State and persistence: The code is stateless apart from the caller's Serpent context. It uses XMM registers and stack-passed arguments. Output is written to the request destination; no global state changes.

Dependencies and integration points: It includes `linux/linkage.h` and is declared by `serpent-sse2.h`. `serpent_sse2_glue.c` calls it through inline wrappers and gates module registration on `X86_FEATURE_XMM2`.

Risks and test signals: The 32-bit ABI and stack offsets are fragile. SSE2 register use must match kernel FPU ownership in the glue helpers. Tests should include 32-bit build coverage, 4-block and tail Serpent vectors, CBC decrypt through the glue helper, in-place requests, and verification that the XOR-enabled encrypt path is only used by callers that expect it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-i586-asm_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements the SSE2 Serpent 8-way block routines used when AVX is not required or not selected. It is structurally similar to the AVX implementation but uses SSE2-compatible XMM instructions and the x86-64 calling convention.

Important APIs/types/functions: Public symbols are `__serpent_enc_blk_8way` and `serpent_dec_blk_8way`. The encryption entry accepts a `bool xor` parameter for normal output or XOR output. The file defines two-lane S-box macros (`S0_1`/`S0_2`, etc.), inverse macros, `K2`, `LK2`, `KL2`, `SP`, `transpose_4x4`, `read_blocks`, `write_blocks`, and `xor_blocks`.

Control flow: Eight input blocks are arranged as two four-block groups in XMM registers. Encryption runs key mixing and 32 Serpent rounds, then either writes the generated ciphertext or XORs it into the destination depending on the flag. Decryption applies the inverse round schedule and writes plaintext. The C glue's CBC helper handles chaining after decryption.

State and persistence: It has no persistent state and reads only the caller-provided Serpent key schedule. It mutates destination buffers and uses XMM registers under the caller's FPU ownership.

Dependencies and integration points: It includes `linux/linkage.h`; `serpent-sse2.h` declares its ABI for non-32-bit builds. `serpent_sse2_glue.c` registers the Crypto API algorithms and checks `X86_FEATURE_XMM2`.

Risks and test signals: Register ordering differs between encrypted and decrypted outputs, so the write macros must match the C wrapper expectation. Build and runtime tests should include x86-64 SSE2-only module loading, 8-block Serpent known-answer vectors, CBC in-place decrypt, XOR path coverage from any XTS/LRW-style users, and comparison with generic Serpent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-x86_64-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2.h

Purpose: This header abstracts the 32-bit and 64-bit SSE2 Serpent assembly ABIs behind common inline wrappers for glue code.

Important APIs/types/functions: On `CONFIG_X86_32`, `SERPENT_PARALLEL_BLOCKS` is 4 and declarations target `__serpent_enc_blk_4way` plus `serpent_dec_blk_4way`. Otherwise the parallel count is 8 and declarations target `__serpent_enc_blk_8way` plus `serpent_dec_blk_8way`. Inline wrappers `serpent_enc_blk_xway`, `serpent_enc_blk_xway_xor`, and `serpent_dec_blk_xway` normalize the caller interface and set the encryption XOR flag.

Control flow: The header has no standalone runtime flow. Glue code calls the common inline names, which dispatch to the architecture-width-specific assembly entry points.

State and persistence: It owns no state. It passes caller-owned `struct serpent_ctx`, source, and destination pointers to assembly.

Dependencies and integration points: It includes `linux/crypto.h` and `crypto/serpent.h`. It connects `serpent_sse2_glue.c` to either `serpent-sse2-i586-asm_32.S` or `serpent-sse2-x86_64-asm_64.S`.

Risks and test signals: The parallel block constant must match the selected assembly routine and the glue walk thresholds. Tests should compile both 32-bit and 64-bit configurations and run Serpent vector tests across ECB and CBC modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx2_glue.c

Purpose: This file registers the highest-priority AVX2 Serpent ECB and CBC skcipher implementations. It layers a 16-block AVX2 path over the existing 8-block AVX and scalar fallbacks.

Important APIs/types/functions: It declares `serpent_ecb_enc_16way`, `serpent_ecb_dec_16way`, and `serpent_cbc_dec_16way`. `serpent_setkey_skcipher()` calls `__serpent_setkey()`. `serpent_algs[]` registers `ecb-serpent-avx2` and `cbc-serpent-avx2` with priority 600 and aliases `serpent`/`serpent-asm`.

Control flow: Init checks `X86_FEATURE_AVX2`, `X86_FEATURE_OSXSAVE`, and SSE/YMM xstate. ECB handlers process 16-block AVX2 chunks, then 8-block AVX chunks, then one-block generic Serpent. CBC encryption remains scalar; CBC decryption uses 16-way, then 8-way, then scalar paths. The shared helper starts the FPU section when at least eight blocks are available, so both vector widths run under FPU ownership.

State and persistence: Persistent module state is the registered skcipher table. Per-transform state is `struct serpent_ctx`. Request-local state is in `skcipher_walk` and CBC IV.

Dependencies and integration points: It depends on `serpent-avx.h` for the 8-way fallback ABI, `ecb_cbc_helpers.h`, generic Serpent key setup/block routines, and the AVX2 assembly file. It integrates with Crypto API priority selection above AVX and SSE2 drivers.

Risks and test signals: The AVX2 driver has a stronger CPU feature contract than the AVX fallback it calls. If the AVX module symbols are not linked/exported as expected, registration or calls fail. Tests should cover driver priority selection, AVX2 feature refusal, 16+8+tail decomposition, CBC in-place decrypt, and generic equivalence vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx2_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx_glue.c

Purpose: This file registers AVX-accelerated Serpent ECB and CBC skcipher algorithms and exports the 8-way AVX assembly symbols for other optimized modules.

Important APIs/types/functions: Exported symbols are `serpent_ecb_enc_8way_avx`, `serpent_ecb_dec_8way_avx`, and `serpent_cbc_dec_8way_avx`. `serpent_setkey_skcipher()` initializes `struct serpent_ctx`. `serpent_algs[]` registers `ecb-serpent-avx` and `cbc-serpent-avx` with priority 500.

Control flow: Module init verifies SSE and YMM xstate. ECB encrypt/decrypt handlers walk the skcipher request, use AVX 8-way routines for bulk, and fall back to `__serpent_encrypt`/`__serpent_decrypt` one block at a time. CBC encrypt is scalar, while CBC decrypt uses the 8-way assembly before scalar tail handling.

State and persistence: Per-transform key schedule state lives in `struct serpent_ctx`; algorithm registration persists while the module is loaded. No additional global mutable state is created.

Dependencies and integration points: It depends on generic Serpent, the shared helper macros, x86 FPU xstate support, and the AVX assembly file. Exported symbols are consumed by `serpent_avx2_glue.c`.

Risks and test signals: Because this module exports assembly entry points, ABI stability matters for AVX2 fallback users. Tests should include module dependency loading, Serpent ECB/CBC known-answer vectors, in-place CBC decrypt, requests smaller than eight blocks, and xstate-gated load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_avx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_sse2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_sse2_glue.c

Purpose: This file registers SSE2-accelerated Serpent ECB and CBC skcipher algorithms for x86. It supports 4-way operation on 32-bit and 8-way operation on 64-bit through `serpent-sse2.h`.

Important APIs/types/functions: `serpent_setkey_skcipher()` wraps `__serpent_setkey`. `serpent_decrypt_cbc_xway()` adapts the assembly decrypt routine for CBC by preserving previous ciphertext blocks and XORing all but the first block. `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt` are registered in `serpent_algs[]` under driver names `ecb-serpent-sse2` and `cbc-serpent-sse2` with priority 400.

Control flow: Init refuses registration unless the boot CPU advertises SSE2. ECB handlers use the x-way assembly wrapper for bulk and generic scalar helpers for tails. CBC encrypt is scalar. CBC decrypt calls `serpent_decrypt_cbc_xway` for full x-way groups and then scalar decrypt for remainders.

State and persistence: Runtime state consists of `struct serpent_ctx`, walk-local pointers and IV, and a small stack buffer in the CBC x-way helper for in-place decryption safety. Registered algorithms persist until module exit.

Dependencies and integration points: It depends on `serpent-sse2.h`, generic Serpent, `crypto/b128ops.h`, the shared ECB/CBC helper macros, and x86 SSE2 assembly. It provides a lower-priority fallback beneath AVX and AVX2 implementations.

Risks and test signals: The CBC helper has a custom in-place preservation path because the generic CBC macro only XORs the first block. Tests should cover both 32-bit and 64-bit parallel widths, exact x-way group sizes, in-place CBC decrypt, scalar tails, and priority fallback when AVX drivers are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent_sse2_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx-asm_64.S

Purpose: This x86-64 assembly file implements AES-NI/AVX accelerated SM4 primitives for up to 8 parallel blocks, CTR encryption, and CBC decryption. It uses AES `aesenclast` plus affine transforms to implement the SM4 S-box efficiently.

Important APIs/types/functions: Public symbols are `sm4_aesni_avx_crypt4`, `sm4_aesni_avx_crypt8`, `sm4_aesni_avx_ctr_enc_blk8`, and `sm4_aesni_avx_cbc_dec_blk8`. Local `__sm4_crypt_blk8` performs the 32 SM4 rounds. Key macros include `transpose_4x4`, `transform_pre`, `transform_post`, `ROUND`, and `inc_le128`. Constant tables provide byte-swap masks, affine transform lookup masks, inverse shift rows, and rotate masks.

Control flow: `sm4_aesni_avx_crypt4` handles 1 to 4 blocks by loading available blocks, byte-swapping, transposing, iterating 32 rounds in groups of four round-key broadcasts, then storing only requested outputs. `sm4_aesni_avx_crypt8` delegates to the 4-block path for small counts, otherwise loads 5 to 8 blocks and calls `__sm4_crypt_blk8`. CTR builds eight counter blocks from the IV, stores the incremented IV, encrypts the counters, and XORs keystream with input. CBC decrypt decrypts eight ciphertext blocks, XORs with IV/previous ciphertext, updates IV with the last ciphertext block, and stores plaintext.

State and persistence: It mutates only destination buffers and the caller-provided IV for CTR/CBC helpers. Round keys are read from the `struct sm4_ctx` arrays passed by C glue. It clears vector state with `vzeroall` before returning from major public paths.

Dependencies and integration points: It includes linkage, CFI type metadata, and frame annotations. It is called by `sm4_aesni_avx_glue.c` under `kernel_fpu_begin()` after AVX, AES-NI, OSXSAVE, and YMM xstate checks.

Risks and test signals: Counter endian handling and carry propagation are critical for CTR. CBC must preserve ciphertext for IV update under in-place operation. S-box affine tables must match SM4 exactly. Tests should include SM4 ECB/CBC/CTR vectors, partial block-count calls from 1 to 8 full blocks, CTR carry near 2^64 low-counter wrap, in-place CBC decrypt, and CPU feature gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx2-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx2-asm_64.S

Purpose: This file implements AVX2/AES-NI SM4 16-block CTR and CBC-decrypt primitives. It widens the AVX algorithm to YMM registers while still using AES round hardware to realize the SM4 S-box.

Important APIs/types/functions: Public symbols are `sm4_aesni_avx2_ctr_enc_blk16` and `sm4_aesni_avx2_cbc_dec_blk16`. Local `__sm4_crypt_blk16` encrypts sixteen counter or ciphertext blocks. Macros include `transpose_4x4`, `transform_pre`, `transform_post`, `ROUND`, and `inc_le128`; the code also uses XMM subregister aliases for AES-NI operations on YMM lanes.

Control flow: The core byte-swaps and transposes sixteen blocks, iterates 32 SM4 rounds with round-key broadcasts, then transposes and byte-swaps back. CTR constructs sixteen counter blocks from the IV, handles low 64-bit counter overflow with a slower carry path when needed, stores IV+16, encrypts counters, XORs with source, and stores output. CBC decrypt loads sixteen ciphertext blocks, decrypts them, XORs with IV and previous ciphertext blocks, writes the last ciphertext as the new IV, and stores plaintext.

State and persistence: The only persistent mutation visible to callers is IV advancement/update for CTR/CBC and output buffer writes. Round keys remain caller-owned. The routine uses `vzeroupper`/`vzeroall` around AVX2 work to manage vector state transitions.

Dependencies and integration points: It includes linkage, CFI types, and frame annotations. It is registered by `sm4_aesni_avx2_glue.c`, which shares common ECB/CBC/CTR glue from the AVX module for smaller chunks and scalar tails.

Risks and test signals: The 16-counter construction must preserve big-endian counter semantics and handle carry correctly. CBC lane order across 32-byte YMM vectors is a subtle source of errors. Tests should cover 16-block CTR/CBC vectors, IV wrap boundary, in-place CBC, AVX2 feature gating, and decomposition of long requests into 16-block plus smaller fallback chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-aesni-avx2-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-avx.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-avx.h

Purpose: This header defines the shared C ABI for SM4 AVX and AVX2 glue code. It allows the AVX2 module to reuse common ECB, CBC encrypt, CBC decrypt, and CTR request-walking helpers from the AVX implementation.

Important APIs/types/functions: `sm4_crypt_func` is a function pointer for bulk helpers taking round keys, destination, source, and IV. Declarations include `sm4_avx_ecb_encrypt`, `sm4_avx_ecb_decrypt`, `sm4_cbc_encrypt`, `sm4_avx_cbc_decrypt`, and `sm4_avx_ctr_crypt`.

Control flow: There is no standalone execution. AVX and AVX2 glue code call these helpers with an appropriate block size and assembly function pointer for the selected vector width.

State and persistence: The header owns no state. It describes mutation of caller request buffers and IV through `struct skcipher_request`.

Dependencies and integration points: It includes Linux types and `crypto/sm4.h`. It integrates `sm4_aesni_avx_glue.c` and `sm4_aesni_avx2_glue.c`.

Risks and test signals: Function-pointer signatures must match the assembly wrappers and common C helpers. Build tests should ensure both modules link, and runtime tests should verify that AVX2 can call AVX-provided shared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-avx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx2_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx2_glue.c

Purpose: This file registers AVX2/AES-NI SM4 skcipher drivers for ECB, CBC, and CTR. It reuses common AVX helper functions for ECB and scalar fallback while supplying 16-block AVX2 CBC decrypt and CTR functions.

Important APIs/types/functions: Assembly functions are `sm4_aesni_avx2_ctr_enc_blk16` and `sm4_aesni_avx2_cbc_dec_blk16`. `sm4_skcipher_setkey()` calls `sm4_expandkey()`. Local handlers `cbc_decrypt()` and `ctr_crypt()` call `sm4_avx_cbc_decrypt()` and `sm4_avx_ctr_crypt()` with `SM4_CRYPT16_BLOCK_SIZE`. `sm4_aesni_avx2_skciphers[]` registers `ecb-sm4-aesni-avx2`, `cbc-sm4-aesni-avx2`, and `ctr-sm4-aesni-avx2` with priority 500.

Control flow: Init checks AVX, AVX2, AES-NI, OSXSAVE, and SSE/YMM xstate before registering. ECB encrypt/decrypt use shared AVX helpers, which process up to 8 blocks at a time rather than the AVX2 assembly file. CBC decrypt and CTR use 16-block AVX2 function pointers for large chunks and common helper fallback for smaller chunks/tails.

State and persistence: Per-transform state is `struct sm4_ctx` containing expanded encryption and decryption round keys. Request state includes `skcipher_walk` and IV updates for CBC/CTR. Registered algorithms persist until module exit.

Dependencies and integration points: It depends on `sm4-avx.h`, generic SM4 key expansion, x86 FPU APIs, and the AVX2 assembly file. It integrates as the higher-priority SM4 implementation above the AVX driver.

Risks and test signals: Since ECB is reused from the AVX glue, priority selection may not imply wider ECB execution. Function-pointer block size must match 16-block assembly. Tests should cover SM4 ECB/CBC/CTR vectors, AVX2 module loading without the AVX common helpers failing to resolve, 16-block bulk paths, scalar tails, and IV continuity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx2_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx_glue.c

Purpose: This file implements common SM4 AVX/AES-NI skcipher glue and exports reusable request handlers for AVX2. It registers ECB, CBC, and CTR SM4 algorithms and provides generic walking logic for vector and scalar tails.

Important APIs/types/functions: Assembly functions are `sm4_aesni_avx_crypt4`, `sm4_aesni_avx_crypt8`, `sm4_aesni_avx_ctr_enc_blk8`, and `sm4_aesni_avx_cbc_dec_blk8`. Exported helpers are `sm4_avx_ecb_encrypt`, `sm4_avx_ecb_decrypt`, `sm4_cbc_encrypt`, `sm4_avx_cbc_decrypt`, and `sm4_avx_ctr_crypt`. `sm4_aesni_avx_skciphers[]` registers `ecb(sm4)`, `cbc(sm4)`, and `ctr(sm4)` with priority 400.

Control flow: `ecb_do_crypt()` walks segments, opens the kernel FPU, processes 8-block chunks via assembly, then uses the 1-to-4-block assembly helper for residual full blocks. CBC encryption is serial with `sm4_crypt_block`. CBC decrypt accepts a caller-supplied vector block size/function, processes bulk chunks, then handles up to 8 remaining blocks with a stack keystream buffer and reverse XOR to preserve CBC dependencies. CTR similarly accepts a vector function, processes bulk chunks, handles up to 8 full-block counters in software, and finally processes a short final tail only when it is the last walk segment.

State and persistence: Per-transform state is `struct sm4_ctx` with expanded round keys. CBC and CTR mutate `walk.iv` as part of the Crypto API contract. The exported helper symbols are persistent module interfaces for the AVX2 module.

Dependencies and integration points: It depends on `asm/fpu/api.h`, `crypto/internal/skcipher.h`, `crypto/sm4.h`, and `sm4-avx.h`. It integrates with the Crypto API and module autoloading through aliases `sm4` and `sm4-aesni-avx`.

Risks and test signals: FPU begin/end scopes wrap all vector code and stack keystream use. CTR tail handling must only consume partial bytes on the final segment. CBC decrypt pointer arithmetic walks backwards through a temporary keystream buffer and is sensitive to `nblocks` bounds. Tests should include SM4 official ECB/CBC/CTR vectors, partial CTR tails, segmented scatterlists, IV carry and persistence, in-place CBC decrypt, and missing AVX/AES/YMM feature load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4_aesni_avx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-avx-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-avx-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements 8-way AVX Twofish ECB encryption, ECB decryption, and CBC decryption. It bit-packs two groups of four blocks into XMM registers and performs table-based Twofish G-functions in parallel.

Important APIs/types/functions: Public symbols are `twofish_ecb_enc_8way`, `twofish_ecb_dec_8way`, and `twofish_cbc_dec_8way`. Local cores are `__twofish_enc_blk8` and `__twofish_dec_blk8`. Macros include `lookup_32bit`, `G`, `round_head_2`, `encround_tail`, `decround_tail`, `encrypt_cycle`, `decrypt_cycle`, `inpack_blocks`, `outunpack_blocks`, and register preload helpers. Context offsets `s0` through `s3`, `w`, and `k` match `struct twofish_ctx`.

Control flow: Public wrappers load eight blocks, call the local encrypt/decrypt core, and store ECB or CBC output. The encrypt core applies input whitening, transposes blocks, runs eight Twofish round cycles, applies output whitening, and returns encrypted registers in a reordered layout. Decryption starts from output whitening keys, runs inverse cycles, then applies input whitening. CBC decrypt uses `store_cbc_8way` after decrypting to combine with IV/previous ciphertext.

State and persistence: The assembly reads only the caller's expanded Twofish context and writes destination memory. It preserves the callee-saved general registers it uses and has no globals.

Dependencies and integration points: It includes `glue_helper-asm-avx.S` and is called by `twofish_avx_glue.c` under FPU ownership. It also depends on `twofish.h` declarations and the generic Twofish key schedule layout.

Risks and test signals: Table offsets and block transposition must match the generic Twofish representation. CBC output order must align with the helper macro's chain assumptions. Tests should include Twofish known-answer vectors, 8-block ECB/CBC paths, in-place CBC decrypt, mixed 8/3/1 fallback decomposition, and xstate-gated module loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-avx-x86_64-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-i586-asm_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-i586-asm_32.S

Purpose: This 32-bit x86 assembly file implements single-block Twofish encryption and decryption. It is the i386 counterpart to the x86-64 single-block assembly and backs the base `twofish-asm` cipher driver on 32-bit builds.

Important APIs/types/functions: Public symbols are `twofish_enc_blk` and `twofish_dec_blk`. Macros define argument stack offsets, block word offsets, `struct twofish_ctx` table offsets, input/output whitening, `encrypt_round`, `encrypt_last_round`, `decrypt_round`, and `decrypt_last_round`.

Control flow: Encryption loads a 16-byte block, applies input whitening from context `w`, runs the Twofish round sequence using precomputed S-box tables and round keys, applies output whitening, and stores the block. Decryption performs the inverse order with the decryption round macros. The code uses 32-bit general registers and byte subregisters for table lookups.

State and persistence: No persistent state is owned. It reads the expanded Twofish context passed on the stack and writes the output block. Callee-saved register handling is part of the assembly routine's ABI.

Dependencies and integration points: It includes `linux/linkage.h` and `asm/asm-offsets.h`. It is linked with `twofish_glue.c`, which registers the Crypto API cipher and exports the symbols to multi-block modules.

Risks and test signals: Stack argument offsets and context table offsets are critical. Byte-register lookup code is sensitive to partial-register behavior and endianness. Tests should cover 32-bit build/link, Twofish known-answer vectors for all key lengths, unaligned source/destination, and module interactions with 3-way or AVX glue where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-i586-asm_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64-3way.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64-3way.S

Purpose: This x86-64 assembly file implements 3-way parallel Twofish encryption and decryption using general-purpose 64-bit registers. It improves throughput on out-of-order CPUs without requiring SIMD.

Important APIs/types/functions: Public symbols are `__twofish_enc_blk_3way` and `twofish_dec_blk_3way`. The encryption function accepts an XOR flag used by wrapper code. Macros include `do16bit_ror`, `swap_ab_with_cd`, `g1g2_3`, `encrypt_round3`, `decrypt_round3`, `encrypt_cycle3`, `decrypt_cycle3`, `inpack3`, `outunpack3`, `inpack_enc3`, `outunpack_enc3`, `inpack_dec3`, and `outunpack_dec3`.

Control flow: The encryption entry packs three input blocks into register pairs, applies whitening and eight round cycles, and writes or XORs output depending on the flag. Decryption packs ciphertext, runs inverse cycles, and writes plaintext. Stack slots hold parts of the third block while registers are reused for table lookups and round arithmetic.

State and persistence: The file has no global state. It reads the caller's Twofish context and mutates only destination buffers. It saves/restores callee-saved registers as required by the x86-64 ABI.

Dependencies and integration points: It includes linkage and CFI type headers. `twofish_glue_3way.c` exports the symbols, registers skcipher modes, and decides whether to disable the module on CPUs where this implementation is slower.

Risks and test signals: The performance benefit is CPU-dependent, and the glue blacklists Atom/Pentium 4 unless forced. Correctness risks include packed register ordering, XOR-output mode, and table offsets. Tests should include 3-block ECB vectors, CBC decrypt through the C helper, forced and blacklisted module load paths, and comparison against single-block Twofish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64-3way.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements the base single-block Twofish encryption and decryption routines for the `twofish-asm` cipher driver.

Important APIs/types/functions: Public typed symbols are `twofish_enc_blk` and `twofish_dec_blk`. Macros define context offsets for S-box tables, whitening keys, and round keys, plus `input_whitening`, `output_whitening`, `encrypt_round`, `encrypt_last_round`, `decrypt_round`, and `decrypt_last_round`.

Control flow: Encryption loads the four 32-bit block words, XORs input whitening keys, executes Twofish's round structure with precomputed table lookups and key additions, applies output whitening, and stores output. Decryption reverses the process with decryption round macros and reversed whitening use.

State and persistence: The routines are stateless beyond the caller-owned `struct twofish_ctx`. They use general-purpose registers and preserve callee-saved state needed by the ABI.

Dependencies and integration points: It includes `linux/linkage.h`, CFI type metadata, and `asm/asm-offsets.h`. `twofish_glue.c` registers and exports these routines; 3-way and AVX modules use them as scalar fallbacks.

Risks and test signals: Context layout offsets must match `crypto/twofish.h`. Endianness and table lookup byte selection are correctness-sensitive. Tests should include all official Twofish key sizes, fallback paths from AVX/3-way glue, unaligned buffers, and CFI/objtool validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish.h

Purpose: This header declares x86 Twofish assembly entry points shared by base, 3-way, and AVX glue files.

Important APIs/types/functions: It declares `twofish_enc_blk` and `twofish_dec_blk` for single-block assembly, `__twofish_enc_blk_3way` and `twofish_dec_blk_3way` for 3-way parallel assembly, and `twofish_dec_blk_cbc_3way` as a C helper exported by the 3-way glue. It includes `crypto/twofish.h` and `crypto/b128ops.h`.

Control flow: There is no runtime control flow. Consumers include the header to call the appropriate block function and to compose fallback chains.

State and persistence: The header owns no state and exposes caller-owned context/buffer APIs.

Dependencies and integration points: It ties `twofish_glue.c`, `twofish_glue_3way.c`, `twofish_avx_glue.c`, and their assembly files together. The declarations must match both i386 and x86-64 assembly symbol ABIs where applicable.

Risks and test signals: Prototype mismatches can corrupt registers or stack state. Build tests with all x86 Twofish variants enabled and Crypto API vector tests through each driver are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_avx_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_avx_glue.c

Purpose: This file registers AVX-accelerated Twofish ECB and CBC skcipher drivers. It uses 8-way AVX routines for bulk work, 3-way routines for medium tails, and single-block assembly for final tails or serial CBC encryption.

Important APIs/types/functions: Assembly symbols are `twofish_ecb_enc_8way`, `twofish_ecb_dec_8way`, and `twofish_cbc_dec_8way`. `twofish_enc_blk_3way()` wraps `__twofish_enc_blk_3way(..., false)`. Request handlers `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, and `cbc_decrypt` register in `twofish_algs[]` with priority 400.

Control flow: Init verifies SSE/YMM xstate before registration. ECB paths process 8-block AVX chunks, 3-block 3-way chunks, and one-block scalar chunks. CBC encryption remains scalar. CBC decrypt uses 8-way AVX, then 3-way CBC helper, then scalar fallback.

State and persistence: Per-transform state is `struct twofish_ctx`. The module exports only registered algorithms; request state and IV updates live in `skcipher_walk`.

Dependencies and integration points: It depends on base Twofish symbols from `twofish_glue.c`, 3-way symbols from `twofish_glue_3way.c`, the AVX assembly file, `twofish.h`, and `ecb_cbc_helpers.h`. It integrates as the highest-priority Twofish driver in this set.

Risks and test signals: The fallback chain crosses module boundaries, so link/load ordering matters. The helper starts the FPU only for 8-block chunks and ends it before 3-way/scalar fallbacks. Tests should cover request sizes 1, 3, 8, and combinations such as 11 or 12 blocks, in-place CBC decrypt, blacklisted CPU behavior of the 3-way provider, and comparison against generic Twofish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_avx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue.c

Purpose: This file registers the base x86 assembly-optimized Twofish `crypto_alg` cipher driver. It exposes single-block encrypt/decrypt wrappers for the legacy cipher API and exports the assembly symbols to higher-level modes.

Important APIs/types/functions: Assembly functions `twofish_enc_blk` and `twofish_dec_blk` are exported with `EXPORT_SYMBOL_GPL`. `twofish_encrypt()` and `twofish_decrypt()` adapt the assembly routines to `struct crypto_tfm`. `alg` registers `twofish` under driver name `twofish-asm` with priority 200 and `CRYPTO_ALG_TYPE_CIPHER`.

Control flow: Module init calls `crypto_register_alg(&alg)`. Cipher users call setkey through generic `twofish_setkey`, then single-block encrypt/decrypt through the wrapper functions. Module exit unregisters the algorithm.

State and persistence: Per-transform state is `struct twofish_ctx`. The only module-level state is the static registration descriptor. The assembly exports persist while the module is loaded.

Dependencies and integration points: It depends on generic Twofish key setup and the architecture-specific single-block assembly files. It provides fallback symbols for 3-way and AVX skcipher modules.

Risks and test signals: This is the common scalar fallback, so any bug affects all higher-level optimized variants. Tests should run Crypto API cipher vectors for all Twofish key sizes, ensure exported symbols resolve for dependent modules, and compare skcipher fallbacks against this base driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue_3way.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue_3way.c

Purpose: This file registers 3-way parallel Twofish ECB and CBC skcipher drivers and exports the 3-way block routines for AVX fallback chains. It includes CPU blacklist logic to avoid slower implementations on in-order or rotate-slow processors.

Important APIs/types/functions: It exports `__twofish_enc_blk_3way`, `twofish_dec_blk_3way`, and `twofish_dec_blk_cbc_3way`. `twofish_dec_blk_cbc_3way()` preserves previous ciphertext for in-place CBC decrypt and XORs blocks after 3-way decryption. `tf_skciphers[]` registers `ecb-twofish-3way` and `cbc-twofish-3way` with priority 300. `is_blacklisted_cpu()` checks Intel Atom Bonnell/Saltwell and Pentium 4 families. The `force` module parameter bypasses the blacklist.

Control flow: Init refuses registration if the CPU is blacklisted and `force` is unset. ECB handlers process 3-block chunks with 3-way routines and one-block tails with base assembly. CBC encrypt is scalar. CBC decrypt uses the CBC 3-way helper then scalar tails. Exit unregisters the skcipher table.

State and persistence: Persistent state includes the static `force` module parameter and registered algorithms. Per-transform state is `struct twofish_ctx`; request state is held by `skcipher_walk`.

Dependencies and integration points: It depends on x86 CPU identification, generic Twofish, the base single-block assembly symbols, the 3-way assembly file, and shared ECB/CBC helpers. It is both a standalone skcipher provider and a dependency for `twofish_avx_glue.c`.

Risks and test signals: CPU blacklist accuracy affects performance and algorithm availability. In-place CBC decrypt relies on a two-block buffer before overwriting. Tests should cover blacklist and `force` behavior, 3-block and tail vectors, module export resolution, and comparison against the base Twofish cipher.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue_3way.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/entry/Makefile

Purpose: This Makefile controls the build of x86 low-level entry code, syscall support, vDSO/vsyscall subdirectories, preemption thunks, FRED entry code, and IA32 compatibility entry code.

Important APIs/types/functions: It disables KASAN, UBSAN, and KCOV instrumentation for the directory. It removes ftrace flags from syscall objects, adds `-fno-stack-protector` to syscall C objects and FRED C entry code, builds `entry.o`, `entry_$(BITS).o`, and `syscall_$(BITS).o`, and conditionally adds `thunk.o`, `entry_64_fred.o`, `entry_fred.o`, `entry_64_compat.o`, and `syscall_32.o`.

Control flow: Kbuild evaluates architecture bitness and config symbols. The resulting object list determines whether 32-bit or 64-bit entry assembly is built, whether FRED support is present, and whether IA32 emulation adds compatibility paths.

State and persistence: It has no runtime state. It persists build policy that keeps entry code free of instrumentation that would be unsafe in noinstr/entry contexts.

Dependencies and integration points: It integrates with top-level x86 Kbuild, vDSO and vsyscall subdirectories, syscall C files, preemption thunk code, FRED config, and IA32 emulation.

Risks and test signals: Incorrect instrumentation flags can introduce calls or stack protector references into early entry paths where they are unsafe. Tests should include x86 32-bit and 64-bit builds, FRED-enabled builds, IA32 emulation builds, objtool/noinstr validation, and checking that syscall objects remain free of ftrace and stack protector instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/calling.h -->
# sources/distributed-fs/ceph-client/arch/x86/entry/calling.h

Purpose: This assembly header defines x86 entry calling conventions, register save/restore macros, PTI CR3 switching helpers, speculation mitigation helpers, stack erasure hooks, percpu base loading, and thunk generation for both 64-bit and 32-bit entry code.

Important APIs/types/functions: Major macros include `PUSH_REGS`, `CLEAR_REGS`, `PUSH_AND_CLEAR_REGS`, `POP_REGS`, `SWITCH_TO_KERNEL_CR3`, `SWITCH_TO_USER_CR3_NOSTACK`, `SWITCH_TO_USER_CR3_STACK`, `SAVE_AND_SWITCH_TO_KERNEL_CR3`, `PARANOID_RESTORE_CR3`, `IBRS_ENTER`, `IBRS_EXIT`, `FENCE_SWAPGS_USER_ENTRY`, `FENCE_SWAPGS_KERNEL_ENTRY`, `STACKLEAK_ERASE_NOCLOBBER`, `SAVE_AND_SET_GSBASE`, `STACKLEAK_ERASE`, `LOAD_CPU_AND_NODE_SEG_LIMIT`, `GET_PERCPU_BASE`, and `THUNK`. Constants define PTI page-table and PCID mask bits.

Control flow: Consumers expand these macros in syscall, interrupt, exception, and thunk paths. Register macros construct or tear down `pt_regs` frames. PTI macros inspect and mutate CR3, including PCID no-flush behavior and per-CPU user PCID flush masks. IBRS and swapgs macros insert alternative-patched speculation barriers depending on CPU features and mitigation config. Thunk macros preserve argument registers around C calls and return through the architecture's safe return sequence.

State and persistence: The macros manipulate architectural state: general registers, stack frames, CR3, MSR_IA32_SPEC_CTRL, GS base, percpu offsets, and optional stackleak state. Persistent state touched indirectly includes per-CPU TLB state and speculation-control shadow variables.

Dependencies and integration points: It depends on jump labels, unwind hints, CPU feature alternatives, page types, percpu definitions, asm offsets, processor flags, ptrace ABI offsets, MSR helpers, and nospec branch macros. It is included by `entry.S`, `entry_32.S`, and 64-bit entry files.

Risks and test signals: This header is central to entry safety; offset or mitigation mistakes can corrupt pt_regs, return on the wrong CR3, leak registers to speculation, or break unwind metadata. Tests should include objtool validation, PTI on/off boots, PCID and non-PCID systems, IBRS and swapgs mitigation permutations, stackleak builds, SMP and !SMP builds, and syscall/interrupt stress with unwinding enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/calling.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry.S -->
# sources/distributed-fs/ceph-client/arch/x86/entry/entry.S

Purpose: This common x86 entry assembly file defines shared low-level helpers and exported symbols used by both native entry code and KVM. It lives partly in `.noinstr.text` and `.entry.text` because the routines are called in sensitive entry/exit contexts.

Important APIs/types/functions: `write_ibpb` writes `MSR_IA32_PRED_CMD` with `x86_pred_cmd` and fills the return buffer if needed. `__WARN_trap` emits a `ud1` trap for WARN handling. `x86_verw_sel` is a cache-line-aligned kernel data-segment selector disguised as entry text so VERW can be addressed after page-table switches. `THUNK warn_thunk_thunk, __warn_thunk` creates a register-preserving warning thunk. The file exports `write_ibpb`, `__WARN_trap`, `x86_verw_sel`, and `__ref_stack_chk_guard` under stack protector/SMP conditions.

Control flow: `write_ibpb` is called by mitigation code to issue an indirect branch prediction barrier and optionally clear RSB state. `__WARN_trap` deliberately traps and returns only if the trap machinery resumes. Exit-to-user paths can reference `x86_verw_sel` while KPTI is active for MDS-style buffer clearing. The generated thunk saves registers, calls the C warning thunk, restores registers, and returns.

State and persistence: It writes CPU MSRs and may affect branch predictor/RSB microarchitectural state. `x86_verw_sel` is persistent read-only entry text data. No ordinary kernel heap or file state is used.

Dependencies and integration points: It depends on `calling.h`, MSR indexes, unwind hints, segment definitions, cache alignment, CPU feature alternatives, and nospec helpers. KVM references exported mitigation symbols.

Risks and test signals: These symbols sit in noinstr/entry contexts, so instrumentation and unwind annotations must remain correct. IBPB/RSB clearing must use the right MSR value and feature predicate. Tests should include objtool noinstr validation, KVM module symbol resolution, WARN trap behavior, mitigation selftests, and boot tests with stack protector plus SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/entry/entry_32.S

Purpose: This file contains the 32-bit x86 low-level syscall, interrupt, exception, NMI, double-fault, context-switch, fork-return, PTI, ESPFIX, and entry-stack assembly paths. It constructs `pt_regs`, switches stacks and CR3 values, calls C handlers, and restores user or kernel state.

Important APIs/types/functions: Key macros include `SWITCH_TO_USER_CR3`, `BUG_IF_WRONG_CR3`, `SWITCH_TO_KERNEL_CR3`, `FIXUP_FRAME`, `IRET_FRAME`, `SAVE_ALL`, `SAVE_ALL_NMI`, `RESTORE_REGS`, `RESTORE_ALL_NMI`, `CHECK_AND_APPLY_ESPFIX`, `SWITCH_TO_KERNEL_STACK`, `SWITCH_TO_ENTRY_STACK`, `PARANOID_EXIT_TO_KERNEL_MODE`, `idtentry`, `idtentry_irq`, `FIXUP_ESPFIX_STACK`, and `UNWIND_ESPFIX_STACK`. Important symbols include `__switch_to_asm`, `ret_from_fork_asm`, `entry_SYSENTER_32`, `entry_INT80_32`, `handle_exception`, `asm_exc_double_fault`, `asm_exc_nmi`, and `rewind_stack_and_make_dead`.

Control flow: IDT stubs clear AC, push an error code or C-function pointer, and jump to `handle_exception`, which saves registers, switches stacks when necessary, calls the C handler through `CALL_NOSPEC`, and chooses return-to-user or return-to-kernel restoration. `entry_SYSENTER_32` handles the vDSO fast syscall path: it switches from the entry stack to the task stack, synthesizes missing SYSENTER return frame fields, clears unsafe flags, calls `do_SYSENTER_32`, and may return through opportunistic `sysexit` after switching to user CR3 and clearing CPU buffers. `entry_INT80_32` handles the legacy syscall path and returns via IRET. NMI has special paths for interrupts on SYSENTER and ESPFIX stacks. Double fault is task-gate based and manually clears task-switched/nested-task state before calling `doublefault_shim`, then halts if control returns.

State and persistence: The file mutates architectural state including CR3, segment registers, EFLAGS, TSS stack pointers, entry/task stacks, pt_regs frames, and ESPFIX GDT descriptor bytes. It also updates stack canaries during context switch, fills the RSB on context switch, clears CPU buffers before returns, and may call `make_task_dead` after rewinding the stack.

Dependencies and integration points: It includes many x86 low-level headers plus `calling.h` and generated `asm/idtentry.h`. It integrates with C functions such as `do_SYSENTER_32`, `do_int80_syscall_32`, exception handlers, `exc_nmi`, `doublefault_shim`, `__switch_to`, `ret_from_fork`, `stackleak_erase`, and `make_task_dead`. It depends on per-CPU `cpu_entry_area`, TSS fields, PTI, VM86, ESPFIX, SMAP, and speculation mitigation features.

Risks and test signals: This code is highly sensitive to stack layout and register offsets; comments note that `pt_regs` order must stay synchronized with fork, signal, ptrace, and ptrace ABI definitions. PTI and ESPFIX paths are especially easy to break because NMIs can arrive mid-copy. Tests should include 32-bit boot, SYSENTER and INT80 syscall tests, ptrace/signal frame validation, VM86/ESPFIX coverage, NMI and double-fault handling, PTI debug checks, objtool/unwind checks, context-switch stress, stackleak builds, and syscall restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry_32.S -->
