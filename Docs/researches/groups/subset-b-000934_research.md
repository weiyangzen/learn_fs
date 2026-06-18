# subset-b-000934 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fcrypt.c -->
# sources/distributed-fs/ceph-client/crypto/fcrypt.c

Purpose: Implements the generic `fcrypt` 64-bit block cipher used by the kernel crypto API. It is a legacy DES-like 16-round Feistel cipher with 8-byte keys where each input key byte has one parity bit ignored, leaving 56 effective bits.

Important APIs/types/functions: `struct fcrypt_ctx` stores 16 big-endian round schedules. `fcrypt_setkey()` discards parity bits and rotates the 56-bit key material by 11 bits per round. `F_ENCRYPT()` applies the round function through four fixed S-box tables. `fcrypt_encrypt()` and `fcrypt_decrypt()` unroll all rounds in opposite orders. `fcrypt_alg` registers the cipher under `fcrypt`/`fcrypt-generic` with 8-byte block and key sizes.

Control flow: Module init calls `crypto_register_alg()`. Setkey expands the caller key into `ctx->sched[]`, using a 64-bit path on 64-bit builds and a split high/low 56-bit path otherwise. Encryption copies an 8-byte block into left/right big-endian halves, alternates the Feistel macro for 16 schedules, and writes the resulting block. Decryption uses the same macro with schedules reversed.

State and persistence behavior: Persistent transform state is only the per-tfm schedule array. The S-boxes and registration object are static read-only module data. No IV, request state, filesystem state, or durable storage is involved.

Dependencies and integration points: Depends on `<crypto/algapi.h>` and the classic `crypto_alg` cipher frontend. Consumers obtain it by name through the kernel crypto API, including any filesystem or network code that still needs rxkad/AFS-compatible FCrypt behavior.

Risks: This is legacy crypto with a small block and effective 56-bit key, so new protocols should avoid it. Correctness depends on endian handling, parity-bit removal, and schedule rotation matching historical implementations. The table-driven S-box path is not constant-time with respect to secret-dependent table indices on all hardware.

Test signals: Kernel crypto manager known-answer tests for `fcrypt`, encrypt/decrypt round trips, module load/unload registration, and compatibility vectors from AFS/rxkad are the main signals. Cross-architecture tests should cover both 64-bit and non-64-bit key schedule paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fcrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fips.c -->
# sources/distributed-fs/ceph-client/crypto/fips.c

Purpose: Provides the kernel crypto FIPS-mode switch, metadata sysctls, and a notification hook for crypto subsystem FIPS failures.

Important APIs/types/functions: `fips_enabled` is the exported global mode flag. `fips_fail_notif_chain` is an exported blocking notifier chain. `fips_enable()` parses the early `fips=` boot option. The sysctl table exposes `fips_enabled`, `fips_name`, and `fips_version` under `/proc/sys/crypto`. `fips_fail_notify()` calls the failure notifier chain.

Control flow: At early boot, `__setup("fips=", fips_enable)` sets `fips_enabled` when the option is nonzero. Module init registers the crypto sysctl table; exit unregisters it. Runtime callers invoke `fips_fail_notify()` to broadcast a FIPS module failure to registered listeners.

State and persistence behavior: `fips_enabled` is global process lifetime state set by boot parameters and exported read-only via sysctl mode `0444`. Module name/version strings are static. The notifier chain has kernel runtime registrations but no persisted state.

Dependencies and integration points: Integrates with Linux sysctl, notifier chains, `utsrelease`, and crypto code that gates behavior on `fips_enabled`, such as HMAC key length checks, KDF self-test handling, and jitterentropy panic-on-permanent-health-failure paths.

Risks: Treating `fips_enabled` as a mutable ordinary integer can produce inconsistent policy if code attempts late writes, although the exposed sysctl is read-only. Notifier callbacks run in a blocking chain and must avoid unsafe contexts. FIPS enforcement is distributed; missing checks in individual algorithms are not caught here.

Test signals: Boot with `fips=0` and `fips=1`, verify `/proc/sys/crypto/fips_enabled`, `fips_name`, and `fips_version`, trigger algorithm self-test/failure paths, and validate notifier callbacks receive `fips_fail_notify()` events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/gcm.c -->
# sources/distributed-fs/ceph-client/crypto/gcm.c

Purpose: Implements AEAD templates for Galois/Counter Mode and IPsec-specific GCM wrappers: `gcm`, `gcm_base`, `rfc4106`, and `rfc4543`.

Important APIs/types/functions: `struct crypto_gcm_ctx` owns a CTR skcipher child and prepared GHASH key. `crypto_gcm_setkey()` keys CTR, encrypts the zero block to derive GHASH H, and prepares the GF(2^128) key. `crypto_gcm_encrypt()` and `crypto_gcm_decrypt()` build synthetic scatterlists that prepend the encrypted counter block, run CTR, compute GHASH over AAD/ciphertext/lengths, append or verify tags. `crypto_rfc4106_*()` adapts GCM for ESP with a salt stored in the last four key bytes and IV/AAD reshaping. `crypto_rfc4543_*()` adapts GMAC/authentication-only ESP mode. Template create functions validate child IV size, blocksize, names, priorities, and request sizes.

Control flow: Template registration happens in `crypto_gcm_module_init()`. Instantiation grabs a CTR or AEAD child, validates it is stream-like with 12-byte GCM IV where required, and registers an AEAD instance. Runtime setkey propagates request flags and configures child keys. Encryption initializes `J0`, encrypts the counter block plus plaintext, hashes AAD and ciphertext, XORs GHASH with the encrypted counter block, and writes the auth tag. Decryption hashes ciphertext first, decrypts data, and compares the expected tag with `crypto_memneq()`.

State and persistence behavior: Per-tfm state stores child crypto handles, the 4-byte IPsec salt for RFC wrappers, and GHASH precomputation. Per-request state stores aligned IVs, authentication tags, temporary scatterlists, and child requests. There is no durable persistence, but child transform lifetime and request memory alignment are critical.

Dependencies and integration points: Uses `crypto/internal/aead.h`, skcipher spawns, `gf128hash` GHASH helpers, scatterwalk utilities, `crypto/gcm.h` authsize/assoclen validators, and the template registry. It is a core provider for IPsec, storage, and other AEAD users requesting GCM by name.

Risks: IV and AAD layout is security-critical, especially RFC4106/RFC4543 salt and assoclen handling. Scatterlist forwarding/chaining errors can hash or encrypt the wrong bytes. Authentication tag comparison must remain constant-time. Counter/IV reuse is not prevented here and must be enforced by callers/protocols. Async completion paths must call the final tag operation exactly once.

Test signals: Crypto manager GCM vectors, RFC4106 and RFC4543 ESP vectors, in-place and out-of-place scatterlist tests, async child completion tests, invalid authsize/assoclen rejection, bad-tag `-EBADMSG` behavior, and module alias/template instantiation by `gcm(aes)`, `gcm_base(ctr(aes),ghash)`, `rfc4106(gcm(aes))`, and `rfc4543(gcm(aes))`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/gcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/geniv.c -->
# sources/distributed-fs/ceph-client/crypto/geniv.c

Purpose: Provides shared helper code for AEAD IV generator templates such as `seqiv`, wrapping a child AEAD while adding salt setup and common instance initialization.

Important APIs/types/functions: `aead_geniv_alloc()` creates an `aead_instance`, grabs the child AEAD, validates that the IV is at least `sizeof(u64)`, copies naming/priority/block/alignment/auth metadata, and installs common `setkey`/`setauthsize` forwarding. `aead_init_geniv()` obtains random salt with `crypto_stdrng_get_bytes()`, spawns the child, and sizes requests. `aead_exit_geniv()` frees the child. `aead_geniv_free()` drops the spawn and instance.

Control flow: A specific geniv template calls `aead_geniv_alloc()` during template create, then uses `aead_init_geniv()` and `aead_exit_geniv()` as its transform lifecycle hooks. Runtime key/authsize setters simply forward to `ctx->child`; actual IV construction is left to the specific generator implementation.

State and persistence behavior: `struct aead_geniv_ctx` in the transform context holds the child AEAD and generated salt. Salt persists for the transform lifetime only. Spawn references persist in the instance until the template instance is freed.

Dependencies and integration points: Uses internal AEAD and RNG APIs, crypto template attributes, rtnetlink-safe allocation context indirectly through kernel crypto users, and exports all three helper symbols GPL-only for other crypto modules.

Risks: IV size validation is minimal; generator-specific code must ensure nonce uniqueness. Failure cleanup must drop both child spawns and instances without double frees. Salt generation failure prevents transform initialization and must propagate to callers.

Test signals: Load geniv consumers, instantiate templates with valid and too-small-IV child AEADs, verify setkey/authsize forwarding, confirm request size accounts for child request plus wrapper request, and test salt randomness/failure paths with RNG availability issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/geniv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hash.h -->
# sources/distributed-fs/ceph-client/crypto/hash.h

Purpose: Local internal header connecting hash frontend code to the core crypto internals.

Important APIs/types/functions: Declares `extern const struct crypto_type crypto_shash_type` and `int hash_prepare_alg(struct hash_alg_common *alg)`. Includes `<crypto/internal/hash.h>` and local `internal.h`.

Control flow: This header has no executable flow. Compilation units include it when they need shared hash registration/type preparation declarations.

State and persistence behavior: No state is stored. The declarations refer to crypto type metadata and algorithm preparation implemented elsewhere.

Dependencies and integration points: Bridges hash code to `struct hash_alg_common`, the shash frontend, and the internal crypto algorithm registry helpers in `internal.h`.

Risks: Because it exposes internal symbols, declaration drift with the implementation can break shash registration or module linkage. It intentionally is not a public UAPI header.

Test signals: Build coverage of hash/shash modules, successful shash algorithm registration, and no unresolved symbol or type mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hctr2.c -->
# sources/distributed-fs/ceph-client/crypto/hctr2.c

Purpose: Implements the `hctr2` and `hctr2_base` skcipher templates for length-preserving encryption using a 16-byte block cipher, XCTR stream mode, and POLYVAL hashing.

Important APIs/types/functions: `struct hctr2_tfm_ctx` owns the block cipher, XCTR skcipher, prepared POLYVAL key, prehashed tweak-length blocks, and `L = E_K(1)`. `hctr2_setkey()` keys both children, derives `H = E_K(0)`, `L`, and precomputed tweak hashes. `hctr2_crypt()` handles both encryption and decryption. `hctr2_hash_tweak()`, `hctr2_hash_message()`, and `hctr2_finish()` implement the HCTR2 hash/encrypt/hash construction. Template create functions validate `xctr(<cipher>)`, derive the underlying block cipher name, require 16-byte block size, and expose a 32-byte tweak as the IV.

Control flow: Create grabs the `xctr` child and matching raw block cipher, then registers a skcipher instance. Runtime requires `cryptlen >= 16`; it copies the first block, forwards scatterlists past the first block for the bulk part, hashes tweak plus bulk data, block-encrypts or decrypts the first-block mask, computes the XCTR IV, runs XCTR over the bulk portion, and after async completion hashes the transformed bulk to write the final first block.

State and persistence behavior: Per-transform state persists child handles and derived POLYVAL/blockcipher material until exit. Per-request state holds the copied first block, XCTR IV, forwarded scatterlists, saved hashed tweak, and a union reused as POLYVAL context or child skcipher request. No disk or global mutable state is maintained.

Dependencies and integration points: Uses internal cipher/skcipher template APIs, `polyval-lib` through `gf128hash.h`, scatterwalk helpers, and imports the `CRYPTO_INTERNAL` namespace. Fscrypt is a key expected consumer because the implementation chooses a 32-byte fixed tweak size to avoid per-file key derivation in some use cases.

Risks: Length-preserving modes are sensitive to exact byte ordering, padding marker handling for partial final blocks, and tweak hashing. The request context union is space-sensitive and protected by a `BUILD_BUG_ON`; layout changes can corrupt child requests. Async XCTR completion must run final hashing once. Inputs shorter than one block are rejected.

Test signals: HCTR2 known-answer vectors, encrypt/decrypt round trips for exact-block and partial-block lengths, 32-byte tweak behavior, in-place/out-of-place scatterlists, async child XCTR completion, template instantiation through `hctr2(aes)` and `hctr2_base(xctr(aes),polyval-lib)`, and fscrypt integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hctr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hmac.c -->
# sources/distributed-fs/ceph-client/crypto/hmac.c

Purpose: Implements `hmac` templates for both synchronous hash (`shash`) and asynchronous hash (`ahash`) frontends, wrapping an unkeyed hash algorithm with RFC2104 HMAC processing.

Important APIs/types/functions: `struct hmac_ctx` and `struct ahash_hmac_ctx` store child hash handles plus exported inner and outer pad states. `hmac_setkey()` and `hmac_setkey_ahash()` hash oversized keys, enforce a 112-bit minimum in FIPS mode, build ipad/opad, and export preinitialized hash states. Shash operations include init/update/finup/export/import and core export/import. Ahash operations mirror them with child `ahash_request` forwarding and async finup completion. `hmac_create()` selects ahash or shash based on requested type, while `hmac-shash` forces shash.

Control flow: Template creation grabs an unkeyed child hash, rejects keyed children and invalid digest/state sizes, names the instance, and registers it. Setkey prepares reusable inner/outer states. A digest operation imports the inner state, processes data, finalizes the inner digest, imports the outer state, and hashes the inner digest to produce the HMAC. Ahash finup may complete synchronously or through `hmac_finup_done()`.

State and persistence behavior: Per-transform state stores child transform references and pad-state snapshots for the transform lifetime. Per-request state stores child descriptors/requests. Sensitive request and key-derived buffers are zeroed with stack/request zero helpers or sensitive frees where used.

Dependencies and integration points: Uses `crypto/hmac.h`, internal hash template APIs, Linux FIPS mode, ahash virtual request support, and the crypto template registry. It is foundational for KDFs, Kerberos, IPsec, and many kernel authentication users.

Risks: Underlying hashes requiring keys are deliberately rejected; missing that check would create nested keyed semantics. Exported state sizes must be at least the block size or pad export would overrun. Ahash request sizing is validated because wrapper requests embed child requests. FIPS key-length rejection can break callers that previously used short keys.

Test signals: HMAC known-answer tests for shash and ahash, long-key normalization, export/import and export_core/import_core, async completion paths, invalid child hash rejection, FIPS short-key rejection, clone_tfm behavior, and template lookup for `hmac(sha256)` and `hmac-shash(sha256)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/internal.h -->
# sources/distributed-fs/ceph-client/crypto/internal.h

Purpose: Declares core internal crypto API structures and helpers shared by algorithm lookup, larval/test handling, template/type frontends, transform allocation, proc reporting, notifications, and reference management.

Important APIs/types/functions: `struct crypto_larval` represents a placeholder algorithm awaiting testing or module resolution. `struct crypto_type` defines frontend-specific callbacks and sizing. The header declares algorithm lookup/allocation (`crypto_find_alg()`, `crypto_alg_mod_lookup()`, `crypto_alloc_tfm_node()`), larval testing (`crypto_larval_alloc()`, `crypto_schedule_test()`, `crypto_alg_tested()`), spawn removal, transform creation/clone helpers, notifier helpers, module/template ref helpers, and predicates for larval/dead/moribund algorithms.

Control flow: Runtime crypto allocation uses frontend `crypto_type` metadata to find an algorithm, load modules if needed, create a transform on a NUMA node, and run algorithm tests through larvals before making an adult algorithm visible. Registration/removal paths use the declared global algorithm list, semaphore, notifier chain, and spawn cleanup helpers.

State and persistence behavior: Declares global registry state: `crypto_alg_sem`, `crypto_alg_list`, `crypto_chain`, and optionally the static key marking boot self-test completion. Algorithm and transform lifetimes are reference-counted through `crypto_alg_get/put()`, template module refs, and `crypto_tfm_get()`.

Dependencies and integration points: Pulls in algapi, notifier, completion, module, NUMA, refcount, scatterlist, and scheduler primitives. It is consumed by many crypto core frontends, including hash, kpp, skcipher, aead, and template implementations.

Risks: This is central registry infrastructure. Reference-counting mistakes can leak modules or free algorithms while still visible. Larval/test state races can expose untested algorithms or block lookups. Static-key behavior differs when algapi is modular or selftests are disabled, so boot-test assumptions must match config.

Test signals: Crypto manager selftests, module autoload lookup, concurrent algorithm registration/removal, `/proc/crypto` reporting when enabled, notifier events, transform clone/allocation tests, and KASAN/KCSAN coverage of algorithm lifetime and larval completion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-kcapi.c -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy-kcapi.c

Purpose: Adapts the standalone jitterentropy collector to the Linux kernel crypto RNG API as `jitterentropy_rng`, providing allocation, time/hash primitives, initialization tests, and runtime generation.

Important APIs/types/functions: `jent_kvzalloc()`, `jent_kvzfree()`, `jent_zalloc()`, and `jent_zfree()` are memory hooks for the standalone code. `jent_get_nstime()` samples `random_get_entropy()` or `ktime_get_ns()` and feeds the optional test interface. `jent_hash_time()` and `jent_read_random_block()` implement SHA3-256 conditioning. `struct jitterentropy` stores a mutex, collector pointer, and SHA3 state. `jent_kcapi_init()`, `jent_kcapi_cleanup()`, `jent_kcapi_random()`, and `jent_kcapi_reset()` provide the RNG transform operations.

Control flow: Module init enables the test interface, runs `jent_entropy_init()` with configured oversampling, and registers the RNG only if startup health/timer checks pass. Transform init initializes SHA3 and allocates a collector. Generate locks the transform, calls `jent_read_entropy()`, maps collector errors to `-EAGAIN`, `-EFAULT`, or `-EINVAL`, and panics on permanent health-test failure in FIPS mode.

State and persistence behavior: Each RNG transform has independent collector state and SHA3 pool protected by `jent_lock`. Module-level state is limited to crypto registration and optional debugfs test setup. Sensitive SHA3 and collector memory are zeroed/freed on cleanup.

Dependencies and integration points: Integrates with `crypto/internal/rng.h`, SHA3 primitives, Linux timing sources, FIPS policy, KMSAN unpoisoning, and `jitterentropy-testing.c` through `jent_raw_hires_entropy_store()`.

Risks: Entropy quality depends on high-resolution timer behavior and compiler constraints from `jitterentropy.c`. Permanent health failures in FIPS mode intentionally panic the kernel. Locking serializes generation per transform; misuse without the mutex would corrupt collector state. `seed()` is a no-op, so callers cannot reseed this RNG externally.

Test signals: Module load on supported/unsupported timers, RNG generation through the crypto API, FIPS and non-FIPS permanent/intermittent health failure behavior, debugfs raw timer capture when enabled, KMSAN clean output buffers, and repeated init/exit leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-kcapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-testing.c -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy-testing.c

Purpose: Provides an optional debugfs interface for collecting raw high-resolution timing samples from jitterentropy for SP800-90B style analysis and boot-time data capture.

Important APIs/types/functions: `struct jent_testing` stores a 1024-entry u64 ring buffer, reader/writer indices, enable flag, spinlock, and waitqueue. `jent_testing_store()` records samples and handles boot-test state transitions. `jent_testing_reader()` drains samples into an aligned kernel buffer, optionally blocking for runtime samples. `jent_testing_extract_user()` copies chunks to userspace. `jent_raw_hires_entropy_store()` is the exported producer hook, and `jent_testing_init()/exit()` create/remove `debugfs/<module>/jent_raw_hires`.

Control flow: On init, debugfs is created. Every `jent_get_nstime()` call may call the store hook. Reads from `jent_raw_hires` enable runtime collection unless boot capture is active, drain u64 samples in chunks, block on the waitqueue if no data is available, and disable/reset runtime capture when done.

State and persistence behavior: State is module-global in `jent_raw_hires` and `boot_raw_hires_test`. Boot mode keeps the collected buffer available until read; runtime mode resets the buffer on entry/exit. No data persists beyond module lifetime or debugfs removal.

Dependencies and integration points: Depends on debugfs, module parameters, wait queues, spinlocks, atomics, user copy helpers, and the jitterentropy header. The production code calls it through inline no-ops when `CONFIG_CRYPTO_JITTERENTROPY_TESTINTERFACE` is disabled.

Risks: This intentionally exposes raw timing data through debugfs and should remain optional and root-readable. Ring buffer wrap and boot-state transitions must avoid losing the first boot samples unexpectedly. Reader blocking must handle signals and scheduling. `debugfs_create_file_unsafe()` is acceptable only because lifetime is controlled by module teardown.

Test signals: Enable the config, read `jent_raw_hires`, verify u64-aligned sample counts, exercise `boot_raw_hires_test=1`, interrupt a blocking read, test multiple partial reads for at least 1000 samples, and ensure debugfs cleanup removes all files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy-testing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.c -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy.c

Purpose: Contains the standalone CPU jitter entropy collector core, using timing variation, optional memory access noise, SHA3-256 conditioning, and SP800-90B health tests to produce random bytes.

Important APIs/types/functions: `struct rand_data` stores SHA3 pool state, previous timing deltas, oversampling rate, optional memory buffer, RCT/APT counters, and health failure bits. `jent_measure_jitter()` performs memory access, samples time, computes deltas, runs stuck/RCT/APT tests, and conditions the data. `jent_gen_entropy()` collects enough non-stuck measurements. `jent_read_entropy()` returns conditioned bytes and handles health failures. `jent_entropy_collector_alloc/free()` manage collector memory. `jent_entropy_init()` performs startup timer and health tests.

Control flow: Allocation optionally allocates a configured memory area, initializes oversampling and APT cutoff values, and primes the entropy pool. Generation primes `prev_time`, then loops until `(DATA_SIZE_BITS + safety_factor) * osr` good measurements are collected or a FIPS health failure appears. Read requests repeatedly generate a 256-bit block, check health status, extract bytes through the SHA3 conditioner, and return transient/permanent errors when needed. Startup initialization runs 1024 test measurements after cache-clearing iterations and rejects unavailable, coarse, or non-monotonic timers.

State and persistence behavior: Collector state persists across reads and includes sensitive hash/timing data. APT/RCT health state is retained, with intermittent bits reset during reinitialization and permanent bits preserved. Optional memory noise storage persists for the collector lifetime and is freed sensitively.

Dependencies and integration points: This file intentionally avoids normal optimized compilation and relies on hooks from `jitterentropy-kcapi.c` for timing, allocation, hashing, and output extraction. It reads `fips_enabled` to enable runtime health-test enforcement and extra safety-factor collection.

Risks: The file must be compiled with optimizations disabled, as enforced by `#ifdef __OPTIMIZE__`. Entropy assumptions are hardware/timer dependent and validated only by startup and health tests. FIPS mode changes runtime behavior and can cause permanent failures. Off-by-one errors in RCT/APT cutoffs or masking would affect compliance. The collector is stateful and must be externally serialized.

Test signals: Startup return codes for missing/coarse/nonmonotonic timers, RCT/APT induced failure tests, FIPS vs non-FIPS health behavior, statistical/raw-data collection through the test interface, memory-access enabled/disabled configurations, oversampling values, and repeated reads of non-block-sized output lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.h -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy.h

Purpose: Declares the interface between the standalone jitterentropy core, the kernel crypto API adapter, and the optional test interface.

Important APIs/types/functions: Declares allocation hooks, `jent_get_nstime()`, SHA3 conditioning hooks `jent_hash_time()` and `jent_read_random_block()`, opaque `struct rand_data`, collector lifecycle `jent_entropy_collector_alloc/free()`, initialization `jent_entropy_init()`, and generation `jent_read_entropy()`. It also exposes `jent_raw_hires_entropy_store()`, `jent_testing_init()`, and `jent_testing_exit()` or inline no-ops depending on `CONFIG_CRYPTO_JITTERENTROPY_TESTINTERFACE`.

Control flow: No executable flow exists in the header except test-interface no-op inlines. Including files use it to call from the collector into kernel-provided hooks and from the kernel adapter into the collector.

State and persistence behavior: The header stores no state. It defines the opaque collector boundary so `struct rand_data` state remains private to `jitterentropy.c`.

Dependencies and integration points: Depends on `struct sha3_ctx` and kernel fixed-width integer types. Bridges `jitterentropy.c`, `jitterentropy-kcapi.c`, and `jitterentropy-testing.c`.

Risks: Prototype mismatches would break the delicate separation between standalone and kernel-specific code. Inline no-ops must exactly match optional test behavior so production builds do not depend on debugfs symbols.

Test signals: Build both with and without `CONFIG_CRYPTO_JITTERENTROPY_TESTINTERFACE`, verify no unresolved symbols, and run jitterentropy module init/generation in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/kdf_sp800108.c -->
# sources/distributed-fs/ceph-client/crypto/kdf_sp800108.c

Purpose: Implements the SP800-108 counter-mode KDF using a keyed `shash` MAC, plus a self-test vector for HMAC-SHA256.

Important APIs/types/functions: `crypto_kdf108_ctr_generate()` emits KDF output by repeatedly MACing a big-endian 32-bit counter followed by caller-provided info vectors. `crypto_kdf108_setkey()` rejects IKM, enforces key length at least the MAC digest size, and keys the MAC. `kdf_ctr_hmac_sha256_tv_template` provides a NIST CAVP-derived test vector. `crypto_kdf108_init()` runs the test when crypto selftests are enabled.

Control flow: Callers first set the MAC key, then request output. Generation initializes the shash for each block, updates with counter and all info kvecs, copies full digest blocks or a truncated final block, increments the counter, and zeroes all output if an error occurs. Module init conditionally runs `kdf_test()` and panics on self-test failure in FIPS mode.

State and persistence behavior: The function itself maintains only stack descriptor/counter state. The keyed MAC transform supplied by the caller holds persistent key state. Temporary partial digest buffers are zeroed.

Dependencies and integration points: Uses `<crypto/kdf_sp800108.h>`, internal KDF selftest helpers, shash APIs, Linux `kvec`, and `fips_enabled`. Exported symbols are available to kernel consumers needing SP800-108 derivation.

Risks: Counter mode has a finite counter space; this implementation does not explicitly reject wrap for very large outputs. Info vector ordering and length are caller-controlled and must match protocol definitions. Zeroing all output on error is important to prevent partial-key use. The SP800-108 check rejects IKM by design, which may surprise callers expecting HKDF-like input.

Test signals: The built-in HMAC-SHA256 vector, multi-block and partial-final-block outputs, multiple info vectors, error injection from shash operations, FIPS panic/warn behavior on self-test failure, and invalid key/IKM rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/kdf_sp800108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/khazad.c -->
# sources/distributed-fs/ceph-client/crypto/khazad.c

Purpose: Implements the generic Khazad 64-bit block cipher with a 128-bit key for the kernel crypto API.

Important APIs/types/functions: `struct khazad_ctx` stores encryption and decryption round-key arrays. Large `T0` through `T7` lookup tables and constants `c[]` implement the Khazad round transformations. `khazad_setkey()` derives encryption keys and inverse decryption keys. `khazad_crypt()` applies the 8-round table-based permutation. `khazad_encrypt()` and `khazad_decrypt()` select the round-key array. `khazad_alg` registers `khazad-generic`.

Control flow: Module init registers the cipher. Setkey reads two big-endian 64-bit halves, iterates constants to fill `E[]`, then derives `D[]` from reversed encryption keys through table substitutions. Runtime crypt XORs the initial round key, runs rounds 1 through 7 with full T-table mixing, performs a final masked table round, and writes the big-endian output block.

State and persistence behavior: Per-transform state is the expanded key schedule only. All T-tables and constants are static module data. There is no IV, request context, or durable state.

Dependencies and integration points: Uses the classic crypto cipher API, unaligned big-endian helpers, Linux module registration, and any mode wrapper that can use an 8-byte block cipher by name.

Risks: Khazad is a legacy/niche cipher and should not be selected for new designs without a protocol requirement. Table lookups are secret-dependent and may be side-channel relevant. Key length is fixed at 16 bytes and relies on the crypto API to enforce min/max sizes. The 64-bit block size limits safe data volume in block modes.

Test signals: Khazad known-answer vectors, encrypt/decrypt inverse tests, unaligned input/output tests, module registration by name, and mode-wrapper tests over 8-byte blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/khazad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/kpp.c -->
# sources/distributed-fs/ceph-client/crypto/kpp.c

Purpose: Implements the kernel crypto frontend/type plumbing for Key-agreement Protocol Primitives (KPP), such as Diffie-Hellman style algorithms.

Important APIs/types/functions: `crypto_kpp_type` defines type metadata, report/proc callbacks, init/free hooks, and layout offsets. `crypto_alloc_kpp()`, `crypto_grab_kpp()`, and `crypto_has_kpp()` expose lookup/spawn helpers. `crypto_register_kpp()`, `crypto_unregister_kpp()`, and `kpp_register_instance()` register raw algorithms and template instances. `crypto_kpp_init_tfm()` and `crypto_kpp_exit_tfm()` call algorithm-specific init/exit hooks.

Control flow: Registration calls `kpp_prepare_alg()` to set `cra_type` and KPP flags before registering with the core. Allocation uses `crypto_alloc_tfm()` with `crypto_kpp_type`. Transform init installs an exit wrapper if the algorithm has one, then calls the algorithm init hook. Instance registration requires an instance free callback before registering with the template core.

State and persistence behavior: This file stores no per-algorithm key material itself. It controls transform lifetime state through the embedded `crypto_tfm` and algorithm callbacks. KPP algorithm objects are registered in the global crypto registry.

Dependencies and integration points: Includes internal KPP APIs, cryptouser netlink reporting, `/proc/crypto` reporting, and shared crypto internal registry helpers. Consumers include key agreement implementations and templates that spawn KPP children.

Risks: Frontend layout offsets must match `struct crypto_kpp` and `struct kpp_alg`. Missing `inst->free` would leak template instances, so it is warned/rejected. Algorithm init/exit callbacks are trusted to manage private state and must be paired correctly.

Test signals: KPP algorithm registration/unregistration, `crypto_alloc_kpp()` lookup, template spawn with `crypto_grab_kpp()`, `/proc/crypto` and netlink reports, algorithms with and without init/exit hooks, and instance free callback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/kpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Kconfig -->
# sources/distributed-fs/ceph-client/crypto/krb5/Kconfig

Purpose: Defines build configuration for the Kerberos 5 crypto library and its optional selftests.

Important APIs/types/functions: `config CRYPTO_KRB5` is a tristate option selecting crypto manager, Kerberos encryption wrapper, authenc, skcipher, hash metadata, HMAC, CMAC, SHA1, SHA256, SHA512, CBC, CTS, AES, and Camellia. `config CRYPTO_KRB5_SELFTESTS` is a bool depending on `CRYPTO_KRB5`.

Control flow: Kconfig selection determines whether the Kerberos crypto module is built and which dependent algorithms are guaranteed available. Enabling selftests compiles and runs additional module-load checks through `krb5_selftest()`.

State and persistence behavior: No runtime state. It persists only as kernel build configuration.

Dependencies and integration points: Intended for network filesystems, as stated in help text. It ensures the Kerberos implementation can instantiate all encryption/checksum names referenced by the profile files.

Risks: Adding an enctype without updating Kconfig selects can produce runtime `-ENOPKG` when a dependent cipher/hash is missing. Selftests are optional, so production builds may lack module-load vector validation.

Test signals: Kconfig dependency resolution, allmodconfig/build tests, module load with and without `CRYPTO_KRB5_SELFTESTS`, and runtime crypto allocation for all selected AES/Camellia/HMAC/CMAC/CTS/CBC algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Makefile -->
# sources/distributed-fs/ceph-client/crypto/krb5/Makefile

Purpose: Builds the Kerberos 5 crypto module from the API, KDF, simplified profile, enctype profile, and optional selftest objects.

Important APIs/types/functions: `krb5-y` lists `krb5_kdf.o`, `krb5_api.o`, `rfc3961_simplified.o`, `rfc3962_aes.o`, `rfc6803_camellia.o`, and `rfc8009_aes2.o`. `krb5-$(CONFIG_CRYPTO_KRB5_SELFTESTS)` adds `selftest.o` and `selftest_data.o`. `obj-$(CONFIG_CRYPTO_KRB5) += krb5.o` links the module/built-in object.

Control flow: Kbuild aggregates the listed objects into `krb5.o` when `CONFIG_CRYPTO_KRB5` is enabled, adding selftest objects only when configured.

State and persistence behavior: No runtime state. It controls build-time object composition.

Dependencies and integration points: Integrates the Kerberos source files into the kernel crypto Makefile hierarchy and matches the Kconfig option names.

Risks: Omitting an object can leave supported enctype externs unresolved or make the public API incomplete. Adding selftest data unconditionally would increase footprint; omitting it when selftests are enabled would break module init validation.

Test signals: Incremental and clean builds for built-in and module configurations, with and without selftests, plus linker checks for all exported Kerberos symbols and enctype tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/internal.h -->
# sources/distributed-fs/ceph-client/crypto/krb5/internal.h

Purpose: Declares private Kerberos 5 crypto profiles, buffer sizing helpers, selftest vector structures, and cross-file entry points shared by the Kerberos module.

Important APIs/types/functions: `struct krb5_crypto_profile` is the method table for PRF, Kc/Ke/Ki derivation, key packaging/loading, encrypt/decrypt, and MIC get/verify operations. Alignment macros compute request, IV, descriptor, and digest buffer sizes. Test structs describe PRF, key, encryption, and MIC vectors. The header declares public-internal helpers from `krb5_api.c`, `krb5_kdf.c`, `rfc3961_simplified.c`, and profile externs for AES-SHA1, AES-SHA2, and Camellia enctypes.

Control flow: Public API functions select a `krb5_enctype`, then dispatch to the profile function pointers declared here. Enctype definition files bind concrete profiles to algorithm names and sizes. Selftest code uses the vector structs and extern arrays when configured.

State and persistence behavior: The header itself has no state. The profile/enctype objects it declares are static const runtime metadata. Temporary crypto buffers are sized using the macros so request layouts remain aligned for the crypto API.

Dependencies and integration points: Includes public `<crypto/krb5.h>`, scatterlist, shash, and skcipher APIs. It is the private contract among all Kerberos crypto compilation units and optional selftests.

Risks: Profile function signatures are security-sensitive; mismatch between enctype sizes and profile behavior can derive wrong keys, truncate checksums incorrectly, or misplace confounders. Alignment macro changes can break AEAD/shash request layout. Extern declarations must track Kconfig/Makefile composition.

Test signals: Build with selftests, run Kerberos vectors for every enctype, validate AEAD/shash buffer alignment under KASAN, and exercise public API calls for prepare/encrypt/decrypt/MIC across all profiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_api.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/krb5_api.c

Purpose: Exposes the public kernel Kerberos 5 crypto API: enctype lookup, buffer sizing, transform preparation, encryption/decryption, MIC generation/verification, and module selftest startup.

Important APIs/types/functions: `krb5_supported_enctypes[]` lists AES128/256 SHA1, AES128/256 SHA2, and Camellia128/256 CMAC enctypes. Exported functions include `crypto_krb5_find_enctype()`, `crypto_krb5_how_much_buffer()`, `crypto_krb5_how_much_data()`, `crypto_krb5_where_is_the_data()`, `crypto_krb5_prepare_encryption()`, `crypto_krb5_prepare_checksum()`, `crypto_krb5_encrypt()`, `crypto_krb5_decrypt()`, `crypto_krb5_get_mic()`, and `crypto_krb5_verify_mic()`.

Control flow: Callers find an enctype by numeric ID, compute buffer layout, prepare an AEAD or shash by deriving profile-specific keys, then call encrypt/decrypt or MIC helpers. The top-level cryptographic operations validate basic scatterlist bounds and dispatch to `krb5->profile` methods. Module init runs `krb5_selftest()` when configured.

State and persistence behavior: The supported enctype array and module metadata are static. Prepared crypto handles returned to callers hold derived key state and must be freed by callers with crypto API free functions. Temporary derived key buffers are freed after transform setup.

Dependencies and integration points: Exports symbols for network filesystem clients and other in-kernel Kerberos users. Integrates with crypto AEAD/shash allocation by algorithm names from enctype tables and maps missing algorithms to `-ENOPKG`.

Risks: Buffer offset/length helpers must match profile implementations exactly or callers may allocate too little space or authenticate wrong bytes. The API trusts caller scatterlists after bounds checks. Key buffers must be freed on all error paths. Optional selftests mean unsupported vectors can escape if disabled.

Test signals: Lookup each supported enctype, prepare encryption/checksum transforms, encrypt/decrypt and MIC round trips over scatterlists, invalid offset/length warnings returning `-EMSGSIZE`, missing algorithm handling, and module-load selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_kdf.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/krb5_kdf.c

Purpose: Implements shared Kerberos key derivation helpers for PRF+ and the Kc, Ke, and Ki usage-specific keys.

Important APIs/types/functions: `crypto_krb5_calc_PRFplus()` implements RFC4402 PRF+ by concatenating `PRF(K, n || S)` blocks and truncating to the requested length. `krb5_derive_Kc()`, `krb5_derive_Ke()`, and `krb5_derive_Ki()` build the 5-byte usage constant from big-endian usage plus the checksum/encryption/integrity seed byte, set the expected output length, and call the profile-specific KDF.

Control flow: PRF+ allocates a combined temporary buffer for generated PRF blocks and `n || S`, loops counter values from 1 until enough material is produced, then copies exactly `L` bytes to the caller's preallocated result. Kc/Ke/Ki derivation is a thin dispatch layer over the selected `krb5_crypto_profile`.

State and persistence behavior: No persistent state. Temporary PRF+ material is freed with `kfree_sensitive()`. Caller-provided result buffers carry output.

Dependencies and integration points: Uses public export for PRF+, private profile methods, Kerberos usage seed constants from `<crypto/krb5.h>`, and allocation alignment helper `round16()`.

Risks: The PRF+ loop assumes the result buffer is already allocated and sized by the caller. Counter overflow is not a practical issue for normal Kerberos lengths but is not explicitly bounded. Usage constants must be exactly encoded or keys for checksum/encryption/integrity will not interoperate.

Test signals: RFC PRF+ vectors, Kc/Ke/Ki derivation vectors for all enctypes/usages, error propagation from profile PRF/KDF methods, sensitive-free checks, and boundary tests where output length is not a multiple of PRF length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_kdf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3961_simplified.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc3961_simplified.c

Purpose: Implements the RFC3961 simplified Kerberos crypto profile: n-fold, DK/DR derivation, PRF, authenc key packaging, AEAD encrypt/decrypt wrappers, and checksum MIC helpers.

Important APIs/types/functions: `crypto_shash_update_sg()` hashes a scatterlist range. `rfc3961_nfold()` implements the RFC n-fold operation. `rfc3961_calc_DK()` derives keys by repeated encryption of folded constants and optional random-to-key conversion. `rfc3961_calc_PRF()` hashes input, derives a `prf` key, and encrypts the truncated hash. `authenc_derive_encrypt_keys()` and `authenc_load_encrypt_keys()` package Ke/Ki for `authenc`. `rfc3961_derive_checksum_key()` and `rfc3961_load_checksum_key()` prepare Kc. `krb5_aead_encrypt/decrypt()` perform confounder insertion, AEAD processing, and boundary adjustment. `rfc3961_get_mic()` and `rfc3961_verify_mic()` calculate/verify keyed checksums.

Control flow: Key derivation folds the constant to block size, repeatedly encrypts blocks with the base key until enough raw key bytes exist, then either copies or random-to-key converts the result. Encryption expects data immediately after the confounder, optionally writes a random confounder, zero-pads if needed, then encrypts/checksums the secure region through AEAD. MIC generation hashes optional metadata plus data and writes the checksum immediately before data; verification recomputes and compares against the stored checksum.

State and persistence behavior: No global mutable state. Sensitive key, digest, request, and confounder buffers are temporary and freed with sensitive zeroing. Scatterlist data is modified in place for encryption/MIC insertion and offsets/lengths are updated on successful decrypt/verify.

Dependencies and integration points: Uses kernel random bytes, scatterlist helpers, sync skcipher, shash, authenc key parameter format, and the Kerberos profile table. It backs AES-SHA1 and also provides shared encrypt/MIC helpers for Camellia and AES-SHA2 profiles.

Risks: Scatterlist offset arithmetic must not authenticate or copy outside the intended buffer. `memcmp()` is used for MIC comparison, which is acceptable only if timing side channels are not relevant in the calling context; crypto constant-time comparison would be safer. Error paths in `authenc_derive_encrypt_keys()` currently return after allocation on a failed Ke derivation without freeing `setkey->data`, relying on caller cleanup behavior. Exact RFC n-fold behavior is easy to break.

Test signals: RFC3961/RFC3962 known-answer vectors, n-fold vectors, DK/PRF/Kc/Ke/Ki derivation tests, encryption/decryption with and without preconfounded input, MIC metadata tests, short/invalid buffer rejection, scatterlist segmentation tests, and KMSAN/KASAN checks for temporary buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3961_simplified.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3962_aes.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc3962_aes.c

Purpose: Defines the RFC3962 AES CTS HMAC-SHA1 Kerberos enctypes for AES-128 and AES-256.

Important APIs/types/functions: Exports `krb5_aes128_cts_hmac_sha1_96` and `krb5_aes256_cts_hmac_sha1_96` as `struct krb5_enctype` metadata. Each binds Kerberos etype/ctype numbers, algorithm names (`krb5enc(hmac(sha1),cts(cbc(aes)))`, `hmac(sha1)`, `sha1`, `cts(cbc(aes))`), key lengths, block/confounder/checksum/hash/PRF lengths, identity random-to-key, and `rfc3961_simplified_profile`.

Control flow: There is no executable function flow. `krb5_api.c` includes these const objects in the supported enctype table, and profile code uses their fields to allocate transforms and size buffers.

State and persistence behavior: Static const enctype metadata only. Prepared transforms created from these fields hold runtime key state elsewhere.

Dependencies and integration points: Depends on `internal.h` declarations and the RFC3961 simplified profile. Kconfig selects AES, CTS, CBC, SHA1, HMAC, and Kerberos encryption wrapper support needed by these names.

Risks: Any mismatch in key/checksum lengths or algorithm names breaks interoperability. SHA1-HMAC-96 is legacy but required for Kerberos compatibility. The metadata assumes identity random-to-key for AES.

Test signals: Kerberos AES-SHA1 known-answer tests, enctype lookup by numeric etype, transform allocation by listed names, key derivation vectors, and encrypt/decrypt/MIC vectors for both 128- and 256-bit variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3962_aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc6803_camellia.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc6803_camellia.c

Purpose: Implements the RFC6803 Camellia Kerberos profile and defines Camellia128/256 CTS-CMAC enctypes.

Important APIs/types/functions: `rfc6803_calc_KDF_FEEDBACK_CMAC()` implements KDF-FEEDBACK-CMAC with `K(i-1) || i || constant || 0x00 || k`. `rfc6803_calc_PRF()` derives `Kp` using the `prf` constant and CMACs the octet string. `rfc6803_crypto_profile` reuses shared authenc encryption and RFC3961 MIC helpers while using CMAC KDF/PRF methods. `krb5_camellia128_cts_cmac` and `krb5_camellia256_cts_cmac` define the enctype metadata.

Control flow: KDF allocates a CMAC shash, sets the protocol key, constructs the feedback input buffer, iterates until the result buffer is filled, and copies each CMAC segment. PRF derives a PRF key then computes CMAC over the input. Public API paths dispatch here through the enctype profile.

State and persistence behavior: Only static const profile/enctype metadata persists. Temporary CMAC descriptors, feedback buffers, and derived keys are allocated per call and freed sensitively.

Dependencies and integration points: Uses `cmac(camellia)`, `krb5enc(cmac(camellia),cts(cbc(camellia)))`, shared authenc packaging, and RFC3961 encrypt/MIC helpers. Kconfig selects Camellia, CMAC, CTS, CBC, and authenc.

Risks: Feedback KDF buffer layout and bit-length encoding must exactly match RFC6803. The result length is profile-driven; wrong `Kc_len`, `Ke_len`, or `Ki_len` silently produces incompatible keys. Because encryption/MIC helpers are shared with RFC3961, changes there affect Camellia too.

Test signals: RFC6803 Camellia KDF, PRF, encryption, and checksum vectors; 128/256 lookup and transform allocation; scatterlist encrypt/decrypt round trips; and failure tests for missing CMAC/Camellia providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc6803_camellia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc8009_aes2.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc8009_aes2.c

Purpose: Implements the RFC8009 AES CTS HMAC-SHA2 Kerberos profile and defines AES128-SHA256 and AES256-SHA384 enctypes.

Important APIs/types/functions: `rfc8009_calc_KDF_HMAC_SHA2()` builds `0x00000001 || label || 0x00 || context || k`, HMACs it, and truncates to the requested key length. `rfc8009_calc_PRF()`, `rfc8009_calc_Ke()`, and `rfc8009_calc_Ki()` derive PRF, encryption, checksum, and integrity keys using RFC8009 labels/usages. `rfc8009_encrypt()` and `rfc8009_decrypt()` include the starting IV as associated data before delegating to authenc. `rfc8009_crypto_profile` binds these methods with shared key packaging and MIC helpers. The two exported enctype objects define SHA256/128-bit checksum and SHA384/192-bit checksum variants.

Control flow: Key derivation allocates an HMAC shash, verifies digest capacity, constructs the KDF input, computes one HMAC block, and copies the requested prefix. Encryption writes a confounder if needed, chains a synthetic scatterlist containing the IV-sized associated-data buffer before the payload scatterlist, sets AEAD AD length, and encrypts in place. Decryption mirrors this and adjusts output offset/length after authentication succeeds.

State and persistence behavior: Static const profile/enctype metadata persists. Temporary HMAC, AEAD request, IV/AD, and derived-key buffers are allocated per operation and freed sensitively. The encrypted scatterlist is modified in place.

Dependencies and integration points: Uses `authenc(hmac(sha256|sha384),cts(cbc(aes)))`, shared authenc packaging, RFC3961 checksum helpers, and public Kerberos API dispatch. Kconfig selects SHA256, SHA512, HMAC, AES, CBC, CTS, and authenc.

Risks: The `ad` buffer is zero-filled by allocation and represents the starting IV associated data; changing initialization can break RFC8009 authentication. `hash_len` metadata is 20 in both enctype definitions despite SHA2 use, so tests should verify no code relies on that field incorrectly for RFC8009 paths. KDF label/context composition and checksum truncation are interoperability-critical.

Test signals: RFC8009 KDF/PRF/encrypt/checksum vectors, AES128-SHA256 and AES256-SHA384 lookup, bad checksum rejection, associated-data coverage tests that alter the starting IV, scatterlist segmentation, and missing SHA384/authenc provider errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc8009_aes2.c -->
