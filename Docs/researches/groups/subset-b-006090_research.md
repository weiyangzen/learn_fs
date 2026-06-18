# subset-b-006090 Research

Grouped research report for the requested Ceph client crypto subset. Each section preserves the original source path and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha256-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha256-testvecs.h

Purpose: generated SHA-256 test-vector data for the common KUnit hash test template. It declares `hash_testvecs[]`, where each entry binds a message length to a `SHA256_DIGEST_SIZE` expected digest, plus consolidated expected digests for all hash and HMAC vector outputs.

Important APIs/types/functions: the file is data-only and expects the including C file to have `u8`, `size_t`, and `SHA256_DIGEST_SIZE` in scope. `hash_testvecs[]`, `hash_testvec_consolidated`, and `hmac_testvec_consolidated` are consumed by `hash-test-template.h` after the including test driver defines the SHA-256 macro layer.

Control flow: none locally. The generated lengths intentionally cover empty input, short inputs, block-boundary and near-boundary cases around 64 and 128 bytes, multi-block inputs, and larger 16 KiB data. The template loops over these lengths, generates deterministic message bytes, compares individual digests, then verifies the consolidated digest over all vector results.

State and persistence: static const data only; no mutable state, allocation, I/O, or persistence. Dependencies are the SHA-256 constants and the shared test template contract.

Integration points: included by `sha256_kunit.c`, which binds these generic names to the SHA-256 implementation and HMAC-SHA256 implementation.

Risks: stale generated data would make the KUnit test enforce incorrect outputs; manual edits are high risk because the table has no self-describing input bytes. Boundary coverage depends on `gen-hash-testvecs.py` and the shared deterministic input generator matching the template.

Test signals: strong regression signal for digest correctness, block padding, length accounting, and HMAC coverage across boundary lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha256-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha256_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha256_kunit.c

Purpose: KUnit coverage and optional benchmarking for SHA-256, HMAC-SHA256, and the optimized two-message finalization helper `sha256_finup_2x()`.

Important APIs/types/functions: it binds `HASH`, `HASH_CTX`, `HASH_INIT`, `HASH_UPDATE`, `HASH_FINAL`, and the HMAC macro family to the shared `hash-test-template.h`. Local helpers include `alloc_guarded_buf()`, `test_sha256_finup_2x()`, `test_sha256_finup_2x_defaultctx()`, `test_sha256_finup_2x_hugelen()`, and `benchmark_sha256_finup_2x()`.

Control flow: the template contributes `HASH_KUNIT_CASES` and `benchmark_hash`. The custom finup test allocates vmalloc-backed buffers ending at a page boundary, fills random data and salt, prepares an initial context, calls `sha256_finup_2x()`, asserts the input context is unchanged, and compares both outputs with ordinary `sha256_update()`/`sha256_final()` results. The default-context test compares a NULL context against an initialized empty context. The huge-length test seeds the internal bytecount above 32 bits and verifies finalization length encoding. Benchmark cases skip unless `CONFIG_CRYPTO_LIB_BENCHMARK` and optimized finup support are present.

State and persistence: all buffers are KUnit-managed through `kunit_add_action_or_reset()` and freed with `vfree`; no persistent state. It mutates temporary hash contexts and a shared test buffer from the template.

Dependencies: `<crypto/sha2.h>`, generated SHA-256 vectors, KUnit, vmalloc, random test helpers from the template, timing helpers, and optional crypto benchmark config.

Integration points: registers suite `sha256`; validates architecture and generic SHA-256 paths exposed behind the public SHA-2 library API.

Risks: guarded-buffer arithmetic returns `buf + full_len - len`; zero-length allocations rely on caller behavior and current test lengths. Randomized loops increase coverage but failures need logged salt/data lengths to reproduce. Optimized assembly errors are specifically targeted through guard pages.

Test signals: strong correctness signal for SHA-256, HMAC, context immutability, tail padding, huge byte counts, and out-of-bounds accesses in optimized finup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha256_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha3-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha3-testvecs.h

Purpose: generated SHA3-256 and SHAKE consolidated test-vector data for the SHA3 KUnit suite.

Important APIs/types/functions: declares `hash_testvecs[]` with `SHA3_256_DIGEST_SIZE` outputs, `hash_testvec_consolidated`, `shake128_testvec_consolidated`, and `shake256_testvec_consolidated`. It is data-only and is included after the SHA3 test driver defines the template macros.

Control flow: no local execution. The vector lengths mirror the shared hash-vector shape: empty, small inputs, 63/64/65 and 127/128/129 boundary lengths, multi-block lengths, and 16 KiB. SHAKE consolidated values are used by the SHA3 driver after concatenating outputs for input/output length sweeps.

State and persistence: static const arrays only; no mutable storage, allocation, or persistence.

Dependencies: SHA3 digest-size constants and the shared `hash-test-template.h` variable names. The data was generated by `scripts/crypto/gen-hash-testvecs.py sha3`, so the semantic input bytes live in the generator/template rather than this header.

Integration points: included by `sha3_kunit.c`, where `hash_testvecs[]` validates SHA3-256 streaming behavior and the SHAKE consolidated values validate `shake128()` and `shake256()` length sweeps.

Risks: consolidated SHAKE values obscure the individual failing length if a mismatch occurs unless the caller narrows the sweep. Generated data should not be hand-edited; any change must keep the deterministic input generator and template in sync.

Test signals: covers SHA3-256 padding/rate handling and SHAKE extensible-output behavior over many input/output sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha3-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha384-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha384-testvecs.h

Purpose: generated SHA-384 test vectors for the common KUnit hash and HMAC template.

Important APIs/types/functions: defines `hash_testvecs[]` entries with `SHA384_DIGEST_SIZE` digests, `hash_testvec_consolidated`, and `hmac_testvec_consolidated`. The including driver supplies all function and type bindings.

Control flow: none locally. The table covers empty input, short data, SHA-512-family 128-byte block boundaries and nearby sizes, 256/511/513/1000/3333-byte cases, and larger 4 KiB to 16 KiB cases. The shared template iterates these lengths and validates digest/HMAC behavior against the arrays.

State and persistence: constant read-only data only. It has no allocation, side effects, I/O, or persistent state.

Dependencies: `<crypto/sha2.h>` definitions in the including file, `SHA384_DIGEST_SIZE`, `u8`, `size_t`, and the `hash-test-template.h` variable contract.

Integration points: included only by `sha384_kunit.c` in this subset. It tests the SHA-384 API, which is usually implemented as SHA-512 with different IV and truncated output.

Risks: table size makes human review error-prone; corrupted vector bytes can either hide implementation bugs or create false failures. Since inputs are generated elsewhere, future changes to deterministic test data generation must regenerate this header.

Test signals: good coverage for SHA-384 padding, length encoding, update/final sequencing, and HMAC key preparation/finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha384-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha384_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha384_kunit.c

Purpose: minimal KUnit suite wiring for SHA-384 and HMAC-SHA384 using the shared hash test template.

Important APIs/types/functions: maps template macros to `sha384_ctx`, `sha384_init()`, `sha384_update()`, `sha384_final()`, `hmac_sha384_key`, `hmac_sha384_ctx`, `hmac_sha384_preparekey()`, `hmac_sha384_init()`, `hmac_sha384_update()`, `hmac_sha384_final()`, `hmac_sha384()`, and `hmac_sha384_usingrawkey()`. It registers `hash_test_cases[]` and `hash_test_suite`.

Control flow: compile-time macro binding causes `hash-test-template.h` to generate the standard tests and benchmark function. Runtime suite execution runs `HASH_KUNIT_CASES`, then `benchmark_hash` when benchmarks are enabled by the template/config.

State and persistence: no local mutable state. Suite lifecycle is delegated to `hash_suite_init` and `hash_suite_exit` from the shared template.

Dependencies: `<crypto/sha2.h>`, generated `sha384-testvecs.h`, KUnit module machinery, and the shared template.

Integration points: registers suite name `sha384`, exercising the public crypto library SHA-384/HMAC functions independent of higher-level protocols.

Risks: this file has little custom logic, so coverage quality depends almost entirely on vector quality and template behavior. It does not add SHA-384-specific edge tests beyond the generated vector set.

Test signals: validates streaming and one-shot hash/HMAC paths through the macro-generated cases, including boundary lengths inherited from the vector header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha384_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha3_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha3_kunit.c

Purpose: KUnit suite for SHA3-256 template tests plus explicit SHA3-224/256/384/512 and SHAKE128/SHAKE256 one-shot and streaming-squeeze behavior.

Important APIs/types/functions: binds the shared template to `sha3_256_init()`, `sha3_update()`, and `sha3_final()`. Local tests cover `sha3_224()`, `sha3_256()`, `sha3_384()`, `sha3_512()`, `shake128()`, `shake256()`, `shake128_init()`, `shake256_init()`, `shake_update()`, and `shake_squeeze()`.

Control flow: basic SHA3/SHAKE tests hash a repeated sample sentence into output buffers padded with 8-byte guard regions and compare the full guarded arrays. NIST SHAKE tests check empty and 1600-bit sample inputs. The all-lengths test runs input lengths 0 through 4096, derives varied output lengths, hashes concatenated SHAKE outputs with SHA3-256, and compares a consolidated digest. The multi-squeeze test compares one-shot output to randomized sequences of `shake_squeeze()` calls. Guard-buffer tests run in-place SHAKE on buffers ending at the shared test buffer boundary.

State and persistence: temporary KUnit allocations and the shared random test buffer only; no persistent state. The SHAKE context is local per randomized trial.

Dependencies: `<crypto/sha3.h>`, generated vectors, KUnit, random helpers and lifecycle from `hash-test-template.h`.

Integration points: suite name `sha3`; validates both hash and extensible-output APIs in the crypto library.

Risks: consolidated all-length failures need bisection to find the exact bad length. Guard-buffer testing protects against overrun but only within the shared buffer model, not true unmapped pages.

Test signals: strong coverage for SHA3 digest sizes, SHAKE output-length handling, repeated squeeze semantics, NIST examples, and output overwrite boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha3_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha512-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha512-testvecs.h

Purpose: generated SHA-512 test vectors for the shared hash/HMAC KUnit template.

Important APIs/types/functions: data definitions `hash_testvecs[]`, `hash_testvec_consolidated`, and `hmac_testvec_consolidated` using `SHA512_DIGEST_SIZE`.

Control flow: none locally. Runtime behavior is provided by the including suite and template, which use the length/digest table to validate SHA-512 streaming and HMAC results. The vector set includes empty input, small lengths, SHA-512 block-boundary lengths around 128 bytes, and large multi-block data up to 16 KiB.

State and persistence: read-only static data; no mutable state or side effects.

Dependencies: `SHA512_DIGEST_SIZE`, `u8`, `size_t`, and the shared hash test naming convention. Generated provenance is `scripts/crypto/gen-hash-testvecs.py sha512`.

Integration points: included by `sha512_kunit.c`, which maps the table to SHA-512 and HMAC-SHA512 library calls.

Risks: manual byte corruption is difficult to spot visually. The table tests deterministic generated input rather than named external message strings, so failures must be diagnosed through the generator/template.

Test signals: good regression coverage for SHA-512 padding, 128-byte block processing, length encoding, digest output, and HMAC wrapper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha512-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha512_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sha512_kunit.c

Purpose: minimal KUnit suite wiring for SHA-512 and HMAC-SHA512 using generated vectors and the shared hash test template.

Important APIs/types/functions: maps `HASH_*` macros to `sha512_ctx`, `sha512_init()`, `sha512_update()`, `sha512_final()`, and maps HMAC macros to `hmac_sha512_*` APIs. Registers `hash_test_cases[]` with `HASH_KUNIT_CASES` and `benchmark_hash`.

Control flow: template-generated tests execute the vector table and consolidated HMAC checks. The benchmark case is included in the suite and is controlled by the template/config runtime skip behavior.

State and persistence: no local allocations or persistent state; suite init/exit are delegated to the shared hash test template.

Dependencies: `<crypto/sha2.h>`, `sha512-testvecs.h`, KUnit, and `hash-test-template.h`.

Integration points: suite name `sha512`; validates the crypto library SHA-512 public API and HMAC API used by kernel consumers.

Risks: no SHA-512-specific custom edge tests beyond generated vectors. Any flaw in `hash-test-template.h` affects this suite and other hash suites in the same pattern.

Test signals: verifies update/final sequencing, one-shot/HMAC helper consistency, and performance benchmark availability for SHA-512.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sha512_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sm3-testvecs.h -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sm3-testvecs.h

Purpose: generated SM3 digest test-vector data for the shared KUnit hash template.

Important APIs/types/functions: defines `hash_testvecs[]` with `SM3_DIGEST_SIZE` digests and `hash_testvec_consolidated`. There is no HMAC data in this header because the SM3 driver only maps the plain hash macro set.

Control flow: none locally. The template uses the table to test deterministic generated inputs over the same boundary-oriented lengths used by other hash vector headers, including empty input, block boundaries around 64/128 bytes, and larger multi-block inputs.

State and persistence: constant data only; no mutation, allocation, or persistence.

Dependencies: `SM3_DIGEST_SIZE`, `u8`, `size_t`, and generated-vector conventions. The header was produced by `scripts/crypto/gen-hash-testvecs.py sm3`.

Integration points: included by `sm3_kunit.c` to validate `<crypto/sm3.h>` implementations.

Risks: because the data is generated and compact, input content is implicit; diagnosis requires tracing the shared generator/template. If future SM3 implementation changes alter endian handling or padding, this table should catch it but not explain it.

Test signals: covers SM3 digest correctness across padding and block-boundary cases; no HMAC signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sm3-testvecs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sm3_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crypto/tests/sm3_kunit.c

Purpose: KUnit suite registration for SM3 hash correctness and optional benchmark coverage.

Important APIs/types/functions: maps the shared template to `sm3_ctx`, `sm3_init()`, `sm3_update()`, `sm3_final()`, and `SM3_DIGEST_SIZE`. It registers `sm3_test_cases[]` and `sm3_test_suite`.

Control flow: `HASH_KUNIT_CASES` from `hash-test-template.h` run the generated vector checks, followed by `benchmark_hash`. Module registration occurs through `kunit_test_suite(sm3_test_suite)`.

State and persistence: no local state; template lifecycle manages any shared test buffer.

Dependencies: `<crypto/sm3.h>`, generated `sm3-testvecs.h`, KUnit, and shared hash template.

Integration points: suite name `sm3`; validates the kernel crypto library SM3 implementation for consumers needing the Chinese SM3 hash algorithm.

Risks: coverage is generic and lacks SM3-specific named standard vectors in this file. Failures may need checking both generated vector provenance and implementation endian/padding logic.

Test signals: validates streaming hash behavior and benchmark path for SM3 across generated lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/tests/sm3_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/utils.c -->
# sources/distributed-fs/ceph-client/lib/crypto/utils.c

Purpose: shared crypto utility implementation for bytewise XOR operations behind `crypto_xor()` and `crypto_xor_cpy()`.

Important APIs/types/functions: exports `__crypto_xor(u8 *dst, const u8 *src1, const u8 *src2, unsigned int len)` with `EXPORT_SYMBOL_GPL`. It uses `get_unaligned()`/`put_unaligned()` when efficient unaligned access is configured.

Control flow: on architectures without efficient unaligned access, it computes the relative alignment among `dst`, `src1`, and `src2`, byte-walks until destination alignment matches the relative alignment, then processes as many 64-bit, 32-bit, and 16-bit chunks as alignment permits. Remaining bytes are XORed one at a time. On efficient-unaligned systems, it directly uses unaligned word loads/stores in the wide loops.

State and persistence: no persistent state; only writes to caller-provided `dst`. Aliasing of `dst` with a source is explicitly allowed.

Dependencies: `<crypto/utils.h>`, export/module headers, unaligned access helpers, `CONFIG_64BIT`, and `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS`.

Integration points: common helper for block cipher modes, hash/MAC glue, and any crypto code using the public XOR wrappers.

Risks: alignment logic is subtle; incorrect `relalign` handling can fault on strict-alignment architectures or lose wide-loop optimization. Source/destination overlap is only safe for aliases matching the documented use, not arbitrary partially overlapping ranges. The 64-bit loop is compile-time gated but still sensitive to unaligned helper correctness.

Test signals: no local tests in this subset. Expected validation comes indirectly from crypto self-tests and consumers of `crypto_xor()`/`crypto_xor_cpy()` under varied alignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/aes-aesni.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/aes-aesni.S

Purpose: x86 AES-NI assembly primitives for AES-128/AES-256 key expansion and AES block encryption/decryption.

Important APIs/types/functions: exports `aes128_expandkey_aesni()`, `aes256_expandkey_aesni()`, `aes_encrypt_aesni()`, and `aes_decrypt_aesni()`. Internal macros `_prefix_sum`, `_gen_round_key`, `_aes_expandkey_aesni`, and `_aes_crypt_aesni` implement the shared logic.

Control flow: key expansion copies the raw initial round key(s), generates remaining round keys using AES-NI SubBytes via `aesenclast` plus round constants, and optionally emits equivalent inverse-cipher round keys by reversing the schedule and applying `aesimc` to interior rounds. Encryption/decryption load a block, XOR the initial key, iterate normal AES rounds with `aesenc` or `aesdec`, then apply the last-round instruction and store the block.

State and persistence: writes only caller-provided round-key and output buffers. It uses XMM registers and has i386/x86_64 calling convention branches; no global state.

Dependencies: AES-NI/SSE4.1-era instructions, `linux/linkage.h`, ABI assumptions (`-mregparm=3` on i386), and caller-side FPU context bracketing.

Integration points: called by `x86/aes.h` when CPU feature gates and FPU usability allow it; generic AES is the fallback.

Risks: assembly must match generic expanded-key layout exactly. Inverse-key pointer may be NULL and is checked. AES-192 is deliberately unsupported in the accelerated expander. Wrong round count or key schedule offsets would break all users.

Test signals: expected to be covered by AES crypto library tests and any mode tests exercising encryption/decryption; no local KUnit file in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/aes-aesni.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/aes.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/aes.h

Purpose: x86 architecture dispatch layer for AES key expansion, encryption, and decryption.

Important APIs/types/functions: declares AES-NI assembly functions and defines `aes_preparekey_arch()`, `aes_encrypt_arch()`, `aes_decrypt_arch()`, and `aes_mod_init_arch()`. It owns static key `have_aes`.

Control flow: module init enables `have_aes` if `X86_FEATURE_AES` is present. Key preparation uses AES-NI only for AES-128 and AES-256 and only when `irq_fpu_usable()` is true; AES-192 and unavailable-FPU cases use `aes_expandkey_generic()`. Encrypt/decrypt similarly bracket AES-NI calls in `kernel_fpu_begin()`/`kernel_fpu_end()` or fall back to generic routines.

State and persistence: persistent state is the read-only-after-init static branch. Per-call state is caller-owned key/output buffers. FPU state is temporarily borrowed and restored through kernel FPU APIs.

Dependencies: `<asm/fpu/api.h>`, CPU feature detection, static keys, generic AES functions and key structs from the including implementation.

Integration points: included by the generic AES library source to override architecture hooks via `#define aes_mod_init_arch`.

Risks: FPU availability in interrupt context is critical; bypassing `irq_fpu_usable()` would corrupt kernel FPU state. AES-192 fallback means mixed performance and timing properties across key sizes. Static key enable assumes boot CPU feature uniformity acceptable for this library.

Test signals: AES library self-tests should compare accelerated and generic outputs. Runtime feature gating can be exercised only on matching x86 hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s-core.S

Purpose: x86_64 SIMD compression functions for BLAKE2s, with SSSE3 and AVX-512 implementations.

Important APIs/types/functions: exports `blake2s_compress_ssse3(struct blake2s_ctx *, const u8 *, size_t, u32)` and `blake2s_compress_avx512(...)`. Both use only `h[8]`, `t[2]`, and `f[2]` from the context. Static tables include IV constants, rotate shuffle masks, and sigma message schedules.

Control flow: each main loop processes one 64-byte block. It loads hash state, increments the 64-bit byte counter by `inc`, builds the BLAKE2s working vector from state/IV/counter/final flags, runs 10 rounds of G mixing with scheduled message words, then XORs the compressed state back into `h`. SSSE3 uses byte shuffles and shift/or rotates; AVX-512 uses vector rotates/permutation and ternary XOR.

State and persistence: mutates only the caller's BLAKE2s context (`h` and `t`); `f` is read. No global state. AVX code calls `vzeroupper` before return.

Dependencies: x86_64 SIMD instruction sets, `linux/linkage.h`, caller-side FPU bracketing, and context layout compatibility with the generic BLAKE2s code.

Integration points: selected by `x86/blake2s.h` via static CPU feature branches.

Risks: context layout comments are a hard ABI. Counter increment and final flag handling must match generic compression. Long SIMD execution must be chunked by callers to avoid excessive preemption-off time.

Test signals: BLAKE2s self-tests and WireGuard/crypto users should catch digest mismatches; performance depends on CPU feature selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s.h

Purpose: x86_64 BLAKE2s compression dispatch layer selecting generic, SSSE3, or AVX-512 compression.

Important APIs/types/functions: declares `blake2s_compress_ssse3()` and `blake2s_compress_avx512()`, defines `blake2s_compress()` and `blake2s_mod_init_arch()`, and owns static keys `blake2s_use_ssse3` and `blake2s_use_avx512`.

Control flow: `blake2s_compress()` falls back to generic when SSSE3 is unavailable or `may_use_simd()` is false. Otherwise it processes at most one 4 KiB page worth of blocks per FPU section, choosing AVX-512 if its static key is enabled, else SSSE3. Module init enables SSSE3 on `X86_FEATURE_SSSE3`; AVX-512 requires AVX, AVX2, AVX512F, AVX512VL, and OS xfeature support for SSE/YMM/AVX512 state.

State and persistence: persistent state is static branch configuration after init. Per-call state is the BLAKE2s context and input pointer. FPU/SIMD state is bracketed.

Dependencies: CPU feature checks, `may_use_simd()`, `kernel_fpu_begin/end`, page size constants, generic BLAKE2s compressor, and context definitions from the including source.

Integration points: architecture hook for the BLAKE2s library, often used in fast hashing/MAC contexts.

Risks: using SIMD when preemption or FPU use is not allowed would be unsafe. AVX-512 xfeature detection must match actual instruction use. The 4 KiB chunking assumes compression can resume cleanly by advancing context counter and data pointer.

Test signals: BLAKE2s known-answer tests plus CPU-feature-specific boot/runtime testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/blake2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx2-x86_64.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx2-x86_64.S

Purpose: AVX2 ChaCha block XOR functions for x86_64, processing 2, 4, or 8 blocks per call.

Important APIs/types/functions: exports `chacha_2block_xor_avx2()`, `chacha_4block_xor_avx2()`, and `chacha_8block_xor_avx2()`. Constant tables provide rotate shuffle masks and counter increments.

Control flow: each function loads/broadcasts the input `struct chacha_state`, adds per-lane block counters, runs `nrounds` as repeated double rounds, adds the original state, XORs keystream with source, and stores up to the requested byte length. The 2-block path operates on duplicated state rows requiring word shuffles after column/diagonal phases. The 4/8-block paths operate on corresponding words across blocks and transpose before output. Partial tails use stack scratch space and `rep movsb` to avoid reading/writing past requested bytes.

State and persistence: no global state; writes caller output only. Uses YMM registers and stack scratch; calls `vzeroupper`.

Dependencies: AVX/AVX2 instructions, x86_64 ABI, caller-side FPU bracketing and CPU feature dispatch in `chacha.h`.

Integration points: selected by `chacha_dosimd()` when AVX2 is enabled and input length benefits from multi-block SIMD.

Risks: counter lane setup and caller-side `state->x[12]` advancement must agree. Tail handling is security-sensitive because out-of-bounds reads can leak or fault. ChaCha allows variable `nrounds`; loops assume even round counts.

Test signals: ChaCha/XChaCha known-answer tests, partial-length encryption tests, and guard-buffer tests are needed to catch tail and counter mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx2-x86_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx512vl-x86_64.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx512vl-x86_64.S

Purpose: AVX-512VL/BW ChaCha block XOR functions for x86_64, optimized variants for 2, 4, and 8 blocks.

Important APIs/types/functions: exports `chacha_2block_xor_avx512vl()`, `chacha_4block_xor_avx512vl()`, and `chacha_8block_xor_avx512vl()`. It uses counter constants `CTR2BL`, `CTR4BL`, and `CTR8BL`.

Control flow: like the AVX2 file, functions broadcast/load ChaCha state, add counter lanes, run repeated double rounds, add original state, XOR source, and store output. AVX-512VL paths use `vprold` rotate instructions instead of byte-shuffle or shift/or sequences. Wider register availability lets the 8-block path keep original state in `ymm16`-`ymm31`. Partial final writes use mask registers and masked loads/stores where applicable, reducing scratch handling.

State and persistence: no persistent state. Uses AVX-512 register state and `vzeroupper`; caller must bracket FPU use.

Dependencies: AVX, AVX2, AVX512VL, AVX512BW (`kmovq` use), OS xfeature support as checked by `chacha.h`, and x86_64 ABI.

Integration points: highest-priority SIMD path in `chacha_dosimd()` when the static key is enabled.

Risks: AVX-512 state usage must be gated correctly or the kernel can fault/corrupt state. Masked tail handling must preserve exact byte counts. Counter advancement remains split between assembly lane constants and C dispatcher state mutation.

Test signals: same ChaCha known-answer and partial-length tests as AVX2, plus CPU-feature-specific runtime coverage for AVX-512VL/BW systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-avx512vl-x86_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-ssse3-x86_64.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-ssse3-x86_64.S

Purpose: SSSE3 ChaCha and HChaCha primitives for x86_64, including one-block and four-block encryption paths.

Important APIs/types/functions: local `chacha_permute` implements one-block permutation. Exports `chacha_block_xor_ssse3()`, `hchacha_block_ssse3()`, and `chacha_4block_xor_ssse3()`.

Control flow: `chacha_permute` operates on a state matrix in XMM registers, performing double rounds with SSSE3 byte shuffles for 8/16-bit rotates and shift/or for 7/12-bit rotates, with row shuffles between column and diagonal phases. The one-block XOR path saves original state, permutes, adds state back, XORs source, and handles partial tails via stack scratch copy. HChaCha permutes and stores words 0..3 and 12..15. The four-block path broadcasts state words across lanes, adds counter increments, performs parallel rounds without per-round word shuffles, then transposes for output.

State and persistence: no global state; only caller buffers and stack scratch are mutated. Uses XMM registers under caller-managed FPU context.

Dependencies: SSSE3, x86_64 calling conventions, `linux/linkage.h`, frame macros, and dispatcher in `chacha.h`.

Integration points: baseline SIMD implementation once SSSE3 is available; also used for HChaCha even when AVX2/AVX512 accelerate bulk ChaCha.

Risks: partial-block code must avoid overread/overwrite. HChaCha output word selection must match XChaCha construction. Round-count loop assumes even `nrounds`.

Test signals: ChaCha, HChaCha/XChaCha known-answer vectors and guard-buffer partial-length tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha-ssse3-x86_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/chacha.h

Purpose: x86_64 dispatch layer for ChaCha encryption and HChaCha derivation across generic, SSSE3, AVX2, and AVX-512VL implementations.

Important APIs/types/functions: declares all assembly entry points; defines static keys `chacha_use_simd`, `chacha_use_avx2`, `chacha_use_avx512vl`, helper `chacha_advance()`, dispatcher `chacha_dosimd()`, hooks `hchacha_block_arch()`, `chacha_crypt_arch()`, and `chacha_mod_init_arch()`.

Control flow: init enables SSSE3 baseline, then AVX2 if AVX/AVX2 and YMM xfeatures are available, then AVX512VL if AVX512VL/BW are present. `chacha_crypt_arch()` uses generic for no SIMD or <=1 block, otherwise chunks work to at most 4 KiB per FPU section. `chacha_dosimd()` prefers AVX512VL, then AVX2, then SSSE3, selecting 8/4/2/1-block functions based on remaining byte count and advancing `state->x[12]` by rounded block count.

State and persistence: persistent static keys after init; mutable caller state counter is updated after SIMD calls. No file I/O or persistence.

Dependencies: CPU feature detection, OS xfeature checks, static keys, `kernel_fpu_begin/end`, generic ChaCha/HChaCha functions.

Integration points: architecture hooks for the ChaCha library used by stream cipher and XChaCha consumers.

Risks: counter overflow is not checked here. Incorrect `chacha_advance()` or branch thresholds would desynchronize keystream counters. FPU bracketing and 4 KiB chunking are required for kernel scheduling safety.

Test signals: known-answer vectors across lengths 0..multi-block, state counter advancement tests, and CPU-feature matrix testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/chacha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/curve25519.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/curve25519.h

Purpose: BMI2/ADX-optimized x86_64 Curve25519 scalar multiplication and basepoint multiplication, with generic fallbacks.

Important APIs/types/functions: constant-time helpers `eq_mask()`, `gte_mask()`, field operations `fadd()`, `fsub()`, `fmul()`, `fmul2()`, `fmul_scalar()`, `fsqr()`, `fsqr2()`, `cswap2()`, ladder helpers `point_add_and_double()`, `point_double()`, `montgomery_ladder()`, inversion/encoding helpers `finv()`, `store_felem()`, `encode_point()`, and top-level `curve25519_ever64()` / `curve25519_ever64_base()`. Architecture hooks are `curve25519_arch()`, `curve25519_base_arch()`, and `curve25519_mod_init_arch()`.

Control flow: generic scalar multiplication decodes the public point, masks the top bit, runs a Montgomery ladder with conditional swaps and point add/double operations, then inverts Z and encodes X/Z. Basepoint multiplication uses a generated precomputed ladder table, clamps a copied scalar, iterates scalar bits through table-assisted operations, performs final doublings, encodes, and zeroes temporaries.

State and persistence: persistent state is static key `curve25519_use_bmi2_adx`. Secret temporaries are stack arrays explicitly cleared with `memzero_explicit()` in main paths. Output is caller-provided.

Dependencies: BMI2 `mulx`, ADX `adcx/adox`, constant-time conditional moves, CPU feature checks, generic Curve25519 fallback, and basepoint constants.

Integration points: included by the Curve25519 library as x86 architecture hooks. Used by WireGuard and other X25519 consumers.

Risks: cryptographic constant-time behavior is critical; inline assembly, conditional swaps, table access, and scalar bit loops must not introduce secret-dependent branches or memory addresses beyond intended fixed patterns. Unaligned `u64` loads from `pub` assume x86 tolerance. The precomputed table is large and generated; corruption breaks basepoint multiplication.

Test signals: X25519 known-answer tests, differential tests against generic implementation, all-zero/shared-secret edge cases, and CPU feature fallback tests are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/curve25519.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/gf128hash.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/gf128hash.h

Purpose: x86 dispatch for GF(2^128) GHASH and POLYVAL multiplication/block processing using PCLMULQDQ, with AVX POLYVAL support.

Important APIs/types/functions: declares `polyval_mul_pclmul()`, `polyval_mul_pclmul_avx()`, `ghash_blocks_pclmul()`, and `polyval_blocks_pclmul_avx()`. Defines hooks `polyval_preparekey_arch()`, `ghash_mul_arch()`, `polyval_mul_arch()`, `ghash_blocks_arch()`, `polyval_blocks_arch()`, and `gf128hash_mod_init_arch()`.

Control flow: init enables `have_pclmul` and optionally `have_pclmul_avx`. POLYVAL key preparation stores the raw key in the last `h_powers` slot and fills preceding powers by repeated multiplication, using AVX PCLMUL when possible. Single multiply chooses AVX PCLMUL, non-AVX PCLMUL, or generic based on static keys and `irq_fpu_usable()`. GHASH/POLYVAL block processing uses SIMD in 4 KiB chunks, otherwise generic.

State and persistence: static branch state persists after init. Key-preparation mutates caller key schedules; block functions mutate the accumulator.

Dependencies: PCLMULQDQ, AVX, FPU APIs, generic GF128 hash routines, `struct polyval_elem`, `struct polyval_key`, `struct ghash_key`.

Integration points: architecture hooks for GHASH used by GCM and POLYVAL used by AES-GCM-SIV-like constructions.

Risks: GHASH and POLYVAL have different endian conventions; assembly contracts must match key representation. SIMD use in IRQ/FPU-unusable contexts must fall back. Precomputed power count must stay synchronized with `NUM_H_POWERS`.

Test signals: GHASH/POLYVAL known-answer tests, block-count boundaries, fallback comparison, and feature-specific runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/gf128hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/ghash-pclmul.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/ghash-pclmul.S

Purpose: PCLMULQDQ assembly for GF(2^128) multiplication and GHASH block accumulation.

Important APIs/types/functions: local `__clmul_gf128mul_ble` multiplies two 128-bit operands modulo the GHASH/POLYVAL polynomial in ble representation. Exports `polyval_mul_pclmul()` and `ghash_blocks_pclmul()`.

Control flow: the internal multiply computes low/high carry-less products plus Karatsuba cross term, combines them into a 256-bit product, then reduces modulo the field polynomial in two phases using shifts and XORs. `polyval_mul_pclmul()` loads two operands, calls the internal multiply, and stores the result. `ghash_blocks_pclmul()` loads an accumulator and key, byte-swaps each input block with `pshufb`, XORs it into the accumulator, multiplies, and loops for `nblocks`.

State and persistence: mutates only caller-provided accumulator/operand memory. Uses XMM registers and no global state.

Dependencies: PCLMULQDQ, SSSE3 `pshufb` for byte swap, x86_64 frame macros, caller-side FPU context handling in `gf128hash.h`.

Integration points: called by the GF128 hash architecture dispatch for GHASH and POLYVAL.

Risks: endian conversion is central; a wrong byte-swap mask breaks GHASH while POLYVAL direct multiply may still appear correct. `nblocks` is expected nonzero when called; callers control chunking and fallback.

Test signals: AES-GCM GHASH known answers, POLYVAL multiplication vectors, and comparison against generic implementation across multiple blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/ghash-pclmul.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/nh-avx2.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/nh-avx2.S

Purpose: AVX2 accelerated NH ε-almost-universal hash function for x86_64.

Important APIs/types/functions: exports `nh_avx2(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. Internal macro `_nh_2xstride` processes two NH strides in parallel.

Control flow: the function initializes four pass accumulators, preloads key vectors, and processes 64-byte chunks in a loop. Each stride adds message words to keyed words, shuffles 32-bit pairs, performs unsigned 32x32-to-64 multiplies with `vpmuludq`, and accumulates 64-bit sums for four passes. Remainders of 16, 32, or 48 bytes are handled with partial vector paths; the final single stride zeroes high lanes to avoid incorporating garbage. Horizontal reductions combine vector lanes into four `__le64` pass outputs.

State and persistence: no persistent state; writes only the output hash array. Uses YMM registers and calls `vzeroupper`.

Dependencies: AVX2, x86_64 ABI, key/message alignment tolerance through unaligned loads, and caller-side FPU bracketing.

Integration points: selected by `nh.h` when message length is at least 64 bytes and AVX2 is available.

Risks: message length is guaranteed by caller to be a multiple of 16; violating that would read beyond the valid message. Remainder handling and horizontal sum ordering must match generic NH exactly.

Test signals: NH known-answer/differential tests against generic, especially lengths 16, 32, 48, 64, and non-multiple-of-64 multiples of 16.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/nh-avx2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/nh-sse2.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/nh-sse2.S

Purpose: SSE2 accelerated NH hash implementation for x86_64.

Important APIs/types/functions: exports `nh_sse2(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. Macro `_nh_stride` processes one 16-byte stride for four NH passes.

Control flow: initializes pass accumulators and preloads the first key vectors. The main loop handles four 16-byte strides per 64-byte chunk, rotating key registers through `_nh_stride`. Each stride loads message and key words, adds them, shuffles 32-bit values into multiply pairs, uses `pmuludq` for 32x32-to-64 products, and accumulates pass sums. Tail handling processes one to three remaining 16-byte strides. Final reduction packs and adds low/high accumulator lanes into four 64-bit outputs.

State and persistence: no global state; writes caller hash buffer only. Uses XMM registers under FPU context managed by the caller.

Dependencies: SSE2, x86_64 ABI, NH generic contract that `message_len % 16 == 0`, and dispatch in `nh.h`.

Integration points: baseline x86 SIMD path when SSE2 is present and AVX2 is unavailable.

Risks: assumes message/key buffers are valid for the guaranteed multiple-of-16 length. Register-rotation macro is dense; ordering mistakes produce pass-specific mismatches. No `vzeroupper` is needed for SSE-only code.

Test signals: generic-vs-SSE2 differential tests over boundary lengths and randomized keys/messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/nh-sse2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/nh.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/nh.h

Purpose: x86 architecture dispatch for the NH universal hash.

Important APIs/types/functions: declares `nh_sse2()` and `nh_avx2()`, defines static keys `have_sse2` and `have_avx2`, implements `nh_arch()`, and provides `nh_mod_init_arch()`.

Control flow: module init enables SSE2 on `X86_FEATURE_XMM2`, then AVX2 when CPU feature and OS SSE/YMM xfeatures are available. `nh_arch()` uses SIMD only for messages at least 64 bytes, when SSE2 is enabled, and when `irq_fpu_usable()` is true. It brackets the selected SSE2/AVX2 assembly call in `kernel_fpu_begin/end()` and returns true; otherwise it returns false so the generic caller can handle the message.

State and persistence: static branch state persists after init. Per-call state is the caller's key, message, and hash output.

Dependencies: FPU APIs, static keys, CPU feature detection, `NH_NUM_PASSES`, and generic NH caller fallback.

Integration points: included by the NH library as an optional architecture hook, likely for Adiantum/HPolyC-style constructions.

Risks: short messages intentionally use generic code; callers must respect the boolean return. SIMD use depends on IRQ/FPU context. AVX2 xfeature gating must match assembly use or faults can occur.

Test signals: dispatch tests should confirm false return for short/FPU-unusable paths and correct outputs for SSE2 and AVX2 paths compared with generic NH.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/nh.h -->
