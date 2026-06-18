# subset-b-006082 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/curve25519-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/curve25519-core.S

## Purpose
This ARMv7 NEON assembly file implements `curve25519_neon`, a kernel-space X25519 scalar multiplication routine. It derives from SUPERCOP/Bernstein-Schwabe code but is rewritten for Linux calling conventions and kernel SIMD use. It computes `out = scalar * point` over Curve25519 using radix-limb field arithmetic, a Montgomery ladder, and final inversion.

## Important APIs, Types, And Functions
The sole exported entry is `ENTRY(curve25519_neon)`, matching the header prototype `curve25519_neon(u8 out[32], const u8 secret[32], const u8 basepoint[32])`. Internal state is stack-resident field elements, stored as 10 alternating 25/26-bit limbs. Important labels are `.Lmainloop` for the 255-bit ladder, `.Linvertloop` and `.Lsquaringloop` for exponentiation-based inversion, and final carry/serialization code that writes the 32-byte little-endian result.

## Control Flow
The function saves callee registers, allocates an aligned 704-byte frame, clamps the scalar, decodes the input point into limbs, initializes projective ladder points, then iterates bits from 254 down to 0. Each ladder step conditionally swaps point coordinates with bit-mask NEON operations, performs differential addition and doubling with vectorized multiply/add/reduce sequences, and stores limbs back to stack slots. After the ladder, it computes `z^-1` through a fixed sequence of squarings and multiplications, multiplies by `x`, normalizes carries, and packs limbs to bytes.

## State And Persistence
All state is transient: stack slots hold scalar bytes, constants, intermediate field elements, and ladder state. The routine updates only the caller-provided output buffer and has no persistent storage. Secret-dependent control flow is avoided in the ladder by mask-based swaps; loop counts are fixed by scalar length and inversion schedule.

## Dependencies And Integration Points
It depends on `<linux/linkage.h>`, ARMv7-A, and NEON. `curve25519.h` calls it only inside `scoped_ksimd()` when the NEON static key is enabled and SIMD is usable. The generic Curve25519 implementation is the fallback.

## Risks And Edge Cases
Correctness depends on exact limb bounds, carry propagation, scalar clamping, and final canonicalization modulo `2^255-19`. The large hand-written frame makes offset drift risky. Kernel callers must not enter this function without SIMD context protection. Side-channel risk centers on unintended secret-dependent memory/control behavior and microarchitectural leakage in vector arithmetic.

## Test Signals
Use X25519 known-answer tests, Wycheproof-style public key edge cases including all-zero and high-bit encodings, differential tests against `curve25519_generic`, KASAN/KMSAN stack checks, ARM32 NEON boot tests, and crypto selftests under preemption/softirq contexts that exercise `crypto_simd_usable()` gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/curve25519-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/curve25519.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/curve25519.h

## Purpose
This header wires the ARM32 NEON X25519 implementation into the generic Curve25519 library. It selects `curve25519_neon` when hardware and context allow, otherwise falling back to generic C.

## Important APIs, Types, And Functions
It declares `asmlinkage void curve25519_neon(...)`, defines a `__ro_after_init` static key `have_neon`, and provides `curve25519_arch`, `curve25519_base_arch`, and `curve25519_mod_init_arch`. The arch wrappers preserve the generic API shape used by common Curve25519 code.

## Control Flow
At module init, `curve25519_mod_init_arch` enables `have_neon` when `elf_hwcap & HWCAP_NEON`. Runtime calls to `curve25519_arch` check that static key plus `crypto_simd_usable()`, enter `scoped_ksimd()`, and call assembly; otherwise they call `curve25519_generic`. `curve25519_base_arch` supplies the standard base point.

## State And Persistence
Only the `have_neon` jump label persists after init. Per-call scalar, point, and output buffers are supplied by the caller. No key material is retained by the header.

## Dependencies And Integration Points
It includes ARM hwcap/SIMD headers, `crypto/internal/simd.h`, Linux types, and jump labels. It integrates with generic Curve25519 symbols such as `curve25519_generic`, `curve25519_base_point`, and `CURVE25519_KEY_SIZE`.

## Risks And Edge Cases
The main risk is entering NEON code from an unsafe context. The header uses both static feature detection and runtime SIMD usability to prevent that. Build configurations must provide the generic fallback and the assembly symbol consistently.

## Test Signals
Crypto selftests should exercise both NEON-enabled and fallback paths. Boot logs/builds for ARM without NEON, with NEON but unusable SIMD contexts, and module init static-branch state are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/curve25519.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/gf128hash.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/gf128hash.h

## Purpose
This ARM32 header provides GHASH acceleration glue using NEON `vmull.p8` polynomial multiplication. It supplies an architecture-specific `ghash_blocks_arch` hook for the common GF(2^128) hashing layer.

## Important APIs, Types, And Functions
It declares `pmull_ghash_update_p8(size_t blocks, struct polyval_elem *dg, const u8 *src, const struct polyval_elem *h)`, defines `have_neon`, implements `ghash_blocks_arch`, and defines `gf128hash_mod_init_arch`.

## Control Flow
Initialization enables `have_neon` when `HWCAP_NEON` is present. `ghash_blocks_arch` checks the static key and `may_use_simd()`. On the fast path it processes input in chunks capped at 4096 bytes, entering `scoped_ksimd()` for each chunk so long GHASH operations allow rescheduling. Otherwise it calls `ghash_blocks_generic`.

## State And Persistence
Persistent state is only the feature static key. The accumulator `acc`, hash key `key->h`, and input stream are caller-owned and updated in memory by the chosen implementation.

## Dependencies And Integration Points
The header depends on ARM hwcap, NEON, SIMD helpers, `struct ghash_key`, `struct polyval_elem`, `GHASH_BLOCK_SIZE`, and generic GHASH fallback helpers. It is included by the common GF128 hash implementation when building ARM32 crypto.

## Risks And Edge Cases
The fast path assumes `nblocks > 0`; callers should avoid empty work or tolerate a no-op loop contract. SIMD use must remain guarded. The 4 KiB chunking is important for scheduler latency and should be preserved if the function is refactored.

## Test Signals
Signals include GHASH known-answer tests, AES-GCM crypto selftests, fallback-vs-NEON comparisons, preemptible kernel runs with large messages, and ARM32 builds with and without `CONFIG_KERNEL_MODE_NEON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/gf128hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/ghash-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/ghash-neon-core.S

## Purpose
This ARM32 NEON assembly file implements GHASH block update using `vmull.p8` byte polynomial multiplication. It accelerates AES-GCM style GF(2^128) accumulation without requiring ARMv8 PMULL.

## Important APIs, Types, And Functions
The exported routine is `pmull_ghash_update_p8(size_t blocks, struct polyval_elem *dg, const u8 *src, const struct polyval_elem *h)`. Core macros are `__pmull_p8` for 64x64 polynomial multiply built from 8x8 operations, `__pmull_reduce_p8` for reduction by the GHASH polynomial, `vrev64_if_be` for endian handling, and `ghash_update` for the per-block loop.

## Control Flow
The function loads the hash subkey, precomputes shifted variants for Karatsuba-style multiplication, initializes masks, loads the accumulator, then loops over blocks. Each block reverses input byte order, xors it into the accumulator, computes low/high/cross polynomial products, reduces the 256-bit product, and continues until `blocks` reaches zero. It stores the updated accumulator and returns.

## State And Persistence
All vector temporaries live in NEON registers. Persistent state is the caller's accumulator buffer, updated in place. No global state is touched.

## Dependencies And Integration Points
It uses `<linux/linkage.h>`, `<asm/assembler.h>`, `.fpu neon`, and is called by `arm/gf128hash.h` inside a SIMD-safe section. It integrates with common GHASH key/accumulator layout represented as `struct polyval_elem`.

## Risks And Edge Cases
Endian conversions must match common GHASH formatting. The routine assumes valid block count and 16-byte readable inputs. Register aliasing in macros is subtle, and incorrect overlap could corrupt the product. As assembly, it needs architecture-specific build and unwind scrutiny.

## Test Signals
AES-GCM vectors, random differential tests against `ghash_blocks_generic`, big-endian build coverage, unaligned input tests if callers permit them, and PMULL-free NEON ARM32 hardware tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/ghash-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/nh-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/nh-neon-core.S

## Purpose
This file implements the NH epsilon-almost-universal hash for ARM32 NEON. NH is used by higher-level keyed hashing constructions that process messages in 64-byte strides.

## Important APIs, Types, And Functions
The exported symbol is `nh_neon(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. The `_nh_stride` macro loads four vectors of key material and message words, performs pairwise additions, multiplies widened 32-bit pairs, and accumulates four pass sums.

## Control Flow
`nh_neon` initializes four 128-bit sum accumulators to zero, loops over 64-byte message strides in `.Lloop4`, and handles a final smaller multiple of the required chunk shape before `.Ldone`. The loop advances key and message pointers together, accumulating low/high halves into four 64-bit sums, then stores four little-endian 64-bit results.

## State And Persistence
State is limited to vector accumulators and caller-provided output. No persistent key schedule or global state is stored.

## Dependencies And Integration Points
It depends on `<linux/linkage.h>` and NEON. `arm/nh.h` calls it only for messages at least 64 bytes and when `may_use_simd()` succeeds; otherwise the generic NH path remains responsible.

## Risks And Edge Cases
Message length assumptions matter: the header filters very short inputs, while the common NH caller must provide lengths aligned to the algorithm contract. Endianness of `__le64` outputs and message word loading must match the generic implementation. Kernel SIMD context protection is required.

## Test Signals
NH vectors, Adiantum or other users of NH, randomized generic-vs-NEON comparisons across boundary lengths near 64 bytes, and ARM32 NEON build/runtime tests are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/nh-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/nh.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/nh.h

## Purpose
This ARM32 header connects the NEON NH assembly implementation to the common NH library. It opportunistically accelerates only workloads large enough to benefit.

## Important APIs, Types, And Functions
It declares `nh_neon`, defines `have_neon`, implements `nh_arch`, and defines `nh_mod_init_arch`. `nh_arch` returns a boolean indicating whether the architecture path handled the request.

## Control Flow
Initialization enables `have_neon` when `HWCAP_NEON` is present. `nh_arch` checks `have_neon`, `message_len >= 64`, and `may_use_simd()`. If true, it enters `scoped_ksimd()`, calls `nh_neon`, stores the digest words, and returns true; otherwise it returns false so generic code handles the hash.

## State And Persistence
Only the static key persists. Key, message, and hash buffers are caller-owned and not retained.

## Dependencies And Integration Points
It includes ARM NEON/SIMD headers and relies on common NH constants such as `NH_NUM_PASSES`. It integrates with the generic NH implementation through the `nh_arch` hook.

## Risks And Edge Cases
The size threshold avoids overhead for small inputs; changing it can affect performance but not correctness if the assembly supports the sizes. SIMD context gating and static-branch initialization are the main safety risks.

## Test Signals
Compare generic and NEON outputs for boundary lengths, especially 0, short, 64, and multi-stride messages. Build tests should cover ARM32 without NEON and with `CONFIG_KERNEL_MODE_NEON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/nh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/poly1305-armv4.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/poly1305-armv4.pl

## Purpose
This Perl generator emits ARMv4-compatible and ARMv7 NEON Poly1305 assembly for the kernel. It is Cryptogams/OpenSSL-derived code adapted to expose Linux symbols for Poly1305 block initialization, block processing, and tag emission.

## Important APIs, Types, And Functions
Generated exported symbols are `poly1305_block_init` (via `poly1305_init` macro), `poly1305_blocks_arm`, `poly1305_blocks_neon`, and `poly1305_emit`. Internal generator/body regions include scalar `poly1305_blocks`, scalar `poly1305_emit`, `poly1305_init_neon`, and the long NEON loop with `.Lbase2_26_neon`, `.Loop_neon`, `.Long_tail`, and `.Lshort_tail`.

## Control Flow
The generator prints assembly after substituting register and syntax helpers. `poly1305_init` clears the accumulator, clamps the key, records scalar key limbs, and for non-kernel OpenSSL builds may choose function pointers by ARM capability. The scalar block routine processes 16-byte blocks in base 2^32-like limbs with multiplication by the clamped key and modular reduction. The NEON path requires at least 64 bytes, converts state to base 2^26, precomputes powers of `r`, processes up to four blocks per vectorized iteration, handles long/short tails, lazily reduces, and stores the hash. `poly1305_emit` finalizes and adds the nonce.

## State And Persistence
Persistent algorithm state is the caller's `struct poly1305_block_state` and final `struct poly1305_state`. The NEON path stores an `is_base2_26` marker in the state so scalar and vector code can convert formats safely. The generator itself has no runtime state after build.

## Dependencies And Integration Points
It depends on Perl at build time and kernel ARM assembler support at output time. `arm/poly1305.h` declares the generated symbols and selects scalar vs NEON through static keys and `may_use_simd()`.

## Risks And Edge Cases
Risks include generator drift, state radix conversion bugs, tail handling for non-64-byte multiples, endian handling, and clamping/final reduction mistakes. The scalar routine must remain ARMv4-compatible while the NEON routine must preserve VFP/NEON ABI registers. Mixing scalar and NEON updates relies on the state marker.

## Test Signals
Poly1305 RFC vectors, randomized split-update tests that alternate scalar and NEON paths, tail lengths from 0 to 127 bytes, big-endian build checks, ABI register preservation tests, and differential comparison with the generic implementation are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/poly1305-armv4.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/poly1305.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/poly1305.h

## Purpose
This header provides ARM32 Poly1305 dispatch glue. It exposes generated scalar and NEON assembly to the common Poly1305 library while keeping unsafe SIMD use out of non-SIMD contexts.

## Important APIs, Types, And Functions
It declares `poly1305_block_init`, `poly1305_blocks_arm`, `poly1305_blocks_neon`, and `poly1305_emit`. It defines the `have_neon` static key and the `poly1305_blocks` arch hook, plus `poly1305_mod_init_arch` when kernel-mode NEON is enabled.

## Control Flow
`poly1305_blocks` checks `CONFIG_KERNEL_MODE_NEON`, `have_neon`, and `may_use_simd()`. If all pass, it processes data in `SZ_4K` chunks inside `scoped_ksimd()` using `poly1305_blocks_neon`; otherwise it calls `poly1305_blocks_arm` once. Init enables `have_neon` on `HWCAP_NEON`.

## State And Persistence
The only persistent header state is `have_neon`. Poly1305 accumulator/key state lives in caller-provided structures and is mutated by assembly routines.

## Dependencies And Integration Points
It depends on ARM hwcap/SIMD, jump labels, `linux/kernel.h`, and common Poly1305 constants/types. It integrates with the generated `poly1305-armv4.pl` output and the generic Poly1305 API.

## Risks And Edge Cases
The NEON path is chunked for scheduler latency and must preserve state across chunk boundaries. The scalar and vector state formats must stay compatible with the generated assembly. Configuration without kernel-mode NEON must still expose the scalar path.

## Test Signals
Signals include Poly1305 crypto selftests, split updates across 4 KiB boundaries, fallback-only ARM builds, NEON-enabled ARM runtime tests, and context tests where `may_use_simd()` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv4-large.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv4-large.S

## Purpose
This file implements a scalar ARM SHA-1 block compression routine for ARMv4-compatible systems. It is the non-NEON fallback for ARM32 SHA-1 acceleration.

## Important APIs, Types, And Functions
The exported symbol is `sha1_block_data_order(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. Important labels include `.Lloop`, `.L_00_15`, `.L_20_39_or_60_79`, `.L_40_59`, `.L_done`, and constants `.LK_00_19` through `.LK_60_79`.

## Control Flow
The routine loads five SHA-1 chaining words, loops over 64-byte blocks, expands the message schedule in registers/stack, runs the 80 rounds grouped by SHA-1 boolean function and constant, then adds working variables back into state. It handles endian conversion while loading message words and exits when all blocks are consumed.

## State And Persistence
Only the caller's `sha1_block_state` is updated persistently. Stack/register state is transient. No static writable data is used.

## Dependencies And Integration Points
It uses Linux ARM linkage macros and is declared by `arm/sha1.h`. The header selects it when NEON/crypto extensions are unavailable or SIMD cannot be used.

## Risks And Edge Cases
The routine is performance-sensitive and has high register pressure. Endian loading and exact 80-round sequencing are the main correctness risks. It assumes full 64-byte blocks and leaves padding/finalization to higher-level SHA-1 code.

## Test Signals
SHA-1 known-answer tests, generic-vs-assembly differential tests over many block counts, ARMv4/ARMv5 build compatibility, and tests with `CONFIG_KERNEL_MODE_NEON` disabled exercise this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv4-large.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv7-neon.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv7-neon.S

## Purpose
This ARMv7 NEON assembly file accelerates SHA-1 block compression using vectorized message schedule precalculation while scalar ARM registers carry the five working variables.

## Important APIs, Types, And Functions
The exported routine is `sha1_transform_neon(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. Macro families `W_PRECALC_*`, `_R`, and `R` generate schedule and round code. Constants `.LK_VEC` hold the four SHA-1 round constants as vectors.

## Control Flow
The function rejects zero blocks, saves registers, aligns a stack work area, loads constants and chaining variables, and precalculates schedule words for the first block. `.Loop` interleaves rounds 0-79 with NEON schedule preparation for the next block, adding final working variables into the state at the end of each block. `.Lend` handles the final block without preloading a successor, and `.Ldo_nothing` returns for empty input.

## State And Persistence
The SHA-1 state buffer is updated in place. Temporary schedule data is on the stack and in NEON registers. No persistent globals are written.

## Dependencies And Integration Points
It depends on ARMv7 NEON and Linux linkage. `arm/sha1.h` invokes it from inside `scoped_ksimd()` when NEON is available and SHA-1 crypto extensions are not preferred.

## Risks And Edge Cases
The interleaving between current rounds and next-block schedule is subtle; off-by-one mistakes affect only multi-block streams. Stack alignment and VFP/NEON register preservation must match kernel ABI. It assumes full block input and correct caller-side finalization.

## Test Signals
SHA-1 selftests over one-block and multi-block messages, randomized comparison with scalar `sha1_block_data_order`, NEON register preservation tests, and preemption/SIMD context stress are appropriate signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-armv7-neon.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-ce-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-ce-core.S

## Purpose
This ARM32 assembly file implements SHA-1 compression using ARMv8 SHA-1 crypto extension instructions exposed to ARM state.

## Important APIs, Types, And Functions
It exports `sha1_ce_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. It uses vector registers for the state, message schedule, and round constants stored at `.Lsha1_rcon`.

## Control Flow
The routine loads the current SHA-1 state and constants, loops over input blocks, uses SHA-1 extension instructions to perform rounds and schedule updates, accumulates results into the state, advances the input pointer, and stores the final chaining state.

## State And Persistence
Only the caller-provided state is updated. All message schedule and working state are transient registers.

## Dependencies And Integration Points
It requires ARM crypto extension support, NEON/SIMD context, and Linux linkage macros. `arm/sha1.h` chooses it when both NEON and `HWCAP2_SHA1` are enabled.

## Risks And Edge Cases
The fast path must be used only on CPUs with SHA-1 instructions; illegal instruction faults are otherwise possible. Byte ordering and state vector lane layout must match generic SHA-1. Padding remains outside this routine.

## Test Signals
Run SHA-1 vectors on ARMv8-capable ARM32 hardware, compare with NEON and scalar outputs, and verify fallback when `HWCAP2_SHA1` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1.h

## Purpose
This header dispatches ARM32 SHA-1 block compression among scalar, NEON, and crypto-extension implementations.

## Important APIs, Types, And Functions
It declares `sha1_block_data_order`, `sha1_transform_neon`, and `sha1_ce_transform`. It defines static keys `have_neon` and `have_ce`, implements `sha1_blocks`, and defines `sha1_mod_init_arch`.

## Control Flow
At init, NEON enables `have_neon`; SHA-1 crypto extension capability additionally enables `have_ce`. At runtime `sha1_blocks` chooses crypto extensions inside `scoped_ksimd()` when available, otherwise NEON, otherwise scalar ARM.

## State And Persistence
Feature availability persists in jump labels. SHA-1 chaining state is caller-owned and updated by selected compression routines.

## Dependencies And Integration Points
It uses `<asm/simd.h>`, hardware capability variables, kernel-mode NEON configuration, and common SHA-1 block state types. It integrates with the common SHA-1 library through the `sha1_blocks` hook.

## Risks And Edge Cases
Feature detection must prevent crypto-extension instructions on unsupported CPUs. Calls in non-SIMD contexts must fall back to scalar. Build combinations without kernel-mode NEON must still compile.

## Test Signals
SHA-1 selftests should run with static keys forced or observed for scalar, NEON, and CE paths. CPU feature matrix builds and runtime fallback tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-armv4.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-armv4.pl

## Purpose
This Perl generator emits ARMv4 scalar, ARMv7 NEON, and optional ARMv8 SHA-256 crypto-extension block compression assembly derived from OpenSSL/Cryptogams.

## Important APIs, Types, And Functions
Generated symbols include `sha256_block_data_order`, `sha256_block_data_order_neon`, and `sha256_block_data_order_armv8`. The generator defines `BODY_00_15`, `BODY_16_XX`, `Xupdate`, `Xpreload`, and `body_00_15` helpers and emits the `K256` round table.

## Control Flow
The scalar routine loads the SHA-256 state, loops over 64-byte blocks, builds the message schedule, executes 64 rounds, and stores accumulated state. In non-kernel OpenSSL-style builds it can inspect `OPENSSL_armcap_P` and branch to NEON or ARMv8 code. The NEON path vectorizes schedule construction and parts of round preparation. The ARMv8 path uses SHA-256 extension instructions when generated for capable targets.

## State And Persistence
Runtime persistence is limited to the caller's `sha256_block_state`. The generator emits read-only constants and code; it has no runtime data state in the kernel.

## Dependencies And Integration Points
It depends on Perl at build time and ARM assembler support. `arm/sha256.h` declares the generated scalar/NEON symbols and separately declares `sha256_ce_transform` from the dedicated CE source.

## Risks And Edge Cases
Maintaining multiple generated variants risks divergence. Endian conversion, round constants, and schedule recurrence must be exact. Non-kernel capability code is present in the generator but the kernel dispatch is controlled by headers, so symbol naming and build flags must stay aligned.

## Test Signals
SHA-224/SHA-256 vectors, large multi-block streams, random comparison with generic C, builds for pre-ARMv7 and ARMv7 NEON, and generator reproducibility checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-armv4.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-ce.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-ce.S

## Purpose
This ARM32 assembly file implements SHA-256 compression using ARMv8 SHA-2 crypto extension instructions.

## Important APIs, Types, And Functions
The exported symbol is `sha256_ce_transform(struct sha256_block_state *state, const u8 *data, size_t nblocks)`. It uses `.Lsha256_rcon` for round constants and vector registers for state/message schedule.

## Control Flow
The routine loads initial state and constants, loops over input blocks, uses SHA-256 extension instructions to run rounds and update the schedule, accumulates results back into chaining variables, and writes state after all blocks.

## State And Persistence
Only the caller's SHA-256 state is updated. Temporary vectors and pointers are transient.

## Dependencies And Integration Points
It requires crypto-extension-capable ARM hardware, Linux linkage, and guarded SIMD entry. `arm/sha256.h` selects it when NEON is available and `HWCAP2_SHA2` is set.

## Risks And Edge Cases
Illegal instruction risk exists if dispatch is wrong. Lane ordering and endian loads must match SHA-256 big-endian block semantics. Finalization and partial block padding are not handled here.

## Test Signals
SHA-256 known-answer tests on CPUs with SHA2 extensions, comparison against scalar and NEON outputs, and fallback tests when `HWCAP2_SHA2` is absent are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha256-ce.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha256.h

## Purpose
This header dispatches ARM32 SHA-256 block compression between scalar, NEON, and SHA-2 crypto-extension implementations.

## Important APIs, Types, And Functions
It declares `sha256_block_data_order`, `sha256_block_data_order_neon`, and `sha256_ce_transform`. It defines `have_neon`, `have_ce`, `sha256_blocks`, and `sha256_mod_init_arch`.

## Control Flow
`sha256_mod_init_arch` enables NEON when `HWCAP_NEON` is present and enables CE when `HWCAP2_SHA2` is present. `sha256_blocks` chooses CE first inside `scoped_ksimd()`, then NEON, otherwise scalar.

## State And Persistence
Feature jump labels persist after init. The SHA-256 chaining state remains caller-owned.

## Dependencies And Integration Points
It includes ARM NEON/SIMD headers and uses common `struct sha256_block_state`. It integrates generated Cryptogams assembly with the dedicated CE assembly and generic SHA-256 library.

## Risks And Edge Cases
SIMD and CE dispatch must match hardware. The fallback scalar path is required for non-NEON or non-SIMD contexts. Configuration guards must keep declarations available only when corresponding objects are built.

## Test Signals
SHA-256 selftests across scalar, NEON, and CE paths, boot on ARM32 CPUs with partial feature sets, and `may_use_simd()` false-context tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha512-armv4.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha512-armv4.pl

## Purpose
This Perl generator emits ARMv4 scalar and ARMv7 NEON SHA-512 block compression assembly. It is OpenSSL/Cryptogams-derived and relicensed for GPLv2 kernel use.

## Important APIs, Types, And Functions
Generated symbols are `sha512_block_data_order` and `sha512_block_data_order_neon`. Generator helpers include `BODY_00_15`, `NEON_00_15`, and `NEON_16_79`. The `K512` table stores 80 64-bit constants in endian-aware word order.

## Control Flow
The scalar path treats each 64-bit SHA-512 word as high/low 32-bit halves, loads the state, processes 128-byte blocks through 80 rounds, updates the message schedule on stack, and stores accumulated state. The NEON path uses vector 64-bit operations for schedule and state accumulation, loops through `.Loop_neon` and `.L16_79_neon`, and rewinds the constants table between blocks.

## State And Persistence
Only the caller's `sha512_block_state` persists. Generated constant data is read-only. The stack holds schedule words and saved registers.

## Dependencies And Integration Points
It depends on Perl and ARM assembler support at build time. `arm/sha512.h` selects scalar or NEON generated routines depending on runtime NEON usability.

## Risks And Edge Cases
SHA-512 on 32-bit ARM is sensitive to high/low word ordering, carries, rotations spanning word halves, and endian configuration. The NEON routine includes an early Cortex-A8 erratum barrier and must preserve VFP ABI expectations.

## Test Signals
SHA-384/SHA-512 known-answer tests, multi-block randomized comparisons with generic C, big-endian build coverage, ARMv4 compatibility builds, and NEON runtime tests validate this generator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha512-armv4.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha512.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/sha512.h

## Purpose
This header dispatches ARM32 SHA-512 block compression between scalar and NEON implementations.

## Important APIs, Types, And Functions
It declares `sha512_block_data_order` and `sha512_block_data_order_neon`, defines `have_neon`, implements `sha512_blocks`, and defines `sha512_mod_init_arch`.

## Control Flow
Initialization enables `have_neon` when `cpu_has_neon()` reports support. Runtime `sha512_blocks` checks kernel-mode NEON, the static key, and `may_use_simd()`; it uses `sha512_block_data_order_neon` in `scoped_ksimd()` or falls back to scalar.

## State And Persistence
Only the static key persists. SHA-512 state is updated through caller-supplied memory.

## Dependencies And Integration Points
It includes ARM NEON/SIMD headers and common SHA-512 block state types. It integrates with assembly generated by `sha512-armv4.pl`.

## Risks And Edge Cases
The fallback is required for non-SIMD contexts. The NEON routine must only run when kernel-mode NEON is configured and usable. Because SHA-512 block size is 128 bytes, callers must pass full blocks only.

## Test Signals
SHA-512 and SHA-384 selftests, NEON vs scalar comparison, build coverage with and without `CONFIG_KERNEL_MODE_NEON`, and runtime tests under preemption-sensitive contexts are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/sha512.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce-core.S

## Purpose
This ARM64 assembly file implements single-block AES primitives using ARMv8 Crypto Extensions. It is the core used by high-level AES encryption/decryption and key schedule helpers.

## Important APIs, Types, And Functions
Exported symbols are `__aes_ce_encrypt`, `__aes_ce_decrypt`, `__aes_ce_sub`, and `__aes_ce_invert`. The first two process one 16-byte block with a provided round-key schedule and round count. `__aes_ce_sub` uses `aese` as an S-box primitive for key expansion, and `__aes_ce_invert` applies `aesimc` for decryption key derivation.

## Control Flow
Encrypt/decrypt load the input block and round keys, execute AES rounds in a compact loop that adapts to AES-128/192/256 round counts, apply final `aese`/`aesd` without MixColumns, xor the last round key, and store output. The helper routines are straight-line single-instruction transformations around loads/stores.

## State And Persistence
No persistent state exists. The caller-provided output buffer and key schedule are the only memory effects.

## Dependencies And Integration Points
It requires `.arch armv8-a+crypto`, Linux linkage, and is called by `arm64/aes.h` inside `scoped_ksimd()` when AES instructions are available.

## Risks And Edge Cases
Wrong round count or key schedule layout corrupts results. Dispatch must prevent execution on CPUs without AES instructions. The implementation assumes 16-byte block buffers and a compatible expanded-key format.

## Test Signals
AES ECB known-answer tests for 128/192/256-bit keys, key expansion tests exercising `__aes_ce_sub` and `__aes_ce_invert`, fallback comparison with scalar AES, and CPU feature gating tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce.S

## Purpose
This file provides ARM64 Crypto Extension versions of AES block modes by defining AES instruction macros and including the shared `aes-modes.S` template.

## Important APIs, Types, And Functions
Through `AES_FUNC_START(func)` it emits `ce_aes_ecb_encrypt`, `ce_aes_ecb_decrypt`, CBC/CTS/CTR/XCTR/XTS/ESSIV variants, and optionally `ce_aes_mac_update`. Local macros include `load_round_keys`, `enc_prepare`, `dec_prepare`, `do_block_Nx`, `encrypt_block{,4x,5x}`, and `decrypt_block{,4x,5x}`.

## Control Flow
The file preloads round keys into vector registers and maps template block operations to ARMv8 `aese/aesmc` or `aesd/aesimc`. `aes-modes.S` then supplies the mode control flow. Multi-block paths interleave up to five blocks to improve throughput, while single-block/tail paths reuse the same macros.

## State And Persistence
There is no global mutable state. Mode functions mutate caller-provided buffers and IV/tweak state according to mode contracts.

## Dependencies And Integration Points
It requires ARMv8 crypto extensions and includes `aes-modes.S`. Symbols are declared/exported by `arm64/aes.h` for in-kernel crypto mode users.

## Risks And Edge Cases
The included template assumes macro semantics for encryption, decryption, key switching, and XTS tweak helpers. Any macro mismatch affects all modes. Calls must be gated by AES feature availability and SIMD usability.

## Test Signals
AES mode selftests for ECB, CBC, CTS, CTR, XCTR, XTS, ESSIV, and CBC-MAC on AES-capable arm64 hardware are key. Compare with `aes-neon.S` and generic fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-cipher-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-cipher-core.S

## Purpose
This ARM64 assembly file provides scalar/table-based AES single-block encrypt/decrypt routines for systems or contexts where Crypto Extensions are unavailable.

## Important APIs, Types, And Functions
It exports `__aes_arm64_encrypt` and `__aes_arm64_decrypt`. The body uses table lookup macros such as `__pair1` to read 32-bit T-table entries and combine SubBytes, ShiftRows, MixColumns, and round key operations.

## Control Flow
The routines load a plaintext/ciphertext block, map bytes through AES lookup tables round by round, xor round keys, perform the final round without MixColumns, and store the block. The implementation is straight-line/macro-expanded around the round count.

## State And Persistence
No persistent state is kept. It reads the expanded key schedule and writes the caller's output block.

## Dependencies And Integration Points
It depends on Linux linkage, assembler helpers, cache alignment definitions, and AES tables available from the surrounding build. `arm64/aes.h` uses these routines as the fallback for `aes_encrypt_arch` and `aes_decrypt_arch`.

## Risks And Edge Cases
Table-based AES can have cache side-channel considerations compared with AES instructions. It must remain a fallback for contexts without AES CE but should not be preferred when CE is available. Key schedule layout must match the CE path.

## Test Signals
AES known-answer tests with AES feature disabled, comparison with CE output for all key sizes, and side-channel policy review for table use in kernel contexts are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-cipher-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-modes.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-modes.S

## Purpose
This shared ARM64 assembly template implements AES modes over macro-provided block primitives. It is included by both Crypto Extension and NEON AES implementations.

## Important APIs, Types, And Functions
Template-emitted functions include AES ECB encrypt/decrypt, CBC encrypt/decrypt, ESSIV CBC encrypt/decrypt, CBC-CTS encrypt/decrypt, CTR, XCTR, XTS encrypt/decrypt, and optional `aes_mac_update`. Local helpers include 4x/5x block wrappers, `ctr_encrypt`, `next_tweak`, `xts_load_mask`, CTS permutation table logic, and CBC-MAC loops.

## Control Flow
ECB and CBC paths process multi-block chunks with 4x or 5x interleaving, then handle single-block tails. CTR/XCTR constructs counter vectors, encrypts them, xors input, updates IV/counter state, and handles partial final blocks with documented overlapping temporary buffers. XTS encrypt/decrypt maintain and store tweaks, handle first-tweak encryption, process 4-block groups, and perform ciphertext stealing for non-block-multiple lengths. MAC update xors blocks into a digest and conditionally encrypts before/after.

## State And Persistence
Persistent state is caller-owned IV, counter, tweak, digest, input/output buffers, and key schedules. The template itself has no globals except read-only permutation data.

## Dependencies And Integration Points
It depends on includer-provided macros: `AES_FUNC_START`, `enc_prepare`, `dec_prepare`, `encrypt_block`, `decrypt_block`, multi-block variants, key switching, and XTS mask handling. `arm64/aes-ce.S` and `arm64/aes-neon.S` are the direct includers.

## Risks And Edge Cases
Tail handling is the highest-risk area. CTR/XCTR requires at least 16-byte temporary buffers even for sub-block sizes, with data at the end of the buffer. XTS CTS uses overlapping stores and pointer rewinds. Macro contract drift can break both CE and NEON variants simultaneously.

## Test Signals
Mode vectors for all exported modes, partial block tests for CTR/XCTR and CTS, in-place encryption/decryption tests, IV/tweak continuation tests, and comparison between CE, NEON, and generic implementations are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-modes.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-neon.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-neon.S

## Purpose
This ARM64 file implements AES modes using pure ASIMD/NEON operations rather than ARMv8 AES instructions. It provides a fallback accelerated mode implementation when ASIMD exists but AES CE does not.

## Important APIs, Types, And Functions
By defining `AES_FUNC_START(func)` as `neon_ ## func` and including `aes-modes.S`, it emits `neon_aes_*` mode functions. Local macros implement AES S-box/substitution, MixColumns, ShiftRows, and 4-block encrypt/decrypt operations with vector table/permutation instructions. Read-only tables include forward/reverse ShiftRows and rotate-by-8 permutations.

## Control Flow
The file sets up NEON AES round transformations, xors round keys, applies ShiftRows and SubBytes, performs MixColumns or inverse MixColumns as needed, and delegates mode-specific loops to `aes-modes.S`. Multi-block paths process four blocks at a time using vectorized transformations.

## State And Persistence
No global mutable state is used. Mode state lives in caller buffers, IVs, counters, tweaks, and key schedules.

## Dependencies And Integration Points
It requires ASIMD and the shared mode template. `arm64/aes.h` selects this path for CBC-MAC and exported internal mode helpers when ASIMD is available but AES CE is not.

## Risks And Edge Cases
The software S-box/MixColumns implementation is more complex than CE instruction use and may have timing/microarchitectural concerns. It shares all tail and mode risks from `aes-modes.S`. Correct table constants are critical.

## Test Signals
AES mode selftests on ASIMD-only arm64 targets or with AES feature masked, generic/CE comparison, in-place and tail tests, and KASAN checks around partial-block temporary buffers validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-neon.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes.h

## Purpose
This header is the ARM64 AES integration layer. It handles feature detection, key expansion, single-block dispatch, exported internal mode symbols, and optional CBC-MAC acceleration.

## Important APIs, Types, And Functions
It defines `struct aes_block`, static keys `have_neon` and `have_aes`, declarations for scalar, CE, and mode assembly symbols, `aes_expandkey_arm64`, `aes_preparekey_arch`, exported `ce_aes_expandkey`, `aes_encrypt_arch`, `aes_decrypt_arch`, `aes_cbcmac_blocks_arch`, and `aes_mod_init_arch`.

## Control Flow
Key expansion uses generic C when AES CE is unavailable or SIMD cannot be used; otherwise it uses `__aes_ce_sub` for key schedule S-box operations and `__aes_ce_invert` for inverse round keys. Single-block encrypt/decrypt choose CE inside `scoped_ksimd()` when possible and scalar otherwise. CBC-MAC chooses CE or NEON mode update under ASIMD. Init enables ASIMD and AES static keys through named CPU features.

## State And Persistence
Persistent state is limited to static keys. Expanded keys are stored in caller-owned AES key structures. `ce_aes_expandkey` mutates `struct crypto_aes_ctx` and is exported for remaining arch crypto users.

## Dependencies And Integration Points
It depends on ASIMD/SIMD helpers, unaligned access helpers, cpufeature APIs, generic AES key expansion/check helpers, and exported internal crypto symbols for mode code. It bridges lib/crypto and legacy arch/arm64 crypto users.

## Risks And Edge Cases
The expanded key format must stay compatible across scalar, CE, NEON modes, and exported users. `ce_aes_expandkey` is temporary but externally visible. SIMD usability checks are required for key expansion too because `__aes_ce_sub` uses vector crypto instructions.

## Test Signals
AES key expansion tests for all key sizes, encrypt/decrypt KATs, module symbol users such as CCM/XTS/CBC, fallback with AES feature disabled, and CBC-MAC tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha-neon-core.S

## Purpose
This ARM64 ASIMD assembly file implements ChaCha and HChaCha core functions, including a high-throughput multi-block XOR path.

## Important APIs, Types, And Functions
Exported symbols are `chacha_block_xor_neon`, `hchacha_block_neon`, and `chacha_4block_xor_neon`; `chacha_permute` is local. Read-only tables include `CTRINC` for counter increments, `ROT8` for byte rotations, and `.Lpermute` for tail permutation/overlap handling.

## Control Flow
`chacha_permute` runs the requested double rounds on one state. `chacha_block_xor_neon` permutes one block, adds original state words, xors 64 input bytes, and writes output. `hchacha_block_neon` emits the HChaCha words. `chacha_4block_xor_neon` constructs four or more counter states in parallel, runs vectorized rounds, adds original words, transposes lanes into byte streams, xors input, stores full blocks, and uses permutation/overlapping-store logic for 128-320 byte tails.

## State And Persistence
No global mutable state exists. The caller owns the ChaCha state and increments its counter in the C header after each call. Output buffers are written in place or out of place.

## Dependencies And Integration Points
It depends on Linux linkage/assembler macros and ASIMD. `arm64/chacha.h` calls it inside `scoped_ksimd()` when ASIMD is available and SIMD is usable.

## Risks And Edge Cases
Partial tail handling uses overlapping loads/stores and assumes caller-provided buffers satisfy the header's chunking expectations. Counter increment and overflow behavior are split between assembly and C wrapper. Round count must match caller expectations for ChaCha20 or reduced-round variants.

## Test Signals
ChaCha20 and HChaCha vectors, XChaCha tests, in-place encryption, lengths around 64/128/192/256/320 bytes, counter continuation tests, and ASIMD-disabled fallback comparisons are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha.h

## Purpose
This header dispatches ARM64 ChaCha/HChaCha operations to ASIMD assembly when beneficial and safe, otherwise generic C.

## Important APIs, Types, And Functions
It declares `chacha_block_xor_neon`, `chacha_4block_xor_neon`, and `hchacha_block_neon`. It defines `have_neon`, `chacha_doneon`, `hchacha_block_arch`, `chacha_crypt_arch`, and `chacha_mod_init_arch`.

## Control Flow
`chacha_crypt_arch` falls back to generic code if ASIMD is unavailable, the message is at most one block, or SIMD is unusable. Otherwise it enters `scoped_ksimd()` and calls `chacha_doneon`, which processes up to five blocks per iteration, uses a stack buffer for a final single partial block, and advances `state->x[12]` by consumed blocks. HChaCha similarly chooses generic or NEON.

## State And Persistence
The ChaCha state is caller-owned but its block counter is updated by the wrapper. No key material is stored globally. The static key persists after init.

## Dependencies And Integration Points
It depends on `crypto/internal/simd.h`, jump labels, kernel helpers, ARM64 hwcap/SIMD, and common ChaCha state constants. It integrates with generic ChaCha/XChaCha library hooks.

## Risks And Edge Cases
Counter updates must match bytes processed, especially for partial final blocks. The wrapper copies short tails through a 64-byte stack buffer to satisfy assembly block assumptions. SIMD gating is mandatory in atomic/preempt-disabled contexts.

## Test Signals
ChaCha vectors over many lengths, counter wrap/continuation tests, HChaCha vectors, generic-vs-NEON comparison, and testing with `crypto_simd_usable()` false validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/chacha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/gf128hash.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/gf128hash.h

## Purpose
This ARM64 header provides architecture hooks for GHASH and POLYVAL using ASIMD and PMULL acceleration, with generic fallbacks.

## Important APIs, Types, And Functions
It defines `NUM_H_POWERS`, static keys `have_asimd` and `have_pmull`, declares `pmull_ghash_update_p8`, `polyval_mul_pmull`, and `polyval_blocks_pmull`, and implements `polyval_preparekey_arch`, `polyval_mul_arm64`, `ghash_mul_arch`, `polyval_mul_arch`, `ghash_blocks_arch`, `polyval_blocks_arch`, and `gf128hash_mod_init_arch`.

## Control Flow
Initialization enables ASIMD and optionally PMULL. POLYVAL key preparation stores the raw key as the highest power and computes descending powers with PMULL or generic multiplication. Single multiply uses PMULL when available; with ASIMD but no PMULL it reuses the GHASH p8 routine on a zero block for equivalent POLYVAL multiplication. Block GHASH uses p8 ASIMD; block POLYVAL uses PMULL or generic fallback.

## State And Persistence
Feature static keys persist. `struct polyval_key` stores precomputed powers in caller-owned key memory; accumulators are updated in place.

## Dependencies And Integration Points
It depends on ARM64 cpufeature/SIMD APIs and common GF128 hash types. It integrates `ghash-neon-core.S` and POLYVAL PMULL core routines with generic GHASH/POLYVAL users such as AES-GCM and AES-GCM-SIV.

## Risks And Edge Cases
The equivalence trick for POLYVAL via GHASH p8 relies on format and zero-byte-swap assumptions. Key power order must match `polyval_blocks_pmull`. SIMD context and feature gating must distinguish ASIMD-only from PMULL-capable systems.

## Test Signals
GHASH, POLYVAL, AES-GCM, and AES-GCM-SIV vectors; PMULL and no-PMULL ASIMD feature testing; key precompute comparisons; and randomized generic-vs-arch tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/gf128hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/ghash-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/ghash-neon-core.S

## Purpose
This ARM64 assembly file implements GHASH update using ASIMD polynomial multiply operations. It provides the p8 GHASH primitive used by both GHASH and some POLYVAL fallback paths.

## Important APIs, Types, And Functions
The exported symbol is `pmull_ghash_update_p8`. Macros include `__pmull_p8`, `__pmull2_p8`, `__pmull_pre_p8`, `__pmull_reduce_p8`, and specialized SHASH/SHASH2 helper forms. It prepares permutation vectors and shifted hash-key variants for efficient multiplication.

## Control Flow
The function loads the hash key and accumulator, precomputes low/high/cross multiplication helpers, then loops over input blocks. Each iteration reverses input bytes for GHASH format, xors the block into the accumulator, computes low/high/cross products using PMULL-style p8 operations, reduces the product modulo the GHASH polynomial, and stores the final accumulator after all blocks.

## State And Persistence
Only the caller's accumulator memory is updated. All other data is in vector registers or read-only constants synthesized at runtime.

## Dependencies And Integration Points
It depends on ARM64 assembler helpers and ASIMD/PMULL instruction availability as gated by `arm64/gf128hash.h`. It shares accumulator/key layout with common `struct polyval_elem`.

## Risks And Edge Cases
Byte order and polynomial reduction must match GHASH exactly. The macro-generated product uses many temporary vector registers; aliasing mistakes are hard to spot. Dispatch must avoid unsupported PMULL/p8 instructions.

## Test Signals
AES-GCM vectors, random GHASH comparison with generic C, endian/layout tests, and feature-gated arm64 runs with PMULL are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/ghash-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/nh-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/nh-neon-core.S

## Purpose
This ARM64 ASIMD assembly file implements the NH universal hash fast path.

## Important APIs, Types, And Functions
It exports `nh_neon(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. The `_nh_stride` macro loads message and key vectors, adds them as 32-bit words, widens products, and accumulates pass sums.

## Control Flow
The function initializes four vector accumulators, processes 64-byte strides in `.Lloop4`, handles the final stride path, and stores four 64-bit little-endian hash sums to the output. It advances key and message pointers consistently with the NH pass layout.

## State And Persistence
Only the output hash array is written persistently. Keys and message data are read-only caller inputs.

## Dependencies And Integration Points
It uses Linux linkage macros and ASIMD registers. `arm64/nh.h` gates calls with ASIMD feature detection, minimum message length, and `may_use_simd()`.

## Risks And Edge Cases
Length alignment and short-message handling are delegated to the header/generic caller. Endianness of output and message word interpretation must match generic NH. SIMD context safety is required.

## Test Signals
NH known-answer tests, randomized comparisons with generic NH across boundary lengths, ASIMD feature masking, and users such as Adiantum provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/nh-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/nh.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm64/nh.h

## Purpose
This header connects the ARM64 ASIMD NH implementation to the generic NH library.

## Important APIs, Types, And Functions
It declares `nh_neon`, defines `have_neon`, implements `nh_arch`, and defines `nh_mod_init_arch`.

## Control Flow
Init enables `have_neon` when `cpu_have_named_feature(ASIMD)` is true. `nh_arch` checks `have_neon`, `message_len >= 64`, and `may_use_simd()`, then calls `nh_neon` inside `scoped_ksimd()` and returns true. Otherwise it returns false for generic processing.

## State And Persistence
Only the feature static key persists. The key, message, and hash buffers are caller-owned.

## Dependencies And Integration Points
It depends on ARM64 hwcap/SIMD and cpufeature helpers plus common NH constants and types. It is the arch hook consumed by generic NH code.

## Risks And Edge Cases
The threshold and SIMD gating determine when assembly is used. Incorrect feature detection would cause illegal instructions or missed acceleration. Short inputs must continue to use the generic path.

## Test Signals
Generic-vs-ASIMD NH comparisons, lengths below/at/above 64 bytes, CPU feature masking, and builds on non-ASIMD configurations validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm64/nh.h -->
