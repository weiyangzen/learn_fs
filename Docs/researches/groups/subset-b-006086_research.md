# subset-b-006086 Research

Grouped source research for Ceph-client kernel crypto library hash implementations, RISC-V/s390/SPARC accelerated crypto hooks, architecture assembly kernels, and selected KUnit test vectors. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/poly1305-riscv.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/poly1305-riscv.pl

## Purpose

This Perl generator emits RISC-V assembly for the Poly1305 one-time authenticator. It is derived from OpenSSL/Cryptogams and generates optimized `poly1305_init`, `poly1305_blocks`, and `poly1305_emit` entry points for kernel use. The source was read as a complete 847-line generator.

## Important APIs, Types, and Functions

Generated symbols are `poly1305_init`, `poly1305_blocks`, and `poly1305_emit`. The generator maps ABI registers, selects 64-bit or 32-bit code by its flavour argument, handles CHERI capability substitutions, and emits conditional code for fast versus manually assembled misaligned accesses. The generated state layout stores accumulator limbs, clamped `r`, and precomputed scaled `r` values in the caller-provided Poly1305 block state.

## Control Flow

The script builds assembly text in `$code`, chooses a 64-bit or 32-bit body, then post-processes lines for CHERI or normal RISC-V mnemonics before writing the output file. Runtime flow in the emitted code is split into initialization with optional key clamping, block processing over complete 16-byte blocks, and final emission that reduces the accumulator, conditionally subtracts the Poly1305 modulus, adds the nonce, and stores the 16-byte tag.

## State and Persistence Behavior

No persistent storage is owned by the generator. Emitted code mutates the caller's Poly1305 state in memory and uses stack saves for callee-saved registers during block processing. Secret intermediate key and accumulator values live in registers or the supplied state; final security depends on callers zeroizing state where appropriate.

## Dependencies and Integration Points

The generated assembly is declared by `riscv/poly1305.h` and integrated by the generic Poly1305 library when RISC-V architecture support is selected. It depends on RISC-V integer multiply instructions, Linux build-time assembly preprocessing, and optional CHERI and `__riscv_misaligned_fast` feature macros.

## Risks and Edge Cases

Risks concentrate around ABI drift between generated symbols and C prototypes, misaligned input handling, CHERI post-processing substitutions, endian assumptions, and arithmetic carry/reduction correctness. The block routine intentionally truncates `len` to complete 16-byte blocks, so callers must handle partial buffering correctly outside this code.

## Test Signals

Useful tests are Poly1305 KUnit test vectors, ChaCha20-Poly1305 AEAD vectors, unaligned-key and unaligned-message cases, 32-bit and 64-bit RISC-V build coverage, CHERI build coverage where supported, and comparison against the generic C Poly1305 implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/poly1305-riscv.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/poly1305.h -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/poly1305.h

## Purpose

This small RISC-V header exposes the accelerated Poly1305 assembly contract to the generic crypto library. It was read as a complete 14-line header.

## Important APIs, Types, and Functions

It declares `poly1305_block_init(struct poly1305_block_state *state, const u8 raw_key[POLY1305_BLOCK_SIZE])`, `poly1305_blocks(struct poly1305_block_state *state, const u8 *src, u32 len, u32 hibit)`, and `poly1305_emit(const struct poly1305_state *state, u8 digest[POLY1305_DIGEST_SIZE], const u32 nonce[4])`.

## Control Flow

There is no control flow in the header. Runtime flow is supplied by generated RISC-V assembly and selected by the generic Poly1305 library build for this architecture.

## State and Persistence Behavior

The header owns no storage. It defines the ABI for mutating caller-owned Poly1305 state and for emitting a digest from the final state plus nonce.

## Dependencies and Integration Points

It depends on the generic Poly1305 type definitions being visible before inclusion. It is the declaration bridge between `poly1305-riscv.pl` output and `lib/crypto/poly1305.c`.

## Risks and Edge Cases

The main risk is prototype mismatch with generated assembly, especially the state type split between block and final emit state. Since this is an ABI boundary, argument order or type changes would be silent assembly-level breakage.

## Test Signals

Compile and link tests on RISC-V, Poly1305 KUnit vectors, and generic-versus-accelerated differential tests validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha256-riscv64-zvknha_or_zvknhb-zvkb.S -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/sha256-riscv64-zvknha_or_zvknhb-zvkb.S

## Purpose

This RISC-V vector crypto assembly file implements the SHA-256 compression function for RV64 systems with VLEN at least 128, `Zvknha` or `Zvknhb`, and `Zvkb`. It was read as a complete 225-line assembly file.

## Important APIs, Types, and Functions

It exports `sha256_transform_zvknha_or_zvknhb_zvkb(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. Internal macros `sha256_4rounds` and `sha256_16rounds` drive `vsha2cl.vv`, `vsha2ch.vv`, and `vsha2ms.vv`. The constant table `K256` provides the 64 SHA-256 round constants.

## Control Flow

The function preloads round constants, builds a vector mask for message schedule updates, gathers state words into the vector layout required by the SHA instructions, then loops over blocks. For each block it endian-swaps four vectors of message words, performs 64 rounds in four groups of 16, adds the previous state, and repeats until `nblocks` reaches zero. Final state is scattered back to the C state layout.

## State and Persistence Behavior

The only persistent mutation is the caller-owned SHA-256 block state. Constants live in read-only data. Vector registers hold transient message schedule and state words inside a `kernel_vector_begin()` and `kernel_vector_end()` region supplied by the C wrapper.

## Dependencies and Integration Points

The file is called from `riscv/sha256.h`, which probes vector crypto features and falls back to `sha256_blocks_generic` if unavailable or SIMD use is disallowed. It includes Linux linkage macros and relies on RISC-V vector crypto assembler support.

## Risks and Edge Cases

Risks include vector length assumptions, state gather/scatter index correctness, endian conversion, exact feature gating, and calling the function without saving vector state. It assumes `nblocks` is nonzero when called by the streaming layer.

## Test Signals

SHA-224/SHA-256 KUnit vectors, long multi-block hashes, unaligned input coverage through the generic streaming layer, and comparison against generic C output on vector-capable RISC-V are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha256-riscv64-zvknha_or_zvknhb-zvkb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/sha256.h

## Purpose

This architecture header plugs the RISC-V vector SHA-256 transform into the generic SHA-224/SHA-256 library. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

It defines a `have_extensions` static key, declares `sha256_transform_zvknha_or_zvknhb_zvkb`, implements `sha256_blocks`, and provides `sha256_mod_init_arch`. The block wrapper checks the static key and `may_use_simd()` before entering kernel vector mode.

## Control Flow

Generic `sha256.c` includes this header when `CONFIG_CRYPTO_LIB_SHA256_ARCH` is enabled. During module init, `sha256_mod_init_arch` enables the static key only when `ZVKNHA` or `ZVKNHB`, `ZVKB`, and VLEN >= 128 are present. At update/final/HMAC time, `sha256_blocks` dispatches to vector assembly under vector state protection or to the generic C compression loop.

## State and Persistence Behavior

The persistent state is the read-only-after-init static key. Per-hash state remains in caller-owned `sha256_block_state` and is passed through unchanged aside from compression updates.

## Dependencies and Integration Points

It depends on `<asm/simd.h>`, `<asm/vector.h>`, RISC-V ISA probing, and the generic `sha256_blocks_generic` fallback in `sha256.c`.

## Risks and Edge Cases

Feature detection must match the assembly's actual requirements. The SIMD guard is important for contexts where vector state cannot be used. Missing fallback behavior would break systems without vector crypto, but this header retains the generic path.

## Test Signals

RISC-V builds with and without vector crypto, KUnit SHA-256 coverage, FIPS HMAC-SHA256 self-test when enabled, and forced SIMD-disabled testing provide useful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha512-riscv64-zvknhb-zvkb.S -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/sha512-riscv64-zvknhb-zvkb.S

## Purpose

This RV64 vector crypto assembly file implements the SHA-512 and SHA-384 compression transform for systems with `Zvknhb`, `Zvkb`, and VLEN at least 128. It was read as a complete 203-line file.

## Important APIs, Types, and Functions

It exports `sha512_transform_zvknhb_zvkb(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. Macros `sha512_4rounds` and `sha512_16rounds` use SHA-2 vector crypto instructions over e64 LMUL=2 vectors. The `K512` rodata table stores 80 64-bit round constants.

## Control Flow

The transform prepares a mask and gather indices, loads state into vector order, and processes each 1024-bit message block. It endian-swaps the four vector chunks, executes five groups of 16 rounds, adds previous state vectors, advances the block pointer, and stores the updated state when all blocks are consumed.

## State and Persistence Behavior

The function mutates only the caller's SHA-512 block state. Constants are immutable. Vector registers are transient and must be protected by the caller's kernel vector state management.

## Dependencies and Integration Points

The assembly is selected by `riscv/sha512.h`, which probes `ZVKNHB`, `ZVKB`, and vector length before dispatching. It integrates with the streaming, finalization, and HMAC code in `sha512.c`.

## Risks and Edge Cases

The code is sensitive to e64 vector grouping, gather/scatter byte offsets, endian reversal, and exact nblocks loop semantics. Incorrect feature gating can fault on unsupported CPUs.

## Test Signals

SHA-384/SHA-512 KUnit vectors, FIPS HMAC-SHA512 self-test when enabled, long multi-block hashes, and generic-versus-accelerated comparison on vector RISC-V validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha512-riscv64-zvknhb-zvkb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha512.h -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/sha512.h

## Purpose

This RISC-V architecture header dispatches generic SHA-384/SHA-512 block processing to vector crypto assembly when supported. It was read as a complete 39-line file.

## Important APIs, Types, and Functions

It defines the `have_extensions` static key, declares `sha512_transform_zvknhb_zvkb`, implements `sha512_blocks`, and defines `sha512_mod_init_arch`.

## Control Flow

At module init the header checks `ZVKNHB`, `ZVKB`, and VLEN >= 128. If present, the static key is enabled. Each block-processing call then either enters vector mode, calls the assembly transform, and exits vector mode, or falls back to `sha512_blocks_generic`.

## State and Persistence Behavior

Only the static key persists beyond calls. Hash state remains caller-owned and follows the generic `sha512.c` streaming and HMAC lifecycle.

## Dependencies and Integration Points

The header depends on RISC-V SIMD/vector helpers and the generic SHA-512 implementation. It is included by `sha512.c` when architecture acceleration is configured.

## Risks and Edge Cases

Risks include using vector state in invalid contexts, probing the wrong extension set, and accidentally sharing the `have_extensions` identifier if include patterns change. Current inclusion into one translation unit keeps it local.

## Test Signals

Builds with architecture acceleration, SHA-512 KUnit suites, vector-enabled hardware or emulation, and forced fallback runs validate the dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3-riscv64-zvksh-zvkb.S -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3-riscv64-zvksh-zvkb.S

## Purpose

This RV64 vector crypto assembly file implements the SM3 compression transform using `Zvksh` and `Zvkb`. It was read as a complete 124-line file.

## Important APIs, Types, and Functions

It exports `sm3_transform_zvksh_zvkb(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. The `sm3_8rounds` macro uses `vsm3c.vi` for compression rounds and `vsm3me.vv` for message expansion.

## Control Flow

The function loads and endian-swaps the 8-word SM3 state into a vector, then loops over 512-bit message blocks. For each block it saves the previous state, loads two message vectors, executes eight macro invocations for 64 rounds, XORs the previous state back in, and repeats until all blocks are processed. The final state is endian-swapped back and stored.

## State and Persistence Behavior

The only persistent mutation is the caller's `sm3_block_state`. Vector registers hold temporary state and schedule words inside caller-managed vector state.

## Dependencies and Integration Points

It is declared and dispatched by `riscv/sm3.h`, which is included by the generic `sm3.c` implementation under `CONFIG_CRYPTO_LIB_SM3_ARCH`.

## Risks and Edge Cases

Risks include endian conversion, vector feature gating, correct XOR feed-forward semantics, and ensuring the block count is nonzero. The assembly assumes vector crypto support and relies on its wrapper to enforce that.

## Test Signals

SM3 KUnit vectors, long multi-block inputs, generic-versus-accelerated comparison, and RISC-V vector build coverage are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3-riscv64-zvksh-zvkb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3.h -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3.h

## Purpose

This header integrates the RISC-V vector SM3 transform with the generic SM3 streaming library. It was read as a complete 39-line file.

## Important APIs, Types, and Functions

It defines `have_extensions`, declares `sm3_transform_zvksh_zvkb`, implements `sm3_blocks`, and defines `sm3_mod_init_arch`.

## Control Flow

During module init, `sm3_mod_init_arch` enables acceleration only when `ZVKSH`, `ZVKB`, and VLEN >= 128 are available. During hashing, `sm3_blocks` checks the static key and `may_use_simd()`, wraps the assembly call with kernel vector begin/end, or falls back to `sm3_blocks_generic`.

## State and Persistence Behavior

Persistent state is limited to the static key. Hash state is caller-owned and follows `sm3.c` update/final semantics.

## Dependencies and Integration Points

It depends on RISC-V vector helpers and generic SM3 symbols. It is included by `sm3.c` when architecture SM3 support is enabled.

## Risks and Edge Cases

Feature detection and vector-state safety are the central risks. Fallback correctness is important for systems lacking vector crypto or contexts where SIMD is disabled.

## Test Signals

SM3 KUnit tests, architecture build coverage, forced generic fallback, and accelerated hardware comparison validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/sm3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/aes.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/aes.h

## Purpose

This s390 architecture header accelerates AES block encryption and decryption through CP Assist for Cryptographic Functions. It was read as a complete 106-line file.

## Important APIs, Types, and Functions

It defines static keys `have_cpacf_aes128`, `have_cpacf_aes192`, and `have_cpacf_aes256`; implements `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, helper `aes_crypt_s390`, and `aes_mod_init_arch`.

## Control Flow

Key preparation stores the raw key when CPACF supports the selected key length, because the CPACF KM instruction consumes raw AES keys. Unsupported key sizes fall back to generic expanded round keys. Encryption and decryption try `cpacf_km()` first through `aes_crypt_s390`; if the matching static key is disabled, generic AES round-key encryption or decryption is used.

## State and Persistence Behavior

Static keys persist after init. Per-key state stores either raw key bytes for CPACF use or generic expanded round keys depending on feature support at preparation time.

## Dependencies and Integration Points

The header depends on `<asm/cpacf.h>`, s390 CPU feature probing, and generic AES helpers. It is included by the shared AES library's architecture hook path.

## Risks and Edge Cases

The key representation depends on runtime feature support at key preparation time; encrypt/decrypt must use the same static-key assumptions. CPACF query coverage by key length is essential. Raw key retention has secret-memory implications equivalent to expanded-key retention.

## Test Signals

AES known-answer tests, AES-CMAC/CBC-MAC KUnit coverage, s390 builds with and without MSA, and generic fallback comparison validate the hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.S -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.S

## Purpose

This s390 assembly file implements vectorized ChaCha20 encryption for systems with vector extensions. It was read as a complete 908-line file.

## Important APIs, Types, and Functions

It exports `chacha20_vx_4x` and `chacha20_vx`. The public header declares `chacha20_vx`; the top-level function jumps to the 4-block path for shorter lengths and otherwise uses a larger six-block vector pipeline. The local `sigma` data block contains ChaCha constants, counter increments, byte-permutation masks, and smashed sigma vectors.

## Control Flow

`chacha20_vx_4x` handles up to four 64-byte blocks with ten double-round iterations, transposes vector lanes into output order, XORs keystream with input, and handles tails byte by byte. `chacha20_vx` allocates a stack frame for larger inputs, processes six blocks per outer loop, reloads constants and counters as needed, emits full 64-byte chunks, and uses a byte tail loop for the final partial block.

## State and Persistence Behavior

The assembly does not update the ChaCha state directly. It consumes key and counter pointers and writes ciphertext/plaintext to the output buffer. The C wrapper updates the stream counter after return. Vector registers and stack scratch space hold transient keystream and tail data.

## Dependencies and Integration Points

It depends on s390 vector instruction macros, FPU/vector state management by `s390/chacha.h`, and the generic ChaCha library dispatch. It assumes the C wrapper called `kernel_fpu_begin()`.

## Risks and Edge Cases

Risks include counter increment correctness, tail byte handling, stack frame restore, exact 20-round behavior, overlap assumptions inherited from stream cipher APIs, and ensuring the wrapper never calls this without vector support.

## Test Signals

ChaCha20 known-answer tests, ChaCha20-Poly1305 KUnit tests, lengths around 64 and 256 bytes, odd tail lengths, and generic-versus-vector differential tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.h

## Purpose

This header declares the s390 vector ChaCha20 assembly function. It was read as a complete 14-line file.

## Important APIs, Types, and Functions

It declares `chacha20_vx(u8 *out, const u8 *inp, size_t len, const u32 *key, const u32 *counter)`.

## Control Flow

There is no control flow. The declaration is consumed by `s390/chacha.h`, which handles feature checks and vector-state bracketing.

## State and Persistence Behavior

The function contract writes output and consumes caller-provided key and counter words. The wrapper updates the higher-level ChaCha state after the assembly call.

## Dependencies and Integration Points

It depends on standard crypto integer types being visible before inclusion and integrates `chacha-s390.S` with the generic ChaCha architecture hook.

## Risks and Edge Cases

Prototype mismatch would corrupt registers at the assembly ABI boundary. The assembly is hard-coded for ChaCha20 rounds, so the wrapper must gate non-20-round calls away from it.

## Test Signals

s390 build/link tests and ChaCha KUnit known-answer tests exercise this declaration boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/chacha-s390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/chacha.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/chacha.h

## Purpose

This s390 architecture header dispatches generic ChaCha stream encryption to the vector assembly implementation when appropriate. It was read as a complete 36-line file.

## Important APIs, Types, and Functions

It defines `hchacha_block_arch` as the generic HChaCha implementation and implements `chacha_crypt_arch(struct chacha_state *state, u8 *dst, const u8 *src, unsigned int bytes, int nrounds)`.

## Control Flow

The wrapper uses generic ChaCha if the request is one block or less, if `nrounds` is not 20, or if `cpu_has_vx()` is false. Otherwise it enters kernel FPU/vector mode, calls `chacha20_vx`, exits vector mode, and advances `state->x[12]` by the number of rounded-up 64-byte blocks consumed.

## State and Persistence Behavior

The wrapper mutates the caller-owned ChaCha state counter after vector encryption. It uses an on-stack vector/FPU save area and owns no persistent storage.

## Dependencies and Integration Points

It depends on s390 FPU/vector helpers, CPU feature checks, `chacha-s390.h`, and generic ChaCha helpers. It is included by the generic ChaCha library's architecture hook path.

## Risks and Edge Cases

Counter updates must match the assembly's generated keystream count, especially for partial tails. The one-block fallback is intentional because the assembly cannot handle a block or less efficiently/compatibly. Incorrect FPU bracketing would corrupt kernel vector state.

## Test Signals

ChaCha tests around 0, 1, 64, 65, and large byte counts, non-20-round fallback tests, and vector-disabled fallback tests validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/chacha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/gf128hash.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/gf128hash.h

## Purpose

This s390 architecture header accelerates GHASH through CPACF while retaining the generic GF(2^128) fallback. It was read as a complete 54-line file.

## Important APIs, Types, and Functions

It defines `have_cpacf_ghash`, `ghash_preparekey_arch`, `ghash_blocks_arch`, and `gf128hash_mod_init_arch`. The key preparation stores both POLYVAL-convention key material for fallback and raw GHASH key material for CPACF.

## Control Flow

Key preparation always fills both representations. `ghash_blocks_arch` checks the static key; the accelerated path converts the accumulator from POLYVAL to GHASH convention, builds the CPACF context buffer with accumulator and key, calls `cpacf_kimd(CPACF_KIMD_GHASH)`, converts the accumulator back, and zeroizes the temporary context. Otherwise it calls `ghash_blocks_generic`.

## State and Persistence Behavior

The static key persists after init. Prepared GHASH keys persist in caller-owned key structs in two representations. The CPACF context buffer is local and explicitly zeroized.

## Dependencies and Integration Points

It depends on CPACF, s390 CPU feature probing, and generic GF128 conversion helpers. It integrates with GHASH and POLYVAL library code.

## Risks and Edge Cases

The main risks are representation conversion mistakes, failure to zero temporary key material, CPACF feature misquery, and keeping raw key storage synchronized with generic key storage.

## Test Signals

GHASH and POLYVAL KUnit vectors, all-ones guarded-key tests in the broader test suite, CPACF-enabled s390 runs, and forced generic fallback comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/gf128hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha1.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/sha1.h

## Purpose

This s390 header accelerates SHA-1 block processing through CPACF KIMD. It was read as a complete 28-line file.

## Important APIs, Types, and Functions

It defines `have_cpacf_sha1`, implements `sha1_blocks`, and provides `sha1_mod_init_arch`.

## Control Flow

At init, the code checks MSA and `CPACF_KIMD_SHA_1`; if available, it enables the static key. Block processing either calls `cpacf_kimd` over `nblocks * SHA1_BLOCK_SIZE` bytes or falls back to `sha1_blocks_generic`.

## State and Persistence Behavior

The static key persists after initialization. Hash state remains caller-owned and is updated in place by either CPACF or generic compression.

## Dependencies and Integration Points

It depends on `<asm/cpacf.h>`, s390 CPU feature helpers, and `sha1.c`'s generic fallback. It is included by the generic SHA-1 library under architecture acceleration.

## Risks and Edge Cases

Risks include CPACF function availability mismatch and state layout compatibility with CPACF. SHA-1 is collision-weak cryptographically, but this file is a performance hook, not a policy gate.

## Test Signals

SHA-1/HMAC-SHA1 KUnit vectors, FIPS HMAC-SHA1 self-test when enabled, and generic-versus-CPACF comparisons are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/sha256.h

## Purpose

This s390 header accelerates SHA-256 and SHA-224 block processing through CPACF KIMD. It was read as a complete 28-line file.

## Important APIs, Types, and Functions

It defines `have_cpacf_sha256`, implements `sha256_blocks`, and provides `sha256_mod_init_arch`.

## Control Flow

Initialization enables the static key when MSA and `CPACF_KIMD_SHA_256` are available. Runtime block processing dispatches to CPACF for full blocks or to `sha256_blocks_generic` otherwise.

## State and Persistence Behavior

The static key persists after init. The generic SHA-256 context owns byte counters, buffers, and block state; this header only mutates the block state supplied to it.

## Dependencies and Integration Points

It depends on CPACF query helpers and the generic SHA-224/SHA-256 implementation. It is included by `sha256.c` when architecture hooks are configured.

## Risks and Edge Cases

State layout and byte-order expectations must match CPACF. Feature probing must avoid enabling the path on partial or unsupported hardware.

## Test Signals

SHA-224/SHA-256 KUnit tests, FIPS HMAC-SHA256 self-test, long multi-block messages, and s390 fallback comparison validate the hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha3.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/sha3.h

## Purpose

This s390 header accelerates SHA-3 absorb, Keccak permutation, and one-shot SHA3 hashing through CPACF. It was read as a complete 151-line file.

## Important APIs, Types, and Functions

It defines static keys `have_sha3` and `have_sha3_init_optim`, overrides `sha3_absorb_blocks`, `sha3_keccakf`, and one-shot functions `sha3_224_arch`, `sha3_256_arch`, `sha3_384_arch`, and `sha3_512_arch`. Helper `s390_sha3` uses `cpacf_klmd`.

## Control Flow

Block absorb dispatches by SHA3 block size to the corresponding KIMD function, with SHA3-256 also covering SHAKE256's block size. `sha3_keccakf` invokes KIMD SHA3-512 with a zero block to obtain a plain permutation when accelerated. One-shot hashing uses KLMD and optionally sets `CPACF_KLMD_NIP | CPACF_KLMD_DUFOP` when facility 86 allows optimized initialization. Init checks all required KIMD and KLMD SHA3 functions and enables acceleration only if the complete set is present.

## State and Persistence Behavior

Static keys persist after init. One-shot helper state is stack-local and zeroized. Streaming state remains in caller-owned `sha3_state`.

## Dependencies and Integration Points

It integrates with `sha3.c` via architecture hook macros and depends on CPACF, KMSAN unpoisoning for optimized output, and generic SHA3 fallbacks.

## Risks and Edge Cases

Risks include treating SHA3 facilities as all-or-nothing, block-size dispatch confusion with SHAKE, KMSAN state marking, and ensuring zero-input KIMD semantics really match Keccak-f.

## Test Signals

SHA3 and SHAKE KUnit vectors, NIST SHAKE vectors, all-length squeeze tests, FIPS SHA3-256 self-test, and CPACF fallback comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha512.h -->
# sources/distributed-fs/ceph-client/lib/crypto/s390/sha512.h

## Purpose

This s390 header accelerates SHA-512 and SHA-384 block processing through CPACF KIMD. It was read as a complete 28-line file.

## Important APIs, Types, and Functions

It defines `have_cpacf_sha512`, implements `sha512_blocks`, and provides `sha512_mod_init_arch`.

## Control Flow

Initialization enables the static key when MSA and `CPACF_KIMD_SHA_512` are present. Each block-processing call uses `cpacf_kimd` for accelerated full-block compression or `sha512_blocks_generic` for fallback.

## State and Persistence Behavior

The static key persists after init. The generic SHA-512 context owns counters and buffers; this header updates only the supplied block state.

## Dependencies and Integration Points

It depends on CPACF and generic `sha512.c`, which includes it when architecture hooks are enabled.

## Risks and Edge Cases

The CPACF state layout must match `struct sha512_block_state`. Feature probing and fallback are the main operational risks.

## Test Signals

SHA-384/SHA-512 KUnit tests, FIPS HMAC-SHA512 self-test, long-message coverage, and generic-versus-CPACF comparison validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/s390/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha1.c -->
# sources/distributed-fs/ceph-client/lib/crypto/sha1.c

## Purpose

This file implements generic SHA-1 and HMAC-SHA1 library functions with optional architecture block acceleration and FIPS self-testing. It was read as a complete 336-line file.

## Important APIs, Types, and Functions

Exports include `sha1_init`, `sha1_update`, `sha1_final`, `sha1`, `hmac_sha1_preparekey`, `hmac_sha1_init`, `hmac_sha1_init_usingrawkey`, `hmac_sha1_final`, `hmac_sha1`, and `hmac_sha1_usingrawkey`. Internal pieces include `sha1_block_generic`, `sha1_blocks_generic`, `__sha1_final`, and `__hmac_sha1_preparekey`.

## Control Flow

`sha1_update` accumulates bytes in a partial block buffer, processes full blocks through `sha1_blocks`, and stores any remainder. Finalization adds SHA padding and a 64-bit bit count, processes the final block, emits big-endian digest words, then zeroizes the public context. HMAC preparation hashes overlong keys, builds ipad and opad derived blocks, and precomputes inner and outer SHA-1 states.

## State and Persistence Behavior

`struct sha1_ctx` stores block state, byte count, and a partial buffer. HMAC key structs persist precomputed inner and outer states. Temporary derived keys and contexts are zeroized explicitly.

## Dependencies and Integration Points

It depends on crypto HMAC constants, SHA-1 public headers, unaligned big-endian helpers, optional `$(SRCARCH)/sha1.h`, and `fips.h`. It exports GPL symbols to other kernel crypto users.

## Risks and Edge Cases

SHA-1 is cryptographically weak for collision resistance. Implementation risks include bytecount overflow semantics, padding boundary cases around 56 bytes, architecture hook correctness, and HMAC outer padding length assumptions.

## Test Signals

SHA-1/HMAC-SHA1 KUnit vectors, incremental update split tests from `hash-test-template.h`, FIPS HMAC-SHA1 self-test, and architecture fallback comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha256.c -->
# sources/distributed-fs/ceph-client/lib/crypto/sha256.c

## Purpose

This file implements generic SHA-224, SHA-256, HMAC-SHA224, and HMAC-SHA256 library functions, plus a two-output SHA-256 finup helper. It was read as a complete 515-line file.

## Important APIs, Types, and Functions

Exports include `sha224_init`, `sha256_init`, `__sha256_update`, `sha224_final`, `sha256_final`, `sha224`, `sha256`, `sha256_finup_2x`, `sha256_finup_2x_is_optimized`, HMAC prepare/init/final/one-shot functions for SHA-224 and SHA-256, and module init/exit when needed. Internal functions include `sha256_block_generic`, `sha256_blocks_generic`, `__sha256_init`, `__sha256_final`, `sha256_finup_2x_sequential`, and `__hmac_sha256_preparekey`.

## Control Flow

Streaming update buffers partial 64-byte blocks, calls architecture or generic block compression for full blocks, and leaves a remainder. Finalization pads with a 64-bit bit count and emits the requested digest size, enabling SHA-224 truncation. `sha256_finup_2x` tries an architecture dual-buffer helper when defined, then falls back to sequentially cloning the context and finalizing two inputs. HMAC precomputes inner and outer states from raw keys.

## State and Persistence Behavior

Contexts store block state, byte count, and a partial buffer. The `initial_sha256_ctx` constant supports default two-output finup. HMAC key objects persist precomputed states. Contexts and derived key buffers are zeroized where finalization or key preparation completes.

## Dependencies and Integration Points

It depends on `crypto/sha2.h`, HMAC constants, unaligned helpers, optional `$(SRCARCH)/sha256.h`, FIPS test data, and exported kernel symbols. Pre-boot builds with `__DISABLE_EXPORTS` get only generic SHA-256 code.

## Risks and Edge Cases

Padding boundaries, bytecount overflow, digest truncation for SHA-224, architecture hook selection, and correctness of two-output finup fallbacks are key risks. HMAC final constructs a one-block outer hash manually and depends on digest sizes fitting in one SHA-256 block with ipad/opad state.

## Test Signals

SHA-224/SHA-256 KUnit suites, HMAC vectors, `sha256_finup_2x` tests for default and nondefault contexts, huge-length tests, FIPS HMAC-SHA256 self-test, and architecture differential tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha3.c -->
# sources/distributed-fs/ceph-client/lib/crypto/sha3.c

## Purpose

This file implements generic SHA-3 and SHAKE sponge functions, with optional architecture absorb, permutation, and one-shot hooks. It was read as a complete 411-line file.

## Important APIs, Types, and Functions

Exports include `__sha3_update`, `sha3_final`, `shake_squeeze`, `sha3_224`, `sha3_256`, `sha3_384`, `sha3_512`, `shake128`, and `shake256`. Internal pieces include `sha3_keccakf_one_round_generic`, `sha3_keccakf_generic`, and `sha3_absorb_blocks_generic`. Architecture one-shot hooks default to false when not provided.

## Control Flow

Update XORs input into the sponge rate area, runs the Keccak permutation on full blocks, and tracks absorb offset. SHA3 final applies the `0x06` domain suffix and `0x80` pad bit, permutes, copies the fixed digest, and zeroizes. SHAKE squeeze applies the `0x1f` suffix on first squeeze, marks absorb complete by setting offset to block size, then repeatedly permutes and copies output chunks.

## State and Persistence Behavior

`__sha3_ctx` stores the 1600-bit state, block size, digest size, absorb offset, and squeeze offset. SHA3 final and one-shot SHAKE zeroize contexts after use. Streaming SHAKE contexts persist across multiple squeezes until the caller zeroizes them.

## Dependencies and Integration Points

It depends on `crypto/sha3.h`, `crypto_xor`, unaligned little-endian helpers, optional `$(SRCARCH)/sha3.h`, and FIPS test data. Architecture hooks can override block absorb, permutation, and fixed-length one-shot SHA3 calls.

## Risks and Edge Cases

The main risks are domain separation suffixes, absorb-after-squeeze misuse, endian conversion on non-little-endian systems, output-length handling for SHAKE, and architecture one-shot equivalence with streaming behavior.

## Test Signals

SHA3 and SHAKE KUnit vectors, NIST SHAKE tests, multiple-squeeze tests, guarded buffer tests, FIPS SHA3-256 self-test, and architecture fallback comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha512.c -->
# sources/distributed-fs/ceph-client/lib/crypto/sha512.c

## Purpose

This file implements generic SHA-384, SHA-512, HMAC-SHA384, and HMAC-SHA512 library functions with optional architecture block acceleration. It was read as a complete 440-line file.

## Important APIs, Types, and Functions

Exports include `sha384_init`, `sha512_init`, `__sha512_update`, `sha384_final`, `sha512_final`, `sha384`, `sha512`, HMAC prepare/init/final/one-shot functions for SHA-384 and SHA-512, and optional module init/exit. Internal functions include `sha512_block_generic`, `sha512_blocks_generic`, `__sha512_init`, `__sha512_final`, and `__hmac_sha512_preparekey`.

## Control Flow

The update path tracks a 128-byte block buffer and 128-bit byte count split into high and low fields. Full blocks are compressed through `sha512_blocks`. Finalization adds SHA-512 padding with a 128-bit bit length and emits the requested digest size. HMAC preparation hashes overlong keys, precomputes ipad and opad states, and HMAC final builds a one-block outer hash from the inner digest.

## State and Persistence Behavior

Contexts store block state, high/low byte counts, and partial data. HMAC keys persist precomputed inner and outer block states. Derived key buffers and contexts are explicitly zeroized where sensitive.

## Dependencies and Integration Points

It depends on `crypto/sha2.h`, overflow helpers, HMAC constants, optional `$(SRCARCH)/sha512.h`, and FIPS self-test data. It exports GPL symbols for kernel crypto users.

## Risks and Edge Cases

The 128-bit byte count and padding boundary at 112 bytes are important edge cases. Architecture hook state layout, digest truncation for SHA-384, and manual HMAC outer block construction are risk points.

## Test Signals

SHA-384/SHA-512 KUnit vectors, HMAC vectors, long and boundary-length inputs, FIPS HMAC-SHA512 self-test, and architecture differential tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sha512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/simd.c -->
# sources/distributed-fs/ceph-client/lib/crypto/simd.c

## Purpose

This file provides a per-CPU testing control used by crypto SIMD helpers. It was read as a complete 11-line file.

## Important APIs, Types, and Functions

It defines and exports `DEFINE_PER_CPU(bool, crypto_simd_disabled_for_test)` via `EXPORT_PER_CPU_SYMBOL_GPL`.

## Control Flow

There is no executable control flow beyond per-CPU variable definition and export initialization.

## State and Persistence Behavior

The per-CPU boolean persists for the lifetime of the kernel/module and can be used by tests or internal helpers to suppress SIMD paths on a CPU-local basis.

## Dependencies and Integration Points

It depends on `<crypto/internal/simd.h>` and integrates with architecture crypto dispatch code that consults testing SIMD-disable state.

## Risks and Edge Cases

The main risk is test-only state leaking into non-test execution paths if callers set it incorrectly. Per-CPU semantics mean tests must control the CPU context they are validating.

## Test Signals

Forced generic fallback tests and KUnit paths that disable SIMD for architecture differential coverage exercise this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/simd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sm3.c -->
# sources/distributed-fs/ceph-client/lib/crypto/sm3.c

## Purpose

This file implements the generic SM3 hash library with optional architecture block acceleration. It was read as a complete 290-line file.

## Important APIs, Types, and Functions

Exports include `sm3_init`, `sm3_update`, `sm3_final`, and `sm3`. Internal functions include `sm3_block_generic`, `sm3_blocks_generic`, and `__sm3_final`. The file defines SM3 IV constants, precomputed round constants, boolean functions, permutation macros, and message expansion macros.

## Control Flow

The generic block function performs 64 SM3 rounds with a rolling 16-word schedule and XOR feed-forward into the state. Update buffers partial 64-byte blocks and compresses full blocks. Finalization pads with `0x80`, appends a 64-bit big-endian bit count, compresses the final block, emits big-endian digest words, and zeroizes the context.

## State and Persistence Behavior

`struct sm3_ctx` stores block state, byte count, and a partial block buffer. Temporary message schedule words are zeroized by `sm3_blocks_generic`. No file-backed persistence exists.

## Dependencies and Integration Points

It depends on `crypto/sm3.h`, unaligned big-endian helpers, optional `$(SRCARCH)/sm3.h`, and exported GPL symbols. Architecture hooks can override `sm3_blocks` and provide module init.

## Risks and Edge Cases

Risks include padding boundary handling, bytecount overflow, round constant correctness, architecture hook equivalence, and message schedule carry-over errors.

## Test Signals

SM3 KUnit vectors, incremental update split tests, boundary-length messages, and generic-versus-accelerated comparisons validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sm3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/aes.h -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/aes.h

## Purpose

This SPARC64 architecture header connects generic AES library hooks to SPARC crypto opcodes and assembly routines. It was read as a complete 149-line file.

## Important APIs, Types, and Functions

It defines `have_aes_opcodes`, exports many `aes_sparc64_*` assembly symbols, declares single-block encrypt/decrypt functions for 128/192/256-bit keys, and implements `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, and `aes_mod_init_arch`.

## Control Flow

Key preparation uses `aes_sparc64_key_expand` when AES opcodes are present, copying unaligned input keys into a temporary aligned buffer when needed. Encryption and decryption dispatch by key length to SPARC assembly and use bounce buffers for unaligned input or output. Without opcodes, all operations fall back to generic AES key expansion and block encrypt/decrypt. Init checks hardware capabilities and ASR26 crypto feature bits.

## State and Persistence Behavior

The static key persists after init. Prepared AES keys store SPARC round keys when accelerated; inverse key storage is unused for SPARC because assembly uses the same round-key array for decryption.

## Dependencies and Integration Points

It depends on SPARC opcode, FPU, PSTATE, ELF hwcap, and generic AES helpers. It integrates with `sparc/aes_asm.S` and shared AES library code.

## Risks and Edge Cases

Risks include FPU/register state assumptions in assembly, alignment bounce-buffer correctness, round-key layout compatibility, and feature detection through hardware capability bits.

## Test Signals

AES known-answer tests, ECB/CBC/CTR mode tests, AES-CMAC KUnit coverage, unaligned buffer tests, and generic fallback comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/aes_asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/aes_asm.S

## Purpose

This SPARC64 assembly file implements AES key expansion, single-block encryption/decryption, key loading, and ECB/CBC/CTR block loops using SPARC crypto opcodes. It was read as a complete 1543-line file with symbol and body inspection.

## Important APIs, Types, and Functions

Exports include `aes_sparc64_key_expand`, `aes_sparc64_encrypt_128/192/256`, `aes_sparc64_decrypt_128/192/256`, key-load helpers for encryption and decryption keys, ECB encrypt/decrypt functions, CBC encrypt/decrypt functions, and CTR crypt functions for 128/192/256-bit keys. Macro families define repeated AES encrypt and decrypt rounds.

## Control Flow

The file uses macros to unroll AES rounds for each key length. Key expansion generates SPARC round-key material. Single-block functions load data, run key-length-specific opcode rounds, and store output. ECB/CBC/CTR routines load round keys into floating/vector registers, loop over blocks, perform mode-specific XOR/IV/counter handling, and return updated IV or counter data as required by their calling convention.

## State and Persistence Behavior

Persistent state is caller-owned key material, IVs, counters, and buffers. The assembly uses floating-point registers for round keys and data, so callers and wrappers must respect SPARC VIS/FPU state rules. No static mutable state is owned by the file.

## Dependencies and Integration Points

It depends on `<asm/opcodes.h>` macro definitions and SPARC linkage conventions. `sparc/aes.h` declares and exports these symbols and handles feature gating and alignment bounce buffers.

## Risks and Edge Cases

Risks include mode loop block-count semantics, IV and counter update correctness, register state preservation, alignment expectations, and key schedule layout drift with the C union fields.

## Test Signals

AES ECB/CBC/CTR known-answer tests, AES-CMAC and CBC-MAC tests, unaligned buffer tests through the C wrapper, and generic-versus-SPARC differential tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/aes_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1.h -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1.h

## Purpose

This SPARC64 header dispatches SHA-1 block compression to SPARC crypto opcodes when available. It was read as a complete 43-line file.

## Important APIs, Types, and Functions

It defines `have_sha1_opcodes`, declares `sha1_sparc64_transform`, implements `sha1_blocks`, and defines `sha1_mod_init_arch`.

## Control Flow

Initialization checks `HWCAP_SPARC_CRYPTO`, reads ASR26, tests `CFR_SHA1`, and enables the static key. Block processing then either calls `sha1_sparc64_transform` or falls back to `sha1_blocks_generic`.

## State and Persistence Behavior

The static key persists after init. Hash state remains caller-owned and is updated in place by either assembly or generic code.

## Dependencies and Integration Points

It depends on SPARC ELF hwcap, opcode, and PSTATE headers, plus `sparc/sha1_asm.S`. It is included by generic `sha1.c` when architecture acceleration is configured.

## Risks and Edge Cases

Feature detection and assembly ABI compatibility are the main risks. SHA-1 collision weakness is a broader algorithm risk outside this dispatch code.

## Test Signals

SHA-1/HMAC-SHA1 KUnit vectors, FIPS HMAC-SHA1 self-test, SPARC accelerated boot logs, and fallback comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1_asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1_asm.S

## Purpose

This SPARC64 assembly file implements SHA-1 block compression with SPARC crypto/VIS opcodes. It was read as a complete 72-line file.

## Important APIs, Types, and Functions

It exports `sha1_sparc64_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. It uses `VISEntryHalf`, `VISExitHalf`, and the `SHA1` opcode macro.

## Control Flow

The function loads the five SHA-1 state words into floating registers, checks data alignment, and loops over 64-byte blocks. Aligned input is loaded directly with doubleword loads. Unaligned input uses `alignaddr` and `faligndata` to assemble block words before invoking `SHA1`. After all blocks, it stores the updated state and returns.

## State and Persistence Behavior

The assembly mutates only the caller's SHA-1 state. Floating registers carry transient state and message data within VIS entry/exit protection.

## Dependencies and Integration Points

It depends on SPARC linkage, opcode, and VIS assembly macros. It is declared by `sparc/sha1.h` and called from generic SHA-1 streaming code.

## Risks and Edge Cases

Risks include unaligned load reconstruction, block count loop correctness, VIS state preservation, and state word layout compatibility.

## Test Signals

SHA-1 KUnit vectors, unaligned input tests, multi-block inputs, and generic-versus-SPARC comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha1_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha256.h

## Purpose

This SPARC64 header dispatches SHA-224/SHA-256 block compression to SPARC SHA256 opcodes. It was read as a complete 43-line file.

## Important APIs, Types, and Functions

It defines `have_sha256_opcodes`, declares `sha256_sparc64_transform`, implements `sha256_blocks`, and defines `sha256_mod_init_arch`.

## Control Flow

Initialization checks SPARC crypto hardware capability and the ASR26 `CFR_SHA256` bit. If present, it enables the static key and logs use of the optimized implementation. Runtime block processing chooses assembly or generic C compression.

## State and Persistence Behavior

Only the static key persists. SHA-224 and SHA-256 contexts remain generic caller-owned state.

## Dependencies and Integration Points

It depends on SPARC hwcap/opcode headers and `sparc/sha256_asm.S`, and is included by `sha256.c`.

## Risks and Edge Cases

Feature detection, state layout compatibility, and assembly handling of unaligned input are the main risks.

## Test Signals

SHA-224/SHA-256 KUnit vectors, HMAC tests, FIPS HMAC-SHA256 self-test, and accelerated-versus-generic comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha256_asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha256_asm.S

## Purpose

This SPARC64 assembly file implements SHA-256 block compression with SPARC crypto/VIS opcodes. It was read as a complete 78-line file.

## Important APIs, Types, and Functions

It exports `sha256_sparc64_transform(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. It uses `VISEntryHalf`, `VISExitHalf`, and the `SHA256` opcode macro.

## Control Flow

The transform loads eight 32-bit state words into floating registers, chooses aligned or unaligned input flow, processes each 64-byte block with the `SHA256` macro, advances the input pointer, decrements block count, then stores the updated state.

## State and Persistence Behavior

The caller's SHA-256 state is updated in place. Message words and intermediate state live in floating registers during the VIS-protected region.

## Dependencies and Integration Points

It depends on SPARC linkage, opcode, and VIS macros, is declared by `sparc/sha256.h`, and is called from generic SHA-256/SHA-224 streaming and HMAC code.

## Risks and Edge Cases

Risks include unaligned input reconstruction, VIS state preservation, and exact state word ordering.

## Test Signals

SHA-224/SHA-256 KUnit vectors, unaligned inputs, multi-block messages, and fallback comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha256_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha512.h -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha512.h

## Purpose

This SPARC64 header dispatches SHA-384/SHA-512 block compression to SPARC SHA512 opcodes when available. It was read as a complete 42-line file.

## Important APIs, Types, and Functions

It defines `have_sha512_opcodes`, declares `sha512_sparc64_transform`, implements `sha512_blocks`, and defines `sha512_mod_init_arch`.

## Control Flow

Initialization checks SPARC crypto hardware capability, reads ASR26, tests `CFR_SHA512`, enables the static key, and logs acceleration. Runtime block compression calls SPARC assembly when enabled or generic C otherwise.

## State and Persistence Behavior

The static key persists after init. SHA-384/SHA-512 contexts and block states are caller-owned.

## Dependencies and Integration Points

It depends on SPARC hwcap, opcode, and PSTATE headers and integrates `sparc/sha512_asm.S` with `sha512.c`.

## Risks and Edge Cases

Feature detection, assembly ABI compatibility, and 64-bit state word ordering are the main risks.

## Test Signals

SHA-384/SHA-512 KUnit vectors, HMAC tests, FIPS HMAC-SHA512 self-test, and SPARC generic comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha512_asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/sparc/sha512_asm.S

## Purpose

This SPARC64 assembly file implements SHA-512 block compression with SPARC crypto/VIS opcodes. It was read as a complete 102-line file.

## Important APIs, Types, and Functions

It exports `sha512_sparc64_transform(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. It uses `VISEntry`, `VISExit`, and the `SHA512` opcode macro.

## Control Flow

The function loads eight 64-bit state words, checks input alignment, and loops over 128-byte blocks. Aligned input is loaded directly; unaligned input is aligned with `alignaddr` and `faligndata`. Each block is compressed by `SHA512`, the pointer advances by 128 bytes, and final state words are stored back.

## State and Persistence Behavior

The caller's SHA-512 block state is updated in place. Floating registers carry state and schedule inputs during the VIS-protected region.

## Dependencies and Integration Points

It depends on SPARC linkage, opcode, and VIS macros. It is declared by `sparc/sha512.h` and used by generic SHA-384/SHA-512 code.

## Risks and Edge Cases

Risks include unaligned block reconstruction, 128-byte stride correctness, VIS state management, and state endian/order compatibility.

## Test Signals

SHA-384/SHA-512 KUnit vectors, unaligned input cases, long inputs, and generic comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/sparc/sha512_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/Kconfig -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/Kconfig

## Purpose

This Kconfig file defines KUnit test options for kernel crypto library algorithms and an optional benchmark switch. It was read as a complete 184-line file.

## Important APIs, Types, and Functions

It declares tristate test options for AES-CBC-MAC family, BLAKE2b, BLAKE2s, ChaCha20Poly1305, Curve25519, GHASH, MD5, ML-DSA, NH, Poly1305, POLYVAL, SHA-1, SHA-256/SHA-224, SHA-512/SHA-384, SHA-3, and SM3. It also defines `CRYPTO_LIB_ENABLE_ALL_FOR_KUNIT`, `CRYPTO_LIB_BENCHMARK_VISIBLE`, and `CRYPTO_LIB_BENCHMARK`.

## Control Flow

Kconfig selection controls which KUnit object files are built. Most test options depend on KUNIT and the corresponding crypto library, default to `KUNIT_ALL_TESTS`, and select benchmark visibility. The enable-all option selects the library code needed by the tests without enabling every test directly.

## State and Persistence Behavior

There is no runtime state. Configuration state is persisted in kernel build configuration files.

## Dependencies and Integration Points

It integrates with `lib/crypto/tests/Makefile`, KUnit, and the crypto library Kconfig symbols. Benchmark visibility lets individual test suites include benchmark cases only when selected.

## Risks and Edge Cases

Dependency mistakes can make tests silently unavailable or pull in unwanted crypto code. BLAKE2s is special because it is always built for `/dev/random`, so its test does not depend on a `CRYPTO_LIB_BLAKE2S` option.

## Test Signals

`allnoconfig`/`allyesconfig`/KUnit build coverage, `KUNIT_ALL_TESTS`, and selective enabling of each symbol validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/Makefile -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/Makefile

## Purpose

This Makefile maps crypto KUnit Kconfig symbols to test object files. It was read as a complete 18-line file.

## Important APIs, Types, and Functions

It adds objects such as `aes_cbc_macs_kunit.o`, `blake2b_kunit.o`, `blake2s_kunit.o`, `chacha20poly1305_kunit.o`, `curve25519_kunit.o`, `ghash_kunit.o`, hash KUnit objects, and SM3 tests based on `CONFIG_CRYPTO_LIB_*_KUNIT_TEST`.

## Control Flow

Kbuild includes each object when its corresponding config is built-in or modular. SHA-256 and SHA-512 options each build two test objects to cover the truncated and full variants.

## State and Persistence Behavior

There is no runtime state. Build output composition is determined by configuration.

## Dependencies and Integration Points

It integrates directly with `tests/Kconfig` and the KUnit source files in the same directory.

## Risks and Edge Cases

Missing object mappings make enabled tests disappear at build time. Grouped options must keep their object lists synchronized with the related Kconfig help text.

## Test Signals

KUnit build tests for each config symbol and build logs showing expected objects validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/aes-cmac-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/aes-cmac-testvecs.h

## Purpose

This generated header provides AES-CMAC test vectors for hash-template based KUnit testing. It was read as a complete 181-line file.

## Important APIs, Types, and Functions

It defines `hash_testvecs[]`, each with `data_len` and a 16-byte AES block digest, and `hash_testvec_consolidated[AES_BLOCK_SIZE]` for aggregate verification by the shared hash test template.

## Control Flow

There is no executable flow. `aes_cbc_macs_kunit.c` includes the header and the template iterates over the vector table, computing MACs with a fixed generated key and comparing outputs.

## State and Persistence Behavior

The vectors are static const read-only test data. They persist in the test module image when the KUnit test is built.

## Dependencies and Integration Points

It depends on `AES_BLOCK_SIZE` and the shared `hash-test-template.h` expectations. It was generated by `scripts/crypto/gen-hash-testvecs.py aes-cmac`.

## Risks and Edge Cases

Generated data must match the deterministic test key setup in the test suite. Coverage spans short, block-aligned, near-boundary, and large lengths; if generation changes, consolidated digest values must stay synchronized.

## Test Signals

Successful `aes_cbc_macs` KUnit template cases validate this header, especially incremental update splits and aggregate consolidated digest checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/aes-cmac-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/aes_cbc_macs_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/aes_cbc_macs_kunit.c

## Purpose

This KUnit suite tests AES-CMAC, AES-XCBC-MAC, and AES-CBC-MAC crypto library functions and includes optional benchmark coverage. It was read as a complete 228-line file.

## Important APIs, Types, and Functions

It defines `test_key`, wrapper functions `aes_cmac_init_withtestkey` and `aes_cmac_withtestkey`, suite init/exit, and tests `test_aes_cmac_rfc4493`, `test_aes_xcbcmac_rfc3566`, and `test_aes_cbcmac_rfc3610`. It uses `HASH_KUNIT_CASES` from `hash-test-template.h`.

## Control Flow

Suite init deterministically generates a 256-bit raw key, prepares `test_key`, and initializes shared hash test buffers. Template tests cover CMAC as a fixed-key hash. Additional tests verify RFC 4493 CMAC examples, RFC 3566 XCBC-MAC key preparation and MAC output, and RFC 3610-derived CBC-MAC data including incremental split updates and zero-padding behavior up to a block boundary.

## State and Persistence Behavior

`test_key` is static test-suite state. Per-test keys, contexts, and MAC buffers are stack-local. Shared test buffers are managed by the hash template suite init/exit.

## Dependencies and Integration Points

It depends on `<crypto/aes-cbc-macs.h>`, generated AES-CMAC vectors, KUnit, the shared hash template, and the CRYPTO_INTERNAL namespace.

## Risks and Edge Cases

The deterministic key must match generated vectors. CBC-MAC tests intentionally rely on trailing zero behavior, so regressions in padding or incremental update logic should be caught. Benchmark cases are gated by Kconfig.

## Test Signals

The suite itself is the signal: template vector passes, RFC example passes, split-update coverage, and benchmark execution when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/aes_cbc_macs_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2b-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/blake2b-testvecs.h

## Purpose

This generated header provides BLAKE2b fixed-output test vectors for KUnit hash-template coverage. It was read as a complete 342-line file.

## Important APIs, Types, and Functions

It defines `hash_testvecs[]` with `data_len` and `BLAKE2B_HASH_SIZE` digests, `hash_testvec_consolidated`, and `blake2b_keyed_testvec_consolidated`.

## Control Flow

There is no runtime flow in the header. `blake2b_kunit.c` includes it, then template tests iterate over unkeyed vectors while BLAKE2b-specific tests compare an aggregate of all key-length and output-length combinations.

## State and Persistence Behavior

All data is static const read-only test data included in the test module.

## Dependencies and Integration Points

It depends on BLAKE2b size constants and the shared hash test template. It was generated by `scripts/crypto/gen-hash-testvecs.py blake2b`.

## Risks and Edge Cases

Generated vectors must match deterministic input generation in the template and keyed aggregate test. Because BLAKE2b supports variable output and key lengths, the consolidated keyed digest is an important broad regression signal.

## Test Signals

Passing BLAKE2b KUnit vector, incremental, guarded-buffer, all-key-length, and all-output-length tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2b-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2b_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/blake2b_kunit.c

## Purpose

This KUnit suite tests BLAKE2b hashing, keyed hashing, variable output lengths, guarded buffers, and benchmarks. It was read as a complete 133-line file.

## Important APIs, Types, and Functions

It defines compatibility wrappers `blake2b_default` and `blake2b_init_default`, includes `hash-test-template.h`, and implements `test_blake2b_all_key_and_hash_lens`, `test_blake2b_with_guarded_key_buf`, and `test_blake2b_with_guarded_out_buf`.

## Control Flow

Template tests treat BLAKE2b as an unkeyed fixed-size hash. The all-length test fills deterministic data, iterates key lengths from 0 through `BLAKE2B_KEY_SIZE` and output lengths from 1 through `BLAKE2B_HASH_SIZE`, hashes each result into a main context, and compares a consolidated digest. Guarded-key tests place keys at the end of the shared test buffer and compare one-shot and init-key paths. Guarded-output tests place outputs at the end of the buffer for every output length.

## State and Persistence Behavior

The suite uses shared `test_buf` from the hash template plus stack-local contexts and digests. No persistent runtime state is retained outside KUnit execution.

## Dependencies and Integration Points

It depends on `<crypto/blake2b.h>`, generated vectors, the shared hash template, and KUnit.

## Risks and Edge Cases

Key length zero, maximum key length, output length one, maximum output length, and edge-of-buffer pointers are explicitly covered. Remaining risks are architecture-specific compression bugs if not run on all accelerated platforms.

## Test Signals

All BLAKE2b KUnit cases, benchmark output when enabled, and sanitizer or KASAN runs with guarded buffers are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2b_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2s-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/blake2s-testvecs.h

## Purpose

This generated header provides BLAKE2s fixed-output test vectors and consolidated keyed coverage data. It was read as a complete 238-line file.

## Important APIs, Types, and Functions

It defines `hash_testvecs[]` with `data_len` and `BLAKE2S_HASH_SIZE` digests, `hash_testvec_consolidated`, and `blake2s_keyed_testvec_consolidated`.

## Control Flow

There is no executable control flow. `blake2s_kunit.c` includes the data and the shared hash template iterates over the vectors; the BLAKE2s-specific test uses the keyed consolidated digest as its aggregate oracle.

## State and Persistence Behavior

All vector data is static const test data in the built KUnit object.

## Dependencies and Integration Points

It depends on BLAKE2s size constants and `hash-test-template.h` conventions. It was generated by `scripts/crypto/gen-hash-testvecs.py blake2s`.

## Risks and Edge Cases

The vectors must remain synchronized with deterministic test input generation. Coverage includes short, aligned, near-boundary, and large lengths, while keyed aggregate coverage spans variable key and output lengths.

## Test Signals

Passing BLAKE2s KUnit vector tests, all-key/all-output-length aggregate tests, and guarded buffer tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2s-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2s_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/blake2s_kunit.c

## Purpose

This KUnit suite tests BLAKE2s hashing, keyed hashing, variable output lengths, guarded buffers, and benchmarks. It was read as a complete 133-line file.

## Important APIs, Types, and Functions

It defines `blake2s_default`, `blake2s_init_default`, template hash macros, `test_blake2s_all_key_and_hash_lens`, `test_blake2s_with_guarded_key_buf`, and `test_blake2s_with_guarded_out_buf`.

## Control Flow

Template tests cover unkeyed fixed-size BLAKE2s. The all-length test deterministically fills data and keys, iterates every key length and output length, feeds each result into a main BLAKE2s context, and checks the consolidated digest. Guarded-key tests compare normal and edge-of-buffer key pointers through one-shot and init-key APIs. Guarded-output tests compare normal and edge-of-buffer output pointers for every valid output size.

## State and Persistence Behavior

The suite uses hash-template shared buffers and stack-local contexts. No state persists beyond KUnit execution.

## Dependencies and Integration Points

It depends on `<crypto/blake2s.h>`, generated vectors, KUnit, and shared hash template helpers. BLAKE2s test enablement is special in Kconfig because the implementation is always built for random-device use.

## Risks and Edge Cases

The tests focus on API boundary lengths and guarded pointers. Remaining risk is platform-specific accelerated compression if tests are not run on those platforms.

## Test Signals

Passing KUnit vector, keyed aggregate, guarded key, guarded output, and benchmark cases validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/blake2s_kunit.c -->
