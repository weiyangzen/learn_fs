# subset-b-006085 Research

This grouped report covers Linux/Ceph-client crypto acceleration files under `sources/distributed-fs/ceph-client/lib/crypto/{powerpc,riscv}`. Each section is intended to be split into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-keys.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-keys.S

## Purpose
Implements AES key schedule handling for the 32-bit PowerPC SPE AES backend. It expands 128-, 192-, and 256-bit AES keys into encryption round-key buffers and derives a decryption key schedule from an existing encryption schedule. This is the setup companion to the SPE AES block and mode assembly.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_expand_key_128)`, `_GLOBAL(ppc_expand_key_192)`, `_GLOBAL(ppc_expand_key_256)`, and `_GLOBAL(ppc_generate_decrypt_key)`. Callers pass the output schedule in `r3` and raw key/encryption schedule inputs in `r4`; `ppc_generate_decrypt_key` also consumes the AES key length in `r5`. The file defines `LOAD_KEY`, `INITIALIZE_KEY`, `FINALIZE_KEY`, `LS_BOX`, and `GF8_MUL` macros rather than C types.

## Control Flow
Each expansion routine loads the raw key with endian-aware `LOAD_KEY`, stores the first round key, then iterates a fixed number of key expansion rounds. AES-128 loops 10 times with RotWord/SubWord/Rcon processing every round, AES-192 loops over six-word chunks with an early final exit, and AES-256 handles the extra SubWord step on the fourth generated word. `ppc_generate_decrypt_key` reverses first and last round keys, then applies an InvMixColumns-style transformation to middle schedule words in `ppc_generate_decrypt_block` and `ppc_generate_decrypt_word`.

## State and Persistence
The routines write expanded key material into caller-provided memory and otherwise keep state in GPRs. `FINALIZE_KEY` restores saved registers and clears several volatile registers that held key material, reducing leftover sensitive data in registers. No global state is mutated.

## Dependencies and Integration Points
The code includes `<asm/ppc_asm.h>` and depends on `PPC_AES_4K_ENCTAB` from `aes-tab-4k.S` for S-box lookups in `LS_BOX`. It is called by the PowerPC AES header glue when `CONFIG_SPE` is enabled, which exposes these functions through the AES library arch hooks.

## Risks
Correctness risk centers on key-length-specific schedule sizes and the `r5` encoding used by decrypt-key generation. Because the S-box is table-based, it can expose cache-timing side channels on systems where attacker observation of cache state is realistic. Endian-specific key loading also needs cross-endian coverage.

## Test Signals
Useful signals are AES known-answer tests for 128/192/256-bit keys, encrypt/decrypt round trips through the SPE AES block code, and comparisons of generated schedules against generic AES schedule generation on both big- and little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-keys.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-modes.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-modes.S

## Purpose
Provides SPE-backed AES single-block and mode operations for PowerPC: ECB, CBC, CTR, and XTS. It wraps the lower-level `ppc_encrypt_block` and `ppc_decrypt_block` helpers with mode-specific data loading, IV/tweak handling, endian conversion, and register preservation.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_encrypt_aes)`, `_GLOBAL(ppc_decrypt_aes)`, `_GLOBAL(ppc_encrypt_ecb)`, `_GLOBAL(ppc_decrypt_ecb)`, `_GLOBAL(ppc_encrypt_cbc)`, `_GLOBAL(ppc_decrypt_cbc)`, `_GLOBAL(ppc_crypt_ctr)`, `_GLOBAL(ppc_encrypt_xts)`, and `_GLOBAL(ppc_decrypt_xts)`. Register aliases are imported from `aes-spe-regs.h`. Macros include endian-aware `LOAD_DATA`, `SAVE_DATA`, `LOAD_IV`, `SAVE_IV`, `INITIALIZE_CRYPT`, `FINALIZE_CRYPT`, `START_KEY`, `ENDIAN_SWAP`, and `GF128_MUL`.

## Control Flow
Single-block encrypt/decrypt loads one 16-byte block, xors the first round key, branches to the core block routine, xors the final round key, and stores output. ECB loops whole 16-byte blocks until `rLN` drops below one block. CBC encryption xors input with the current IV and stores each ciphertext as the next IV; CBC decryption processes from the end backward so previous ciphertext is available for chaining, then handles the first block against the original IV. CTR encrypts counter blocks, xors input with the keystream, increments the 128-bit counter, and has a bytewise partial-block tail. XTS optionally encrypts the IV with the tweak key, xors each block with the tweak, encrypts/decrypts, xors the tweak again, then multiplies the tweak by x in GF(2^128) per block.

## State and Persistence
The mode routines update caller-provided IV/tweak buffers for CBC, CTR, and XTS. Stack frames save nonvolatile GPR/SPE state and `FINALIZE_CRYPT` wipes saved sensitive stack slots before returning. No persistent globals are modified.

## Dependencies and Integration Points
Depends on `aes-spe-regs.h`, `PPC_AES_4K_ENCTAB`, `PPC_AES_4K_DECTAB`, and the lower-level SPE AES core functions in the same PowerPC crypto directory. The C AES glue calls these routines inside an SPE-enabled, preemption-disabled region.

## Risks
CBC and XTS assume whole-block input, while CTR accepts partial bytes; callers must satisfy each mode contract. The table backend can leak through cache timing. IV/tweak state is modified in place, so interrupted or retried higher-level calls must respect that side effect. Endian pointer adjustment macros differ substantially between BE and LE and are high-risk for off-by-one errors.

## Test Signals
Use mode known-answer tests for AES-ECB/CBC/CTR/XTS, especially CTR partial tails, CBC decrypt with multiple blocks, and XTS tweak progression. Cross-check IV/tweak output buffers after calls, not just ciphertext/plaintext.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-modes.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-regs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-regs.h

## Purpose
Defines common register aliases for the PowerPC SPE AES implementation. It lets AES mode and core assembly share a stable argument and scratch-register vocabulary.

## Important APIs, Types, and Functions
There are no functions or C types. The file maps logical names such as `rDP`, `rSP`, `rKP`, `rRR`, `rLN`, `rIP`, `rKT`, `rD0` through `rD3`, `rW0` through `rW7`, `rI0` through `rI3`, and `rG0` through `rG3` to PowerPC registers.

## Control Flow
This header has no runtime control flow. It affects code generation by macro substitution in assembly sources that include it.

## State and Persistence
No state is stored. Its aliases document which registers carry source/destination pointers, key schedule pointers, round counts, lengths, IVs, tweaks, and scratch data while the including assembly runs.

## Dependencies and Integration Points
Included by `aes-spe-modes.S` and expected to be consistent with the low-level AES core assembly calling convention. The aliases also reflect Linux PowerPC ABI requirements around volatile and nonvolatile registers that the including files save/restore.

## Risks
Register alias drift would silently break assembly call contracts. `rKT` and `rD0` both alias `r9` in different contexts, so maintainers must preserve the existing phase separation between tweak-key argument use and data-register use.

## Test Signals
Any AES SPE mode known-answer failure can indicate register contract breakage. Assembly build failures or objdump review of function prologues are useful after edits to this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-spe-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-tab-4k.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-tab-4k.S

## Purpose
Defines compact, 4 KiB-aligned AES T-tables and inverse S-box data for the PowerPC SPE AES backend. These tables trade memory footprint and table locality against constant-time behavior.

## Important APIs, Types, and Functions
Exports data symbols `PPC_AES_4K_ENCTAB`, `PPC_AES_4K_DECTAB`, and `PPC_AES_4K_DECTAB2`. The `R(a,b,c,d)` macro emits four rotated 32-bit variants from one AES table entry.

## Control Flow
There is no executable control flow. The file emits `.data` with encryption table words, decryption table words, and a byte inverse S-box table.

## State and Persistence
The tables are persistent read-mostly kernel data once linked. They are used by key expansion and block encryption/decryption and are not modified at runtime.

## Dependencies and Integration Points
Consumed by `aes-spe-keys.S`, `aes-spe-modes.S`, and the AES SPE core. Table values are derived from `crypto/aes_generic.c` but laid out for SPE-friendly indexed loads and rotations.

## Risks
The file explicitly notes cache-timing exposure from table lookups. Any table corruption causes broad AES failure and may be hard to localize because multiple routines depend on the same symbols. Alignment matters for performance and addressing assumptions.

## Test Signals
AES known-answer tests across key sizes and modes validate table contents indirectly. Static checks should confirm symbol names and 4 KiB alignment survive assembler/linker changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes-tab-4k.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes.h

## Purpose
Provides PowerPC AES architecture hooks for the generic AES library. It selects between SPE support when `CONFIG_SPE` is enabled and POWER8 vector crypto support otherwise, with generic fallback when the accelerated key format cannot be used.

## Important APIs, Types, and Functions
Defines `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, and `aes_mod_init_arch`. In the SPE branch it references `ppc_expand_key_*`, `ppc_generate_decrypt_key`, `ppc_encrypt_aes`, and `ppc_decrypt_aes`. In the POWER8 branch it exports and calls `aes_p8_set_encrypt_key`, `aes_p8_set_decrypt_key`, `aes_p8_encrypt`, `aes_p8_decrypt`, CBC/CTR/XTS helpers, `is_vsx_format`, and `rndkey_from_vsx`.

## Control Flow
For SPE, key preparation directly expands SPE schedules and encryption/decryption enters an SPE region around one assembly block call. For POWER8, module init enables a static key when CPU vector crypto is available. Key preparation uses VSX if the static key and `may_use_simd()` are true; otherwise it generates generic round keys and marks the POWER8 key format invalid with `nrounds = 0`. Encrypt/decrypt use POWER8 assembly when the key is in VSX format and SIMD is usable, convert VSX keys to generic format for rare non-SIMD contexts, or fall back to generic AES directly.

## State and Persistence
The `have_vec_crypto` static branch persists CPU feature availability after init. Prepared key objects persist either POWER8 VSX schedules or generic schedules. The POWER8 path disables preemption and page faults around kernel VSX use, while the SPE path disables preemption around SPE use.

## Dependencies and Integration Points
Includes PowerPC SIMD/VSX/SPE, CPU feature, preemption, and uaccess headers. It integrates with common AES types such as `struct aes_enckey`, `struct aes_key`, `union aes_enckey_arch`, and generic AES helpers from the crypto library.

## Risks
The dual key-format logic is subtle: keys prepared under VSX may later be used where SIMD is unavailable, requiring exact `rndkey_from_vsx` conversion. Pagefault and preemption boundaries must remain paired. CPU feature checks must match the assembly instruction set actually emitted by `aesp8-ppc.pl`.

## Test Signals
Run AES self-tests with forced SIMD-enabled and SIMD-disabled contexts, including decryption paths that convert VSX inverse keys. Boot/module init on CPUs with and without POWER8 vector crypto should validate static-key gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aesp8-ppc.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/aesp8-ppc.pl

## Purpose
Generates POWER8 AES vector-crypto assembly from CRYPTOGAMS/perlasm sources. The generated code implements AES key setup, single-block encrypt/decrypt, CBC, CTR32, and XTS with optimized multi-block paths.

## Important APIs, Types, and Functions
The Perl generator emits symbols with the `aes_p8` prefix: `aes_p8_set_encrypt_key`, `aes_p8_set_decrypt_key`, `aes_p8_encrypt`, `aes_p8_decrypt`, `aes_p8_cbc_encrypt`, `aes_p8_ctr32_encrypt_blocks`, `aes_p8_xts_encrypt`, and `aes_p8_xts_decrypt`. It uses `$flavour`, `$SIZE_T`, `$LITTLE_ENDIAN`, `$FRAME`, and `ppc-xlate.pl` to produce ABI- and endian-specific output.

## Control Flow
The script validates the requested 32/64-bit flavour, finds `ppc-xlate.pl`, pipes generated pseudo-assembly through it, and conditionally rewrites endian markers. Generated key setup validates pointers and AES key size, then uses vector AES instructions and constants to derive round keys. Single-block functions align unaligned input/output, loop over rounds with `vcipher` or `vncipher`, and store with masks. CBC encrypt/decrypt contains scalar one-block loops and an 8x decrypt path for long inputs. CTR has single-block and 8x loops and increments counters with 128-bit vector addition. XTS handles optional key2 tweak encryption, tweak chaining mode when key2 is NULL, ciphertext stealing, and 6x/5x helpers for long runs.

## State and Persistence
The script itself persists no state beyond writing generated assembly. Generated routines save and restore VRSAVE and ABI-required vector registers, wipe stack copies of round keys in the optimized paths, update IV/tweak buffers for chaining modes, and return error codes for invalid key setup or too-short XTS input.

## Dependencies and Integration Points
Depends on CRYPTOGAMS perlasm conventions and `ppc-xlate.pl`. The generated symbols are declared and exported by `aes.h` and are used when the PowerPC CPU supports ISA 2.07 vector crypto. It also assumes the kernel enables VSX and manages preemption/page faults before calls.

## Risks
Generated code is difficult to review because Perl string interpolation, endian conditional markers, and assembler translation all affect final instructions. XTS stealing and tweak chaining are high-risk edge cases. Unaligned VSX loads/stores may fault at page boundaries if callers violate kernel access assumptions, which is why the C wrapper disables page faults around key setup and block ops.

## Test Signals
Regenerate and diff the produced assembly after script changes. Run AES vector crypto self-tests for all key sizes and modes, with CBC/CTR/XTS lengths around 1, 7, 8, 16, 96, 128, and non-multiple-of-block XTS tails. Validate big- and little-endian output if both flavours are supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/aesp8-ppc.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha-p10le-8x.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha-p10le-8x.S

## Purpose
Implements a Power10 little-endian VSX/vector accelerated ChaCha20 transform that processes 4 or 8 blocks in parallel for the PowerPC ChaCha arch hook.

## Important APIs, Types, and Functions
Exports `SYM_FUNC_START(chacha_p10le_8x)`. Internal macros include `SAVE_REGS`, `RESTORE_REGS`, `QT_loop_8x`, `QT_loop_4x`, `TP_4x`, `Add_state`, and `Write_256`. Local data symbol `PERMX` supplies permutation constants used by rotate/permutation operations.

## Control Flow
The function returns immediately for nonpositive length. Otherwise it saves a large GPR/vector/VSX register frame, loads the ChaCha constants, key, counter, nonce, and permutation constants, and sets the double-round count from `nrounds / 2`. For input of at least 512 bytes, `Loop_8x` performs two 4-block lanes per iteration. Smaller remaining chunks use `Loop_4x`. Each loop broadcasts state words to vectors, adds per-block counters, runs repeated quarter-round macros, transposes the vector layout, adds the original state, xors with input, writes 256-byte chunks, advances offsets, and updates counter vectors.

## State and Persistence
The assembly writes ciphertext/plaintext to `dst` and does not itself store the updated counter back to the C `chacha_state`; the header wrapper increments `state->x[12]` by processed full blocks after the assembly call. Callee-saved registers and vector state are restored from the stack.

## Dependencies and Integration Points
Included through `chacha.h` on Power10 little-endian systems. It depends on Power10/VSX instructions including `vpermxor`, vector rotates, and unaligned vector load/store patterns. The C wrapper manages `enable_kernel_vsx()` and limits calls to full 256-byte multiples.

## Risks
The split between assembly processing and C-side counter update is a key integration risk. Lengths passed to this function must be block-aligned and chunked as the wrapper expects. The save frame is large and ABI-sensitive. This file is little-endian specific.

## Test Signals
ChaCha20 known-answer tests should cover lengths just over one block, 256-byte multiples, 512-byte multiples, and residual bytes handled by the generic fallback. Tests should assert final `state->x[12]` after mixed accelerated/generic chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha-p10le-8x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha.h

## Purpose
Provides the PowerPC ChaCha architecture hook, selecting Power10 VSX acceleration for large buffers and falling back to the generic ChaCha implementation otherwise.

## Important APIs, Types, and Functions
Declares `asmlinkage void chacha_p10le_8x(...)`, defines `chacha_p10_do_8x`, `chacha_crypt_arch`, `chacha_mod_init_arch`, and maps `hchacha_block_arch` to `hchacha_block_generic`. It maintains `static __ro_after_init DEFINE_STATIC_KEY_FALSE(have_p10)`.

## Control Flow
Module init enables `have_p10` when `CPU_FTR_ARCH_31` is present. `chacha_crypt_arch` uses generic code if Power10 is unavailable, the buffer is at most one block, or SIMD is not usable. Otherwise it processes up to 4 KiB per VSX critical section. `chacha_p10_do_8x` sends the largest 256-byte-aligned prefix to assembly, advances pointers, updates the ChaCha block counter by processed blocks, then uses generic code for the remaining bytes.

## State and Persistence
The static key persists CPU capability. The function mutates `state->x[12]` as data is encrypted/decrypted, matching stream cipher counter semantics. VSX use is enclosed by preemption-disabled `vsx_begin`/`vsx_end`.

## Dependencies and Integration Points
Depends on PowerPC CPU feature and VSX switching APIs plus `crypto_simd_usable()`. Integrated by the generic ChaCha library via `chacha_crypt_arch`.

## Risks
Counter accounting must stay synchronized with the assembly block count. The 4 KiB chunking bounds preemption-off windows, but any future change to chunk size should consider latency. HChaCha is explicitly not accelerated.

## Test Signals
Run ChaCha/XChaCha tests with hardware acceleration available and unavailable, with lengths below one block, one block, 255/256/257 bytes, and over 4 KiB to exercise chunk loops and generic tails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/curve25519-ppc64le_asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/curve25519-ppc64le_asm.S

## Purpose
Implements low-level 51-bit limb arithmetic primitives for PPC64 little-endian X25519 scalar multiplication. The C Montgomery ladder in `curve25519.h` calls these primitives for multiplication, squaring, repeated squaring, conversion, and conditional swaps.

## Important APIs, Types, and Functions
Exports `x25519_fe51_mul`, `x25519_fe51_sqr`, `x25519_fe51_mul121666`, `x25519_fe51_sqr_times`, `x25519_fe51_frombytes`, `x25519_fe51_tobytes`, and `x25519_cswap`. The functions operate on `fe51` arrays of five 64-bit limbs.

## Control Flow
Multiplication loads five limbs from both operands, computes cross-products with `mulld`/`mulhdu`, folds high limbs using the Curve25519 reduction factor 19, then branches into shared reduction logic. Squaring uses symmetry to reduce multiplications and also branches to shared reduction. `mul121666` multiplies all limbs by the Montgomery ladder constant and reduces. `sqr_times` runs the squaring/reduction body under a CTR loop. `frombytes` maps 32 little-endian bytes into five 51-bit limbs. `tobytes` performs full carry reduction, conditionally subtracts the field prime via carry propagation, and packs limbs back into 32 bytes. `x25519_cswap` performs a branchless masked swap over five limbs.

## State and Persistence
All field operations write results to caller-provided buffers. They preserve ABI-required nonvolatile registers using stack frames. No globals are modified.

## Dependencies and Integration Points
Included by the PowerPC Curve25519 arch implementation in `curve25519.h`. It depends on PPC64LE integer multiply/high-multiply support and Linux `SYM_FUNC_START` linkage macros.

## Risks
Finite-field arithmetic has high correctness sensitivity around carries, final reduction, and limb packing. Constant-time behavior depends on `x25519_cswap` remaining branchless with respect to secret bits and on avoiding secret-dependent memory indexing. There is an apparent duplicate restore of register 23 in `x25519_fe51_mul`, which is harmless but worth noticing during maintenance.

## Test Signals
Run RFC 7748 X25519 test vectors, random scalar multiplication comparisons against the generic implementation, and edge cases near field modulus boundaries. Constant-time review should focus on `x25519_cswap` and scalar-bit ladder integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/curve25519-ppc64le_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/curve25519.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/curve25519.h

## Purpose
Implements the PowerPC X25519 architecture hook using a C Montgomery ladder over 51-bit limbs backed by PPC64LE assembly arithmetic primitives.

## Important APIs, Types, and Functions
Defines `typedef uint64_t fe51[5]`, declares `x25519_fe51_*` assembly helpers and `x25519_cswap`, maps core macros `fmul`, `fsqr`, `fmul121666`, and `fe51_tobytes`, and defines `fadd`, `fsub`, `fe51_frombytes`, `finv`, `curve25519_fe51`, `curve25519_arch`, and `curve25519_base_arch`.

## Control Flow
`curve25519_fe51` clamps the scalar, loads the input point, initializes projective points `(x2,z2)` and `(x3,z3)`, then iterates scalar bits from 254 down to 0. Each iteration performs constant-time conditional swaps, ladder differential addition/doubling formulas, multiplication by 121666, and field squaring/multiplication. After the loop, it inverts `z2`, multiplies by `x2`, and serializes the affine coordinate. `curve25519_arch` and `curve25519_base_arch` are thin wrappers for arbitrary and base-point multiplication.

## State and Persistence
The function stack holds scalar and field temporaries. It writes only the public output buffer. The static `prime51` array represents the field modulus in limb form and is read during subtraction.

## Dependencies and Integration Points
Depends on kernel types, CPU feature headers, generic Curve25519 constants, and the PPC64LE assembly file. It is selected by the generic Curve25519 code as the architecture implementation.

## Risks
Scalar clamping and branchless swap are security-critical. The C ladder loops over secret bits but uses conditional swaps instead of secret branches; any helper replacement must preserve this. `fe51_frombytes` copies into an aligned local buffer before assembly conversion, so stack alignment and bounds must remain correct.

## Test Signals
RFC 7748 test vectors, basepoint public-key generation tests, and generic-vs-arch random differential tests are essential. Static analysis should check that secret-dependent control flow is limited to constant-time masked operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/curve25519.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/gf128hash.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/gf128hash.h

## Purpose
Provides PowerPC GHASH/GF(2^128) architecture hooks using POWER8 vector crypto when available, with generic POLYVAL/GHASH fallback.

## Important APIs, Types, and Functions
Declares `gcm_init_p8`, `gcm_gmult_p8`, and `gcm_ghash_p8`. Defines `ghash_preparekey_arch`, `ghash_mul_arch`, `ghash_blocks_arch`, and `gf128hash_mod_init_arch`, plus a `have_vec_crypto` static key.

## Control Flow
Key preparation always stores the raw key in generic POLYVAL form. If vector crypto and SIMD are usable, it enters a VSX region and calls `gcm_init_p8` to build the POWER8 table; otherwise it reproduces the table layout in C. Multiplication and block processing convert the internal POLYVAL accumulator into GHASH byte order, run the vector helper inside VSX, convert back, and zero the temporary accumulator. Fallback paths call generic POLYVAL/GHASH routines.

## State and Persistence
The static branch records CPU feature availability after module init. Each `struct ghash_key` persists both generic and POWER8 table material. Temporary GHASH accumulators are explicitly zeroed after use.

## Dependencies and Integration Points
Depends on PowerPC VSX switching, CPU feature bits `CPU_FTR_ARCH_207S` and `PPC_FEATURE2_VEC_CRYPTO`, and generic GHASH/POLYVAL conversion helpers. The generated helpers come from `ghashp8-ppc.pl`.

## Risks
Byte-order conversion between POLYVAL internal state and GHASH helper state is a primary correctness risk. SIMD availability can differ between key setup and use, so the C fallback table generation must match `gcm_init_p8`. Preemption/pagefault control must remain paired around VSX calls.

## Test Signals
Run GHASH and AES-GCM known-answer tests with vector crypto enabled and disabled. Compare `gcm_init_p8` table output to the C fallback table for random keys on BE and LE builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/gf128hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/ghashp8-ppc.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/ghashp8-ppc.pl

## Purpose
Generates POWER8 GHASH assembly from CRYPTOGAMS perlasm. The generated code provides vector polynomial multiplication helpers for GCM/GHASH.

## Important APIs, Types, and Functions
Emits `.gcm_init_p8`, `.gcm_gmult_p8`, and `.gcm_ghash_p8`. The script configures word size and stack instructions from `$flavour`, locates `ppc-xlate.pl`, and uses vector registers for accumulator, input, hash table entries, reduction constants, and endian masks.

## Control Flow
The script validates the target flavour, opens a pipe to the PowerPC translator, emits assembly text, and removes or comments endian-conditional markers. Generated `gcm_init_p8` loads H, endian-adjusts on LE, twists H into the form expected by the reduction algorithm, and stores a four-entry table. `gcm_gmult_p8` loads Xi and table entries, uses `vpmsumd` to compute carryless products, reduces in two phases, endian-adjusts, and stores Xi. `gcm_ghash_p8` loops over 16-byte input blocks, xors each into Xi, multiplies/reduces, and writes the final accumulator.

## State and Persistence
The generator writes assembly and has no runtime state. Generated routines modify caller-provided table or accumulator buffers and preserve VRSAVE. No global runtime state is used.

## Dependencies and Integration Points
Depends on `ppc-xlate.pl`, PowerISA 2.07 vector instructions, and the C declarations in `gf128hash.h`. The C wrapper is responsible for enabling VSX and converting between GHASH and POLYVAL representations.

## Risks
The `le?`/`be?` marker rewriting makes endian behavior easy to break. GHASH reduction constants and table layout must match the C fallback in `gf128hash.h`. Any translator path change can alter emitted ABI details.

## Test Signals
Regenerate output and compare to checked-in generated assembly when applicable. GHASH known-answer tests and C-fallback table equivalence tests should catch most arithmetic and endian regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/ghashp8-ppc.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5-asm.S

## Purpose
Implements a PowerPC optimized MD5 compression function over one or more 64-byte message blocks.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_md5_transform)`. The public signature is declared in `md5.h` as `void ppc_md5_transform(u32 *state, const u8 *data, size_t nblocks)`. Round macros `R_00_15`, `R_16_31`, `R_32_47`, and `R_48_63` implement the four MD5 boolean/rotation phases.

## Control Flow
The function saves GPRs, loads the four hash words, sets the CTR from `nblocks`, and enters `ppc_md5_main`. Each block runs the 64 MD5 operations unrolled in pairs, with endian-aware input loads. At the end of each block it adds the working hash values back into the state buffer, advances the input pointer where required by endian mode, decrements CTR, and loops.

## State and Persistence
The caller's 128-bit MD5 state is updated in place. No global state is used. Stack-saved registers are restored but message/hash working values are not explicitly wiped beyond normal register reuse.

## Dependencies and Integration Points
Depends on PowerPC assembly helper macros from `<asm/ppc_asm.h>`, `<asm/asm-offsets.h>`, and `<asm/asm-compat.h>`. The generic MD5 library calls it through `md5_blocks` in `md5.h`.

## Risks
MD5 is cryptographically broken for collision resistance, so this optimization is only appropriate where MD5 remains protocol-compatible but not security-critical. Endian load behavior differs between BE and LE. The transform assumes complete 64-byte blocks.

## Test Signals
MD5 digest known-answer tests, multi-block tests, and BE/LE comparisons against the generic C transform validate behavior. Boundary tests should pass `nblocks` of 1 and larger values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5.h

## Purpose
Provides the PowerPC MD5 architecture hook that routes block compression to `ppc_md5_transform`.

## Important APIs, Types, and Functions
Declares `void ppc_md5_transform(u32 *state, const u8 *data, size_t nblocks)` and defines `static void md5_blocks(struct md5_block_state *state, const u8 *data, size_t nblocks)`.

## Control Flow
`md5_blocks` is a thin wrapper that passes `state->h`, data, and block count directly to assembly. It does no feature gating or fallback selection.

## State and Persistence
The MD5 state object is mutated in place by the assembly transform. The header defines no persistent global state.

## Dependencies and Integration Points
Integrated by the generic MD5 implementation when building for PowerPC with this arch header available. It depends on common MD5 block-state definitions being in scope.

## Risks
There is no runtime CPU feature gating; the assembly must be valid for the configured PowerPC target. MD5 security limitations apply at the algorithm level.

## Test Signals
Generic MD5 self-tests should exercise this wrapper. Link tests should verify `ppc_md5_transform` is provided whenever this header is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/poly1305-p10le_64.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/poly1305-p10le_64.S

## Purpose
Implements Power10 little-endian accelerated Poly1305 using vector/VSX and scalar 64-bit arithmetic. It provides a four-block vector path, a scalar 64-bit block path, and final tag emission.

## Important APIs, Types, and Functions
Exports `poly1305_p10le_4blocks`, `poly1305_64s`, and `poly1305_emit_64`. Local helpers include `do_mul`, `Poly1305_init_64`, `Poly1305_mult`, `Carry_reduction`, `poly1305_setup_r`, `do_poly1305_init`, and data symbol `RMASK` containing clamp masks and permutation constants.

## Control Flow
`poly1305_p10le_4blocks` rejects inputs under 64 bytes, saves a large register frame, initializes/clamps r, precomputes powers of r, converts the accumulator into 26-bit vector limbs, loads four message blocks, and loops over 64-byte groups using `mul_odd`, `mul_even`, and carry reduction. It collapses the vector accumulator back into state words before return. `poly1305_64s` handles 16-byte blocks in a loop using 64-bit multiplication helpers and a caller-supplied highbit, updating the accumulator in state. `poly1305_emit_64` conditionally reduces h, adds the nonce/s part, and stores the 16-byte digest.

## State and Persistence
The caller's `poly1305_block_state` or `poly1305_state` is updated in place. Key material and accumulator values live in registers and stack save areas during execution; vector paths restore registers before return. No global mutable state is used.

## Dependencies and Integration Points
Declared by `poly1305.h` and called inside a VSX-enabled region on CPUs with `CPU_FTR_ARCH_31`. Depends on Power10 vector integer multiply instructions such as `vmsumudm` and VSX register save/restore support.

## Risks
Poly1305 correctness is sensitive to clamping, highbit handling for final partial blocks, carry reduction modulo 2^130-5, and endian layout. The four-block path and 64-bit path must agree on state representation. The assembly assumes little-endian Power10.

## Test Signals
RFC 8439 Poly1305 vectors, random comparison against generic Poly1305, lengths around 0, 16, 64, 80, and final partial blocks are important. Tag emission tests should include accumulator values near the modulus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/poly1305-p10le_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/poly1305.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/poly1305.h

## Purpose
Provides the PowerPC Poly1305 architecture hook, selecting Power10 accelerated block and emit routines when available.

## Important APIs, Types, and Functions
Declares `poly1305_p10le_4blocks`, `poly1305_64s`, and `poly1305_emit_64`. Defines `poly1305_block_init`, `poly1305_blocks`, `poly1305_emit`, `poly1305_mod_init_arch`, and a `have_p10` static key.

## Control Flow
Module init enables `have_p10` on `CPU_FTR_ARCH_31`. `poly1305_block_init` either calls generic init or initializes h to zero and stores raw r key halves for assembly. `poly1305_blocks` falls back generically if acceleration is unavailable; otherwise it enters VSX, processes a large four-block multiple through `poly1305_p10le_4blocks`, then processes remaining whole blocks through `poly1305_64s`, and exits VSX. `poly1305_emit` selects generic or accelerated final tag output.

## State and Persistence
The static key persists CPU capability. The block state stores accumulator h and key material. VSX use disables preemption while accelerated blocks are running.

## Dependencies and Integration Points
Depends on PowerPC VSX switching, CPU feature checks, Linux unaligned access helpers, and generic Poly1305 functions. It is consumed by the generic Poly1305 library via arch hook names.

## Risks
This header does not call `crypto_simd_usable()` before entering VSX, so its callers and broader crypto context must ensure use is allowed. The transition from four-block vector processing to 64-bit block processing relies on both assembly paths sharing state layout. Partial-block handling remains outside this loop except for generic higher-level buffering.

## Test Signals
Poly1305 known-answer and random differential tests should run with acceleration on/off. Tests must include messages that leave 0, 1, 2, and 3 full blocks after a four-block multiple.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-powerpc-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-powerpc-asm.S

## Purpose
Implements the standard PowerPC SHA-1 compression function for non-SPE builds, processing one 64-byte block per call.

## Important APIs, Types, and Functions
Exports `_GLOBAL(powerpc_sha_transform)`, declared in `sha1.h`. Macros `STEPD0_*`, `STEPD1*`, `STEPD2_UPDATE`, `STEP0LD4`, `STEPUP4`, and `STEPUP20` unroll SHA-1 rounds and message schedule generation.

## Control Flow
The function saves registers, loads A through E from the state, loads initial message words with endian-aware `LWZ`, runs the 80 SHA-1 rounds in four constant phases, updates the message schedule in a 16-word rolling window, adds the resulting working values back into the input state, stores state, restores registers, and returns.

## State and Persistence
Mutates the 160-bit SHA-1 state in place for exactly one block. It uses stack only for register saves and has no global state.

## Dependencies and Integration Points
Depends on PowerPC assembly support headers. `sha1.h` loops over input blocks and calls this transform for each block when `CONFIG_SPE` is not enabled.

## Risks
SHA-1 is collision-broken, so algorithm use is security-sensitive outside compatibility contexts. Endian conversion must match SHA-1 big-endian message word semantics. The transform handles only one block per call.

## Test Signals
SHA-1 digest known-answer tests, multi-block wrapper tests, and BE/LE comparison against the generic implementation validate the transform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-powerpc-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-spe-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-spe-asm.S

## Purpose
Implements an SPE SIMD optimized SHA-1 compression routine for PowerPC, processing multiple 64-byte blocks per call.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_spe_sha1_transform)`. Uses constants table `PPC_SPE_SHA1_K` and macros `R_00_15`, `R_16_19`, `R_20_39`, `R_40_59`, and `R_60_79` to process two 32-bit rounds per 64-bit SPE register where possible.

## Control Flow
The function saves nonvolatile GPR/SPE state, loads the five hash words and constants pointer, sets CTR from block count, and enters `ppc_spe_sha1_main`. For each block, it loads message words with endian handling, runs the 80 SHA-1 rounds with rolling message schedule updates, advances the input pointer per endian mode, adds working values back to state, and loops until CTR reaches zero.

## State and Persistence
Updates the caller's SHA-1 block state in place. `FINALIZE` restores registers and wipes stack slots that held saved SPE data. No global mutable state is used.

## Dependencies and Integration Points
Called by `sha1.h` when `CONFIG_SPE` is enabled, inside `enable_kernel_spe()`/`disable_kernel_spe()` regions. Depends on Linux PowerPC SPE assembler macros and the SHA-1 constants table in this file.

## Risks
The preemption-disabled caller chunks work to bound latency; bypassing that wrapper could create long critical sections. Endian-specific input pointer increments differ. SHA-1's algorithm-level collision weakness remains.

## Test Signals
SHA-1 known-answer tests with block counts above one validate loop behavior. SPE builds should test chunking boundaries from `sha1.h` near 2048 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1-spe-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1.h

## Purpose
Selects the PowerPC SHA-1 architecture implementation, either SPE multi-block compression under `CONFIG_SPE` or the regular PowerPC one-block transform otherwise.

## Important APIs, Types, and Functions
For SPE, declares `ppc_spe_sha1_transform`, defines `MAX_BYTES 2048`, `spe_begin`, `spe_end`, and multi-block `sha1_blocks`. For non-SPE, declares `powerpc_sha_transform` and defines a simple per-block `sha1_blocks` loop.

## Control Flow
In SPE builds, `sha1_blocks` chunks work into at most `MAX_BYTES / SHA1_BLOCK_SIZE` blocks per preemption-disabled SPE section, calls assembly, advances pointers, and repeats. In non-SPE builds, it calls `powerpc_sha_transform` once per block until all blocks are processed.

## State and Persistence
The SHA-1 state is mutated by the selected assembly transform. SPE begin/end temporarily disable preemption and enable kernel SPE state; no persistent globals are used.

## Dependencies and Integration Points
Includes PowerPC SPE switching and preemption headers. It is wired into the generic SHA-1 library by defining the architecture `sha1_blocks` helper.

## Risks
The SPE chunk size is chosen to limit preemption-off latency; changing it affects scheduler latency. Non-SPE one-block looping has more call overhead but simpler state handling. SHA-1 is not collision-resistant.

## Test Signals
Digest tests on SPE and non-SPE builds, plus large-buffer tests that cross the 2048-byte chunk boundary, validate both wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha256-spe-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha256-spe-asm.S

## Purpose
Implements an SPE optimized SHA-256 compression routine for PowerPC, processing multiple 64-byte blocks per call.

## Important APIs, Types, and Functions
Exports `_GLOBAL(ppc_spe_sha256_transform)`. Uses `PPC_SPE_SHA256_K` constants and macros `R_LOAD_W` and `R_CALC_W` to unroll initial message loads and calculated schedule rounds.

## Control Flow
The function saves nonvolatile SPE/GPR registers, loads the eight SHA-256 state words, sets CTR from block count, and enters `ppc_spe_sha256_main`. For each block it loads the first 16 message words, runs rounds using SHA-256 sigma, choice, and majority operations, loops through schedule calculation in 16-round groups, advances the input pointer, adds working variables back to the state words, and repeats until all blocks are processed.

## State and Persistence
Mutates the caller's 256-bit SHA-256 state in place. The finalization macro restores saved registers and zeros stack slots that may contain sensitive context from shared code paths. No global state is mutated.

## Dependencies and Integration Points
Declared and called by `sha256.h` inside SPE-enabled regions. Depends on PowerPC SPE instruction support and Linux assembler macros.

## Risks
Long preemption-disabled sections are controlled by the header wrapper, not this assembly. Endian handling must preserve SHA-256 big-endian message semantics. Round constants and calculated schedule are high-value correctness areas.

## Test Signals
SHA-256 known-answer tests and random differential tests against generic SHA-256 are needed. SPE wrapper chunk boundary tests near 1024 bytes verify multi-call state continuity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha256-spe-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha256.h

## Purpose
Provides the PowerPC SPE SHA-256 architecture hook and bounds how much data is processed per preemption-disabled SPE section.

## Important APIs, Types, and Functions
Defines `MAX_BYTES 1024`, declares `ppc_spe_sha256_transform`, and implements `spe_begin`, `spe_end`, and `sha256_blocks`.

## Control Flow
`sha256_blocks` loops while blocks remain, selecting `unit = min(nblocks, MAX_BYTES / SHA256_BLOCK_SIZE)`. It enables kernel SPE with preemption disabled, calls assembly for `unit` blocks, disables SPE, advances `data`, subtracts processed blocks, and repeats.

## State and Persistence
The SHA-256 state is mutated in place by the assembly transform. SPE use is transient and preemption state is restored after each chunk. No static CPU feature key is used here.

## Dependencies and Integration Points
Depends on PowerPC SPE switch APIs and generic SHA-256 block-state definitions. It integrates with the common SHA-256 implementation through the arch `sha256_blocks` hook.

## Risks
Only SPE builds should select this header. The latency calculation in comments assumes rough operation counts and e500-class issue behavior; changes to chunk size should be conservative.

## Test Signals
SHA-256 self-tests with messages crossing 1024-byte boundaries and comparisons to generic SHA-256 validate chunking and state continuity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/aes-riscv64-zvkned.S -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/aes-riscv64-zvkned.S

## Purpose
Implements RISC-V vector AES single-block encrypt and decrypt using the Zvkned vector AES extension.

## Important APIs, Types, and Functions
Exports `aes_encrypt_zvkned` and `aes_decrypt_zvkned`. Macros `__aes_crypt_zvkned` and `aes_crypt_zvkned` wrap shared AES macro code from `../../arch/riscv/crypto/aes-macros.S` and select 128-, 192-, or 256-bit paths based on key length.

## Control Flow
Each function loads a 16-byte block into vector register `v16` with `vle32.v`, invokes `aes_begin` and `aes_crypt` from the included macro library, stores the result with `vse32.v`, and returns. Label targets `128:` and `192:` implement key-size dispatch while the fall-through path handles 256-bit keys.

## State and Persistence
Only caller-provided output is written. Vector state is used transiently inside a kernel vector region managed by the C wrapper. No globals are mutated.

## Dependencies and Integration Points
Requires RV64I, RISC-V V with VLEN at least 128, and Zvkned. Declared by `riscv/aes.h`, which performs CPU feature and SIMD gating and provides generic fallback.

## Risks
The assembly expects standard round keys, including for decryption; this differs from generic fallback decryption, which uses inverse keys. Vector length assumptions are enforced by the wrapper, so direct calls without gating would be unsafe.

## Test Signals
AES encrypt/decrypt known-answer tests for 128/192/256-bit keys under Zvkned and fallback paths. Tests should verify decryption uses normal round keys in the accelerated path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/aes-riscv64-zvkned.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/aes.h -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/aes.h

## Purpose
Provides RISC-V AES architecture hooks that use Zvkned vector AES when available and generic AES otherwise.

## Important APIs, Types, and Functions
Declares `aes_encrypt_zvkned` and `aes_decrypt_zvkned`. Defines `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, `aes_mod_init_arch`, and static key `have_zvkned`.

## Control Flow
Key preparation always calls `aes_expandkey_generic` and produces both normal and inverse schedules when requested. Encrypt/decrypt check `have_zvkned` and `may_use_simd()`. Accelerated calls enter `kernel_vector_begin()`, call the Zvkned assembly with normal round keys and key length, then call `kernel_vector_end()`. Fallback calls generic AES; decryption fallback uses inverse round keys.

## State and Persistence
The static branch persists whether Zvkned and sufficient vector length were detected at init. Key objects store generic-format round keys. No vector state escapes the begin/end region.

## Dependencies and Integration Points
Depends on RISC-V SIMD/vector headers, generic AES expansion and fallback routines, and the assembly file in this directory. `aes_mod_init_arch` checks `riscv_isa_extension_available(NULL, ZVKNED)` and `riscv_vector_vlen() >= 128`.

## Risks
The accelerated and fallback decrypt paths use different key schedules, so key preparation must keep both schedules available. `may_use_simd()` must be respected for contexts that cannot use vector state.

## Test Signals
AES known-answer tests with vector enabled/disabled and decryption tests that intentionally exercise both accelerated normal-round-key use and generic inverse-key fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha-riscv64-zvkb.S -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha-riscv64-zvkb.S

## Purpose
Implements RISC-V vector ChaCha encryption/decryption using the Zvkb vector crypto bit-manipulation extension.

## Important APIs, Types, and Functions
Exports `chacha_zvkb(struct chacha_state *state, const u8 *in, u8 *out, size_t nblocks, int nrounds)`. Macro `chacha_round` implements one quarter-round pattern over four vectorized columns/diagonals.

## Control Flow
The function saves callee-saved scalar registers, loads the 16-word ChaCha state into scalar registers, then loops while blocks remain. Each iteration sets `vl` to the number of blocks the vector unit can handle, broadcasts constants/key/nonce into vector registers, creates per-lane counters with `vid.v`, loads input with strided segment loads, runs double-rounds until `nrounds` is consumed, adds the original state, xors with input, stores output with strided segment stores, advances pointers and block count, and repeats. It writes the updated counter back to `state->x[12]`.

## State and Persistence
The input/output buffers are transformed in place or out of place according to caller pointers. The ChaCha counter in the state is persisted after all full blocks. Saved registers are restored before return.

## Dependencies and Integration Points
Requires RV64I, V with VLEN at least 128, and Zvkb. Called by `riscv/chacha.h`, which handles vector begin/end and tail buffering.

## Risks
The function requires `nblocks` to be nonzero and whole-block based. Counter overflow behavior follows a 32-bit `state->x[12]` convention. Strided segment loads/stores rely on correct vector length and block layout.

## Test Signals
ChaCha20 known-answer tests for multiple block counts and non-default round counts. Header-level tests should verify tail handling and final counter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha-riscv64-zvkb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha.h -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha.h

## Purpose
Provides RISC-V ChaCha architecture hooks using Zvkb vector acceleration for full blocks and generic ChaCha fallback for unsupported or non-SIMD contexts.

## Important APIs, Types, and Functions
Declares `chacha_zvkb`, defines `chacha_crypt_arch`, `chacha_mod_init_arch`, and maps `hchacha_block_arch` to `hchacha_block_generic`. Maintains static key `use_zvkb`.

## Control Flow
`chacha_crypt_arch` computes full-block and tail-byte counts. If Zvkb is unavailable or SIMD is unusable, it calls generic ChaCha for the entire buffer. Otherwise it begins a vector region, calls `chacha_zvkb` for full blocks, then copies any tail into a 64-byte stack buffer, encrypts one block in place with `chacha_zvkb`, copies only the requested tail bytes to output, and ends the vector region.

## State and Persistence
The ChaCha state counter is updated by the assembly for full blocks and for the synthetic one-block tail. The stack tail buffer is transient but not explicitly zeroed. The static key records CPU capability after init.

## Dependencies and Integration Points
Depends on RISC-V vector/SIMD headers, `crypto_simd_usable()`, and generic ChaCha functions. Module init checks `ZVKB` and vector length at least 128.

## Risks
Tail processing encrypts a stack buffer containing copied plaintext bytes and zeros/uninitialized bytes for the rest depending on stack contents; only the requested output bytes are copied, but explicit zeroing could reduce residual data. State counter update for tail consumes a whole block, which is correct for stream position.

## Test Signals
Known-answer tests for 0, 1, 63, 64, 65, and multi-block byte counts validate full-block and tail paths. Tests should check the updated counter after tail-only calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/gf128hash.h -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/gf128hash.h

## Purpose
Provides RISC-V GHASH architecture hooks using the Zvkg vector GCM/GMAC extension when available.

## Important APIs, Types, and Functions
Declares `ghash_zvkg`. Defines `ghash_preparekey_arch`, `ghash_blocks_arch`, `gf128hash_mod_init_arch`, and static key `have_zvkg`.

## Control Flow
Key preparation stores the key both as generic POLYVAL form and raw GHASH bytes for Zvkg. Block processing checks `have_zvkg` and `may_use_simd()`. Accelerated processing converts the internal accumulator to GHASH byte order, enters a vector region, calls `ghash_zvkg`, exits, converts back to POLYVAL, and zeros the temporary. Fallback calls `ghash_blocks_generic`.

## State and Persistence
The `struct ghash_key` persists generic and raw key forms. The accumulator is mutated in place after conversion back. The temporary GHASH accumulator is explicitly zeroed.

## Dependencies and Integration Points
Depends on RISC-V vector/SIMD headers, generic GHASH/POLYVAL conversion helpers, and `ghash-riscv64-zvkg.S`. Module init checks `ZVKG` plus VLEN at least 128.

## Risks
No `ghash_mul_arch` single-block hook is defined here, so callers use block processing or generic multiply depending on higher-level selection. Conversion between POLYVAL and GHASH representations is correctness-critical.

## Test Signals
GHASH and AES-GCM test vectors with Zvkg enabled/disabled, plus randomized generic-vs-arch differential tests over several block counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/gf128hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/ghash-riscv64-zvkg.S -->
# sources/distributed-fs/ceph-client/lib/crypto/riscv/ghash-riscv64-zvkg.S

## Purpose
Implements RISC-V vector GHASH block processing using the Zvkg `vghsh.vv` instruction.

## Important APIs, Types, and Functions
Exports `ghash_zvkg(u8 accumulator[16], const u8 key[16], const u8 *data, size_t nblocks)`. Register aliases name `ACCUMULATOR`, `KEY`, `DATA`, and `NBLOCKS`.

## Control Flow
The function sets vector length to four 32-bit lanes, loads accumulator and key into vector registers, then loops over data blocks. For each 16-byte block it loads data into `v3`, applies `vghsh.vv v1, v2, v3`, advances the data pointer, decrements block count, and repeats until zero. It stores the final accumulator and returns.

## State and Persistence
Only the accumulator buffer is updated in place. Key and data are read-only. No stack or global state is used.

## Dependencies and Integration Points
Requires RV64I, V with VLEN at least 128, and Zvkg. Called by `riscv/gf128hash.h` after accumulator/key representation setup and vector begin.

## Risks
The function contract says `nblocks` must be nonzero; callers must avoid zero-block calls. All representation conversion is outside this file, so mismatched byte order in the wrapper would make this correct primitive produce incorrect GHASH results.

## Test Signals
GHASH known-answer tests for one and many blocks, plus zero-block caller tests at wrapper level to ensure the assembly is not invoked with `nblocks == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/riscv/ghash-riscv64-zvkg.S -->
