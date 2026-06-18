# subset-b-006083 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/poly1305-armv8.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/poly1305-armv8.pl

## Purpose
Perl perlasm generator for the ARMv8 Poly1305 block, emit, and optional NEON block routines used by the kernel crypto library. In kernel builds it renames the generated public labels to `poly1305_block_init`, `poly1305_blocks_arm64`, and `poly1305_blocks_neon`.

## Important APIs, Types, And Functions
Generated symbols are `poly1305_init`, `poly1305_blocks`, `poly1305_emit`, and `poly1305_blocks_neon`; kernel preprocessor aliases expose the first two as arm64 crypto-lib ABI symbols. Internal generated helpers include `poly1305_mult` and `poly1305_splat` for multiplication and key-power table setup.

## Control Flow
`poly1305_init` zeros the accumulator, clamps and stores `r`, and seeds an impossible key-power marker. `poly1305_blocks` handles 16-byte multiples in scalar base-2^64 form, converts from base-2^26 when needed, accumulates message limbs plus `padbit`, multiplies by `r`, and partially reduces. `poly1305_emit` canonicalizes the accumulator, adds the nonce, and writes the tag. `poly1305_blocks_neon` falls back for short input, otherwise saves ABI registers, converts or initializes base-2^26 state, precomputes powers through `r^4`, processes multi-block vectors, and stores the base-2^26 accumulator marker.

## State, Persistence, And Dependencies
All persistent state is in the caller's `poly1305_block_state` memory: accumulator limbs, clamped key limbs, cached powers, and a radix marker. The script depends on `arm-xlate.pl` when a flavor is requested and on generated AArch64/NEON instructions at build time. No filesystem or runtime persistence exists beyond the generated assembly artifact.

## Integration Points
Included through the arm64 Poly1305 arch header and ultimately used by generic Poly1305 and ChaCha20-Poly1305 code. The kernel wrapper decides between scalar and NEON entry points with ASIMD feature and SIMD-context checks.

## Risks
Risk concentrates in ABI offsets, endian handling, radix conversion, short-input fallback, and lazy key-power caching. Any mismatch between generated labels and C prototypes breaks kernel linkage. NEON state handling must remain inside kernel SIMD critical sections supplied by the caller.

## Test Signals
Known-answer Poly1305 vectors, mixed short and long messages, final partial-block callers that vary `padbit`, big-endian assembly builds, and stress that alternates scalar and NEON paths should all produce identical tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/poly1305-armv8.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/poly1305.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/poly1305.h

## Purpose
ARM64 Poly1305 dispatch header that plugs architecture-specific assembly into the generic Poly1305 library.

## Important APIs, Types, And Functions
Declares `poly1305_block_init`, `poly1305_blocks_arm64`, `poly1305_blocks_neon`, and `poly1305_emit`. Defines the local static key `have_neon`, the arch override `poly1305_blocks()`, and `poly1305_mod_init_arch()`.

## Control Flow
`poly1305_blocks()` checks `have_neon` and `may_use_simd()`. If both pass, it enters `scoped_ksimd()` and calls `poly1305_blocks_neon`; otherwise it uses `poly1305_blocks_arm64`. Module init enables the static branch only when `cpu_have_named_feature(ASIMD)` is true.

## State, Persistence, And Dependencies
State is entirely caller-owned Poly1305 block state. The only global state is a read-mostly static key initialized once after CPU feature detection. It depends on `asm/hwcap.h`, `asm/simd.h`, jump labels, and the generated assembly symbols.

## Integration Points
This header is selected by `CONFIG_CRYPTO_LIB_POLY1305_ARCH` from the generic Poly1305 implementation. It is also on the authentication path used by ChaCha20-Poly1305.

## Risks
Incorrect static key enablement or missing `may_use_simd()` gating can use vector state in invalid kernel contexts. Prototype mismatches with generated assembly would corrupt registers or state. Tests need to cover fallback when SIMD is unavailable or preemption/context forbids it.

## Test Signals
Boot-time CPU feature combinations, forced generic/scalar/NEON paths, and Poly1305 vectors for both one-shot and incremental callers verify the dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/polyval-ce-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/polyval-ce-core.S

## Purpose
ARMv8 Crypto Extensions implementation of POLYVAL multiplication and block evaluation using PMULL.

## Important APIs, Types, And Functions
Exports `polyval_mul_pmull(struct polyval_elem *a, const struct polyval_elem *b)` and `polyval_blocks_pmull(struct polyval_elem *acc, const struct polyval_key *key, const u8 *data, size_t nblocks)`. Major macros are `karatsuba1`, `karatsuba1_store`, `karatsuba2`, `montgomery_reduction`, `full_stride`, and `partial_stride`.

## Control Flow
Single multiplication loads two 128-bit elements, performs Karatsuba polynomial multiplication, reduces modulo `x^128 + x^127 + x^126 + x^121 + 1`, and stores back to `a`. Block processing loads an accumulator and precomputed powers `h^8` through `h^1`, consumes full 8-block strides with interleaved multiplication and one reduction per stride, then handles remaining partial blocks before storing the accumulator.

## State, Persistence, And Dependencies
The accumulator is updated in caller memory. Key powers are read-only input supplied by the generic POLYVAL key setup. The code requires ARMv8 crypto/PMULL instructions and Linux linkage macros.

## Integration Points
This is the acceleration backend for POLYVAL users such as AES-GCM-SIV style authentication in the kernel crypto library.

## Risks
The finite-field representation is Montgomery-style and easy to misuse; key-power order, endian assumptions, and block-count tail handling are the high-risk areas. Register aliases are dense, so ABI clobbering or macro edits can silently corrupt authentication tags.

## Test Signals
POLYVAL known-answer tests should compare generic and PMULL paths for 0, 1, 7, 8, 9, and many-block inputs, with randomized key powers and accumulator seeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/polyval-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1-ce-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1-ce-core.S

## Purpose
ARMv8 SHA1 Crypto Extensions block transform for the kernel SHA1 block API.

## Important APIs, Types, And Functions
Exports `sha1_ce_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. Uses macros `loadrc`, `add_only`, and `add_update` around `sha1h`, `sha1c`, `sha1p`, `sha1m`, `sha1su0`, and `sha1su1`.

## Control Flow
The function loads SHA1 round constants and the 160-bit state, then loops over 64-byte blocks. Each block is loaded big-endian via `rev32`, expanded with SHA1 schedule instructions, run through all rounds, added back to the chaining state, and stored after `nblocks` reaches zero.

## State, Persistence, And Dependencies
Only the caller-provided block state is mutated. There is no persistent global state in assembly. It depends on ARMv8 SHA1 instructions and is only called by the dispatch header after CPU feature and SIMD-context gating.

## Integration Points
`sha1.h` routes generic SHA1 block processing to this function when `have_ce` is enabled and SIMD is allowed.

## Risks
SHA1 is legacy and collision-broken for new designs, so integration must remain for compatibility only. Implementation risks are endian conversion, state layout at five 32-bit words, and incomplete feature gating before executing CE opcodes.

## Test Signals
SHA1 known-answer vectors, multi-block messages, incremental messages crossing 64-byte boundaries, and forced generic-vs-CE comparisons are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1.h

## Purpose
ARM64 SHA1 architecture dispatch header that selects the SHA1 Crypto Extensions transform when available.

## Important APIs, Types, And Functions
Declares `sha1_ce_transform`, defines static key `have_ce`, overrides `sha1_blocks()`, and provides `sha1_mod_init_arch()`.

## Control Flow
`sha1_blocks()` branches to `sha1_ce_transform()` inside `scoped_ksimd()` when the static key is likely and `may_use_simd()` succeeds. Otherwise it calls `sha1_blocks_generic()`. Init enables the key if `cpu_have_named_feature(SHA1)`.

## State, Persistence, And Dependencies
Hash state is caller-owned. Persistent state is a single static key initialized after CPU feature detection. Dependencies include `asm/simd.h`, `linux/cpufeature.h`, and the generic SHA1 implementation.

## Integration Points
Included by the generic SHA1 library when arm64 arch acceleration is configured. It is used by HMAC and FIPS self-test paths that rely on SHA1 compatibility.

## Risks
Incorrect use of CE without `may_use_simd()` can break kernel execution contexts. The fallback must remain present for CPUs lacking SHA1 CE. Algorithm-level risk is SHA1's weak collision security.

## Test Signals
Feature-gated boot tests, KUnit or crypto testmgr SHA1 vectors, and forced static-key off runs verify the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha2-armv8.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha2-armv8.pl

## Purpose
OpenSSL-derived perlasm generator for ARMv8 SHA-256 and SHA-512 block transforms, including scalar code and SHA256 NEON/hardware variants.

## Important APIs, Types, And Functions
Generates `sha256_block_data_order` or `sha512_block_data_order` depending on output name. For SHA256 it can also generate `sha256_block_armv8` for hardware SHA instructions and `sha256_block_neon` for ASIMD schedule acceleration. Important generator subroutines are `BODY_00_xx`, `Xpreload`, `Xupdate`, and the NEON body helpers.

## Control Flow
The script chooses 32-bit or 64-bit word parameters from the output name, emits constants, emits the scalar block loop, and for SHA256 emits optional hardware and NEON paths. Non-kernel builds dispatch based on OpenSSL capability flags; kernel use exposes the selected symbols to C dispatch code. The generated loops load state, convert input endianness, expand the message schedule, process 64 or 80 rounds, add chaining state, and iterate over blocks.

## State, Persistence, And Dependencies
Runtime state is only the caller's SHA block state. Build-time dependencies are Perl and `arm-xlate.pl`. Generated code depends on AArch64 ABI rules and optional ARMv8 SHA/NEON instructions.

## Integration Points
The arm64 SHA256 and SHA512 headers declare and dispatch to the generated block functions, while `sha256-ce.S` and `sha512-ce-core.S` provide newer CE-specific alternatives.

## Risks
Generated assembly is sensitive to output filename, flavor, register allocation, and kernel/non-kernel preprocessor branches. Endian conversion and stack save/restore errors would break all hashes. Since this is imported crypto assembly, local modifications need vector parity tests.

## Test Signals
SHA-224, SHA-256, SHA-384, and SHA-512 testmgr vectors, long-message tests, big-endian builds, and comparison of scalar, NEON, and CE/hardware paths are required signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha2-armv8.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha256-ce.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha256-ce.S

## Purpose
ARMv8 Crypto Extensions SHA-224/SHA-256 transform plus a two-buffer SHA-256 finalization fast path.

## Important APIs, Types, And Functions
Exports `sha256_ce_transform` and `sha256_ce_finup2x`. Uses `.Lsha2_rcon`, `load_round_constants`, `add_only`, `add_update`, `do_4rounds_2x`, and `do_16rounds_2x`. Assumes `struct __sha256_ctx` offsets for `state`, `bytecount`, and `buf`.

## Control Flow
`sha256_ce_transform()` loads round constants and state, loops over 64-byte blocks, byte-swaps input words, runs SHA256 CE rounds with schedule updates, adds chaining state, and stores state. `sha256_ce_finup2x()` clones an initial context into two states, folds any buffered bytes, interleaves rounds for two equal-length message tails, constructs padding and count blocks, then byte-swaps and stores both digests.

## State, Persistence, And Dependencies
The block transform mutates caller state. The finup path reads an immutable context and writes two digest buffers. It depends on ARM SHA2 instructions, vector registers, and exact C struct layout verified by `sha256.h`.

## Integration Points
Selected by `sha256.h` when SHA2 CE is available. The two-buffer finup hook accelerates callers that finalize two same-length SHA-256 streams from the same base context.

## Risks
`sha256_ce_finup2x()` has tight preconditions: `len >= SHA256_BLOCK_SIZE`, `len <= INT_MAX`, equal tail lengths, and accessible 64-byte reads for padding construction. Offset drift in `struct __sha256_ctx` would be severe, hence the header assertions. The stack scratch area and final-step state machine are high-risk for boundary lengths 56, 64, and buffered contexts.

## Test Signals
Generic-vs-CE comparison, SHA256 and SHA224 vectors, two-way finup tests for buffered and unbuffered contexts, lengths around 56/63/64/65 bytes, and KMSAN output initialization checks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha256-ce.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha256.h

## Purpose
ARM64 SHA-256 architecture dispatch header for scalar, NEON, CE, and two-way finalization acceleration.

## Important APIs, Types, And Functions
Declares `sha256_block_data_order`, `sha256_block_neon`, `sha256_ce_transform`, and `sha256_ce_finup2x`. Defines static keys `have_neon` and `have_ce`, `sha256_blocks()`, `sha256_finup_2x_arch()`, `sha256_finup_2x_is_optimized_arch()`, and `sha256_mod_init_arch()`.

## Control Flow
Block processing prefers NEON when ASIMD is enabled and SIMD may be used; inside the SIMD section it chooses CE if SHA2 is present, else NEON, otherwise scalar. The 2x finup path additionally requires CE, `len >= SHA256_BLOCK_SIZE`, `len <= INT_MAX`, and SIMD availability before calling assembly and unpoisoning outputs.

## State, Persistence, And Dependencies
Persistent state is two static keys set at module init. Hash state is caller-owned. Static assertions bind assembly assumptions to `struct __sha256_ctx` offsets.

## Integration Points
Included by the generic SHA256 library under arm64 acceleration. The optimized 2x hook is exposed to generic SHA256 finalization logic that can batch matching tails.

## Risks
The 2x path is only valid for SHA-256, not SHA-224, because digest size and context finalization semantics are fixed by the assembly prototype. Missing KMSAN unpoisoning would cause false positives. Static key and SIMD gating errors can select invalid instructions or corrupt vector state.

## Test Signals
Boot-time feature matrix tests, testmgr SHA256/SHA224 vectors, paired finup vectors, forced scalar fallback, and sanitizer runs around the 2x outputs are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3-ce-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3-ce-core.S

## Purpose
ARMv8.2 SHA3 Crypto Extensions implementation of Keccak absorb and permutation.

## Important APIs, Types, And Functions
Exports `sha3_ce_transform(struct sha3_state *state, const u8 *data, size_t nblocks, size_t block_size)`. Defines instruction macros `eor3`, `rax1`, `bcax`, and `xar`, plus the 24-round constant table `.Lsha3_rcon`.

## Control Flow
The function loads the 25-lane Keccak state into vector registers. For each block it XORs input lanes according to `block_size` branches for SHA3-512, SHA3-384, SHA3-256/SHAKE256, SHA3-224, and SHAKE128, then runs 24 rounds using SHA3 CE ternary XOR, rotate-XOR, Chi, and round constant operations. After all blocks it stores the state.

## State, Persistence, And Dependencies
State is the caller's `sha3_state`. The assembly has no persistent storage. It depends on ARMv8.2 SHA3 instructions encoded with `.inst` and on the wrapper to gate CPU features and SIMD context.

## Integration Points
Called by `sha3.h` for both absorbing data blocks and for `sha3_keccakf()` by passing a zero block.

## Risks
Only specific rate values are supported by control-flow assumptions. A bad `block_size` from the caller could absorb the wrong number of lanes. Encoded instruction macros are less self-checking than mnemonic assembly and require assembler/CPU compatibility.

## Test Signals
SHA3-224/256/384/512 and SHAKE128/256 vectors, direct Keccak-f tests through finalization, and generic-vs-CE comparisons for every rate value are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3.h

## Purpose
ARM64 SHA3 dispatch header that replaces generic absorb and Keccak permutation with SHA3 CE implementations when available.

## Important APIs, Types, And Functions
Declares `sha3_ce_transform`, defines static key `have_sha3`, overrides `sha3_absorb_blocks()` and `sha3_keccakf()`, and provides `sha3_mod_init_arch()`.

## Control Flow
Absorb uses CE when the static key is enabled and `may_use_simd()` succeeds; otherwise it calls `sha3_absorb_blocks_generic()`. `sha3_keccakf()` uses the CE transform with a static zero block and `SHA3_512_BLOCK_SIZE` to run a plain permutation, or falls back to `sha3_keccakf_generic()`.

## State, Persistence, And Dependencies
State is caller-owned `sha3_state`. Persistent state is the static key enabled on `cpu_have_named_feature(SHA3)`. Dependencies include kernel SIMD helpers and CPU feature detection.

## Integration Points
Used by the generic SHA3/SHAKE implementation and by FIPS SHA3-256 self-test vectors.

## Risks
The zero-block permutation trick depends on transform semantics: zero input must only trigger Keccak-f without changing absorbed lanes. SIMD gating must protect vector registers. Unsupported rates must not reach the assembly path.

## Test Signals
SHA3 and SHAKE vectors across all rates, tests invoking finalization with no pending data, and fallback-vs-CE comparisons validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha512-ce-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha512-ce-core.S

## Purpose
ARMv8 SHA512 Crypto Extensions block transform for SHA-384/SHA-512 style 64-bit SHA2 states.

## Important APIs, Types, And Functions
Exports `sha512_ce_transform(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. Uses a `dround` macro, `sha512h`, `sha512h2`, `sha512su0`, `sha512su1`, and the `.Lsha512_rcon` table.

## Control Flow
For each 128-byte block, the transform loads eight 64-bit message vectors, reverses bytes for big-endian SHA words, snapshots the current state, performs 80 rounds while updating the schedule, adds the original chaining state, and loops until all blocks are consumed.

## State, Persistence, And Dependencies
Mutates only the caller's `sha512_block_state`. It requires ARM SHA512 instructions and is expected to be called only from the feature-gated wrapper.

## Integration Points
`sha512.h` dispatches to this implementation when the SHA512 CPU feature is present and SIMD may be used. Generic code otherwise uses `sha512_block_data_order`.

## Risks
State lane ordering, byte swapping, and round constant sequencing are critical. Since SHA-384 and SHA-512 share the block function, digest-specific initialization and finalization must remain in generic code.

## Test Signals
SHA-384 and SHA-512 known-answer vectors, long messages over many blocks, and generic-vs-CE comparisons on CPUs with and without SHA512 instructions should cover this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha512-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha512.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha512.h

## Purpose
ARM64 SHA512 dispatch header that chooses between generated scalar assembly and SHA512 CE assembly.

## Important APIs, Types, And Functions
Declares `sha512_block_data_order` and `sha512_ce_transform`, defines static key `have_sha512_insns`, overrides `sha512_blocks()`, and provides `sha512_mod_init_arch()`.

## Control Flow
`sha512_blocks()` calls CE inside `scoped_ksimd()` when the SHA512 static key is enabled and SIMD is usable. Otherwise it calls the scalar block routine. Init enables the key when `cpu_have_named_feature(SHA512)`.

## State, Persistence, And Dependencies
Hash state is caller-owned. The static key is global, read-mostly, and initialized once. It depends on arm64 SIMD and CPU feature helpers.

## Integration Points
Included by the generic SHA512 library for arm64 acceleration. It supports SHA512-family consumers including HMAC-SHA512 and FIPS self-tests.

## Risks
CE dispatch without a SHA512 feature would fault. Missing scalar fallback would break older ARM64 CPUs. Shared block function use across SHA-384 and SHA-512 requires generic code to keep algorithm-specific state separate.

## Test Signals
SHA384/SHA512 testmgr vectors, forced static-key fallback, and tests under contexts where `may_use_simd()` is false validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-ce-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-ce-core.S

## Purpose
ARMv8 SM3 Crypto Extensions block transform for the Chinese SM3 hash.

## Important APIs, Types, And Functions
Exports `sm3_ce_transform(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. Uses SM3 instructions such as `sm3ss1`, `sm3tt1a/b`, `sm3tt2a/b`, `sm3partw1`, and `sm3partw2` through `round` and `qround` macros, with constants in `.Lt`.

## Control Flow
The transform loads state, reorders it into vector-friendly form, loads each 64-byte block, byte-swaps words, runs the first and second SM3 round families with schedule expansion, XORs the result with the previous state per SM3 compression, loops for all blocks, and stores state in the C layout.

## State, Persistence, And Dependencies
Only caller state is updated. The code has no persistent storage and depends on ARM SM3 instructions plus wrapper-side feature gating.

## Integration Points
`sm3.h` selects this path when both ASIMD and SM3 features are present; otherwise it may use the NEON assembly or generic C.

## Risks
State reorder around load/store is easy to break. The CE path and NEON path must produce identical compression results. Executing SM3 instructions without the CPU feature would fault.

## Test Signals
SM3 known-answer vectors, multi-block messages, randomized generic-vs-CE comparisons, and CPU feature matrix tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-neon-core.S

## Purpose
ARM64 ASIMD/NEON implementation of SM3 compression for CPUs without dedicated SM3 Crypto Extensions.

## Important APIs, Types, And Functions
Exports `sm3_neon_transform(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. Defines register aliases for scalar state, vector schedule registers, stack schedule area, Boolean functions `FF/GG`, round macros `R`, `R1`, `R2`, and extensive load/schedule macros.

## Control Flow
The function saves callee-saved registers, allocates an aligned stack schedule buffer, preloads and byte-swaps the first block, then loops through 64 SM3 rounds while overlapping schedule precomputation with compression. Between blocks it XORs the compressed state into the chaining variables and preloads the next block. On exit it clears vector temporaries and the stack message expansion area, restores registers, and returns.

## State, Persistence, And Dependencies
State is the caller's SM3 block state. Temporary message expansion lives on the stack and is explicitly cleared. It requires ASIMD but not SM3 CE instructions.

## Integration Points
Selected by `sm3.h` when ASIMD is present but SM3 CE is absent, or as a fallback below the CE path inside the SIMD section.

## Risks
The hand-scheduled macro body is large and sensitive to stack alignment, register preservation, and zeroization. Stack clearing is a useful hardening signal; regressions could leave message data in kernel stack memory.

## Test Signals
SM3 vectors across 1 and many blocks, generic-vs-NEON comparisons, register clobber tests, stack sanitizer runs, and feature-gated selection tests are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3.h

## Purpose
ARM64 SM3 dispatch header selecting CE, NEON, or generic SM3 compression.

## Important APIs, Types, And Functions
Declares `sm3_neon_transform` and `sm3_ce_transform`, defines static keys `have_neon` and `have_ce`, overrides `sm3_blocks()`, and provides `sm3_mod_init_arch()`.

## Control Flow
When ASIMD is enabled and SIMD is usable, `sm3_blocks()` enters `scoped_ksimd()` and picks CE if `have_ce` is enabled, otherwise NEON. If ASIMD or SIMD context is unavailable, it calls `sm3_blocks_generic()`. Init enables ASIMD and then the SM3 CE key when CPU features allow.

## State, Persistence, And Dependencies
Caller-owned block state is the only mutable hash state. Static keys are global feature flags initialized once. Dependencies are CPU feature detection and kernel SIMD helpers.

## Integration Points
Used by the generic SM3 crypto library for arm64 acceleration and by higher-level consumers needing SM3 hashes.

## Risks
CE and NEON availability are separate: SM3 CE requires ASIMD wrapping too. A dispatch bug can either fault on unsupported instructions or miss acceleration. Generic fallback is required in non-SIMD contexts.

## Test Signals
Feature matrix tests, forced generic/NEON/CE paths, and SM3 known-answer vectors through streaming APIs verify the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/blake2b.c -->
# sources/distributed-fs/ceph-client/lib/crypto/blake2b.c

## Purpose
Generic BLAKE2b hash and PRF implementation with optional architecture compression override.

## Important APIs, Types, And Functions
Key functions are `blake2b_update()`, `blake2b_final()`, `blake2b_compress_generic()`, `blake2b_increment_counter()`, and `blake2b_set_lastblock()`. It exports update and final symbols and includes `blake2b.h` for an arch `blake2b_compress` when configured.

## Control Flow
The compression loop increments the 128-bit byte counter, loads a 128-byte block as little-endian words, initializes the 16-word work vector from chaining state, IV, counters, and finalization flags, runs 12 BLAKE2b rounds using the sigma table, and XORs results into `ctx->h`. Update buffers partial data, compresses complete non-final blocks, and leaves the last block buffered. Final marks the last block, pads with zeroes, compresses with the actual byte count, writes little-endian output, and zeroes the context.

## State, Persistence, And Dependencies
State is in `struct blake2b_ctx`: chaining words, counters, flags, output length, buffer, and buffer length. No filesystem persistence exists. It depends on kernel endian helpers, `unrolled_full`, module exports, and optional arch compression.

## Integration Points
Provides exported crypto-lib BLAKE2b streaming primitives used by in-kernel keyed hashing and PRF callers. Optional `blake2b_mod_init_arch()` is invoked at subsys init if an arch header defines it.

## Risks
Finalization consumes and zeroes the context, so callers must not reuse it. Multi-block compression requires `inc == BLAKE2B_BLOCK_SIZE`; debug warns on misuse. Output length must have been initialized correctly by the caller.

## Test Signals
BLAKE2b known-answer vectors, keyed and unkeyed PRF cases, empty input, one-block and multi-block messages, variable digest sizes, and generic-vs-arch comparisons validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/blake2b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/blake2s.c -->
# sources/distributed-fs/ceph-client/lib/crypto/blake2s.c

## Purpose
Generic BLAKE2s hash and PRF implementation with optional architecture compression override.

## Important APIs, Types, And Functions
Key functions are `blake2s_update()`, `blake2s_final()`, `blake2s_compress_generic()`, `blake2s_increment_counter()`, and `blake2s_set_lastblock()`. It exports update and final symbols.

## Control Flow
Compression increments the 64-bit effective counter split over two 32-bit words, loads a 64-byte little-endian message block, initializes the work vector from chaining state, IV, counter, and final flags, executes 10 rounds with the BLAKE2s sigma table, and folds the work vector back into state. Update fills the partial buffer, compresses all but the final block, and buffers the tail. Final sets the last-block flag, zero-pads, compresses with the real buffered length, writes little-endian output, and wipes the context.

## State, Persistence, And Dependencies
All state is `struct blake2s_ctx`. There is no external persistence. It depends on kernel endian helpers, unroll support, module exports, and optional `CONFIG_CRYPTO_LIB_BLAKE2S_ARCH`.

## Integration Points
Used by kernel crypto-lib BLAKE2s callers and optional arch backends. A subsys init hook runs only when the arch include defines `blake2s_mod_init_arch`.

## Risks
Like BLAKE2b, the final call destroys the context. Buffer boundary handling around exactly one block and two blocks is critical. Callers must initialize `outlen` and keyed initial state outside this file.

## Test Signals
BLAKE2s official vectors, empty and partial inputs, keyed mode, variable digest lengths, and parity between generic and any arch compression are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/blake2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/chacha-block-generic.c -->
# sources/distributed-fs/ceph-client/lib/crypto/chacha-block-generic.c

## Purpose
Generic ChaCha core permutation and HChaCha block functions.

## Important APIs, Types, And Functions
Defines internal `chacha_permute()` and exports `chacha_block_generic()` plus `hchacha_block_generic()`. It operates on `struct chacha_state` and constants from `<crypto/chacha.h>`.

## Control Flow
`chacha_permute()` validates that the round count is 20 or 12, then runs alternating column and diagonal quarter rounds in two-round increments. `chacha_block_generic()` copies input state, permutes it, adds the original state, writes 64 little-endian keystream bytes, increments counter word 12, and wipes the temporary state. `hchacha_block_generic()` permutes without feed-forward addition and outputs words 0-3 and 12-15 for XChaCha subkey derivation.

## State, Persistence, And Dependencies
The caller's ChaCha state is mutated only by the stream block counter increment. Temporary state is zeroized. Dependencies include bit rotation, unaligned little-endian stores, export symbols, and crypto headers.

## Integration Points
Used by `chacha.c` as the generic backend and by XChaCha initialization in `chacha20poly1305.c`.

## Risks
Counter overflow behavior is only word-12 increment here; higher-level nonce/counter policy must prevent keystream reuse. HChaCha output must not be used as normal stream keystream. Round count warning does not prevent execution if invalid in non-fatal debug configurations.

## Test Signals
RFC ChaCha20 and HChaCha/XChaCha vectors, 12-round test cases if supported, counter increment tests, and generic-vs-arch comparisons verify behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/chacha-block-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/chacha.c -->
# sources/distributed-fs/ceph-client/lib/crypto/chacha.c

## Purpose
Streaming ChaCha wrapper that selects generic or architecture-specific crypt and HChaCha implementations.

## Important APIs, Types, And Functions
Defines `chacha_crypt_generic()` and exports `chacha_crypt()` and `hchacha_block()`. Optional arch include may define `chacha_crypt_arch`, `hchacha_block_arch`, and `chacha_mod_init_arch`.

## Control Flow
The generic stream function repeatedly calls `chacha_block_generic()` to generate a 64-byte keystream block and XOR it into `dst`, then handles a final partial block. Public wrappers delegate to the selected arch or generic functions. Optional module init invokes arch initialization.

## State, Persistence, And Dependencies
The ChaCha state is caller-owned and its counter advances through block generation. A stack keystream block is used for generic XOR and is not explicitly wiped in this file. Dependencies include `crypto_xor_cpy`, module lifecycle helpers, and optional arch headers.

## Integration Points
Used by ChaCha20-Poly1305 and other in-kernel stream cipher consumers. Exports are GPL-only.

## Risks
Caller nonce/counter uniqueness is critical; this file provides no misuse resistance. Overlapping source and destination must match `crypto_xor_cpy()` expectations. Partial final blocks consume a full counter block.

## Test Signals
ChaCha20 RFC vectors, in-place and out-of-place XOR tests, partial lengths from 0 to 65, and arch/generic parity are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/chacha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/chacha20poly1305.c -->
# sources/distributed-fs/ceph-client/lib/crypto/chacha20poly1305.c

## Purpose
ChaCha20-Poly1305 and XChaCha20-Poly1305 AEAD construction, including linear-buffer and in-place scatterlist APIs.

## Important APIs, Types, And Functions
Exports `chacha20poly1305_encrypt()`, `xchacha20poly1305_encrypt()`, `chacha20poly1305_decrypt()`, `xchacha20poly1305_decrypt()`, `chacha20poly1305_encrypt_sg_inplace()`, and `chacha20poly1305_decrypt_sg_inplace()`. Internal helpers include `chacha_load_key()`, `xchacha_init()`, `__chacha20poly1305_encrypt()`, `__chacha20poly1305_decrypt()`, and `chacha20poly1305_crypt_sg_inplace()`.

## Control Flow
Encryption derives the one-time Poly1305 key from ChaCha block 0, authenticates associated data with padding, encrypts plaintext with ChaCha20, authenticates ciphertext with padding and length block, then writes the tag. Decryption authenticates associated data and ciphertext before decrypting on tag match. XChaCha first derives a subkey with HChaCha over the first 16 nonce bytes and builds a 96-bit nonce from the final 8 bytes. Scatterlist mode walks pages atomically, handles partial ChaCha blocks across segments, and stores or verifies the tag at the end of the scatterlist.

## State, Persistence, And Dependencies
All state is per call: `chacha_state`, `poly1305_desc_ctx`, scatterlist iterator, and temporary union. Secret key words, IVs, tags, and stream buffers are explicitly zeroed where held in local unions or states. It depends on ChaCha, Poly1305, zero page padding, scatterlist helpers, unaligned loads, and constant-time `crypto_memneq`.

## Integration Points
Provides exported AEAD helpers used by kernel protocols needing compact crypto-lib primitives without the full crypto API request layer.

## Risks
Nonce reuse with a key is catastrophic and must be prevented by callers. Scatterlist mode has complex tag placement logic when the tag crosses segment boundaries. `src_len > INT_MAX` is rejected for SG mode. Decryption must never release plaintext before tag verification; linear mode satisfies this by decrypting only after `crypto_memneq` succeeds.

## Test Signals
RFC8439 vectors, XChaCha vectors, tampered tag tests, associated-data padding lengths, plaintext lengths around 0/15/16/64, in-place SG layouts with tag split across segments, and nonce/key zeroization checks are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/chacha20poly1305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/curve25519-fiat32.c -->
# sources/distributed-fs/ceph-client/lib/crypto/curve25519-fiat32.c

## Purpose
32-bit Fiat-derived generic Curve25519 scalar multiplication backend using 10-limb field arithmetic.

## Important APIs, Types, And Functions
Defines `fe` and `fe_loose` limb types, field helpers such as `fe_frombytes`, `fe_tobytes`, `fe_add`, `fe_sub`, `fe_mul_*`, `fe_sq_*`, `fe_invert`, `fe_cswap`, `fe_mul121666`, and exports implementation symbol `curve25519_generic()`.

## Control Flow
Inputs are decoded into field elements, the scalar is copied and clamped, and a Montgomery ladder iterates from bit 254 down to 0. Each step conditionally swaps projective points in constant-time, performs differential addition and doubling with loose/tight field elements, and updates the swap flag. After the loop it swaps once more, inverts `z`, multiplies to recover affine `x`, serializes 32 bytes, and zeroes the scalar.

## State, Persistence, And Dependencies
All arithmetic state is stack-local. The caller receives only the public output. It depends on Curve25519 header helpers, fixed-width integer types, and generated Fiat arithmetic invariants.

## Integration Points
Selected by `curve25519.c` when no arch backend exists and the build target does not use the HACL64 backend. It provides the same `curve25519_generic` ABI as the 64-bit backend.

## Risks
Constant-time behavior depends on `fe_cswap` and generated arithmetic not being optimized into branches. Limb bounds must match Fiat preconditions. Stack-local secret scalar is wiped, but intermediate field elements also contain secret-dependent values and rely on stack lifetime.

## Test Signals
RFC7748 vectors, all-zero and low-order point rejection via wrapper, randomized cross-checks against HACL64 or arch backends, and side-channel review of generated code are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/curve25519-fiat32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/curve25519-hacl64.c -->
# sources/distributed-fs/ceph-client/lib/crypto/curve25519-hacl64.c

## Purpose
64-bit HACL-derived generic Curve25519 backend using 5 51-bit limbs and 128-bit intermediates.

## Important APIs, Types, And Functions
Defines constant-time mask helpers, carry/reduction helpers, multiplication and squaring routines, `crecip`, point swap/copy functions, Montgomery ladder helpers, format expand/contract routines, and `curve25519_generic()`.

## Control Flow
The backend expands the basepoint into 51-bit limbs, clamps a local scalar copy, initializes projective ladder state, runs the ladder over all scalar bytes using conditional swaps and add/double steps, converts projective coordinates back by inverting `z`, contracts the field element to canonical 32-byte little-endian form, and wipes large temporary buffers and scalar copies.

## State, Persistence, And Dependencies
All state is stack-local, including aligned buffers for points and scalar. It depends on `u128`, unaligned little-endian accessors, and Curve25519 constants. No persistent global state exists.

## Integration Points
Used as `curve25519_generic` on 64-bit targets with 128-bit integer support when no arch override is selected by `curve25519.c`.

## Risks
Correctness depends on 128-bit arithmetic availability and carry bounds. Constant-time conditional swaps and trim masks must remain branchless. As with all X25519 code, low-order outputs are rejected by the wrapper, not by this backend itself.

## Test Signals
RFC7748 vectors, random scalar/basepoint comparisons against known-good implementations, low-order point wrapper tests, and compiler-output review for secret-dependent branches are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/curve25519-hacl64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/curve25519.c -->
# sources/distributed-fs/ceph-client/lib/crypto/curve25519.c

## Purpose
Public Curve25519/X25519 crypto-lib wrapper selecting arch or generic scalar multiplication and enforcing null-output rejection.

## Important APIs, Types, And Functions
Exports `curve25519()` and `curve25519_generate_public()`. Defines static aligned `curve25519_null_point` and `curve25519_base_point`. Optional arch include may provide `curve25519_arch`, `curve25519_base_arch`, and `curve25519_mod_init_arch`.

## Control Flow
`curve25519()` computes scalar multiplication with the selected backend and returns true only if the output differs from all zeroes. `curve25519_generate_public()` first rejects an all-zero secret, then multiplies by the canonical base point and rejects an all-zero public output. Optional module init calls arch initialization.

## State, Persistence, And Dependencies
No state persists across calls beyond static constant points and optional arch static keys. Secret handling and scalar clamping are delegated to the backend. It depends on `crypto_memneq` for nonzero tests.

## Integration Points
Primary exported API for in-kernel Curve25519 users such as key agreement protocols. It hides backend selection from callers.

## Risks
The wrapper does not authenticate peers or manage protocol-level key validation beyond all-zero output rejection. Secret zeroization is backend-specific. Callers must check the boolean return because `__must_check` marks both exported APIs.

## Test Signals
Public-key generation vectors, shared-secret agreement tests, all-zero secret rejection, low-order basepoint rejection, and arch/generic parity are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/curve25519.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/des.c -->
# sources/distributed-fs/ceph-client/lib/crypto/des.c

## Purpose
Generic DES and Triple DES EDE block cipher implementation for the kernel crypto API.

## Important APIs, Types, And Functions
Exports `des_expand_key()`, `des_encrypt()`, `des_decrypt()`, `des3_ede_expand_key()`, `des3_ede_encrypt()`, and `des3_ede_decrypt()`. Internal pieces include permutation tables `pc1`, `rs`, `pc2`, S-box tables `S1` through `S8`, key schedule helpers `des_ekey()` and `dkey()`, and round/permutation macros `IP`, `FP`, and `ROUND`.

## Control Flow
DES key expansion validates key length, builds 16 round subkeys using PC1/PC2 lookup tables and rotations, and rejects weak keys by returning `-ENOKEY`. Encryption/decryption load a 64-bit block little-endian, apply initial permutation, run 16 Feistel rounds with subkeys forward or reverse, apply final permutation, and store output. 3DES verifies keying material, builds encrypt/decrypt/encrypt schedules for three keys, and runs three DES phases in EDE order for encryption or reverse order for decryption.

## State, Persistence, And Dependencies
Expanded keys are stored in caller-owned `des_ctx` or `des3_ede_ctx`. No runtime global state exists; tables are static read-only. It depends on internal DES verification helpers, unaligned accessors, and Linux crypto error codes.

## Integration Points
Used by legacy cipher registrations and compatibility paths. FIPS mode may reject DES/3DES use elsewhere, but this file provides the primitives and weak-key handling.

## Risks
DES is cryptographically obsolete and 3DES is legacy with small block-size risks. Table lookups are key/data dependent and not designed as a modern constant-time side-channel-resistant implementation. Weak-key and keying-option handling must align with `des3_ede_verify_key()`.

## Test Signals
NIST DES/3DES known-answer vectors, weak-key rejection, invalid key length errors, encrypt-decrypt round trips, and keying-option tests for 3DES are required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/des.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/fips-mldsa.h -->
# sources/distributed-fs/ceph-client/lib/crypto/fips-mldsa.h

## Purpose
Generated ML-DSA-65 FIPS self-test vector header containing signature, public key, and message bytes.

## Important APIs, Types, And Functions
Defines `fips_test_mldsa65_signature`, `fips_test_mldsa65_public_key`, and `fips_test_mldsa65_message` as `static const u8` arrays marked `__initconst __maybe_unused`.

## Control Flow
There is no executable control flow. Including self-test code reads these arrays during init-time FIPS validation and the compiler can drop them when unused.

## State, Persistence, And Dependencies
The arrays live in init-const storage and are not mutable. They depend on `<linux/fips.h>` for annotations and common FIPS declarations.

## Integration Points
Consumed by ML-DSA self-test code to verify post-quantum signature verification against a known message and public key.

## Risks
The header is generated from leancrypto vectors; accidental byte edits, truncation, or length mismatches would invalidate FIPS self-tests. Because arrays are large and opaque, review should verify sizes and source provenance rather than hand-inspect every byte.

## Test Signals
FIPS power-up self-test success for ML-DSA-65, array-size assertions in consuming code, and regeneration diff checks from the source vector are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/fips-mldsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/fips.h -->
# sources/distributed-fs/ceph-client/lib/crypto/fips.h

## Purpose
Generated common FIPS self-test vector header for symmetric, MAC, and hash algorithms.

## Important APIs, Types, And Functions
Defines `fips_test_data`, `fips_test_key`, `fips_test_hmac_sha1_value`, `fips_test_hmac_sha256_value`, `fips_test_hmac_sha512_value`, `fips_test_sha3_256_value`, and `fips_test_aes_cmac_value` as init-const byte arrays.

## Control Flow
There is no executable control flow. FIPS self-test code includes the header and compares algorithm outputs against these constants during initialization.

## State, Persistence, And Dependencies
All state is immutable init-time data. It depends on `<linux/fips.h>` for annotations and is generated by `gen-fips-testvecs.py`.

## Integration Points
Used by FIPS mode self-tests for HMAC-SHA1, HMAC-SHA256, HMAC-SHA512, SHA3-256, and AES-CMAC. It indirectly exercises the accelerated hash files in this subset when enabled.

## Risks
Generated constants are single points of truth for self-test expectations; byte corruption can create false failures or false confidence. Since test data and key are simple fixed strings, these vectors are sanity checks rather than exhaustive algorithm validation.

## Test Signals
FIPS self-test pass/fail at boot, regeneration reproducibility from `gen-fips-testvecs.py`, and consuming-code length checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/fips.h -->
