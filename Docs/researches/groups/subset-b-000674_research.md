# subset-b-000674 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-core.S -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-core.S

### Purpose
Implements ARM64 NEON bit-sliced AES block transforms for the kernel crypto API glue in `aes-neonbs-glue.c`. It provides constant-time AES key conversion plus ECB, CBC decrypt, CTR, and XTS encrypt/decrypt workers that process up to eight 16-byte blocks per inner call.

### Important APIs, Types, And Functions
Exports `aesbs_convert_key`, `aesbs_ecb_encrypt`, `aesbs_ecb_decrypt`, `aesbs_cbc_decrypt`, `aesbs_ctr_encrypt`, `aesbs_xts_encrypt`, and `aesbs_xts_decrypt`. Local helpers include `aesbs_encrypt8`, `aesbs_decrypt8`, `__xts_crypt8`, the bit-slice transpose macros, S-box/inverse S-box macros, round-key load macros, CTR increment, XTS tweak multiplication, and constant permutation tables `M0`, `SR`, `ISR`, and variants.

### Control Flow
Callers pass normal AES round keys, converted bit-sliced keys, block counts, IV/counter/tweak buffers, and round count. ECB loads up to eight blocks, invokes the encrypt/decrypt eight-block core, and stores only the blocks requested. CBC decrypt decrypts batches then XORs with the previous ciphertext/IV and persists the final IV. CTR builds counters, encrypts them, XORs with input, and carries partial-byte masking in the caller. XTS applies tweak whitening before and after the AES core and advances tweaks in GF(2^128).

### State, Persistence, And Dependencies
The file keeps no static writable state. Persistent effects are writes to output buffers and IV/counter/tweak buffers supplied by the C glue. It depends on `linux/linkage.h`, `linux/cfi_types.h`, `asm/assembler.h`, NEON/SIMD register conventions, and the C glue's `scoped_ksimd()` protection.

### Integration Points
The symbols are declared by `aes-neonbs-glue.c` and registered as Linux skcipher algorithms. The code relies on the generic AES key expansion and skcipher walk code to provide block-aligned chunks, tail handling, and safe SIMD entry/exit.

### Risks
The main risks are off-by-one block masks in the up-to-eight-block paths, IV/counter/tweak update mistakes across walk boundaries, endian or permutation-table drift, CFI/linkage mismatch for typed symbols, and using NEON without the caller disabling preemption or saving kernel SIMD state.

### Test Signals
Use `tcrypt`/crypto selftests for AES ECB, CBC decrypt, CTR, and XTS with 128/192/256-bit keys; compare against generic AES for chunk boundaries from 1 to 8 blocks and scatterlist splits; run KASAN/KMSAN-style tests around short tails and overlapping buffers; cross-build ARM64 with CFI enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-glue.c -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-glue.c

### Purpose
Registers bit-sliced NEON AES skcipher implementations for ECB, CBC, CTR, and XTS and adapts Linux scatterlist requests to the assembly workers in `aes-neonbs-core.S`.

### Important APIs, Types, And Functions
Context types are `struct aesbs_ctx`, `struct aesbs_cbc_ctr_ctx`, and `struct aesbs_xts_ctx`. Important functions are `aesbs_setkey`, `aesbs_cbc_ctr_setkey`, `aesbs_xts_setkey`, `__ecb_crypt`, `cbc_encrypt`, `cbc_decrypt`, `ctr_encrypt`, `__xts_crypt`, `xts_encrypt`, `xts_decrypt`, `aes_init`, and `aes_exit`. Assembly entry points include `aesbs_convert_key`, `aesbs_ecb_encrypt`, `aesbs_ecb_decrypt`, `aesbs_cbc_decrypt`, `aesbs_ctr_encrypt`, and XTS/CTR variants.

### Control Flow
Setkey expands the AES key with generic helpers and converts encrypt/decrypt round keys into bit-sliced form. ECB/CBC/CTR/XTS requests walk virtual scatterlists, choose whole-block work for assembly, and handle partial CTR/XTS tails in C where necessary. CBC encryption uses the generic CBC path while CBC decrypt uses the parallel assembly path. Module init registers all skcipher algorithms through `simd_register_skciphers_compat()`.

### State, Persistence, And Dependencies
Per-transform state is round keys and round count in crypto contexts; per-request state is the skcipher walk, IV, and temporary tail buffers. There is no filesystem persistence. Dependencies include `asm/neon.h`, `asm/simd.h`, AES/CTR/XTS helpers, `crypto/internal/simd.h`, skcipher/scatterwalk APIs, and module registration.

### Integration Points
This is the public kernel crypto API surface for `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, and `xts(aes)` on ARM64 NEON. Ceph depends on these indirectly through kernel crypto users such as network, disk, and protocol authentication paths.

### Risks
Risks include incorrect fallback or tail behavior for non-block-size CTR lengths, XTS ciphertext stealing mistakes, IV persistence across scatterlist segments, invalid key length handling, and accidentally calling assembly when SIMD is unavailable.

### Test Signals
Run crypto manager selftests and `tcrypt` vectors for all registered modes, including scatterlist fragmentation, in-place encryption, odd CTR lengths, XTS data-unit sizes around 16 bytes, invalid key lengths, and module load/unload on ARM64 systems with NEON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-core.S -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-core.S

### Purpose
Provides PMULL-accelerated GHASH and integrated AES-GCM encryption/decryption assembly for ARMv8 Crypto Extensions.

### Important APIs, Types, And Functions
Exports `pmull_ghash_update_p64`, `pmull_gcm_encrypt`, and `pmull_gcm_decrypt`. Local helpers include `pmull_gcm_ghash_4x`, `pmull_gcm_enc_4x`, `load_round_keys`, AES round macros, PMULL reduction macros, and `.Lpermute_table` for short-block and tag comparisons.

### Control Flow
`pmull_ghash_update_p64` consumes full GHASH blocks, optionally combining a buffered head block, and stores the updated digest. `pmull_gcm_encrypt` and `pmull_gcm_decrypt` share `pmull_gcm_do_crypt`: load AES keys and GHASH powers, process four-block rounds, use special paths for 1-63 byte final chunks, hash ciphertext on encrypt or input ciphertext on decrypt, and optionally finalize with length block plus tag generation/comparison.

### State, Persistence, And Dependencies
The assembly updates caller-provided digest, counter, destination, and tag buffers only. It depends on ARM64 AES instructions, PMULL, NEON registers, `asm/assembler.h`, and C glue that supplies key schedules, GHASH tables, safe buffers for overlapping tail loads, and `scoped_ksimd()`.

### Integration Points
Used by `ghash-ce-glue.c` for `gcm(aes)` and `rfc4106(gcm(aes))`. The assembly expects AES round-count conventions from `struct aes_enckey` and GHASH reflected key tables produced by the glue.

### Risks
Short input paths intentionally use overlapping loads and may read before the first input pointer unless the caller provides a safe bounce buffer. Other risks are authsize masking errors, counter endian drift, tag compare mistakes, PMULL reduction bugs, and register-clobber ABI issues.

### Test Signals
Run AES-GCM and RFC4106 vectors with all supported tag sizes, AAD-only cases, zero-length plaintext, 1-63 byte tails, fragmented scatterlists, in-place decrypt failure paths, and KASAN guard-page tests around final chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-glue.c -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-glue.c

### Purpose
Registers AES-GCM and RFC4106 AES-GCM AEAD algorithms using ARMv8 AES/PMULL assembly and handles scatterlist, AAD, tag, and key-table setup.

### Important APIs, Types, And Functions
Defines `struct arm_ghash_key` and `struct gcm_aes_ctx`. Key functions are `ghash_reflect`, `gcm_aes_setkey`, `gcm_update_mac`, `gcm_calculate_auth_mac`, `gcm_encrypt`, `gcm_decrypt`, `rfc4106_setkey`, `rfc4106_encrypt`, `rfc4106_decrypt`, and module init/exit. It calls `pmull_ghash_update_p64`, `pmull_gcm_encrypt`, and `pmull_gcm_decrypt`.

### Control Flow
Setkey prepares AES encryption keys, computes `H = AES_K(0)`, reflects it, and derives `H^1..H^4`. AAD is walked and padded into GHASH. Encrypt/decrypt initialize IV counter block 2, walk payload scatterlists, bounce short final chunks into a 16-byte buffer, call assembly for each segment, and append or compare the authentication tag. RFC4106 prepends the stored nonce and validates IPsec AAD shape.

### State, Persistence, And Dependencies
Transform state contains AES round keys, RFC4106 nonce, and GHASH powers. Request state includes digest, IV, length block, tag buffer, and skcipher walk state. Dependencies include AES, GHASH, GCM, gf128 multiplication, scatterwalk, AEAD/skcipher internals, CPU feature checks, unaligned helpers, and `asm/simd.h`.

### Integration Points
Exports high-priority `gcm(aes)` and `rfc4106(gcm(aes))` drivers to the kernel crypto API when ASIMD and PMULL are present. Ceph or lower network/storage layers can consume these through standard AEAD allocation.

### Risks
AAD buffering and partial payload handling are the highest-risk areas. Incorrect authsize validation, nonce length assumptions, IV counter reuse, failed tag comparison propagation, or missing CPU feature gates would cause security or crash bugs.

### Test Signals
Run crypto selftests for GCM/RFC4106, NIST vectors, malformed tags, all legal auth sizes, AAD lengths around 0/15/16/17/0xff00, fragmented source/destination lists, and CPU-feature-negative module init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-asm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-asm.h

### Purpose
Supplies reusable ARMv8 SM4 Crypto Extension assembly macros for one, two, four, and eight block transforms.

### Important APIs, Types, And Functions
Macro surface includes `SM4_PREPARE`, `SM4_CRYPT_BLK_BE`, `SM4_CRYPT_BLK`, `SM4_CRYPT_BLK2_BE`, `SM4_CRYPT_BLK2`, `SM4_CRYPT_BLK4_BE`, `SM4_CRYPT_BLK4`, `SM4_CRYPT_BLK8_BE`, and `SM4_CRYPT_BLK8`. The macros assume the including file defines the `sm4e` instruction macro and uses v24-v31 for expanded round keys.

### Control Flow
Including assembly files call `SM4_PREPARE(ptr)` to load eight 128-bit round-key vectors, then invoke the block macros inside mode-specific loops. The macros perform required endian conversion, issue the SM4 round instruction for every round-key vector, then reverse the final word order into the kernel's block layout.

### State, Persistence, And Dependencies
No standalone state or object code is generated. The macros only affect registers and caller buffers when expanded by assembly sources such as SM4 CE core, CCM, and GCM. Dependencies are ARMv8 SM4 Crypto Extension instruction encodings and consistent vector register allocation.

### Integration Points
Included by `sm4-ce-core.S`, `sm4-ce-ccm-core.S`, and `sm4-ce-gcm-core.S` to keep SM4 block logic consistent across modes.

### Risks
Macro register assumptions are global and fragile; a caller reusing v24-v31 or omitting endian preparation can silently corrupt output. Any SM4 round-order bug affects every CE mode.

### Test Signals
Cross-build all including assembly files; run SM4 ECB/CBC/CTR/XTS/CCM/GCM known-answer tests; disassemble to confirm expected `sm4e` instruction encodings and no accidental register overlap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-core.S -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-core.S

### Purpose
Implements ARMv8 SM4 Crypto Extension assembly for CCM mode payload encryption/decryption, CBC-MAC updates, and final tag encryption.

### Important APIs, Types, And Functions
Exports `sm4_ce_cbcmac_update`, `sm4_ce_ccm_final`, `sm4_ce_ccm_enc`, and `sm4_ce_ccm_dec`. Important macros are `inc_le128`, `SM4_PREPARE`, `SM4_CRYPT_BLK`, and `SM4_CRYPT_BLK2`; `RMAC` holds the CBC-MAC accumulator.

### Control Flow
`sm4_ce_cbcmac_update` encrypts the current MAC and XORs full AAD/message blocks. `sm4_ce_ccm_enc` advances CTR values, encrypts plaintext with CTR keystream, and folds plaintext into the MAC. `sm4_ce_ccm_dec` decrypts ciphertext then folds recovered plaintext into the MAC. Tail loops operate byte-by-byte, updating the saved MAC buffer. `sm4_ce_ccm_final` encrypts both MAC and CTR0 and XORs them to produce the tag.

### State, Persistence, And Dependencies
State is caller-owned: round keys, CTR/IV buffer, MAC buffer, source, and destination. Full-block paths update CTR and MAC; byte-tail paths write partial MAC bytes in place. Dependencies include `sm4-ce-asm.h`, `asm/assembler.h`, linkage/CFI types, and SIMD protection by C glue.

### Integration Points
Called only by `sm4-ce-ccm-glue.c`, which formats CCM B0/AAD, validates auth size, and walks scatterlists.

### Risks
Tail MAC byte writes, CTR carry/endian behavior, and encrypt-vs-decrypt MAC input selection are subtle. A mismatch with `ccm_format_input()` or walk tail decisions can produce invalid tags or plaintext corruption.

### Test Signals
Run RFC8998/NIST CCM vectors for SM4, AAD-only and payload-only requests, message lengths crossing 15/16/17/63/64 bytes, odd auth sizes rejection, decrypt tag failure, and segmented scatterlists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-glue.c -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-glue.c

### Purpose
Registers `ccm(sm4)` AEAD using ARMv8 SM4 Crypto Extensions and coordinates CCM formatting, AAD authentication, payload walking, and tag handling.

### Important APIs, Types, And Functions
Key functions are `ccm_setkey`, `ccm_setauthsize`, `ccm_format_input`, `ccm_calculate_auth_mac`, `ccm_crypt`, `ccm_encrypt`, `ccm_decrypt`, `sm4_ce_ccm_init`, and `sm4_ce_ccm_exit`. Assembly dependencies are `sm4_ce_expand_key`, `sm4_ce_crypt_block`, `sm4_ce_cbcmac_update`, `sm4_ce_ccm_enc`, `sm4_ce_ccm_dec`, and `sm4_ce_ccm_final`.

### Control Flow
Setkey validates the 128-bit SM4 key and expands CE round keys. Encrypt/decrypt call `ccm_format_input()` to build B0 and encode message length, then initialize a skcipher walk. `ccm_crypt()` preserves CTR0, increments the working counter, optionally authenticates AAD, passes whole walk chunks to assembly while retaining tails for the final segment, finalizes the MAC, and appends or checks the tag.

### State, Persistence, And Dependencies
Per-transform state is `struct sm4_ctx`; per-request state is MAC, CTR0, walk IV, and scatterlist cursor. No persistent storage exists. Dependencies include AEAD/skcipher internals, scatterwalk, `crypto/sm4.h`, `crypto_xor`, and `asm/simd.h`.

### Integration Points
Provides a `cra_priority` 400 `ccm-sm4-ce` AEAD driver gated by `module_cpu_feature_match(SM4)`.

### Risks
CCM has strict length and auth-size rules: bad `L` validation, assoclen encoding, final tail treatment, or non-constant tag comparison would be security-sensitive. All assembly calls require a valid kernel SIMD context.

### Test Signals
Exercise auth sizes 4 through 16, invalid odd/short auth sizes, IV `L` values 2..8 and invalid/out-of-range payload lengths, AAD length transitions at 0xff00, scatterlist fragmentation, and decrypt failures returning `-EBADMSG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-core.S -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-core.S

### Purpose
Implements the single-block SM4 cipher primitive using ARMv8 Crypto Extension `sm4e` instructions for the legacy `crypto_alg` cipher interface.

### Important APIs, Types, And Functions
Exports `sm4_ce_do_crypt(const u32 *rk, void *out, const void *in)`. It defines a local `sm4e` instruction macro and loads eight round-key vectors from the provided key schedule.

### Control Flow
The function loads one 16-byte input block, applies little-endian byte reversal when needed, loads the full key schedule in two vector batches, runs eight `sm4e` vector rounds, reverses the final word order, converts endian back on little-endian builds, stores the output, and returns.

### State, Persistence, And Dependencies
There is no internal state. The only effects are reading the caller's round-key and input buffers and writing the output block. Dependencies are `linux/linkage.h`, `asm/assembler.h`, ARM64 SM4 instruction support, and glue-side SIMD availability checks.

### Integration Points
Called by `sm4-ce-cipher-glue.c` for synchronous single-block `sm4` encryption and decryption. It uses the generic SM4 expanded keys produced by `sm4_expandkey()`.

### Risks
Because this is a minimal primitive, risks concentrate in endian conversion, key schedule ordering for decrypt versus encrypt, and executing the instruction on CPUs without SM4 support.

### Test Signals
Run SM4 ECB known-answer vectors through both `sm4` and `sm4-ce` driver names, compare encrypt/decrypt against generic `sm4_crypt_block`, and verify module loading only occurs with the SM4 CPU feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-glue.c -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-glue.c

### Purpose
Registers the ARMv8 Crypto Extension single-block SM4 cipher driver and selects assembly or generic fallback based on SIMD availability.

### Important APIs, Types, And Functions
Defines `sm4_ce_setkey`, `sm4_ce_encrypt`, `sm4_ce_decrypt`, `sm4_ce_alg`, `sm4_ce_mod_init`, and `sm4_ce_mod_fini`. It declares assembly `sm4_ce_do_crypt`.

### Control Flow
Setkey delegates to generic `sm4_expandkey()`. Encrypt/decrypt fetch the transform context and check `crypto_simd_usable()`: if false, they call generic `sm4_crypt_block()` with encrypt/decrypt keys; otherwise, they enter `scoped_ksimd()` and call the CE assembly primitive. Module init registers a `CRYPTO_ALG_TYPE_CIPHER` driver named `sm4-ce`.

### State, Persistence, And Dependencies
Transform state is `struct sm4_ctx` containing expanded encryption and decryption keys. No request queueing or persistent storage exists. Dependencies include `asm/neon.h`, `asm/simd.h`, `crypto/algapi.h`, `crypto/internal/simd.h`, `crypto/sm4.h`, CPU feature matching, and module metadata.

### Integration Points
Provides the `sm4` base cipher used by other kernel crypto modes and by direct users of the cipher API. The driver has priority 300 and aliases `sm4` and `sm4-ce`.

### Risks
The critical behavior is fallback correctness when SIMD is unavailable in interrupt/atomic contexts. A missing CPU feature gate or incorrect key schedule choice would affect all users of the base SM4 cipher.

### Test Signals
Run crypto selftests for `sm4`, force paths with SIMD usable/unusable where possible, test invalid key lengths, compare `sm4-ce` against generic SM4, and verify module register/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-core.S -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-core.S

### Purpose
Implements high-throughput ARMv8 Crypto Extension SM4 key expansion and block-mode workers for ECB-like bulk crypt, CBC, CBC-CTS, CTR, XTS, and MAC update.

### Important APIs, Types, And Functions
Exports `sm4_ce_expand_key`, `sm4_ce_crypt_block`, `sm4_ce_crypt`, `sm4_ce_cbc_enc`, `sm4_ce_cbc_dec`, `sm4_ce_cbc_cts_enc`, `sm4_ce_cbc_cts_dec`, `sm4_ce_ctr_enc`, `sm4_ce_xts_enc`, `sm4_ce_xts_dec`, and `sm4_ce_mac_update`. It uses `SM4_PREPARE` and block macros from `sm4-ce-asm.h`, plus local CTR and XTS tweak helpers.

### Control Flow
Key expansion loads FK/CK constants, produces encryption keys, and writes reversed decryption keys. Bulk crypt handles 8-, 4-, and 1-block tails. CBC encrypt chains serially; CBC decrypt parallelizes and XORs with previous ciphertext. CTS and XTS use permutation tables and overlapping loads/stores for partial final blocks. CTR constructs little-endian internal counters from big-endian buffers and persists the new counter. MAC update optionally encrypts before or after block folding.

### State, Persistence, And Dependencies
All state is caller-owned key arrays, IV/counter/tweak buffers, digest buffers, and source/destination memory. Dependencies include `sm4-ce-asm.h`, ARMv8 SM4 instructions, `asm/assembler.h`, and C glue that validates sizes and wraps SIMD use.

### Integration Points
Used by `sm4-ce-glue.c` and exported symbols used by CCM/GCM glue through `sm4-ce.h`.

### Risks
Risks include CTS overlapping memory math, XTS tweak advancement and ciphertext stealing, CTR carry/endian handling, CBC IV persistence, and keeping exported prototypes synchronized with C declarations.

### Test Signals
Run SM4 ECB/CBC/CTS/CTR/XTS/CMAC/XCBC/CBCMAC vectors, chunk sizes around 1/4/8 blocks, partial CTS/XTS lengths, in-place requests, IV/counter continuation across scatterlist segments, and cross-build/disassembly for SM4 opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-core.S -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-core.S

### Purpose
Implements SM4-GCM assembly using ARMv8 SM4 Crypto Extensions and PMULL GHASH acceleration.

### Important APIs, Types, And Functions
Exports `sm4_ce_pmull_ghash_setup`, `pmull_ghash_update`, `sm4_ce_pmull_gcm_enc`, and `sm4_ce_pmull_gcm_dec`. Important macro groups include `PMUL_128x128`, `PMUL_128x128_4x`, `REDUCTION`, `SM4_CRYPT_PMUL_128x128_BLK`, `SM4_CRYPT_PMUL_128x128_BLK3`, `inc32_le128`, and `GTAG_HASH_LENGTHS`.

### Control Flow
GHASH setup encrypts zero to derive H and stores H through H^4 in bit-reflected form. Standalone GHASH consumes four blocks at a time then single blocks. GCM encrypt processes four full blocks, then one-block and byte-tail paths, hashes ciphertext, finalizes optional length block and tag, and updates counter/MAC when not final. Decrypt hashes ciphertext before XORing keystream and uses a three-block fused loop to fit register pressure.

### State, Persistence, And Dependencies
Caller-owned state includes round keys, IV/counter, GHASH accumulator, GHASH table, source, destination, and optional length block. Dependencies include `sm4-ce-asm.h`, PMULL, SM4 CE instructions, and C glue that wraps the assembly in `scoped_ksimd()`.

### Integration Points
Used by `sm4-ce-gcm-glue.c` to implement `gcm(sm4)`. It shares `sm4_ce_expand_key` key material with other SM4 CE modes.

### Risks
GCM is sensitive to counter construction, GHASH bit reflection, reduction constants, partial-block padding, and final length block handling. Any mismatch between assembly finalization and C tag comparison is security-critical.

### Test Signals
Run RFC8998 SM4-GCM vectors with auth sizes 4, 8, and 12-16; test zero-length payload, AAD-only, short tails 1-15 bytes, counter carry cases, fragmented scatterlists, bad tags, and PMULL/SM4 CPU-feature module gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-glue.c -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-glue.c

### Purpose
Registers ARMv8 CE/PMULL accelerated `gcm(sm4)` AEAD and handles SM4 key expansion, GHASH table setup, AAD hashing, scatterlist walking, and tag verification.

### Important APIs, Types, And Functions
Defines `struct sm4_gcm_ctx`, `gcm_setkey`, `gcm_setauthsize`, `gcm_calculate_auth_mac`, `gcm_crypt`, `gcm_encrypt`, `gcm_decrypt`, `sm4_ce_gcm_init`, and `sm4_ce_gcm_exit`. Assembly calls are `sm4_ce_pmull_ghash_setup`, `pmull_ghash_update`, `sm4_ce_pmull_gcm_enc`, and `sm4_ce_pmull_gcm_dec`.

### Control Flow
Setkey expands SM4 keys and computes the GHASH table in one SIMD section. AAD is scatterwalked, buffered to 16-byte blocks, and padded. `gcm_crypt()` zeroes GHASH, builds IV with counter 2, computes lengths, runs each skcipher walk segment through the assembly worker, and passes the length block on the final segment. Encrypt appends the computed tag; decrypt maps the stored tag and compares with `crypto_memneq()`.

### State, Persistence, And Dependencies
Transform state is SM4 key material plus a 64-byte GHASH table. Request state is IV, GHASH accumulator, length block, authtag, and skcipher walk cursor. Dependencies include AEAD/skcipher internals, scatterwalk, b128 operations, `crypto/sm4.h`, `asm/simd.h`, and CPU feature tables for SM4 and PMULL.

### Integration Points
Provides `gcm-sm4-ce` with priority 400 via the kernel crypto API and depends on base CE key helpers from `sm4-ce.h`.

### Risks
Risks include ignoring an initial skcipher walk error before `gcm_crypt()`, AAD buffer edge cases, final-segment length signaling, tag compare coverage for short auth sizes, and CPU feature combinations where SM4 exists without PMULL.

### Test Signals
Run GCM vectors across auth sizes, AAD lengths around block boundaries, payload lengths 0/1/15/16/17/64, fragmented walks, in-place decrypt with bad tags, and module auto-load on CPUs advertising both SM4 and PMULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-glue.c -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-glue.c

### Purpose
Registers ARMv8 Crypto Extension SM4 skcipher and shash algorithms for ECB, CBC, CBC-CTS, CTR, XTS, CMAC, XCBC, and CBC-MAC.

### Important APIs, Types, And Functions
Context types include `struct sm4_xts_ctx`, `struct sm4_mac_tfm_ctx`, and `struct sm4_mac_desc_ctx`. Major functions include `sm4_setkey`, `sm4_xts_setkey`, `sm4_ecb_do_crypt`, CBC/CTS/CTR/XTS crypt helpers, `sm4_cbcmac_setkey`, `sm4_cmac_setkey`, `sm4_xcbc_setkey`, `sm4_mac_init`, `sm4_mac_update`, `sm4_cmac_finup`, and `sm4_cbcmac_finup`. It exports `sm4_ce_expand_key`, `sm4_ce_crypt_block`, and `sm4_ce_cbc_enc`.

### Control Flow
Setkey expands SM4 CE keys. Skcipher helpers walk virtual scatterlists, pass whole-block work to assembly, and handle CTR tails with generic block encryption. XTS validates two keys and performs tweak handling in assembly. MAC setup derives subkeys for CMAC/XCBC; update accumulates full blocks through assembly and finup handles padding/final encryption before returning digests.

### State, Persistence, And Dependencies
State is per-transform expanded keys and per-request IV/digest buffers. No filesystem persistence exists. Dependencies include skcipher/hash internals, `crypto/sm4.h`, `crypto/xts.h`, `crypto/utils.h`, `crypto/b128ops.h`, scatterwalk, CPU features, and `asm/simd.h`.

### Integration Points
Provides high-priority `sm4-ce` mode drivers and exported helpers used by CCM/GCM modules. These drivers are consumed through the generic kernel crypto API.

### Risks
High-risk areas are CTS/XTS tail semantics, CMAC/XCBC subkey generation and padding, update/finup block retention, IV persistence, and correct cleanup if registering shash algorithms fails after skciphers succeeded.

### Test Signals
Run SM4 mode vectors for every registered algorithm, XTS weak-key rejection, CTS partial final lengths, CTR non-block tails, MAC incremental updates with every split point, module init failure injection, and selftests comparing against generic SM4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce.h -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce.h

### Purpose
Declares shared SM4 Crypto Extension helper functions used across SM4 CE mode glue files.

### Important APIs, Types, And Functions
Declares `sm4_ce_expand_key(const u8 *key, u32 *rkey_enc, u32 *rkey_dec, const u32 *fk, const u32 *ck)`, `sm4_ce_crypt_block(const u32 *rkey, u8 *dst, const u8 *src)`, and `sm4_ce_cbc_enc(const u32 *rkey_enc, u8 *dst, const u8 *src, u8 *iv, unsigned int nblocks)`.

### Control Flow
The header has no runtime flow; it establishes compile-time prototypes for assembly symbols defined in `sm4-ce-core.S`. Callers use these declarations after validating key sizes and entering a safe SIMD context.

### State, Persistence, And Dependencies
No local state or persistence. It depends on included type definitions from the including C file, specifically `u8` and `u32`.

### Integration Points
Included by SM4 CCM and GCM glue, and aligns their assembly declarations with the core CE implementation.

### Risks
Prototype drift is the main risk. A type or parameter order mismatch with assembly can corrupt key, IV, or output buffers at runtime without compiler visibility.

### Test Signals
Cross-build all SM4 CE glue files with `W=1`, enable CFI/linkage checks where applicable, and run all SM4 CE mode selftests after changes to this header or the assembly symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-core.S -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-core.S

### Purpose
Implements SM4 ECB-like bulk crypt, CBC decrypt, and CTR crypt using plain ARMv8 NEON table operations for systems without SM4 Crypto Extensions.

### Important APIs, Types, And Functions
Exports `sm4_neon_crypt`, `sm4_neon_cbc_dec`, and `sm4_neon_ctr_crypt`. Important macros include `SM4_PREPARE`, `transpose_4x4`, `transpose_4x4_2x`, `rotate_clockwise_4x4`, `ROUND4`, `ROUND8`, `SM4_CRYPT_BLK4`, and `SM4_CRYPT_BLK8`. The S-box is loaded into vectors v16-v31.

### Control Flow
Bulk crypt loads 8, 4, or tail blocks, transposes words for parallel S-box lookup, performs 32 SM4 rounds in groups, rotates output back, and stores blocks. CBC decrypt parallelizes decryption then XORs with IV/previous ciphertext and persists the final IV. CTR constructs counter blocks, encrypts them, XORs source data, and updates the counter buffer.

### State, Persistence, And Dependencies
No internal writable state. It mutates caller-provided output, IV, and counter buffers. Dependencies are `linux/linkage.h`, `asm/assembler.h`, NEON table instructions, generic SM4 expanded keys, and C glue providing `scoped_ksimd()`.

### Integration Points
Used by `sm4-neon-glue.c` for lower-priority `ecb(sm4)`, `cbc(sm4)`, and `ctr(sm4)` drivers on ARM64 NEON.

### Risks
Risks include S-box table indexing errors, transposition/rotation mistakes, tail paths that process 1-3 blocks through a 4-lane macro, and incorrect IV/counter persistence across scatterlist boundaries.

### Test Signals
Run SM4 ECB/CBC/CTR vectors against generic SM4, with nblocks 1 through 9, fragmented walks, in-place requests, CTR tails handled by C glue, and CPU configurations where CE drivers are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-glue.c -->
## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-glue.c

### Purpose
Registers plain NEON SM4 skcipher drivers for ECB, CBC, and CTR and bridges skcipher walks to `sm4-neon-core.S`.

### Important APIs, Types, And Functions
Declares assembly `sm4_neon_crypt`, `sm4_neon_cbc_dec`, and `sm4_neon_ctr_crypt`. Key functions are `sm4_setkey`, `sm4_ecb_do_crypt`, `sm4_ecb_encrypt`, `sm4_ecb_decrypt`, `sm4_cbc_encrypt`, `sm4_cbc_decrypt`, `sm4_ctr_crypt`, `sm4_init`, and `sm4_exit`.

### Control Flow
Setkey delegates to generic `sm4_expandkey()`. ECB and CBC decrypt process whole blocks through NEON assembly. CBC encrypt remains generic and serial because chaining prevents useful parallelization. CTR sends whole blocks to assembly and handles final partial bytes with generic `sm4_crypt_block()`, `crypto_inc()`, and `crypto_xor_cpy()`. Module init registers three skcipher algorithms.

### State, Persistence, And Dependencies
Transform state is `struct sm4_ctx`; per-request state is skcipher walk and IV. Dependencies include skcipher internals, `crypto/internal/simd.h`, `crypto/sm4.h`, `asm/neon.h`, and `asm/simd.h`.

### Integration Points
Provides lower-priority SM4 software acceleration (`cra_priority` 200) through the kernel crypto API, acting as a fallback below Crypto Extension implementations.

### Risks
Fallback/generic CBC encrypt must stay semantically identical to assembly decrypt. Tail handling in CTR must only run on the final walk segment, and assembly must never run without kernel SIMD context.

### Test Signals
Run SM4 ECB/CBC/CTR vectors, fragmented scatterlists, partial CTR lengths, in-place operation, comparison with `sm4-ce` and generic SM4, and module load/unload tests on ARM64 NEON-only configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/hyperv/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/hyperv/Makefile

### Purpose
Builds the ARM64 Hyper-V architecture support objects.

### Important APIs, Types, And Functions
The only build rule is `obj-y := hv_core.o mshyperv.o`, making both objects built into the ARM64 kernel when this directory is selected by the parent build.

### Control Flow
There is no runtime control flow. At build time, Kbuild includes `hv_core.c` and `mshyperv.c` in the built-in object list.

### State, Persistence, And Dependencies
No runtime state. The dependency is Kbuild's object aggregation and the parent ARM64 Hyper-V configuration.

### Integration Points
Connects low-level SMCCC hypercall helpers and Hyper-V initialization to the ARM64 kernel image.

### Risks
The file is small but build-critical: omitting either object breaks exported Hyper-V helpers or initialization, while changing `obj-y` to conditional rules could alter built-in behavior.

### Test Signals
Cross-build ARM64 with `CONFIG_HYPERV`, confirm both objects are linked, boot under Hyper-V, and verify exported symbols from `hv_core.o` are available to dependent drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/hyperv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/hyperv/hv_core.c -->
## sources/distributed-fs/ceph-client/arch/arm64/hyperv/hv_core.c

### Purpose
Provides low-level ARM64 Hyper-V hypercall and virtual processor register helpers plus legacy panic reporting.

### Important APIs, Types, And Functions
Exports `hv_do_hypercall`, `hv_do_fast_hypercall8`, `hv_do_fast_hypercall16`, `hv_set_vpreg`, `hv_get_vpreg_128`, `hv_get_vpreg`, and `hyperv_report_panic`. It uses `struct arm_smccc_res`, `struct arm_smccc_1_2_regs`, `struct hv_get_vp_registers_output`, and Hyper-V register constants.

### Control Flow
Normal hypercalls convert input/output virtual pointers to physical addresses and invoke `arm_smccc_1_1_hvc()`. Fast hypercalls pass one or two register arguments with the fast bit set. VP register access uses fast Hyper-V register calls; 128-bit reads require SMCCC 1.2 registers beyond x0-x3. Panic reporting writes crash parameters once, then notifies Hyper-V through `HV_REGISTER_GUEST_CRASH_CTL`.

### State, Persistence, And Dependencies
The only file-local state is static `panic_reported`, preventing duplicate crash notifications. Hypervisor-visible state is VP registers and crash data. Dependencies include SMCCC, `virt_to_phys`, Hyper-V HVDK definitions, `asm/mshyperv.h`, and panic/oops globals.

### Integration Points
Used by ARM64 Hyper-V initialization and common Hyper-V drivers. Exported GPL symbols are consumed by the broader Hyper-V guest stack.

### Risks
Hypercall argument register ordering must match Hyper-V ABI exactly. `BUG_ON()` on VP register failure is intentionally fatal. Panic reporting must avoid double reporting and must not run for non-panic oops when `panic_on_oops` is false.

### Test Signals
Boot ARM64 guests on Hyper-V, validate feature/register reads, run synthetic device drivers using fast and normal hypercalls, inject panic/oops paths, and test `CONFIG_HYPERV` builds with SMCCC 1.1/1.2 support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/hyperv/hv_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/hyperv/mshyperv.c -->
## sources/distributed-fs/ceph-client/arch/arm64/hyperv/mshyperv.c

### Purpose
Detects Hyper-V on ARM64, initializes common Hyper-V guest state, publishes feature flags, and tracks initialization completion.

### Important APIs, Types, And Functions
Exports `hv_get_hypervisor_version` and `hv_is_hyperv_initialized`. Internal functions are `hyperv_detect_via_acpi`, `hyperv_detect_via_smccc`, and `hyperv_init`. File-local state is `hyperv_initialized`.

### Control Flow
Early init first detects Hyper-V via ACPI FADT hypervisor ID or SMCCC UUID. If not detected, it returns success without initialization. On Hyper-V, it sets the guest OS ID, reads privilege/features/hints VP registers, identifies partition type, runs `hv_common_init()`, installs CPU hotplug callbacks, optionally reads partition ID and VTL, runs late init, then marks initialization complete.

### State, Persistence, And Dependencies
Persistent kernel state includes `ms_hyperv` feature fields, common Hyper-V allocations, CPU hotplug state, partition ID/VTL, and `hyperv_initialized`. Dependencies include ACPI, SMCCC hypervisor UUID support, Linux version code, cpuhotplug, and common Hyper-V functions declared in `asm/mshyperv.h`.

### Integration Points
Runs as `early_initcall`, preparing Hyper-V services before dependent drivers initialize. It integrates ARM64 detection with generic Hyper-V guest infrastructure.

### Risks
Detection must avoid false positives on non-Hyper-V ACPI systems. Failure cleanup after CPU hotplug setup must free common resources. Feature field interpretation depends on `hv_core.c` VP register reads.

### Test Signals
Boot with and without Hyper-V, with ACPI enabled/disabled, validate SMCCC UUID detection, exercise CPU hotplug online/offline callbacks, inspect `ms_hyperv` feature logs, and verify `hv_is_hyperv_initialized()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/hyperv/mshyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/Kbuild

### Purpose
Declares ARM64 generated, syscall, and generic asm headers for Kbuild.

### Important APIs, Types, And Functions
Lists syscall-generated headers `syscall_table_32.h`, `syscall_table_64.h`, `unistd_32.h`, and `unistd_compat_32.h`; generic header fallbacks such as `early_ioremap.h`, `mcs_spinlock.h`, `qrwlock.h`, and `qspinlock.h`; and generated headers `cpucap-defs.h`, `kernel-hwcap.h`, and `sysreg-defs.h`.

### Control Flow
No runtime flow. Kbuild consumes `syscall-y`, `generic-y`, and `generated-y` variables to export or generate architecture include files.

### State, Persistence, And Dependencies
No runtime state. Build outputs are generated headers under the kernel build tree. Dependencies are syscall table generation, generic asm-generic headers, and ARM64 system register/capability generators.

### Integration Points
Supports userspace UAPI syscall constants, VDSO/seccomp/sigreturn includes, and generic architecture header resolution for ARM64.

### Risks
Missing generated headers break builds; wrong generic fallbacks can change locking or memory-management ABI; syscall header drift can break compat userspace.

### Test Signals
Run ARM64 `headers_install`, allmodconfig/defconfig builds, compat syscall table generation, and include-what-you-use style compile checks for generic-y headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/acenv.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/acenv.h

### Purpose
Provides the ARM64 ACPICA environment header placeholder required unconditionally by ACPI core.

### Important APIs, Types, And Functions
Only defines the `_ASM_ACENV_H` include guard. There are no macros, functions, or types beyond the guard.

### Control Flow
No runtime control flow. It exists to satisfy include paths.

### State, Persistence, And Dependencies
No state, persistence, or includes. Any future ARM64-specific ACPICA definitions would be added here.

### Integration Points
Included by ACPI/ACPICA core code through architecture-specific environment hooks.

### Risks
The current risk is mostly accidental removal or adding architecture definitions that diverge from ACPICA assumptions.

### Test Signals
Build ACPI-enabled ARM64 configs and ensure ACPICA sources include this header without requiring additional definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/acenv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/acpi.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/acpi.h

### Purpose
Defines ARM64 ACPI integration hooks, MADT validation helpers, CPU idle context flags, ACPI enable/disable helpers, NUMA hooks, and APEI attributes.

### Important APIs, Types, And Functions
Important macros include `ACPI_MADT_GICC_MIN_LENGTH`, `BAD_MADT_GICC_ENTRY`, `ACPI_MADT_GICC_SPE`, `ACPI_MADT_GICC_TRBE`, `CPUIDLE_*`, `PHYS_CPUID_INVALID`, `cpu_physical_id`, and `ACPI_TABLE_UPGRADE_MAX_PHYS`. Functions/prototypes include `arch_get_idle_state_flags`, `disable_acpi`, `enable_acpi`, `acpi_cpu_get_madt_gicc`, `get_cpu_for_acpi_id`, `acpi_init_cpus`, `apei_claim_sea`, `acpi_parking_protocol_valid`, `acpi_set_mailbox_entry`, `acpi_get_enable_method`, and NUMA helpers.

### Control Flow
Most behavior is inline and configuration-selected. ACPI enable/disable toggles global ACPI/PCI/IRQ flags. CPU init paths query MADT, PSCI, and parking protocol support. Idle code maps ACPI architecture context-loss flags to cpuidle flags. APEI and NUMA hooks dispatch to real implementations only when enabled.

### State, Persistence, And Dependencies
State is global kernel ACPI flags and CPU maps maintained elsewhere. Dependencies include cpuidle, EFI, memblock, PSCI, cputype, I/O mapping, ptrace, SMP platform, and TLB flush headers.

### Integration Points
Used by ARM64 ACPI boot, CPU discovery, idle, error reporting, NUMA, and table upgrade code.

### Risks
MADT length checks must match ACPI revisions; incorrect enable-method logic can prevent CPU bring-up; global ACPI flags affect boot-wide behavior; NUMA fallback values must be safe for non-NUMA builds.

### Test Signals
Boot ACPI ARM64 systems with PSCI and parking protocol, validate MADT parsing and GICC optional fields, run kdump CPU mapping, APEI SEA injection, NUMA initialization, and DT-only builds where ACPI stubs compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative-macros.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative-macros.h

### Purpose
Defines C and assembly macros for ARM64 alternatives: runtime instruction patching based on CPU capabilities or callbacks.

### Important APIs, Types, And Functions
Key macros are `ARM64_CB_SHIFT`, `ARM64_CB_BIT`, `ALTINSTR_ENTRY`, `ALTINSTR_ENTRY_CB`, `ALTERNATIVE`, `ALTERNATIVE_CB`, `_ALTERNATIVE_CFG`, `alternative_insn`, `alternative_if`, `alternative_if_not`, `alternative_else`, `alternative_endif`, `alternative_else_nop_endif`, and `alternative_cb_end`. Inline helpers are `alternative_has_cap_likely()` and `alternative_has_cap_unlikely()`.

### Control Flow
Compile-time macros emit original instructions, replacement instructions in subsections, and metadata in `.altinstructions`. Early boot or module load code later scans entries and patches instructions when a CPU capability is present. The inline `alternative_has_cap_*` helpers use `asm goto` so hot paths become patched branch/nop sequences.

### State, Persistence, And Dependencies
No writable state in this header; it emits ELF sections consumed by alternative patching code. Dependencies include cpucap definitions, instruction definitions, VDSO bits, assembler macros, and stringify/types helpers.

### Integration Points
Used throughout ARM64 assembly and inline C for errata workarounds, feature selection, VDSO, KVM, timers, GIC, and security mitigations.

### Risks
Replacement and original instruction lengths must match unless a callback is used. Bad labels, branches into alternative sections, or overflowing capability encodings can break boot-time patching.

### Test Signals
Build with many CPU feature configs, boot on heterogeneous ARM64 systems, enable module alternatives, inspect `.altinstructions`, and run objdump checks for length-balanced replacements and VDSO builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative-macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative.h

### Purpose
Declares the ARM64 alternative patching metadata structure and patch application APIs.

### Important APIs, Types, And Functions
Defines `struct alt_instr` with original/replacement offsets, cpucap, and lengths. Defines `alternative_cb_t`. Declares `apply_boot_alternatives`, `apply_alternatives_all`, `alternative_is_applied`, `apply_alternatives_module`, and `alt_cb_patch_nops`.

### Control Flow
The header itself has no runtime flow. Boot and module code call the declared functions to apply instruction alternatives emitted by `alternative-macros.h`.

### State, Persistence, And Dependencies
Patch state and applied-capability records live in implementation files. This header depends on `alternative-macros.h`, init/types/stddef headers, and module configuration.

### Integration Points
Used by ARM64 boot, CPU feature, module loading, and any code that emits or queries alternatives.

### Risks
The struct layout is an ABI between assembly-emitted sections and C patching code. Changing fields or sizes can corrupt patch scanning. Module stubs must preserve behavior when `CONFIG_MODULES` is disabled.

### Test Signals
Boot tests with alternatives enabled, module load/unload tests for alternative sections, compile tests for assembler and C include paths, and objdump validation of `struct alt_instr` record size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/apple_m1_pmu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/apple_m1_pmu.h

### Purpose
Defines Apple M1 implementation-defined PMU system register encodings and bit fields.

### Important APIs, Types, And Functions
Defines counter registers `SYS_IMP_APL_PMC0_EL1` through `SYS_IMP_APL_PMC9_EL1`; control registers `SYS_IMP_APL_PMCR0_EL1` through `PMCR4`; event selector registers `PMESR0/1`; status register `PMSR`; and bit masks such as `PMCR0_CNT_ENABLE_*`, `PMCR0_PMI_ENABLE_*`, `PMCR0_IMODE_*`, `PMCR1_COUNT_A64_*`, and `PMSR_OVERFLOW`.

### Control Flow
No runtime flow. PMU drivers include these constants and use generic system-register accessors to program Apple-specific counters.

### State, Persistence, And Dependencies
No local state. Hardware PMU register state persists in CPU system registers. Dependencies are `linux/bits.h` and `asm/sysreg.h`.

### Integration Points
Used by Apple M1 PMU/perf support to configure counters, interrupts, overflow status, and event selection.

### Risks
Implementation-defined register encodings must be exact. Wrong bit masks can misprogram counters, expose EL0 counting unexpectedly, or break PMU interrupt delivery.

### Test Signals
Run perf event tests on Apple M1 hardware, validate counter overflow interrupts, user/kernel counting filters, event selector programming, and cross-build non-Apple ARM64 configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/apple_m1_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_gicv3.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_gicv3.h

### Purpose
Provides ARM64 GICv3 system-register and redistributor/ITS MMIO accessors, including erratum-aware interrupt acknowledge handling and priority masking helpers.

### Important APIs, Types, And Functions
Important helpers include `read_gicreg`, `write_gicreg`, `gic_write_dir`, `gic_read_iar_common`, `gic_read_iar_cavium_thunderx`, `gic_read_iar`, `gic_write_ctlr`, `gic_read_ctlr`, `gic_write_grpen1`, `gic_write_sgi1r`, `gic_read_sre`, `gic_write_sre`, `gic_write_pmr`, `gic_read_pmr`, `gic_flush_dcache_to_poc`, and ITS/GICR read/write macros.

### Control Flow
Inline accessors read and write ICC system registers with required `isb()`, `dsb()`, or memory barriers. `gic_read_iar()` dynamically selects the Cavium ThunderX workaround using alternatives. Priority masking helpers manipulate PMR or DAIF based on system capability.

### State, Persistence, And Dependencies
State is in GIC CPU interface registers and MMIO redistributor/ITS tables. Dependencies include sysreg definitions, GIC common constants, barrier/cacheflush helpers, CPU capability alternatives, and relaxed MMIO accessors.

### Integration Points
Used by the GICv3 irqchip driver, interrupt entry/exit, SGI delivery, ITS setup, and priority-mask based interrupt disabling.

### Risks
Missing barriers can lose or reorder interrupts. Erratum selection must be correct for ThunderX. Relaxed MMIO accessors require callers to add ordering where necessary. PMR masking must align with irqflags semantics.

### Test Signals
Boot GICv3 systems, run interrupt storm and CPU hotplug tests, SGI/IPI tests, ITS/MSI tests, ThunderX erratum coverage, priority masking lockdep/irqsoff tests, and virtualization interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_gicv3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_timer.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_timer.h

### Purpose
Defines ARM64 architectural timer register accessors, stable counter reads, erratum workaround indirection, and event stream feature publication.

### Important APIs, Types, And Functions
Defines `enum arch_timer_erratum_match_type`, `struct arch_timer_erratum_workaround`, per-CPU `timer_unstable_counter_workaround`, `arch_timer_read_cntpct_el0`, `arch_timer_read_cntvct_el0`, `arch_timer_reg_write_cp15`, `arch_timer_reg_read_cp15`, `arch_timer_get_cntfrq`, `arch_timer_get_cntkctl`, `arch_timer_set_cntkctl`, `__arch_counter_get_cntpct`, `__arch_counter_get_cntvct`, stable variants, and event-stream helpers.

### Control Flow
Counter reads use alternatives to select ECV self-synchronizing registers when available, otherwise `isb; mrs`. Stable read macros route through per-CPU erratum handlers when configured. Timer register read/write helpers compile-time select physical or virtual timer registers and insert `isb()` after control writes.

### State, Persistence, And Dependencies
State lives in architectural timer registers, per-CPU workaround pointers, compat hwcap bits, and CPU feature flags. Dependencies include barriers, hwcap, sysreg, jump labels/percpu types, and generic clocksource timer definitions.

### Integration Points
Used by the ARM arch timer clocksource/clockevent driver, VDSO timekeeping decisions, compat HWCAP exposure, and erratum workaround framework.

### Risks
Timer reads require strict ordering; wrong ECV alternative or erratum handler selection can make time go backward. Register accessors must match physical/virtual timer paths. Event stream feature exposure affects userspace ABI.

### Test Signals
Run clocksource watchdog, high-resolution timer, suspend/resume, CPU hotplug, VDSO time tests, ECV-capable hardware tests, erratum workaround platform tests, and compat HWCAP validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/archrandom.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/archrandom.h

### Purpose
Implements ARM64 architecture random-number hooks using RNDR/RNDRRS CPU instructions and SMCCC TRNG calls.

### Important APIs, Types, And Functions
Defines `ARM_SMCCC_TRNG_MIN_VERSION`, declares `smccc_trng_available`, and implements `smccc_probe_trng`, `__arm64_rndr`, `__arm64_rndrrs`, `__cpu_has_rng`, `arch_get_random_longs`, `arch_get_random_seed_longs`, and `__early_cpu_has_rndr`.

### Control Flow
Boot can probe SMCCC TRNG version. Runtime random hooks first check max output count and CPU capabilities. `arch_get_random_longs()` uses RNDR for one word. `arch_get_random_seed_longs()` prefers SMCCC TRNG, returning up to three longs from SMCCC registers, and falls back to RNDRRS when available.

### State, Persistence, And Dependencies
State is the global `smccc_trng_available` flag and CPU capability finalization state. Hardware state is the CPU RNG or firmware TRNG. Dependencies include SMCCC, IRQ/preemption rules, cpufeature alternatives, sysreg encodings, and bug/kernel helpers.

### Integration Points
Used by the kernel random subsystem for architecture entropy and seed material on ARM64.

### Risks
Capability checks before finalization must not migrate across CPUs with different features. SMCCC return value interpretation and register ordering must be correct. RNDRRS is a DRBG reseed path, not equivalent to a direct entropy source.

### Test Signals
Boot on RNDR-capable and non-capable CPUs, firmware with/without SMCCC TRNG, test early CPU detection, run random subsystem health tests, and verify preemption-sensitive capability paths with CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm-cci.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm-cci.h

### Purpose
Provides the ARM64 platform hook for secure CCI access.

### Important APIs, Types, And Functions
Defines `platform_has_secure_cci_access()` as an inline function that always returns `false`.

### Control Flow
No complex flow. Callers query the helper and receive a fixed negative answer on ARM64.

### State, Persistence, And Dependencies
No state or persistence. It assumes no ARM64 platform exposes secure CCI access through this hook.

### Integration Points
Used by ARM CCI/cache-coherent interconnect code to decide whether secure-only CCI registers can be accessed.

### Risks
If a future platform requires secure CCI access from the kernel, this hardcoded false value would need revisiting. The current conservative answer avoids illegal secure register access.

### Test Signals
Build CCI-related ARM64 configs and boot platforms using CCI drivers, confirming they do not attempt secure-only accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm-cci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_dsu_pmu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_dsu_pmu.h

### Purpose
Defines low-level register access helpers for ARM DynamIQ Shared Unit PMU cluster counters.

### Important APIs, Types, And Functions
Defines DSU PMU sysreg encodings such as `CLUSTERPMCR_EL1`, `CLUSTERPMCNTENSET_EL1`, `CLUSTERPMOVS*`, `CLUSTERPMSELR_EL1`, `CLUSTERPMINTEN*`, `CLUSTERPMCCNTR_EL1`, `CLUSTERPMXEVTYPER_EL1`, `CLUSTERPMXEVCNTR_EL1`, and `CLUSTERPMCEID*`. Helpers include `__dsu_pmu_read_pmcr`, `__dsu_pmu_write_pmcr`, `__dsu_pmu_get_reset_overflow`, counter select/read/write, event setup, cycle counter access, enable/disable, interrupt enable/disable, and `__dsu_pmu_read_pmceid`.

### Control Flow
Inline helpers select counters through `CLUSTERPMSELR_EL1`, access selected event registers, and use `isb()` after writes that must take effect before subsequent operations. Overflow read clears overflow bits by writing the read value back.

### State, Persistence, And Dependencies
State is in DSU PMU cluster system registers and counters. Dependencies include bitops, build bug checks, compiler/types, barriers, and sysreg helpers.

### Integration Points
Consumed by DSU PMU perf driver code to program cluster-level events and interrupts.

### Risks
Counter selection is shared state; missing barriers can read/write the wrong selected counter. Invalid PMCEID index intentionally triggers `BUILD_BUG()`. Interrupt and overflow clear masks must match hardware.

### Test Signals
Run perf stat/record on DSU events, overflow interrupt tests, counter enable/disable tests, multi-CPU cluster tests, and cross-build configs without DSU hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_dsu_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_pmuv3.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_pmuv3.h

### Purpose
Provides ARM PMUv3 system-register accessors and feature helpers for perf and virtualization code.

### Important APIs, Types, And Functions
Important helpers include `read_pmevcntrn`, `write_pmevcntrn`, `write_pmevtypern`, `read_pmevtypern`, `read_pmmir`, `read_pmuver`, `pmuv3_has_icntr`, `write_pmcr`, `read_pmcr`, `write_pmselr`, cycle/instruction counter accessors, counter enable/interrupt/filter helpers, `read_pmceid0/1`, `pmuv3_implemented`, `is_pmuv3p4`, `is_pmuv3p5`, and `is_pmuv3p9`.

### Control Flow
Counter-numbered helpers use `PMEVN_SWITCH()` to compile to direct register accesses for supported event counter indices. Feature helpers read ID registers and compare PMU version fields.

### State, Persistence, And Dependencies
State lives in PMU system registers. Dependencies include KVM host definitions for counter-switch macros, cpufeature extraction, and sysreg helpers.

### Integration Points
Used by ARM64 perf PMU drivers, KVM PMU virtualization, and user-access control for PMU counters.

### Risks
Register selection and PMU version comparisons must track ARM architectural revisions. Incorrect user enable or filter writes can expose counters incorrectly or misattribute events. KVM dependencies must not create include cycles.

### Test Signals
Run perf tests across PMUv3 revisions, KVM guest PMU tests, instruction counter support checks, user-access enable/disable tests, and compile coverage for PMUv3p4/p5/p9 feature logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_pmuv3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-bug.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-bug.h

### Purpose
Defines assembly macros for ARM64 BUG/WARN trap emission and optional bug-table metadata.

### Important APIs, Types, And Functions
Important macros include `_BUGVERBOSE_LOCATION`, `__BUG_ENTRY_START`, `__BUG_ENTRY_END`, `__BUG_ENTRY`, `ASM_BUG_FLAGS`, `ASM_BUG`, `__BUG_LOCATION_STRING`, `__BUG_ENTRY_STRING`, `ARCH_WARN_ASM`, and `ARCH_WARN_REACHABLE`.

### Control Flow
Assembly call sites expand the macros to optionally emit records into `__bug_table` and then execute `brk BUG_BRK_IMM`. Verbose builds also store file/line strings and offsets in rodata and bug records.

### State, Persistence, And Dependencies
No runtime state in the header. It emits ELF sections used by bug handling. Dependencies include `asm/brk-imm.h` and configuration flags `CONFIG_GENERIC_BUG` and `CONFIG_DEBUG_BUGVERBOSE`.

### Integration Points
Used by low-level ARM64 assembly code, warning macros, and exception handling to map breakpoints back to BUG/WARN metadata.

### Risks
Section layout and relative offsets must match generic bug-table parsing. Incorrect `brk` immediate values or missing alignment would break exception classification.

### Test Signals
Build with and without generic/verbose bug support, trigger assembly WARN/BUG test paths, inspect `__bug_table`, and verify exception handlers decode `BUG_BRK_IMM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-extable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-extable.h

### Purpose
Defines ARM64 assembly and inline-asm exception table record macros for uaccess, kaccess, BPF, copy, and unaligned zeropad fixups.

### Important APIs, Types, And Functions
Defines exception types `EX_TYPE_NONE`, `EX_TYPE_BPF`, `EX_TYPE_UACCESS_ERR_ZERO`, `EX_TYPE_KACCESS_ERR_ZERO`, `EX_TYPE_UACCESS_CPY`, and `EX_TYPE_LOAD_UNALIGNED_ZEROPAD`; data bitfields such as `EX_DATA_REG_ERR`, `EX_DATA_REG_ZERO`, and `EX_DATA_UACCESS_WRITE`; and macros `_ASM_EXTABLE_UACCESS*`, `_ASM_EXTABLE_KACCESS*`, `_ASM_EXTABLE_LOAD_UNALIGNED_ZEROPAD`, plus assembler helpers `_asm_extable_uaccess`, `_cond_uaccess_extable`, and `_asm_extable_uaccess_cpy`.

### Control Flow
Fault-prone instructions emit records into `__ex_table` with relative instruction/fixup offsets, type, and packed data. The runtime exception handler uses those records to branch to fixups, zero registers, set error registers, or complete copy semantics.

### State, Persistence, And Dependencies
The header emits static exception table metadata; no writable state. Dependencies include bit masks and GPR number macros, plus stringify support in C inline-asm mode.

### Integration Points
Used by uaccess assembly, copy routines, BPF JIT helpers, zeropad loads, and kernel access fixups.

### Risks
Incorrect register encoding, type values, or relative offsets will mis-handle faults and can create kernel memory disclosure or usercopy corruption. Inline-asm and assembler macro variants must stay equivalent.

### Test Signals
Run usercopy fault injection, KASAN/KFENCE invalid-user-pointer tests, BPF fault tests, unaligned zeropad tests, and objdump validation of `__ex_table` records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-offsets.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-offsets.h

### Purpose
Forwards ARM64 assembly code to generated structure offset definitions.

### Important APIs, Types, And Functions
The sole content is `#include <generated/asm-offsets.h>`.

### Control Flow
No runtime flow. Assembly sources include this header to obtain constants generated during the build.

### State, Persistence, And Dependencies
No local state. The build system generates `generated/asm-offsets.h` from C structure layouts, making the generated file the persistent build artifact.

### Integration Points
Used by low-level assembly needing offsets into `task_struct`, `thread_info`, pt_regs, pointer-auth keys, and other C-defined layouts.

### Risks
If generated offsets are stale or missing, assembly can access wrong fields or fail to build. This header must remain minimal to avoid circular includes.

### Test Signals
Clean ARM64 builds, generated-offset dependency checks, and boot tests covering exception entry, context switch, and pointer-auth code that consumes offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-prototypes.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-prototypes.h

### Purpose
Provides C prototypes for assembly-exported ARM64 symbols so modversions/genksyms can generate correct CRCs.

### Important APIs, Types, And Functions
Includes SMCCC, ftrace, page, string, uaccess, and generic asm prototypes. Declares compiler helper prototypes `__ashlti3`, `__ashrti3`, `__lshrti3`, and `__hwasan_tag_mismatch`.

### Control Flow
No runtime flow. Kbuild feeds the declarations to genksyms when assembly files export symbols under `CONFIG_MODVERSIONS`.

### State, Persistence, And Dependencies
No state. Dependencies are the included architecture and generic prototype headers and the modversions build pipeline.

### Integration Points
Used by exported ARM64 assembly routines and modules that link against them.

### Risks
Prototype mismatch can create wrong module CRCs or hide ABI drift. `__hwasan_tag_mismatch` has a custom calling convention, so its prototype is intentionally only approximate.

### Test Signals
Build ARM64 with `CONFIG_MODVERSIONS`, load modules using exported assembly helpers, and verify genksyms CRC stability after prototype changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-uaccess.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-uaccess.h

### Purpose
Defines ARM64 assembly macros for enabling/disabling user access and annotating user memory loads/stores with exception table fixups.

### Important APIs, Types, And Functions
Important macros are `__uaccess_ttbr0_disable`, `__uaccess_ttbr0_enable`, `uaccess_ttbr0_disable`, `uaccess_ttbr0_enable`, `USER`, `USER_CPY`, `user_ldp`, `user_stp`, and `user_ldst`.

### Control Flow
When software TTBR0 PAN is enabled and hardware PAN is unavailable, macros save DAIF, switch TTBR0 to reserved page tables or restore task TTBR0/ASID, and then restore interrupts. `USER*` macros wrap faulting instructions and emit exception table records. Pair/unprivileged load/store helpers expand to LDTR/STTR sequences with fixups for each instruction.

### State, Persistence, And Dependencies
State affected is TTBR0_EL1, TTBR1_EL1 ASID bits, DAIF interrupt mask, and exception table metadata. Dependencies include alternatives, extable macros, assembler helpers, kernel page table constants, MMU constants, and sysreg definitions.

### Integration Points
Used by ARM64 usercopy, signal, access_ok-adjacent assembly, and low-level routines that temporarily permit user address translation.

### Risks
TTBR/ASID switching must be interrupt-safe and ordered by ISB. Missing exception table entries can turn user faults into kernel faults. Hardware PAN alternatives must patch to no-ops correctly.

### Test Signals
Run usercopy fault tests, PAN/SW_TTBR0_PAN boot variants, KASAN invalid user pointer tests, signal frame access tests, and objdump checks for exception table entries around LDTR/STTR sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm_pointer_auth.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm_pointer_auth.h

### Purpose
Defines assembly macros for installing and initializing ARM64 pointer authentication keys.

### Important APIs, Types, And Functions
Important macros include `__ptrauth_keys_install_kernel_nosync`, `ptrauth_keys_install_kernel_nosync`, `ptrauth_keys_install_kernel`, `__ptrauth_keys_install_user`, `__ptrauth_keys_init_cpu`, and `ptrauth_keys_init_cpu`.

### Control Flow
When kernel pointer auth is enabled and address-auth capability is present, macros load kernel APIA key halves from the current task and write `APIAKEYLO/HI_EL1`, optionally followed by `isb`. User-key macros load user keys from thread storage. CPU init reads ID registers, enables SCTLR pointer-auth bits, installs kernel keys, and skips work via alternatives if address auth is absent.

### State, Persistence, And Dependencies
State is in task thread key storage and pointer-auth system registers. Dependencies include alternative patching, generated asm offsets, cpufeature constants, and sysreg encodings.

### Integration Points
Used by entry, context switch, CPU init, and pointer-auth enable paths.

### Risks
Wrong offsets or missing ISB can leave stale keys active. Capability alternatives must not execute pointer-auth system-register writes on unsupported CPUs. Key installation must track task switches exactly.

### Test Signals
Boot with pointer-auth configs on capable and incapable hardware, run context-switch stress, kernel PAC fault tests, userspace PAC tests, and objdump checks for patched alternatives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm_pointer_auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/assembler.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/assembler.h

### Purpose
Provides the central ARM64 assembly macro library for exception entry, barriers, alternatives, per-CPU access, cache/TLB maintenance, page-table helpers, symbol export, GNU property notes, and Spectre mitigations.

### Important APIs, Types, And Functions
Notable macros include DAIF save/restore, single-step control, `esb`, `csdb`, `clearbhb`, `sb`, `nops`, endian selectors `CPU_BE/CPU_LE`, address pseudo-ops `adr_l/ldr_l/str_l`, per-CPU accessors, CTR/cache-line helpers, TCR/physical address helpers, cache maintenance loops, frame helpers, `EXPORT_SYMBOL_NOKASAN`, GNU property emission, `set_sctlr*`, and Spectre BHB mitigation macros.

### Control Flow
The header has no standalone flow; assembly files expand these macros into boot, exception, MMU, cache, KVM, crypto, and mitigation code. Many macros emit alternative sequences that patch at boot based on CPU capabilities or callbacks.

### State, Persistence, And Dependencies
Macros manipulate CPU registers, DAIF, debug registers, cache state, TCR/SCTLR, per-CPU offsets, and ELF metadata sections. Dependencies include alternative patching, bug/extable/offset/cpufeature/cputype/debug/page/pgtable/ptrace/thread headers and Linux export machinery.

### Integration Points
Included by most ARM64 `.S` files in this subset and beyond; it is foundational for low-level kernel assembly.

### Risks
This file has broad blast radius. Register clobber assumptions, missing barriers, incorrect alternatives, cache maintenance fixups, or mitigation patch callbacks can break boot, security, usercopy, KVM, or crypto assembly.

### Test Signals
Full ARM64 defconfig/allmodconfig builds, boot on varied CPUs, KVM tests, exception/usercopy/cache maintenance tests, Spectre mitigation validation, objdump inspection of alternatives, and crypto assembly builds that rely on `frame_push`/`adr_l` macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/assembler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic.h

### Purpose
Defines ARM64 architecture atomic integer and atomic64 operations by dispatching to LSE or LL/SC implementations.

### Important APIs, Types, And Functions
Macro generators create `arch_atomic_*` and `arch_atomic64_*` operations for add, sub, and, andnot, or, xor, fetch variants, return variants with relaxed/acquire/release/full ordering, and `arch_atomic64_dec_if_positive`. Also defines `arch_atomic_read`, `arch_atomic_set`, `ATOMIC64_INIT`, and aliases indicating generic atomic API support.

### Control Flow
Inline functions call `__lse_ll_sc_body()` for each operation, letting `asm/lse.h` select Large System Extensions atomics when available or LL/SC fallbacks otherwise. Reads/writes use `__READ_ONCE` and `__WRITE_ONCE`.

### State, Persistence, And Dependencies
State is caller-owned `atomic_t` or `atomic64_t` counters. No persistence beyond memory. Dependencies include compiler/types, memory barriers, cmpxchg, and LSE selection headers.

### Integration Points
Used by generic kernel atomic API on ARM64 across scheduler, locking, MM, networking, and filesystem code, indirectly supporting Ceph client correctness.

### Risks
Memory-order aliases must match generic expectations. LSE/LLSC dispatch must preserve semantics across heterogeneous CPUs. Atomic64 aliases to atomic read/set assume compatible counter layout.

### Test Signals
Run LKMM atomic litmus tests, locktorture/refcount tests, KCSAN stress, LSE-capable and LL/SC-only boot tests, and compile checks for all generated operation names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_ll_sc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_ll_sc.h

### Purpose
Implements ARM64 LL/SC fallback atomic, cmpxchg, and 128-bit cmpxchg primitives using exclusive load/store loops.

### Important APIs, Types, And Functions
Macro generators define `__ll_sc_atomic_*`, `__ll_sc_atomic_fetch_*`, `__ll_sc_atomic64_*`, and `__ll_sc_atomic64_fetch_*` for arithmetic/bitwise operations and memory-order variants. It also defines `__ll_sc_atomic64_dec_if_positive`, `__ll_sc__cmpxchg_case_*` for 8/16/32/64-bit relaxed/acquire/release/full cases, `union __u128_halves`, and `__ll_sc__cmpxchg128`/`__ll_sc__cmpxchg128_mb`.

### Control Flow
Each operation prefetches for store, loops on `ldxr`/`stxr` or acquire/release variants until the exclusive store succeeds, and emits `dmb ish` or memory clobbers for full ordering. Cmpxchg compares loaded old values before attempting store; 128-bit compare exchange uses `ldxp/stxp` over two 64-bit halves.

### State, Persistence, And Dependencies
State is caller memory protected by exclusive monitors. Dependencies include compiler constraint support, stringify, AArch64 exclusive instruction semantics, and barrier conventions.

### Integration Points
Included through the ARM64 LSE dispatch machinery when LSE atomics are unavailable or patched out.

### Risks
Constraint letters, sub-word casts, clobbers, and memory barriers are correctness-critical. LL/SC loops can livelock under heavy contention. 128-bit cmpxchg must preserve pair alignment and compare high/low halves correctly.

### Test Signals
Run atomic and cmpxchg LKMM tests on LL/SC-only hardware or with LSE disabled, stress contended atomics, test sub-word cmpxchg, run 128-bit cmpxchg users, and build with compilers with/without `K` constraint support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_ll_sc.h -->
