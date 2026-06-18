# subset-b-006084 research

Grouped research report for the subset B work item. Each section is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/gf128hash.c -->
# sources/distributed-fs/ceph-client/lib/crypto/gf128hash.c

## Purpose
Implements library GHASH and POLYVAL over GF(2^128), including generic constant-time multiplication and dispatch to architecture-specific accelerated hooks. It is intended for AEAD and disk-encryption constructions that need these almost-universal polynomial hashes, not as a standalone cryptographic hash.

## Important APIs, Types, and Functions
- Exports `ghash_preparekey()`, `ghash_update()`, `ghash_final()`, `polyval_preparekey()`, `polyval_update()`, and `polyval_final()`.
- Uses public context/key types from `<crypto/gf128hash.h>`: `struct ghash_key`, `struct ghash_ctx`, `struct polyval_key`, `struct polyval_ctx`, and `struct polyval_elem`.
- `clmul64()` and, on non-`CONFIG_ARCH_SUPPORTS_INT128`, `clmul32()` emulate carryless multiply with "holes" in normal integer multiplication.
- `polyval_mul_generic()` performs Karatsuba 128x128 carryless multiplication followed by reduction in the POLYVAL field.
- `ghash_key_to_polyval()`, `ghash_acc_to_polyval()`, and `polyval_acc_to_ghash()` bridge GHASH's big-endian bit mapping to POLYVAL's little-endian representation.

## Control Flow and State
Key preparation either calls `*_preparekey_arch` or stores the converted/raw key. Updates first complete a buffered partial block, then process full blocks via `*_blocks_arch` or generic loops, then XOR any tail into the accumulator and remember `partial`. GHASH stores partial bytes in reverse block order to preserve the GHASH convention; POLYVAL stores partial bytes in natural order. Finalization multiplies a final partial block when present, serializes the accumulator, and zeroes the whole context with `memzero_explicit()`.

## Dependencies and Integration Points
Depends on kernel unaligned helpers, endian conversion, export/module infrastructure, and optional `$(SRCARCH)/gf128hash.h` hooks selected by `CONFIG_CRYPTO_LIB_GF128HASH_ARCH`. Consumers are expected to initialize contexts with a prepared key and stream input using block-size-neutral update calls.

## Risks and Test Signals
The main correctness risks are representation conversion between GHASH and POLYVAL, reduction constants, and partial-block byte ordering. The generic multiplication is designed to avoid secret-dependent lookup tables; architecture hooks must preserve constant-time behavior and equivalent accumulator/key formats. Tests should include NIST GCM GHASH vectors, RFC 8452 POLYVAL vectors, split-update equivalence, empty and partial inputs, and generic-vs-arch comparison on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/gf128hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/gf128mul.c -->
# sources/distributed-fs/ceph-client/lib/crypto/gf128mul.c

## Purpose
Provides legacy GF(2^128) multiplication helpers used by crypto modes such as GHASH/GCM. It supports byte-oriented multiply-by-x^8 helpers, a direct constant-time-ish `lle` multiplier, and a large precomputed 64 KiB table implementation for the `bbe` representation.

## Important APIs, Types, and Functions
- Exports `gf128mul_x8_ble()`, `gf128mul_lle()`, `gf128mul_init_64k_bbe()`, `gf128mul_free_64k()`, and `gf128mul_64k_bbe()`.
- Uses `be128`, `le128`, `struct gf128mul_64k`, and `be128_xor()`/`gf128mul_x_lle()`/`gf128mul_x_bbe()` from `<crypto/gf128mul.h>`.
- `gf128mul_table_be` and `xda_le()`/`xda_be()` encode reduction constants for the polynomial `x^128 + x^7 + x^2 + x + 1`.

## Control Flow and State
`gf128mul_lle()` builds a small stack table of powers of the current multiplicand, with odd elements zeroed and even elements holding powers. It XORs both cacheline-adjacent possibilities for each bit to reduce timing variance, then advances the accumulator by x^8 between input bytes. The 64 KiB path allocates sixteen 256-entry tables, fills powers and XOR combinations for each byte position, then multiplies by table lookup and XOR accumulation. `gf128mul_free_64k()` clears table memory through `kfree_sensitive()`.

## Dependencies and Integration Points
Uses kernel allocation (`kzalloc_obj`, `kfree_sensitive`), endian helpers, and crypto GF128 types. The table API is integrated by callers that can afford per-key memory for faster repeated multiplication.

## Risks and Test Signals
Table lookups indexed by data/key material may be side-channel sensitive depending on caller use; the direct `lle` path has explicit alignment/cacheline mitigation. Allocation failure during 64 KiB table setup must clean partial state, which this file handles by calling `gf128mul_free_64k()`. Test signals include multiplication identity/zero cases, representation-specific known vectors, allocation-failure injection, and cross-checks against a simple reference multiplier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/gf128mul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/hash_info.c -->
# sources/distributed-fs/ceph-client/lib/crypto/hash_info.c

## Purpose
Defines exported metadata tables mapping kernel `enum hash_algo` values to algorithm names and digest sizes.

## Important APIs, Types, and Functions
- Exports `hash_algo_name[HASH_ALGO__LAST]`.
- Exports `hash_digest_size[HASH_ALGO__LAST]`.
- Covers MD4, MD5, SHA-1, RIPEMD variants, SHA-2, Whirlpool, Tiger, SM3, Streebog, and SHA-3 variants as defined in `<crypto/hash_info.h>`.

## Control Flow and State
There is no runtime control flow. The file initializes two const arrays indexed by enum values. State is static read-only data exported for other modules.

## Dependencies and Integration Points
Integrated by signature, integrity, key, and crypto consumers that need a stable enum-to-name or enum-to-digest-size mapping. It depends on digest-size macros from `<crypto/hash_info.h>` and kernel symbol exports.

## Risks and Test Signals
The main risk is table drift when new enum members are added or digest constants change. Tests or build-time review should confirm every live enum value has the expected name/size, that absent algorithms remain null/zero by design, and that MD4 intentionally maps to `MD5_DIGEST_SIZE` only because both are 128-bit digests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/hash_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/md5.c -->
# sources/distributed-fs/ceph-client/lib/crypto/md5.c

## Purpose
Implements MD5 and HMAC-MD5 library functions, with a generic compression function and optional architecture-optimized block processing. This is compatibility crypto, not collision-resistant modern hashing.

## Important APIs, Types, and Functions
- Exports `md5_init()`, `md5_update()`, `md5_final()`, `md5()`, `hmac_md5_preparekey()`, `hmac_md5_init()`, `hmac_md5_init_usingrawkey()`, `hmac_md5_final()`, `hmac_md5()`, and `hmac_md5_usingrawkey()`.
- Uses `struct md5_ctx`, `struct md5_block_state`, `struct hmac_md5_key`, and `struct hmac_md5_ctx` from crypto headers.
- `md5_block_generic()` implements the four MD5 rounds through `F1`-`F4` and `MD5STEP()`.
- `__md5_final()` pads, appends bit length, runs the last block, and serializes state.

## Control Flow and State
`md5_update()` tracks total byte count, fills a 64-byte buffer, dispatches full blocks to `md5_blocks`, and leaves any tail buffered. `md5_final()` pads and zeroes the context. HMAC preparation hashes long keys if needed, XORs with ipad/opad, precomputes inner and outer MD5 states, and clears the derived key. HMAC final computes the inner digest into the working buffer, constructs the one-block outer padded input, finalizes with the precomputed outer state, and zeroes the HMAC context.

## Dependencies and Integration Points
Depends on `<crypto/md5.h>`, `<crypto/hmac.h>`, unaligned/endian helpers, word repeat helpers, and optional `$(SRCARCH)/md5.h` when `CONFIG_CRYPTO_LIB_MD5_ARCH` is enabled. Exported GPL symbols integrate with kernel subsystems still requiring MD5/HMAC-MD5.

## Risks and Test Signals
MD5 must not be used where collision resistance is required. Implementation risks include bytecount overflow semantics, padding boundary cases, endian conversion, and architecture hook equivalence. Tests should include RFC 1321 MD5 vectors, HMAC-MD5 vectors, zero-length input, inputs around 55/56/63/64/65 bytes, split-update equivalence, long HMAC keys, and generic-vs-arch block comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/memneq.c -->
# sources/distributed-fs/ceph-client/lib/crypto/memneq.c

## Purpose
Implements `__crypto_memneq()`, a constant-time memory inequality helper used by the public `crypto_memneq()` wrapper.

## Important APIs, Types, and Functions
- Exports `__crypto_memneq(const void *a, const void *b, size_t size)`.
- `__crypto_memneq_generic()` ORs all byte or word differences without early exit.
- `__crypto_memneq_16()` unrolls the common 16-byte comparison path.
- Uses `OPTIMIZER_HIDE_VAR()` to prevent compiler transformations that could reintroduce data-dependent exits or reductions.

## Control Flow and State
The function dispatches by size: exactly 16 bytes uses a loop-free fast path; all other sizes use the generic loop. It returns nonzero if any byte differs and zero if all compared bytes match. No persistent state is stored.

## Dependencies and Integration Points
Depends on `<crypto/utils.h>`, unaligned access helpers, and `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS` for word-sized loading. It integrates with MAC/tag verification code that must avoid `memcmp()` timing leakage.

## Risks and Test Signals
The function compares exactly the supplied length and does not hide length differences; callers must ensure lengths are public or separately checked safely. Compiler behavior is central to the security property, so generated code review and KUnit/static tests for no early exit are useful. Functional tests should cover equal buffers, first/last-byte differences, 16-byte and non-16-byte lengths, and unaligned inputs on architectures that allow them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/memneq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/chacha-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/mips/chacha-core.S

## Purpose
Provides MIPS assembly implementations of ChaCha stream encryption and HChaCha block derivation.

## Important APIs, Types, and Functions
- Defines global `chacha_crypt_arch(struct chacha_state *state, u8 *dst, const u8 *src, unsigned int bytes, int nrounds)`.
- Defines global `hchacha_block_arch(const struct chacha_state *state, u32 out[HCHACHA_OUT_WORDS], int nrounds)`.
- Uses register macros for ChaCha words `X0`-`X15`, temporary registers, input registers, and `AXR()` quarter-round groups.
- Provides aligned and unaligned store paths plus jump-table entries for final partial words.

## Control Flow and State
`chacha_crypt_arch()` returns immediately for zero bytes, saves callee-saved registers, loads counter word 12 into `NONCE_0`, and loops over 64-byte blocks. Each loop loads the state, executes `nrounds` in two-round steps, adds original state words, endian-converts on big-endian builds, XORs with input, writes output, and increments the counter. Tail handling uses aligned/unaligned jump tables for complete words and byte-by-byte logic for the final one to three bytes. The final counter is written back to the state. `hchacha_block_arch()` runs the same round structure and writes the HChaCha output words.

## Dependencies and Integration Points
Declared by `mips/chacha.h` and selected as an architecture implementation by the generic ChaCha library. It depends on MIPS assembler semantics, `wsbh`/`rotr` availability for endian conversion, and ABI-preserved register rules.

## Risks and Test Signals
Risks include counter writeback errors, final-byte jump-table mistakes, big-endian conversion differences, and ABI register clobbering. Tests should compare aligned and unaligned buffers, in-place encryption, all tail lengths 0-63, multiple `nrounds` values used by the library, HChaCha known vectors, counter wrap behavior expected by callers, and generic-vs-MIPS output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/chacha-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/chacha.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mips/chacha.h

## Purpose
Declares MIPS-optimized ChaCha and HChaCha entry points for the generic ChaCha library.

## Important APIs, Types, and Functions
- Declares `asmlinkage void chacha_crypt_arch(...)`.
- Declares `asmlinkage void hchacha_block_arch(...)`.
- Uses `struct chacha_state`, `HCHACHA_OUT_WORDS`, and standard kernel integer types.

## Control Flow and State
This header has no runtime control flow. It supplies ABI declarations for assembly functions that mutate the ChaCha state counter and write output buffers.

## Dependencies and Integration Points
Included when `CONFIG_CRYPTO_LIB_CHACHA_ARCH` or the MIPS crypto path is enabled. It couples the generic C dispatch to `mips/chacha-core.S`.

## Risks and Test Signals
The declarations must match the assembly ABI exactly, including `asmlinkage` argument passing. Test signals come from successful MIPS builds, modpost symbol resolution, and generic-vs-arch ChaCha/HChaCha vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/chacha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/poly1305-mips.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/mips/poly1305-mips.pl

## Purpose
Perl generator for Cryptogams/OpenSSL-derived MIPS Poly1305 assembly. It emits 64-bit or 32-bit assembly variants for `poly1305_block_init`, `poly1305_blocks`, and `poly1305_emit`.

## Important APIs, Types, and Functions
- Input flavour argument selects `o32`, `n32`, `64`, `nubi32`, or `nubi64`; default is `64`.
- Under `__KERNEL__`, the generated `poly1305_init` symbol is renamed to `poly1305_block_init`.
- Generated functions implement block-state initialization, multi-block accumulation, and tag emission.
- The script emits MIPS R2/R6 differences, endian handling, aligned/unaligned load handling, saved-register masks, and ABI-specific register layouts.

## Control Flow and State
The script builds a `$code` string in two major branches: 64-bit for `64|n32` flavours and 32-bit otherwise. Both branches zero the hash state, clamp the key, precompute `s` multiples, loop over 16-byte blocks with modulo-scheduled reduction, store the accumulator, and emit final tags by reducing, selecting canonical residues, adding nonce, and serializing little-endian bytes. It writes to STDOUT or to a named output path.

## Dependencies and Integration Points
Integrated by the build system that runs the perl generator to create MIPS assembly used by `mips/poly1305.h` declarations and the generic Poly1305 dispatch. It depends on assembler support for MIPS32/MIPS64 R2/R6 variants and the expected kernel symbol names.

## Risks and Test Signals
Generator risks include ABI mismatches, endianness paths, R6 instruction substitutions, register save/restore errors, and divergence between generated symbol names and C declarations. Tests should include regenerating assembly for all intended flavours, building big- and little-endian MIPS configurations, RFC 8439 Poly1305 vectors, unaligned input/key tests, empty input, partial-final-block handling through the generic wrapper, and comparison to the C Donna backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/poly1305-mips.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/poly1305.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mips/poly1305.h

## Purpose
Declares MIPS assembly Poly1305 primitives for the generic Poly1305 wrapper.

## Important APIs, Types, and Functions
- Declares `poly1305_block_init()`, `poly1305_blocks()`, and `poly1305_emit()`.
- Uses `struct poly1305_block_state`, `struct poly1305_state`, `POLY1305_BLOCK_SIZE`, and `POLY1305_DIGEST_SIZE`.

## Control Flow and State
No control flow is present. The declared functions initialize the block state, process complete blocks with caller-provided `hibit`, and emit a digest using a nonce.

## Dependencies and Integration Points
Included by `poly1305.c` when `CONFIG_CRYPTO_LIB_POLY1305_ARCH` is enabled for MIPS. Must match generated assembly from `poly1305-mips.pl`.

## Risks and Test Signals
Declaration/implementation mismatch is the main risk. Build tests on all supported MIPS ABIs plus Poly1305 known vectors through the generic public API are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/sha1.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mips/sha1.h

## Purpose
Provides an OCTEON-accelerated `sha1_blocks()` override for SHA-1 block processing on MIPS systems with OCTEON crypto hardware.

## Important APIs, Types, and Functions
- Defines `octeon_sha1_store_hash()`, `octeon_sha1_read_hash()`, and static `sha1_blocks()`.
- Uses `struct sha1_block_state`, `struct octeon_cop2_state`, and OCTEON crypto register helpers.

## Control Flow and State
`sha1_blocks()` checks `octeon_has_crypto()`. If unavailable, it delegates to `sha1_blocks_generic()`. Otherwise it enables COP2 crypto state, writes the current hash into hardware registers, streams each 64-byte block as eight 64-bit words, starts the hardware SHA-1 operation, reads the resulting hash state, and disables/restores crypto state. Temporary hash-tail union handling avoids leaking the unused word.

## Dependencies and Integration Points
Included by the generic SHA-1 implementation as an architecture override. Depends on `<asm/octeon/crypto.h>` and `<asm/octeon/octeon.h>`.

## Risks and Test Signals
Risks include assuming OCTEON's misaligned access behavior, hash word packing of the fifth SHA-1 word, COP2 state restore bugs, and fallback parity. Tests should compare SHA-1 vectors with and without hardware, run unaligned input buffers, multi-block streams, and preemption/state-save stress where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mips/sha256.h

## Purpose
Provides an OCTEON-accelerated `sha256_blocks()` override for SHA-256 and SHA-224 block processing.

## Important APIs, Types, and Functions
- Defines static `sha256_blocks(struct sha256_block_state *state, const u8 *data, size_t nblocks)`.
- Uses OCTEON 64-bit hash and block register accessors.

## Control Flow and State
The function falls back to `sha256_blocks_generic()` if hardware crypto is unavailable. On hardware, it enables OCTEON crypto, writes the eight 32-bit SHA-256 state words as four 64-bit words, writes each 64-byte block as eight 64-bit words, starts the SHA-256 operation, reads back four 64-bit hash words into the state, and restores COP2 state.

## Dependencies and Integration Points
Included by generic SHA-256 code for MIPS OCTEON builds. It integrates through static function replacement, not exported symbols.

## Risks and Test Signals
Risks include state packing, big/little-endian behavior assumed by OCTEON helpers, and correct fallback when hardware is absent. Test vectors should cover SHA-224 and SHA-256, single and multi-block messages, split updates through the public hash API, and hardware/generic equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/sha512.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mips/sha512.h

## Purpose
Provides an OCTEON-accelerated `sha512_blocks()` override for SHA-512 and SHA-384 block processing.

## Important APIs, Types, and Functions
- Defines static `sha512_blocks(struct sha512_block_state *state, const u8 *data, size_t nblocks)`.
- Uses SHA-512-specific OCTEON hash/block accessors.

## Control Flow and State
The function falls back to `sha512_blocks_generic()` if OCTEON crypto is unavailable. Otherwise it enables hardware crypto, writes all eight 64-bit state words, processes each 128-byte block as sixteen 64-bit words, starts hardware SHA-512, reads back the state, and restores COP2 state.

## Dependencies and Integration Points
Included by generic SHA-512 code on supported MIPS OCTEON configurations. It depends on OCTEON helper headers and the generic block-state layout.

## Risks and Test Signals
Risks include state-register ordering, misaligned block assumptions, and context restore under preemption. Tests should include SHA-384 and SHA-512 vectors, unaligned buffers, multi-block messages, and generic-vs-hardware equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mips/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mldsa.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mldsa.c

## Purpose
Implements ML-DSA signature verification for the kernel crypto library, including FIPS 204 parameter sets, polynomial arithmetic, signature/public-key decoding, challenge reconstruction, and optional FIPS self-test.

## Important APIs, Types, and Functions
- Exports `mldsa_verify(enum mldsa_alg alg, const u8 *sig, size_t sig_len, const u8 *msg, size_t msg_len, const u8 *pk, size_t pk_len)`.
- Defines `struct mldsa_parameter_set`, `struct mldsa_ring_elem`, and `struct mldsa_verification_workspace`.
- Core arithmetic includes `Zq_mult()`, `ntt()`, and `invntt_and_mul_2_32()`.
- Decode/encode helpers include `decode_t1_elem()`, `decode_z()`, `decode_hint_vector()`, `sample_in_ball()`, `rej_ntt_poly()`, `use_hint()`, `use_hint_elem()`, and `encode_w1()`.
- KUnit may export `mldsa_use_hint()` when `CONFIG_CRYPTO_LIB_MLDSA_KUNIT_TEST` is enabled.

## Control Flow and State
Verification selects parameters by algorithm, validates public key and signature lengths, allocates a size-dependent workspace with `kmalloc()`, and frees it with `kfree_sensitive()` through cleanup attributes. It decodes `ctilde`, `z`, and hint vector `h`; rejects malformed z/h values; samples challenge `c`; computes `tr = H(pk)` and `mu = H(tr || domain || msg)`; then hashes reconstructed `w'_1` rows into `ctildeprime`. Each row generates matrix elements from `rho` on demand with SHAKE128, multiplies by decoded z in NTT form, subtracts challenge times scaled public key, inverse-transforms, applies hints, encodes `w1`, and feeds SHAKE256. Verification succeeds only when `ctildeprime` equals `ctilde`; the current compare is `memcmp()`.

## Dependencies and Integration Points
Depends on `<crypto/mldsa.h>`, SHAKE/SHA3 APIs, unaligned helpers, FIPS test vectors in `fips-mldsa.h`, allocation APIs, and module/export infrastructure. Integrated by crypto consumers needing public-key ML-DSA verification. Under `CONFIG_CRYPTO_FIPS`, module init verifies one ML-DSA-65 test vector and panics on failure.

## Risks and Test Signals
Arithmetic range bounds, Montgomery reduction assumptions, decoding malleability checks, hint ordering, and public-key/signature length validation are critical. `memcmp()` leaks first differing byte timing but compares public verification data; any change to secrecy assumptions should revisit this. Tests should include NIST/FIPS 204 vectors for ML-DSA-44/65/87, malformed signatures for z range and hint ordering/omega tails, public-key length/signature length errors, FIPS self-test, KUnit `use_hint()` edge cases around `Q - gamma2`, and cross-checks against a reference implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mldsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/Makefile -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/Makefile

## Purpose
Builds the kernel MPI multiprecision math library when `CONFIG_MPILIB` is enabled.

## Important APIs, Types, and Functions
- Produces `mpi.o` from `mpi-y`.
- Lists generic limb helpers, MPI public operations, coding helpers, division/multiplication internals, modular exponentiation, and utility allocation code.

## Control Flow and State
There is no runtime logic. The file controls object composition and link order for the MPI library.

## Dependencies and Integration Points
Integrated with Kbuild through `obj-$(CONFIG_MPILIB) = mpi.o`. Other crypto and public-key code depend on this library for big integer arithmetic.

## Risks and Test Signals
The risk is omission or ordering errors when adding/removing MPI source files. Build tests with `CONFIG_MPILIB=y/m`, module symbol resolution, and public-key crypto tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-add1.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-add1.c

## Purpose
Implements `mpihelp_add_n()`, the low-level addition of two equal-length limb arrays.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_add_n(mpi_ptr_t res_ptr, mpi_ptr_t s1_ptr, mpi_ptr_t s2_ptr, mpi_size_t size)`.
- Uses `mpi_limb_t`, `mpi_ptr_t`, and signed `mpi_size_t` from `mpi-internal.h`.

## Control Flow and State
The function rewrites pointers so a negative loop index runs from `-size` to `-1`. For each limb it adds prior carry to the second source, detects carry, adds the first source, combines carry-out, and stores the result. It returns final carry. It has no persistent state.

## Dependencies and Integration Points
Used by higher-level MPI add, multiply, division correction, and Karatsuba code. Depends on unsigned wraparound semantics for carry detection.

## Risks and Test Signals
Risks are size precondition violations and aliasing combinations not expected by callers. Tests should cover all-carry, no-carry, in-place result/source overlap where callers permit it, and comparison against arbitrary-precision reference addition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-add1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-lshift.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-lshift.c

## Purpose
Implements limb-array left shift by a nonzero bit count smaller than one limb.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_lshift(mpi_ptr_t wp, mpi_ptr_t up, mpi_size_t usize, unsigned int cnt)`.
- Returns bits shifted out of the most significant limb.

## Control Flow and State
Starting from the most significant limb, it combines high/low source limbs with `cnt` and `BITS_PER_MPI_LIMB - cnt`, stores the shifted result, and returns the outgoing high bits. The destination is adjusted by one so the loop can fill overlapping output safely when `wp >= up`.

## Dependencies and Integration Points
Used by division normalization, modular exponentiation, and MPI bit operations. Preconditions require `0 < cnt < BITS_PER_MPI_LIMB` and correct overlap direction.

## Risks and Test Signals
Calling with `cnt == 0`, `cnt >= limb bits`, or wrong overlap direction is undefined for this helper. Tests should cover all shift counts 1 through limbbits-1, one-limb and multi-limb inputs, returned carry bits, and in-place left shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-lshift.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul1.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul1.c

## Purpose
Implements multiplication of a limb array by one limb.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_mul_1(mpi_ptr_t res_ptr, mpi_ptr_t s1_ptr, mpi_size_t s1_size, mpi_limb_t s2_limb)`.
- Uses `umul_ppmm()` from `longlong.h` to obtain high and low product limbs.

## Control Flow and State
The negative-index loop multiplies each source limb by `s2_limb`, adds carry to the low product, calculates the new carry as high product plus carry-out, stores the low limb, and returns final carry.

## Dependencies and Integration Points
Critical base helper for schoolbook multiplication, squaring, and modular exponentiation. Depends on `longlong.h` providing correct `umul_ppmm()` for the active architecture.

## Risks and Test Signals
Risks include broken architecture multiply macros and carry propagation bugs. Tests should include multiplying by 0, 1, maximum limb, carry-heavy operands, and cross-checking `mpi_mul()` for random numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul2.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul2.c

## Purpose
Implements add-multiply by one limb: `res += s1 * s2_limb`.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_addmul_1(...)`.
- Uses `umul_ppmm()` and carry detection on both product+carry and result+product additions.

## Control Flow and State
For each source limb the helper multiplies, adds incoming carry into the low product, adds the destination limb, stores the sum, and returns final carry. No persistent state is kept.

## Dependencies and Integration Points
Used by schoolbook multiplication, Karatsuba recomposition, squaring, and odd-size handling. It depends on destination space being valid and overlap restrictions controlled by callers.

## Risks and Test Signals
Incorrect carry accumulation corrupts high limbs in all multiplication paths. Test with random long operands, all-ones operands, single-limb and multi-limb values, and compare against reference big integer multiplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul3.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul3.c

## Purpose
Implements subtract-multiply by one limb: `res -= s1 * s2_limb`.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_submul_1(...)`.
- Uses `umul_ppmm()` and borrow detection.

## Control Flow and State
Each iteration multiplies one source limb, adds incoming carry to the low product, subtracts that from the destination limb, stores the result, and accumulates borrow/carry into the returned limb.

## Dependencies and Integration Points
Used heavily by `mpihelp_divrem()` for quotient correction and multi-limb division. Correctness directly affects modular reduction and exponentiation.

## Risks and Test Signals
Borrow propagation is the central risk. Tests should include divisor correction cases in division, all-ones operands, subtracting zero, and random division identity checks `q*d+r == n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-mul3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-rshift.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-rshift.c

## Purpose
Implements limb-array right shift by a nonzero bit count smaller than one limb.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_rshift(mpi_ptr_t wp, mpi_ptr_t up, mpi_size_t usize, unsigned cnt)`.
- Returns bits shifted out of the least significant limb.

## Control Flow and State
The helper combines adjacent source limbs from low to high, writes right-shifted result limbs, and returns the outgoing low bits. It adjusts the destination pointer so in-place shifting is safe when `wp <= up`.

## Dependencies and Integration Points
Used by MPI right shift, division denormalization, and modular exponentiation final reduction. Preconditions require `0 < cnt < BITS_PER_MPI_LIMB`.

## Risks and Test Signals
Risks are invalid zero/full-limb shifts and wrong overlap direction. Tests should cover every bit count, one-limb/multi-limb values, returned low bits, and in-place shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-rshift.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-sub1.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-sub1.c

## Purpose
Implements low-level subtraction of two equal-length limb arrays.

## Important APIs, Types, and Functions
- Function: `mpi_limb_t mpihelp_sub_n(mpi_ptr_t res_ptr, mpi_ptr_t s1_ptr, mpi_ptr_t s2_ptr, mpi_size_t size)`.
- Returns final borrow.

## Control Flow and State
The negative-index loop adds prior borrow to the subtrahend, detects overflow, subtracts from the minuend, detects borrow from the subtraction, stores the result, and returns the combined final borrow.

## Dependencies and Integration Points
Used by high-level signed MPI subtraction, division correction, and Karatsuba difference calculations.

## Risks and Test Signals
Borrow handling and same-size precondition are critical. Tests should cover exact equality, one-limb borrow, full borrow propagation, and random reference comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/generic_mpih-sub1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/longlong.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/longlong.h

## Purpose
Provides architecture-specific and generic macros for double-limb arithmetic used by the MPI library: multiply high/low, divide double-limb by single-limb, add/subtract double words, and leading-zero support.

## Important APIs, Types, and Functions
- Defines or falls back for `umul_ppmm`, `__umulsidi3`, `udiv_qrnnd`, `sdiv_qrnnd`, `add_ssaaaa`, and `sub_ddmmss`.
- Uses compile-time inputs `UWtype`, `UHWtype`, `W_TYPE_SIZE`, and compiler mode typedefs supplied by `mpi-internal.h`.
- Provides architecture branches for many historical CPUs plus active MIPS, ARM, PPC, SPARC, Alpha, x86-style cases and generic C fallback.
- Defines timing hints `UMUL_TIME`, `UDIV_TIME`, and `UDIV_NEEDS_NORMALIZATION`.

## Control Flow and State
This is preprocessor-only code. It selects inline assembly or C formulas based on architecture and word size. The generic multiply splits words into high/low halves. The generic divide `__udiv_qrnnd_c` performs normalized two-half quotient estimation and correction.

## Dependencies and Integration Points
Included by MPI limb helpers and division/multiplication files. It depends on compiler support for inline assembly constraints and GCC integer modes on several paths.

## Risks and Test Signals
Architecture macro bugs can break all MPI arithmetic, and inline assembly constraints are compiler-sensitive. Some old branches may be untested on modern toolchains. Test signals include all-architecture compile coverage, randomized limb multiply/divide property tests, division normalization cases, and comparison of MPI operations across 32-bit and 64-bit limb configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/longlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-add.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-add.c

## Purpose
Implements signed MPI addition/subtraction and modular add/subtract wrappers.

## Important APIs, Types, and Functions
- Exports `mpi_add()`, `mpi_sub()`, `mpi_addm()`, and `mpi_subm()`.
- Uses low-level `mpihelp_add()`, `mpihelp_sub()`, `mpihelp_sub_n()`, `mpihelp_add_n()`, `mpihelp_cmp()`, and `MPN_NORMALIZE()`.

## Control Flow and State
`mpi_add()` orders operands by limb count, resizes the destination, handles zero smaller operand, then either adds magnitudes for equal signs or subtracts magnitudes for differing signs. It normalizes the result and sets sign according to the larger magnitude. `mpi_sub()` copies `v`, flips its sign, and calls `mpi_add()`. Modular wrappers compute the operation then reduce with `mpi_mod()`.

## Dependencies and Integration Points
Used by public-key and modular arithmetic code. It depends on destination resizing before alias-sensitive pointer reads.

## Risks and Test Signals
Risks include sign errors around equal magnitudes and allocation failure when copying for subtraction. Tests should include positive/negative combinations, zero results, aliasing `w == u` or `w == v`, modular add/subtract, and randomized comparisons to a reference big integer library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-bit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-bit.c

## Purpose
Provides bit-level MPI operations: normalization, bit length, bit test, bit set, and right shift.

## Important APIs, Types, and Functions
- Exports `mpi_normalize()`, `mpi_get_nbits()`, `mpi_test_bit()`, `mpi_set_bit()`, and `mpi_rshift()`.
- Uses `count_leading_zeros()`, `mpihelp_rshift()`, `RESIZE_IF_NEEDED()`, and `MPN_NORMALIZE()`.

## Control Flow and State
Normalization trims leading zero limbs in place. `mpi_get_nbits()` normalizes and computes significant bits from the top limb. `mpi_test_bit()` indexes the relevant limb and bit. `mpi_set_bit()` grows and zero-fills as needed before setting the bit. `mpi_rshift()` handles in-place and out-of-place shifts, splits whole-limb and intra-limb shifts, and normalizes the result.

## Dependencies and Integration Points
Used throughout MPI comparison, exponentiation, serialization, and public-key routines. The helpers depend on limb-size macros and allocation routines.

## Risks and Test Signals
Risks include preserving sign on right shift, zeroing newly exposed limbs, and avoiding `mpihelp_rshift()` with zero bit count. Tests should cover bit positions across limb boundaries, zero MPI, in-place/out-of-place shifts, large shifts that clear the number, and random reference checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-cmp.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-cmp.c

## Purpose
Implements MPI comparison against unsigned long and another MPI.

## Important APIs, Types, and Functions
- Exports `mpi_cmp_ui()` and `mpi_cmp()`.
- Uses `mpi_normalize()` and `mpihelp_cmp()`.

## Control Flow and State
Both functions normalize inputs before comparison. `mpi_cmp_ui()` treats negative MPIs as less than any unsigned value and multi-limb positive MPIs as greater than one-limb values. `mpi_cmp()` compares signs first, then limb counts with sign-aware polarity, then same-size limb values, negating the magnitude comparison for negative operands.

## Dependencies and Integration Points
Used by MPI arithmetic, public-key code, and reduction logic needing ordering.

## Risks and Test Signals
Comparison is variable-time and not suitable for secret-order decisions where timing matters. Functional tests should cover zero, positive/negative numbers, equal magnitudes with different signs where normalized zero should be signless by convention, and multi-limb boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-div.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-div.c

## Purpose
Implements high-level MPI truncated and floored division/remainder functions.

## Important APIs, Types, and Functions
- Public/internal functions: `mpi_fdiv_r()`, `mpi_tdiv_r()`, and `mpi_tdiv_qr()`.
- Uses `mpihelp_divmod_1()`, `mpihelp_mod_1()`, `mpihelp_divrem()`, `mpihelp_lshift()`, `mpihelp_rshift()`, `mpihelp_cmp()`, and allocation helpers.

## Control Flow and State
`mpi_fdiv_r()` computes a truncated remainder then adjusts it by the divisor when signs require floored semantics. `mpi_tdiv_qr()` resizes quotient/remainder, handles numerator smaller than denominator, optimizes single-limb divisors, copies overlapping operands to temporary marker buffers, normalizes multi-limb divisors/numerators by left shifting, calls `mpihelp_divrem()`, denormalizes the remainder, assigns signs, and frees temporary limb buffers.

## Dependencies and Integration Points
Used by `mpi_mod()`, modular multiplication, modular exponentiation, and callers that need quotient/remainder. Relies on low-level division preconditions that divisor high bit is normalized for multi-limb division.

## Risks and Test Signals
Division by zero is not explicitly guarded at this high level before helper paths in all cases; callers must provide valid divisors. Alias handling and sign correction are complex. Tests should include all alias combinations (`num == rem`, `den == rem`, `num == quot`), one-limb and multi-limb divisors, negative dividend/divisor floored remainder, exact division, numerator smaller than denominator, and randomized identity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-inline.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-inline.h

## Purpose
Defines inline helper functions for adding/subtracting a single limb and combining unequal-size limb arrays.

## Important APIs, Types, and Functions
- Inline `mpihelp_add_1()`, `mpihelp_add()`, `mpihelp_sub_1()`, and `mpihelp_sub()`.
- Uses exported equal-size helpers `mpihelp_add_n()` and `mpihelp_sub_n()`.

## Control Flow and State
Single-limb helpers process the first limb, propagate carry/borrow until it clears or the input is exhausted, copy any remaining unchanged limbs when destination differs from source, and return final carry/borrow. Multi-limb helpers process the smaller equal-size portion, then apply carry/borrow to the remaining longer operand.

## Dependencies and Integration Points
Included by `mpi-internal.h` for GCC builds. Used by public MPI addition/subtraction, multiplication recomposition, and division correction.

## Risks and Test Signals
The helpers assume size relationships supplied by callers. Tests should cover carry/borrow stopping early, full propagation through all limbs, destination/source identity, and unequal operand lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-internal.h -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-internal.h

## Purpose
Defines private MPI types, macros, prototypes, thresholds, and architecture arithmetic bindings shared by the MPI implementation.

## Important APIs, Types, and Functions
- Defines `mpi_ptr_t`, signed `mpi_size_t`, `KARATSUBA_THRESHOLD`, `RESIZE_IF_NEEDED()`, copy/zero/normalize macros, and `UDIV_QRNND_PREINV()`.
- Declares allocation utilities, low-level limb helpers, division helpers, multiplication/Karatsuba helpers, and shift helpers.
- Supplies `longlong.h` type aliases and includes `mpi-inline.h` for GCC.

## Control Flow and State
The header is mostly declarative. The main executable macro is `UDIV_QRNND_PREINV()`, which estimates quotient/remainder using a precomputed divisor inverse, corrects overestimation, and writes outputs.

## Dependencies and Integration Points
Every MPI C file includes this header. It integrates with `<linux/mpi.h>`, kernel allocation/logging APIs, and `longlong.h`.

## Risks and Test Signals
Macros can evaluate arguments multiple times or depend on signed `mpi_size_t` behavior. `assert()` only logs and does not abort. Tests should focus on full MPI arithmetic, threshold boundary sizes around `KARATSUBA_THRESHOLD`, and division with pre-inverted divisor paths when enabled by timing macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mod.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mod.c

## Purpose
Implements modular reduction wrapper.

## Important APIs, Types, and Functions
- Function: `int mpi_mod(MPI rem, MPI dividend, MPI divisor)`.
- Delegates directly to `mpi_fdiv_r()`.

## Control Flow and State
There is a single call to floored remainder. State changes happen inside `mpi_fdiv_r()` and are reflected in `rem`.

## Dependencies and Integration Points
Used by modular add/subtract and callers needing canonical nonnegative remainders for positive moduli.

## Risks and Test Signals
Correctness depends entirely on `mpi_fdiv_r()` and caller-provided divisor validity. Tests should verify positive modulus results are in `[0, m)`, negative dividend behavior, and aliasing through `mpi_fdiv_r()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mul.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mul.c

## Purpose
Implements high-level signed MPI multiplication and modular multiplication.

## Important APIs, Types, and Functions
- Exports `mpi_mul()` and `mpi_mulm()`.
- Uses `mpihelp_mul()`, `mpi_alloc_limb_space()`, `mpi_assign_limb_space()`, and `mpi_tdiv_r()`.

## Control Flow and State
`mpi_mul()` orders operands by limb count, handles destination aliasing by allocating temporary operand or result limb space, calls low-level multiplication if the smaller operand is nonzero, adjusts result size based on top carry, assigns temporary result space if used, sets sign as XOR of operand signs, and frees temporary operands. `mpi_mulm()` multiplies then reduces by `m`.

## Dependencies and Integration Points
Used by public-key arithmetic and modular exponentiation. It depends on `mpihelp_mul()` requiring `usize >= vsize` and non-overlapping product/input buffers.

## Risks and Test Signals
Alias handling and error cleanup are primary risks. A zero product should conventionally have sign zero; tests should check signed zero normalization expectations. Test with `w == u`, `w == v`, `u == v`, zero operands, negative operands, modular multiplication, and random reference multiplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-mul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-pow.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-pow.c

## Purpose
Implements modular exponentiation `res = base ^ exp mod mod`.

## Important APIs, Types, and Functions
- Exports `mpi_powm()`.
- Uses `mpihelp_divrem()`, `mpihelp_lshift()`, `mpihelp_rshift()`, `mpih_sqr_n_basecase()`, `mpih_sqr_n()`, `mpihelp_mul()`, `mpihelp_mul_karatsuba_case()`, and `karatsuba_ctx`.

## Control Flow and State
The function rejects zero modulus, handles zero exponent as `1 mod mod`, normalizes the modulus for division, reduces an oversized base, handles result/base/exp/mod aliasing with temporary limb storage, initializes result to base, then performs left-to-right square-and-multiply over exponent bits. Each square or multiply is reduced via `mpihelp_divrem()` when wider than the modulus. It alternates temporary buffers to avoid copies, calls `cond_resched()` in the loop, denormalizes the final result, and adjusts negative base odd-exponent results with `mod - result`.

## Dependencies and Integration Points
Used by public-key algorithms requiring modular exponentiation. It relies on MPI multiplication, division, Karatsuba scratch management, and scheduler cooperation.

## Risks and Test Signals
The algorithm is variable-time in exponent bits and operand sizes, so it is unsuitable for secret exponents without blinding or constant-time wrappers. Alias handling and temporary cleanup are complex. Tests should cover exponent zero, modulus one, base greater than modulus, negative base with odd/even exponent, alias combinations, threshold sizes around Karatsuba, allocation-failure injection, and reference modular exponent comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-pow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-sub-ui.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-sub-ui.c

## Purpose
Implements subtraction of an unsigned long from an MPI.

## Important APIs, Types, and Functions
- Exports `mpi_sub_ui(MPI w, MPI u, unsigned long vval)`.
- Uses `mpi_resize()`, `mpihelp_add_1()`, `mpihelp_sub_1()`, and `mpi_normalize()`.

## Control Flow and State
If `u` is zero, the result is `-vval` or zero. For negative `u`, subtracting an unsigned value increases the magnitude and keeps a negative sign. For nonnegative `u`, it compares one-limb values to decide whether the result becomes negative or can subtract in place from `u`'s magnitude. It normalizes before returning.

## Dependencies and Integration Points
Used by code that needs small integer adjustments without constructing a full MPI for the small operand.

## Risks and Test Signals
The path assumes `unsigned long` fits one `mpi_limb_t` for comparison semantics; this is true for normal kernel MPI limb sizing. Tests should include `u=0`, `vval=0`, `u < vval`, `u == vval`, `u > vval`, negative `u`, and aliasing `w == u`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-sub-ui.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpicoder.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpicoder.c

## Purpose
Encodes and decodes MPIs from raw big-endian byte streams, length-prefixed external buffers, and scatterlists.

## Important APIs, Types, and Functions
- Exports `mpi_read_raw_data()`, `mpi_read_from_buffer()`, `mpi_read_buffer()`, `mpi_get_buffer()`, `mpi_write_to_sgl()`, and `mpi_read_raw_from_sgl()`.
- Uses `MAX_EXTERN_MPI_BITS` set to 16384 bits.
- Uses scatterlist mapping iteration for SG input/output and endian conversion for limb serialization.

## Control Flow and State
Raw readers skip leading zero bytes, compute significant bits, reject oversized external MPIs, allocate an MPI, and fill limbs from most-significant bytes into little-endian limb order. `mpi_read_from_buffer()` first parses a two-byte bit count. `mpi_read_buffer()` serializes an MPI to a caller buffer, reporting required length on overflow and optionally returning sign. `mpi_get_buffer()` allocates a buffer and delegates serialization. `mpi_write_to_sgl()` writes optional leading zero padding followed by big-endian limbs into SG entries. `mpi_read_raw_from_sgl()` scans leading zeroes across SG entries, computes size, allocates, and fills limbs.

## Dependencies and Integration Points
Used by public-key parsers, signature verification, and key import/export code. Depends on scatterlist APIs, endian helpers, count-zero helpers, and MPI allocation utilities.

## Risks and Test Signals
Risks include SG iterator edge cases, leading-zero accounting, overflow reporting, and size limit enforcement. Tests should cover empty/zero values, leading zeros, maximum allowed size and one byte over, short length-prefixed buffers, buffer overflow reporting, SG boundaries at every byte offset, and round-trip encode/decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpicoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-cmp.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-cmp.c

## Purpose
Implements equal-size limb-array comparison for natural numbers.

## Important APIs, Types, and Functions
- Function: `int mpihelp_cmp(mpi_ptr_t op1_ptr, mpi_ptr_t op2_ptr, mpi_size_t size)`.

## Control Flow and State
The helper scans from most significant limb down to zero. It returns immediately on the first differing limb with `1` or `-1`, otherwise returns `0`.

## Dependencies and Integration Points
Used by MPI comparison, signed add/subtract magnitude decisions, division normalization/correction, and Karatsuba difference sign detection.

## Risks and Test Signals
The function is variable-time and should not be used for secret comparisons. Tests should include equal arrays, top-limb differences, low-limb differences, and all supported limb sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-div.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-div.c

## Purpose
Implements low-level natural-number division helpers: single-limb modulo, multi-limb divide/remainder, and single-limb quotient/remainder.

## Important APIs, Types, and Functions
- `mpihelp_mod_1()` computes a remainder by one limb.
- `mpihelp_divrem()` divides multi-limb natural numbers, writes quotient limbs, leaves remainder in the numerator buffer, and returns a possible most-significant quotient limb.
- `mpihelp_divmod_1()` divides by one limb and writes full quotient plus remainder.
- Uses `udiv_qrnnd()`, `UDIV_QRNND_PREINV()`, `mpihelp_submul_1()`, `mpihelp_add_n()`, and `mpihelp_cmp()`.

## Control Flow and State
Single-limb functions choose pre-inverted division when configured as faster; otherwise they use direct `udiv_qrnnd()`, with normalization when required. `mpihelp_divrem()` switches on divisor size. For size 1 and 2 it uses specialized quotient estimation/correction. For larger divisors it normalizes assumptions from callers, estimates quotient limbs from the top divisor limbs, subtracts `q * divisor`, corrects if overestimated, stores quotient limbs, and leaves the remainder in place.

## Dependencies and Integration Points
Called by high-level division and modular exponentiation. It assumes `nsize >= dsize`, normalized multi-limb divisors, and carefully constrained overlap between quotient and numerator.

## Risks and Test Signals
Division is fragile: quotient overestimation correction, divisor normalization, and overlap constraints are central. The size-0 switch intentionally traps but should be unreachable. Tests should include one-limb, two-limb, and many-limb divisors, normalized and denormalized high-level inputs through `mpi_tdiv_qr()`, quotient-extra-limb paths if used, random identity checks, and architecture `udiv_qrnnd()` validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-mul.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-mul.c

## Purpose
Implements low-level natural-number multiplication and squaring, including schoolbook base cases and Karatsuba recursion.

## Important APIs, Types, and Functions
- `mpihelp_mul()` is the public low-level multiply entry.
- `mul_n_basecase()` and `mul_n()` handle equal-size multiplication.
- `mpih_sqr_n_basecase()` and `mpih_sqr_n()` handle squaring.
- `mpihelp_mul_karatsuba_case()` handles unequal-size operands with recursive chunks.
- `mpihelp_release_karatsuba_ctx()` frees scratch contexts.

## Control Flow and State
For small operands, multiplication uses schoolbook loops with special cases for multiplier limb 0 or 1. Larger equal-size operands use Karatsuba splitting into high/low halves, calculating high, middle difference product, and low products, then recombining. Odd sizes are handled by recursing on size-1 and adding the top limb separately. Unequal Karatsuba multiplication processes full-size chunks and a residual tail, allocating scratch buffers in a `karatsuba_ctx` chain. The caller owns product storage and result top-limb reporting.

## Dependencies and Integration Points
Used by `mpi_mul()` and `mpi_powm()`. Relies on generic limb add/sub/mul helpers, scratch allocation, and non-overlap between product and operands.

## Risks and Test Signals
Risks include scratch leaks on error, Karatsuba recomposition carry errors, odd-size edge cases, and thresholds. Tests should cover operand sizes below, at, and above `KARATSUBA_THRESHOLD`, square-vs-multiply equivalence, unequal sizes with residual chunks, all-zero/all-one limbs, and randomized reference comparisons under allocation-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpih-mul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpiutil.c -->
# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpiutil.c

## Purpose
Provides allocation, resizing, freeing, and copying utilities for MPI objects and their limb arrays.

## Important APIs, Types, and Functions
- Exports `mpi_alloc()` and `mpi_free()`.
- Defines `mpi_alloc_limb_space()`, `mpi_free_limb_space()`, `mpi_assign_limb_space()`, `mpi_resize()`, and `mpi_copy()`.

## Control Flow and State
`mpi_alloc()` allocates the MPI header and optional limb storage, initializing metadata. `mpi_resize()` grows only; it allocates zeroed new limb space, copies old allocated limbs, and frees old storage sensitively. `mpi_assign_limb_space()` replaces owned limb storage. `mpi_free()` clears limb storage, warns on invalid flags, and frees the header. `mpi_copy()` duplicates metadata and limbs but clears immutable/constant flags.

## Dependencies and Integration Points
All MPI operations depend on these memory helpers. They use kernel allocation APIs and `kfree_sensitive()` for limb data.

## Risks and Test Signals
Integer overflow in `nlimbs * sizeof(mpi_limb_t)` would be a concern for unchecked external sizes, but external decoders cap input size. Copying `alloced` limbs during resize instead of `nlimbs` relies on old allocation being initialized or non-sensitive cleared on free. Tests should include allocation failure, zero-limb allocation, resize grow/no-op, copy independence, and sensitive free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/mpi/mpiutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/nh.c -->
# sources/distributed-fs/ceph-client/lib/crypto/nh.c

## Purpose
Implements the NH almost-universal hash function variant used by Adiantum. It is a keyed universal hash, not a standalone cryptographic hash.

## Important APIs, Types, and Functions
- Exports `nh(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`.
- Optional static `nh_arch()` override comes from `$(SRCARCH)/nh.h` under `CONFIG_CRYPTO_LIB_NH_ARCH`.
- Assumes `NH_PAIR_STRIDE == 2` and `NH_NUM_PASSES == 4`.

## Control Flow and State
`nh()` first lets an architecture implementation consume the request. The generic path initializes four 64-bit sums, processes each 16-byte `NH_MESSAGE_UNIT`, loads four little-endian message words, adds pass-specific key words, multiplies paired sums, advances key and message pointers, and writes four little-endian 64-bit outputs. No persistent state exists.

## Dependencies and Integration Points
Used by Adiantum-related crypto code. Depends on `<crypto/nh.h>`, unaligned little-endian loads, and optional architecture dispatch.

## Risks and Test Signals
The generic loop assumes `message_len` is a multiple of `NH_MESSAGE_UNIT`; callers must pad or constrain input. The key schedule length must match message length. Tests should include Adiantum/NH known vectors, architecture-vs-generic equivalence, zero and multi-unit messages, and rejection or caller-side handling of non-multiple lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/nh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna32.c -->
# sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna32.c

## Purpose
Implements the 32-bit Donna Poly1305 core: key clamping/precomputation, block accumulation, and tag emission.

## Important APIs, Types, and Functions
- Exports `poly1305_core_setkey()`, `poly1305_core_blocks()`, and `poly1305_core_emit()`.
- Uses 5 limbs of 26 bits for the accumulator/key and precomputes `5*r[1..4]`.

## Control Flow and State
Key setup extracts and clamps `r` from the first 16 key bytes. Block processing loads each 16-byte block into 26-bit limbs, applies `hibit`, multiplies accumulator by `r` modulo `2^130-5`, partially carries after every block, and stores accumulator limbs. Emit fully carries, conditionally subtracts the modulus through mask selection, packs the low 128 bits, optionally adds a 128-bit nonce, and writes the tag little-endian.

## Dependencies and Integration Points
Used by generic Poly1305 internals on 32-bit-oriented builds. Depends on unaligned little-endian helpers and `struct poly1305_state`/`struct poly1305_core_key`.

## Risks and Test Signals
Constant-time final conditional subtraction and carry bounds are important. Tests should cover RFC 8439 vectors, empty input, multi-block input, all tail lengths through `poly1305.c`, nonce null/non-null emit behavior if used internally, and comparison with 64-bit/arch implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna64.c -->
# sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna64.c

## Purpose
Implements the 64-bit Donna Poly1305 core optimized around 44/44/42-bit limbs and `u128` intermediates.

## Important APIs, Types, and Functions
- Exports `poly1305_core_setkey()`, `poly1305_core_blocks()`, and `poly1305_core_emit()`.
- Uses three accumulator/key limbs and precomputes `20*r[1..2]`.

## Control Flow and State
Key setup clamps the 128-bit `r` into three limbs. Block processing adds message limbs plus `hibit`, multiplies with `u128` intermediate products, partially reduces carries modulo `2^130-5`, and stores state. Emit fully carries, computes `h + -p`, mask-selects canonical `h`, optionally adds the nonce as two 64-bit chunks, reduces to 128 bits, and writes little-endian tag words.

## Dependencies and Integration Points
Used by Poly1305 builds where 128-bit integer support is available and preferred. Depends on `u128`, unaligned helpers, and internal Poly1305 types.

## Risks and Test Signals
Risks include `u128` availability, carry range assumptions, and constant-time canonical selection. Tests should compare to Donna32 and MIPS arch implementations, include RFC vectors, large multi-block messages, boundary accumulator values, and split-update wrapper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/poly1305.c -->
# sources/distributed-fs/ceph-client/lib/crypto/poly1305.c

## Purpose
Provides the public streaming Poly1305 authenticator wrapper over generic or architecture-specific core primitives.

## Important APIs, Types, and Functions
- Exports `poly1305_init()`, `poly1305_update()`, and `poly1305_final()`.
- Dispatches `poly1305_block_init`, `poly1305_blocks`, and `poly1305_emit` to arch implementations or generic core symbols.
- Uses `struct poly1305_desc_ctx` with `state`, `s` nonce words, partial buffer, and `buflen`.

## Control Flow and State
Initialization stores the second half of the key as nonce `s`, clears partial length, and initializes the block state with the first half. Update fills an existing partial block, processes complete blocks with `hibit=1`, and buffers remaining bytes. Final pads a partial block with a `1` byte and zeroes, processes it with `hibit=0`, emits the MAC using the nonce words, then clears the descriptor.

## Dependencies and Integration Points
Used by crypto APIs and constructions such as ChaCha20-Poly1305. Depends on `<crypto/internal/poly1305.h>` and optional `$(SRCARCH)/poly1305.h` arch hooks.

## Risks and Test Signals
Final partial-block padding and `hibit` selection are key correctness points. The descriptor is cleared with struct assignment, not `memzero_explicit()`, so compiler behavior may matter if key material is considered sensitive after finalization. Tests should include RFC 8439 vectors, every tail length, split updates, zero-length messages, in-place caller patterns, and generic-vs-arch parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/poly1305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-core.S

## Purpose
Implements fast AES single-block encryption and decryption cores for PowerPC SPE SIMD instructions.

## Important APIs, Types, and Functions
- Defines `_GLOBAL(ppc_encrypt_block)` and `_GLOBAL(ppc_decrypt_block)`.
- Uses register definitions from `aes-spe-regs.h`.
- Macros `EAD`, `DAD`, `LWH`, `LWL`, `LBZ`, `LAH`, `LAL`, `LAE`, and `LAD` build T-table/S-box addresses and loads.

## Control Flow and State
Both functions are leaf block cores with no stack setup; callers must prepare registers with pre-xored input, key pointer, table pointer, and CTR round count. Encryption iterates combined table rounds using SPE loads/xors and final S-box byte assembly, then leaves output in data/word registers for caller final XOR. Decryption mirrors this with inverse table addressing and final inverse S-box loads. All working registers are documented as clobbered.

## Dependencies and Integration Points
Integrated by higher-level PowerPC AES SPE assembly/C wrappers that manage mode loops, key schedule, stack, and final stores. Depends on SPE instruction availability, PPC assembler macros, and table layout expected by `aes-spe-regs.h`.

## Risks and Test Signals
Risks include table-index side channels, caller/callee register contract mismatch, CTR round-count setup, and final round byte placement. Tests should include AES-128/192/256 encrypt/decrypt known-answer vectors through the wrapper, all supported modes using this core, build tests for SPE targets, and disassembly/register-clobber review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-core.S -->
