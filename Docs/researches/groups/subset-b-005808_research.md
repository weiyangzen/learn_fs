# subset-b-005808 Research

Grouped research report for the requested Ceph-client imported Linux crypto, CXL, and DRM header subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/if_alg.h -->
# sources/distributed-fs/ceph-client/include/crypto/if_alg.h

Purpose: defines the in-kernel support contract for the AF_ALG user-space crypto socket family. It bridges sockets to crypto API transforms, scatter-gather buffering, synchronous waits, and asynchronous AEAD/skcipher requests.

Important APIs, types, and flow: `struct alg_sock` extends `struct sock` and tracks the parent listener, selected `af_alg_type`, transform-private data, and key/no-key references. `struct af_alg_type` is the per-algorithm vtable for bind, key/entropy/authsize setup, accept, release, proto ops, and module ownership. `af_alg_ctx` tracks TX SGLs, IV/state, AEAD associated-data length, send/receive accounting, operation direction, write/init/more flags, and in-flight AIO. Helpers such as `af_alg_sndbuf()`, `af_alg_rcvbuf()`, `af_alg_sendmsg()`, `af_alg_get_rsgl()`, `af_alg_alloc_areq()`, `af_alg_async_cb()`, and `af_alg_poll()` implement the common sendmsg/recvmsg/request lifecycle used by algorithm-specific AF_ALG frontends.

State and persistence: state is per socket and per request only. Buffer accounting is held in `ctx->used` and atomic `rcvused`; async lifetime is guarded by request ownership and socket references. No filesystem persistence exists.

Dependencies and integration: depends on `linux/if_alg.h`, net sockets, scatterlists, `crypto/aead.h`, `crypto/skcipher.h`, `crypto_wait`, and module ownership. It integrates with `algif_*` implementations and user ABI behavior for `sendmsg`, `recvmsg`, `accept`, AIO, and polling.

Risks and test signals: risks center on pinned-page lifetime, SGL accounting, no-key accept behavior, async completion races, and user-triggered memory growth. Signals include AF_ALG socket tests for key/no-key accept, large and fragmented iovecs, AEAD AAD lengths, partial reads/writes, AIO cancellation/completion, poll readiness, and memory-leak/pin accounting under error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/if_alg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/acompress.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/acompress.h

Purpose: defines the internal asynchronous compression algorithm contract and helper machinery for compression transforms that may operate on scatterlists, virtual buffers, or per-CPU synchronous fallback streams.

Important APIs, types, and flow: `struct acomp_alg` supplies `compress`, `decompress`, optional transform `init`/`exit`, and common compression algorithm metadata shared with synchronous compression. `struct crypto_acomp_streams` owns per-CPU stream contexts, allocation/free callbacks, a work item, and a CPU mask of requested streams. `struct acomp_walk` abstracts either virtual source/destination pointers or scatter walks. Request helpers expose transform/request contexts, detect request buffer modes (`*_isvirt`, `*_isnondma`, `*_issg`), allocate/free streams, lock per-CPU streams with BH-disabled spinlocks, walk virtual buffers, and initialize fallback requests on stack with `ACOMP_FBREQ_ON_STACK`.

State and persistence: state is transform-local context plus per-CPU compression stream contexts guarded by spinlocks. Walk state is transient per request; no persistent storage is used.

Dependencies and integration: includes public `crypto/acompress.h`, `crypto/algapi.h`, scatterwalk helpers, workqueues, cpumasks, and synchronous compression fallback definitions. Registration functions (`crypto_register_acomp*`) attach implementations to the crypto API registry.

Risks and test signals: risks include mixing virtual/scatterlist/NON-DMA flags incorrectly, per-CPU stream locking bugs in softirq context, fallback request flag loss, and destination-length accounting. Signals include acomp self-tests across SG and virtual buffers, compression/decompression with small and oversized outputs, CPU hotplug or preemption-heavy runs, and fallback path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/acompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/aead.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/aead.h

Purpose: provides private AEAD registration, template-instance, spawn, queue, context, and request-size helpers for authenticated encryption algorithms.

Important APIs, types, and flow: `struct aead_instance` overlays `struct crypto_instance` with `struct aead_alg` for template-produced algorithms. `struct crypto_aead_spawn` binds a template instance to an inner AEAD algorithm via `crypto_grab_aead()` and later instantiates it through `crypto_spawn_aead()`. Inline helpers retrieve transform, instance, request, and DMA-aligned request contexts; complete requests; initialize AEAD queues; set normal or DMA-padded request sizes; and expose AEAD chunk size. `crypto_register_aead*()` and `aead_register_instance()` publish algorithms and template instances.

State and persistence: state is held in crypto transform contexts, request contexts, queue entries, and template instance memory. No external persistence exists.

Dependencies and integration: integrates public `crypto/aead.h`, `crypto/algapi.h`, generic spawn/instance infrastructure, and callers implementing AEAD templates such as authenc, CCM/GCM wrappers, or hardware adapters.

Risks and test signals: incorrect `offsetof()` overlay assumptions, DMA alignment padding, request-size underestimation, or chunk-size reporting can corrupt request private data or break streaming AEAD modes. Test signals include crypto manager AEAD self-tests, DMA-aligned hardware drivers, template load/unload tests, and async queue completion ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/akcipher.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/akcipher.h

Purpose: defines the internal asymmetric cipher interface for public-key encryption algorithms and template instances.

Important APIs, types, and flow: `struct akcipher_instance` embeds template lifecycle and an `akcipher_alg`; `struct crypto_akcipher_spawn` references an inner public-key cipher. Helpers expose request/transform contexts, DMA-aligned private data, request-size setters, request completion, algorithm names, instance casting, instance context lookup, spawn grab/drop/instantiate, and algorithm registration through `crypto_register_akcipher()` and `akcipher_register_instance()`.

State and persistence: key material and per-transform state live in `crypto_akcipher` contexts owned by implementations; request contexts are transient. The header itself declares no storage or persistence.

Dependencies and integration: depends on public `crypto/akcipher.h` and crypto algorithm/template infrastructure. It is used by RSA and padding templates and hardware/software asymmetric crypto providers.

Risks and test signals: risks include request context under-allocation, DMA alignment mistakes, stale spawn references during template teardown, and wrong algorithm name/reporting for nested templates. Test signals include RSA encrypt/decrypt/signature padding template self-tests, module unload/load, key-size boundary tests, and hardware driver DMA tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/akcipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/cipher.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/cipher.h

Purpose: declares the internal single-block cipher API for `CRYPTO_ALG_TYPE_CIPHER` algorithms, primarily used by templates and modes that invoke primitive block encryption/decryption one block at a time.

Important APIs, types, and flow: `struct crypto_cipher` wraps `struct crypto_tfm`. Allocation and lookup helpers force the algorithm type/mask to single-block cipher. The API exposes block size, align mask, flags, key setup, one-block encrypt/decrypt, transform cloning, spawn grab/drop/instantiate, and access to the underlying `cipher_alg`. Templates call `crypto_grab_cipher()` during instance creation and `crypto_spawn_cipher()` when constructing per-transform children.

State and persistence: transform key schedule and implementation state live inside the allocated crypto transform. No persistent state exists.

Dependencies and integration: relies on `crypto/algapi.h`, the generic crypto transform allocator, and `cipher_alg` implementations. It is integrated by block modes, skcipher templates, and low-level cipher drivers.

Risks and test signals: callers must enforce block-size buffers and correct key lengths; using this API for stream/chained modes would omit IV/state handling. Signals include primitive cipher self-tests, template self-tests using cloned or spawned ciphers, weak-key propagation, and alignment-sensitive architecture implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/des.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/des.h

Purpose: centralizes DES and 3DES-EDE key verification rules for skcipher and AEAD implementations.

Important APIs, types, and flow: `crypto_des_verify_key()` expands a DES key with `des_expand_key()`, maps weak-key rejection to `-EINVAL` when `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` is set, and zeroizes the temporary context. `des3_ede_verify_key()` rejects collapsed 3DES keys where adjacent keys are equal, and in FIPS mode also rejects all-equal keying; wrapper helpers adapt those checks to skcipher and AEAD transforms while validating AEAD key sizes.

State and persistence: only stack-local temporary key material is used and explicitly cleared. FIPS behavior reads global `fips_enabled`.

Dependencies and integration: depends on DES constants/expansion, crypto transform flags, AEAD/skcipher transform accessors, and Linux FIPS mode. DES-family implementations should call these helpers from setkey paths.

Risks and test signals: failure to call these helpers can admit weak or FIPS-forbidden keys; wrong error mapping can break callers that distinguish weak-key permission. Signals include DES/3DES weak-key vectors, FIPS-mode key rejection tests, AEAD key-length tests, and memory-sanitizer checks for zeroized temporary key schedules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/drbg.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/drbg.h

Purpose: supplies small internal helpers for NIST SP800-90A DRBG derivation functions.

Important APIs, types, and flow: `drbg_cpu_to_be32()` writes a host integer to a caller-provided buffer as big-endian bytes. `struct drbg_string` stores a buffer pointer, length, and list node so DRBG code can concatenate input strings by list traversal without copying. `drbg_string_fill()` initializes one list element.

State and persistence: no owned state beyond caller-managed list nodes and referenced buffers. No persistent state exists.

Dependencies and integration: relies on Linux endian conversion and list heads. It integrates with DRBG derivation and reseed code that needs SP800-90A ordered concatenation of entropy, nonce, personalization, additional input, and counters.

Risks and test signals: risks are unaligned buffer casts, incorrect list ordering, and referenced buffer lifetime. Signals include DRBG known-answer tests, reseed/additional-input vectors, KASAN/UBSAN for unaligned accesses, and big-endian/little-endian cross-build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/drbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/ecc.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/ecc.h

Purpose: defines internal elliptic-curve arithmetic, key validation, ECDH, ECDSA formatting, and VLI helpers for NIST curves up to P-521.

Important APIs, types, and flow: constants define digit counts, byte limits, and point initialization. `struct ecdsa_raw_sig` stores raw `r` and `s` as native-endian VLI arrays. Conversion helpers (`ecc_swap_digits()`, `ecc_digits_from_bytes()`, `vli_from_be64()`, `vli_from_le64()`) normalize external byte encodings into little-endian digit arrays. Key and ECDH functions validate private keys, generate private keys, derive public keys, compute shared secrets, validate public keys partially or fully, allocate/free points, test the point at infinity, and perform Shamir multi-scalar multiplication for signature verification. VLI helpers provide zero check, comparison, subtraction, modular inverse, and slow modular multiplication.

State and persistence: all state is caller-owned key arrays, point allocations, and temporary arithmetic buffers. No persistence exists, but private keys and shared secrets are sensitive and require caller-side zeroization.

Dependencies and integration: depends on `crypto/ecc_curve.h`, unaligned access helpers, ECDSA crypto templates (`ecdsa_x962_tmpl`, `ecdsa_p1363_tmpl`), and KPP/signature implementations.

Risks and test signals: high-risk areas are endian conversion, curve-order bounds, point validation strength, scalar edge cases, timing behavior, and allocation cleanup. Signals include ECDH and ECDSA known-answer tests for P-192/P-256/P-384/P-521, invalid public/private key rejection, ASN.1/raw signature conversions, fuzzed point inputs, and constant-time/leakage review for secret-dependent arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/ecc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/engine.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/engine.h

Purpose: declares internal helpers for crypto engine based drivers that queue asynchronous requests onto hardware or threaded engines.

Important APIs, types, and flow: `crypto_engine_alloc_init_and_set()` creates and initializes an engine with a request queue length, optional retry support, processor callback, prepare/unprepare callbacks, per-algorithm private pointer, and feature flags. `crypto_engine_start()` and `crypto_engine_stop()` control request processing.

State and persistence: engine state is runtime queue/worker/device state owned by the implementation returned from allocation. No persistent state is represented in this header.

Dependencies and integration: depends on public crypto engine types and is used by hardware crypto drivers to integrate with the common crypto request queue and completion model.

Risks and test signals: risks include start/stop races, retry livelock, lost completions, and prepare/unprepare imbalance around hardware DMA setup. Signals include hardware-driver crypto self-tests, queue-depth stress, module removal while requests are pending, suspend/resume, and fault injection in prepare/process paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/geniv.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/geniv.h

Purpose: declares generic IV generator support for AEAD templates.

Important APIs, types, and flow: `aead_geniv_alloc()` creates a generic-IV AEAD instance from a crypto template and rtnetlink attributes; `aead_init_geniv()` initializes a `crypto_aead` transform with the selected generic-IV behavior.

State and persistence: generic-IV state is per instance and per transform; this header stores nothing directly and has no persistence.

Dependencies and integration: depends on AEAD template infrastructure and `struct rtattr`. It integrates with AEAD modes that derive IV handling through crypto templates.

Risks and test signals: risks include IV-size mismatch, bad template attribute parsing, and nonce reuse if geniv setup diverges from mode requirements. Signals include AEAD geniv template self-tests, instance creation with malformed attributes, and algorithm listings in `/proc/crypto`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/geniv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/hash.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/hash.h

Purpose: defines private async and synchronous hash registration, template, spawn, walk, fallback, keying, export/import, and context helpers.

Important APIs, types, and flow: algorithm flags describe block-only behavior, nonzero final requirements, multi-block finup support, and core-export support. `struct crypto_hash_walk` tracks SG traversal for ahash operations. `ahash_instance` and `shash_instance` overlay crypto instances with hash algorithms; spawn helpers bind templates to inner ahash or shash algorithms. Registration APIs publish ahash/shash algorithms and instances. Helpers detect whether algorithms have or need keys, bridge shash operations through ahash request wrappers, set statesize/reqsize including DMA padding, allocate fallback stack requests (`HASH_FBREQ_ON_STACK`), enqueue/dequeue requests, expose transform/request contexts, and export/import core state without partial-block buffers.

State and persistence: state is per transform, per request/descriptor, queued request, or exported caller buffer. Hash state can be serialized through export/import for runtime continuation, but there is no filesystem persistence.

Dependencies and integration: depends on public hash API, crypto queue/spawn/template infrastructure, scatterlists, fallback transforms, and crypto self-tests. Hash algorithms, HMAC/KDF code, and templates use these contracts.

Risks and test signals: state-size math, partial-block removal in core export, keyed-hash enforcement, fallback flag propagation, and DMA alignment are subtle. Signals include ahash/shash self-tests, HMAC with missing keys, export/import continuation tests, SG and virtual request paths, fallback-stack request tests, and template unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/kdf_selftest.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/kdf_selftest.h

Purpose: provides a reusable inline self-test harness for kernel key-derivation functions built on `crypto_shash`.

Important APIs, types, and flow: `struct kdf_testvec` packages key material, input keying material, one `kvec` info value, and expected output. `kdf_test()` allocates an output buffer, allocates the named shash transform, calls the supplied KDF setkey and generate functions, compares the output with the expected vector, frees resources, and reports errors.

State and persistence: all state is temporary allocation and the shash transform; no persistence exists. Test buffers may contain key material and are freed after use.

Dependencies and integration: depends on `crypto/hash.h`, `linux/uio.h`, allocation, logging, and specific KDF implementations such as SP800-108 helpers.

Risks and test signals: the helper currently maps transform allocation errors to `-ENOMEM` and uses raw `memcmp()` for known-answer data. Signals are KDF known-answer tests, error-path coverage for setkey/generate failures, allocation-failure injection, and verification that expected lengths match destination lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/kdf_selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/kpp.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/kpp.h

Purpose: defines private key-agreement protocol primitive registration, template instance, spawn, context, and request helpers.

Important APIs, types, and flow: `struct kpp_instance` overlays `crypto_instance` with a `kpp_alg`, and `struct crypto_kpp_spawn` binds template instances to inner KPP algorithms. Helpers expose request and transform contexts, DMA-aligned request/transform data, request-size setters, request completion, algorithm names, instance casting, instance context lookup, algorithm registration, template instance registration, spawn grab/drop, and transform instantiation.

State and persistence: secrets and per-transform key material live in KPP implementation contexts; request input/output SGs are transient. The header declares no persistent state.

Dependencies and integration: depends on public `crypto/kpp.h` and crypto algorithm/template infrastructure. It is used by ECDH/DH implementations and templates that wrap KPP algorithms.

Risks and test signals: risks include key material lifetime, request-size/DMA alignment mistakes, missing completion on asynchronous failures, and stale spawned algorithm references. Signals include ECDH/DH self-tests, invalid secret handling, max-size output checks, template load/unload, and DMA hardware-driver runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/kpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/poly1305.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/poly1305.h

Purpose: declares low-level Poly1305 core primitives and generic block helpers used by full Poly1305 MAC implementations.

Important APIs, types, and flow: `poly1305_core_setkey()` clamps/prepares the core `r` key; `poly1305_core_init()` zeros the accumulator; `poly1305_core_blocks()` processes whole 16-byte blocks with a caller-provided hibit; and `poly1305_core_emit()` emits either the universal hash or the full MAC when a nonce is supplied. Generic wrappers initialize `poly1305_block_state`, process whole blocks, and emit the digest.

State and persistence: state is the caller-owned accumulator and core key. No persistence exists; key and accumulator material are sensitive.

Dependencies and integration: depends on public Poly1305 types and constants. It is used by generic and architecture-specific Poly1305 implementations and by constructions such as ChaCha20-Poly1305.

Risks and test signals: callers must buffer/pad partial blocks and set `hibit` correctly; misuse can produce invalid tags. Signals include Poly1305 known-answer tests, partial-block boundary tests in full MAC code, architecture/generic comparison, and zeroization review for key-bearing states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/rng.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/rng.h

Purpose: defines internal RNG registration and transform helpers for crypto API random number generators.

Important APIs, types, and flow: `crypto_register_rng*()` and `crypto_unregister_rng*()` manage RNG algorithms. `crypto_del_default_rng()` is available only when RNG support is built. Inline helpers expose transform context and call the algorithm `set_ent` callback to inject entropy.

State and persistence: state lives in RNG transform contexts and default-RNG global state owned by the implementation. No file persistence is declared here.

Dependencies and integration: depends on public RNG API and algorithm registry. It integrates with DRBG/stdrng implementations and callers needing default RNG cleanup during module/runtime transitions.

Risks and test signals: risks include entropy injection into an uninitialized transform, default RNG deletion in disabled Kconfig builds, and missing reseed behavior. Signals include RNG/DRBG self-tests, default RNG lifecycle tests, entropy reset tests, and Kconfig matrix builds with RNG disabled or modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/rng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/rsa.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/rsa.h

Purpose: declares RSA key parsing structures, setkey helper behavior, and RSA template symbols.

Important APIs, types, and flow: `struct rsa_key` stores pointers and sizes for modulus, exponents, CRT factors, and coefficient fields parsed from encoded keys. `rsa_parse_pub_key()` and `rsa_parse_priv_key()` decode public/private keys into that structure. `rsa_set_key()` selects public or private setkey on a child akcipher, queries the resulting modulus size with `crypto_akcipher_maxsize()`, rejects sizes above `PAGE_SIZE`, and publishes the key size. `rsa_pkcs1pad_tmpl` and `rsassa_pkcs1_tmpl` are template exports.

State and persistence: parsed key pointers refer to the caller's encoded key buffer; child transforms own parsed key state after setkey. No persistence exists.

Dependencies and integration: depends on `crypto/akcipher.h` and internal akcipher behavior. It integrates RSA base implementations with PKCS#1 encryption/signature templates.

Risks and test signals: risks include encoded key lifetime, oversized modulus rejection, incomplete CRT field validation, and public/private setkey mixups. Signals include DER key parse tests, RSA encrypt/decrypt/sign/verify vectors, oversized key rejection, invalid CRT fields, and template self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/rsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/scompress.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/scompress.h

Purpose: defines the internal synchronous compression API and its shared relationship with asynchronous compression.

Important APIs, types, and flow: `struct crypto_scomp` wraps a crypto transform; `struct scomp_alg` supplies synchronous `compress`/`decompress` callbacks that operate on linear buffers and optional stream context, owns `crypto_acomp_streams`, and shares common compression metadata. Helpers cast transforms/algorithms, free transforms, call algorithm callbacks, and register/unregister one or multiple synchronous compression algorithms.

State and persistence: state is per transform plus per-CPU stream contexts. No persistence exists.

Dependencies and integration: includes internal acomp definitions and the generic crypto transform API. Synchronous compression algorithms can be exposed as async wrappers through shared stream support.

Risks and test signals: destination length is caller-provided and updated by algorithms, so bounds handling is central. Signals include scomp known-answer compression/decompression tests, stream allocation failure tests, concurrent per-CPU use, and async fallback integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/scompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/sig.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/sig.h

Purpose: defines private public-key signature algorithm registration and template wrapping support.

Important APIs, types, and flow: `struct sig_instance` overlays a crypto instance with `sig_alg`, and `struct crypto_sig_spawn` references an inner signature algorithm. Helpers expose transform context, register/unregister algorithms, register template instances, cast instance/context objects, grab/drop spawns, instantiate spawned transforms, and recover the spawned `sig_alg`.

State and persistence: signature key material and implementation state are held in `crypto_sig` transform contexts. Request data is passed directly to sign/verify APIs; no persistence is declared.

Dependencies and integration: depends on public `crypto/sig.h` and crypto template infrastructure. It supports algorithms such as RSA/ML-DSA signature providers and padding/encoding templates.

Risks and test signals: risks include key-size/digest-size reporting mismatch, stale spawn references, and template instance cleanup. Signals include sign/verify self-tests, invalid key tests, module unload/reload, and template-generated algorithm registration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/sig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/simd.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/simd.h

Purpose: provides shared SIMD-crypto registration helpers and a centralized runtime predicate for whether crypto code may use SIMD registers.

Important APIs, types, and flow: `simd_register_aeads_compat()` registers compatible SIMD AEAD wrappers and returns wrapper handles; `simd_unregister_aeads()` tears them down. `crypto_simd_usable()` normally delegates to `may_use_simd()`, but under full crypto self-tests it also checks a per-CPU flag that temporarily disables SIMD to exercise non-SIMD fallbacks.

State and persistence: state is per-CPU `crypto_simd_disabled_for_test` when full self-tests are enabled and wrapper state returned by registration. No persistence exists.

Dependencies and integration: depends on architecture SIMD permission logic, per-CPU state, AEAD algorithms, and crypto self-test infrastructure.

Risks and test signals: using SIMD in forbidden contexts can corrupt task/FPU state; failing to test fallback paths can hide bugs. Signals include SIMD/non-SIMD self-test parity, preemption/softirq context tests, full self-test runs with forced disable, and architecture-specific FPU state checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/simd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/skcipher.h -->
# sources/distributed-fs/ceph-client/include/crypto/internal/skcipher.h

Purpose: defines private skcipher/lskcipher registration, template, spawn, request-context, fallback, and scatterwalk helpers for symmetric-key ciphers.

Important APIs, types, and flow: instance structs overlay crypto instances with `skcipher_alg` or `lskcipher_alg`; spawn structs bind templates to inner algorithms. `struct skcipher_walk` tracks SG or virtual source/destination traversal, IV handling, remaining byte counts, temporary pages/buffers, block size, stride, and alignment. APIs register algorithms and instances, grab/drop/spawn children, set request size including DMA padding, initialize/advance skcipher walks for normal and AEAD-backed operations, abort walks, expose contexts, test algorithm self-test status, and allocate simple cipher-mode instances around block ciphers or lskciphers.

State and persistence: state lives in transform contexts, request contexts, walk buffers, and template instance contexts. Exportable cipher mode state is handled by public APIs; no persistent storage exists.

Dependencies and integration: depends on `crypto/algapi.h`, internal single-block cipher helpers, public skcipher API, scatterwalk, AEAD request integration, and templates implementing modes such as CBC/CTR/XTS.

Risks and test signals: high-risk areas include SG traversal, IV/state carry between chunks, alignment buffers, request-size flags, and lskcipher/skcipher interop. Signals include skcipher manager tests, SG fragmentation and unaligned buffers, export/import continuation, AEAD-walk callers, simple-template instance creation, and DMA hardware-driver tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/internal/skcipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/kdf_sp800108.h -->
# sources/distributed-fs/ceph-client/include/crypto/kdf_sp800108.h

Purpose: declares the public kernel helpers for NIST SP800-108 counter-mode key derivation using shash-based keyed MACs.

Important APIs, types, and flow: `crypto_kdf108_setkey()` configures the shash KDF handle from a key and optional input keying material. `crypto_kdf108_ctr_generate()` derives output bytes into a destination buffer using an array of `kvec` info/context components and counter-mode iteration.

State and persistence: keying state is stored in the supplied `crypto_shash` transform. Generation output is caller-owned and transient.

Dependencies and integration: depends on shash transforms and `struct kvec`. It is used by protocol code needing SP800-108 KDF output and by KDF self-tests.

Risks and test signals: risks include counter overflow, info vector ordering, incorrect KDF key/IKM separation, and destination length limits. Signals include SP800-108 known-answer vectors, multi-vector info tests, zero/large output sizes, and keyed transform reuse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/kdf_sp800108.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/kpp.h -->
# sources/distributed-fs/ceph-client/include/crypto/kpp.h

Purpose: exposes the public crypto API for key-agreement protocol primitives such as ECDH and DH.

Important APIs, types, and flow: `struct kpp_alg` provides `set_secret`, `generate_public_key`, `compute_shared_secret`, `max_size`, and optional init/exit callbacks. `struct crypto_kpp` holds the transform, request size, and algorithm exit callback. `struct kpp_request` carries source/destination SGs, source length, destination length pointer, base async request, and request-private context. Helpers allocate/free transforms and requests, set callbacks, set input/output buffers, set secrets through `struct kpp_secret`, generate public keys, compute shared secrets, and query max output size.

State and persistence: secrets live in transform context after `crypto_kpp_set_secret()`; requests are transient. No external persistence is present.

Dependencies and integration: uses generic crypto transform allocation, async request completion, scatterlists, and KPP implementations. It is consumed by kernel protocols and asymmetric-key code needing key agreement.

Risks and test signals: risks include caller-provided `dst_len` underruns, secret encoding mismatches, asynchronous completion handling, and insufficient key validation. Signals include KPP known-answer tests, invalid/short secret tests, max-size probes, SG boundary tests, and async request cancellation or completion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/kpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/krb5.h -->
# sources/distributed-fs/ceph-client/include/crypto/krb5.h

Purpose: declares Kerberos 5 crypto type constants, enctype descriptors, and helper APIs for encryption, checksum, MIC verification, and PRF+ generation.

Important APIs, types, and flow: constants enumerate Kerberos enctypes, checksum types, key-usage seeds, and Kerberos error values. `enum krb5_crypto_mode` distinguishes checksum, encryption, integrity, and key derivation use. `struct krb5_buffer` describes external buffers; `struct krb5_enctype` describes enctype identifiers, names, crypto algorithm names, hash/HMAC names, key/confounder/checksum/block sizes, usage seed offsets, and key-derivation hooks. APIs locate encrypted/checksum data ranges, prepare AEAD or shash transforms, decrypt scatterlists, verify MICs, and compute PRF+ output.

State and persistence: state is transform-local and caller-buffer based. Keys are passed to helpers and may be stored in crypto transforms; no persistence exists.

Dependencies and integration: integrates `crypto_aead`, `crypto_shash`, scatterlists, network/security subsystems using Kerberos, and RFC enctype definitions.

Risks and test signals: risks include enctype constant mismatches, key-usage derivation errors, scatterlist data-range mistakes, checksum truncation differences, and weak legacy enctypes. Signals include Kerberos protocol test vectors, AES CTS/HMAC vectors, MIC failure tests, SG-layout coverage, and enctype negotiation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/md5.h -->
# sources/distributed-fs/ceph-client/include/crypto/md5.h

Purpose: exposes compact non-crypto-API MD5 and HMAC-MD5 helper contexts and one-shot functions for kernel users that need direct primitives.

Important APIs, types, and flow: constants define digest, block, state, and initial hash values. `md5_state`, `md5_block_state`, and `md5_ctx` hold incremental hash state; `md5_init()`, `md5_update()`, `md5_final()`, and `md5()` implement incremental and one-shot hashing. `hmac_md5_key` stores prepared inner/outer block keys; `hmac_md5_ctx` combines key and hash context. HMAC helpers prepare keys, initialize from prepared or raw key, update, finalize, and perform one-shot HMAC.

State and persistence: state is caller-owned contexts containing hash and key material. No persistence exists; HMAC contexts should be treated as sensitive.

Dependencies and integration: depends on kernel crypto type definitions and is used by protocol code needing low-overhead MD5/HMAC-MD5. It also exposes the zero-message digest constant.

Risks and test signals: MD5 is cryptographically broken for collision resistance, so use should be limited to legacy/non-adversarial protocols. Signals include RFC MD5/HMAC-MD5 vectors, incremental vs one-shot parity, empty-message hash, raw/prepared key equivalence, and zeroization review for HMAC keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/mldsa.h -->
# sources/distributed-fs/ceph-client/include/crypto/mldsa.h

Purpose: declares ML-DSA algorithm identifiers, public key and signature sizes, and verification entry point.

Important APIs, types, and flow: `enum mldsa_alg` selects ML-DSA-44, ML-DSA-65, or ML-DSA-87. Macros define public-key and signature byte sizes for each parameter set. `mldsa_verify()` validates a signature over a message with the chosen parameter set and public key.

State and persistence: verification is stateless from the header perspective; caller-provided key, message, and signature buffers are transient.

Dependencies and integration: depends on `linux/types.h` style crypto types and integrates with public-key signature verification paths that need post-quantum ML-DSA support.

Risks and test signals: risks include parameter-set size mismatch, signature malleability/encoding validation, and large stack/heap use in implementations. Signals include NIST/PQC known-answer vectors, wrong-size key/signature rejection, corrupted signature tests, and integration with `crypto_sig` or public-key verification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/mldsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/nh.h -->
# sources/distributed-fs/ceph-client/include/crypto/nh.h

Purpose: declares constants and the primitive function for the NH universal hash used by constructions such as Adiantum.

Important APIs, types, and flow: macros define pair stride, message unit, number of passes, hash output bytes, maximum message/key words, and byte sizes. `nh()` hashes a message with a u32 key into a u8 output buffer.

State and persistence: stateless; caller supplies key, message, and output buffers. No persistence exists.

Dependencies and integration: depends on Linux integer types. It is integrated by higher-level wide-block or MAC constructions that provide padding, key scheduling, and domain separation.

Risks and test signals: `nh()` is not a standalone MAC and requires correct caller-side keying and length handling. Signals include NH known-answer vectors, boundary lengths up to `NH_MESSAGE_BYTES`, endian cross-tests, and architecture generic/optimized parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/nh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/null.h -->
# sources/distributed-fs/ceph-client/include/crypto/null.h

Purpose: defines sizes for null crypto algorithms.

Important APIs, types, and flow: constants specify zero key size, one-byte block size, zero digest size, and zero IV size for null cipher/hash behavior.

State and persistence: no state.

Dependencies and integration: used by null algorithm implementations, crypto tests, and templates that need identity transforms.

Risks and test signals: risks are mostly callers assuming nonzero digest/IV/key sizes. Signals include null cipher/hash self-tests, template composition tests, and boundary tests for zero-length digest/key handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/null.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/padlock.h -->
# sources/distributed-fs/ceph-client/include/crypto/padlock.h

Purpose: defines shared constants for VIA PadLock hardware crypto drivers.

Important APIs, types, and flow: constants set hardware alignment requirements, module log prefix, normal and composite crypto priorities, and stack alignment per architecture word size.

State and persistence: no runtime state.

Dependencies and integration: integrates with PadLock AES/SHA drivers and build-time architecture choices.

Risks and test signals: wrong alignment or priority can cause hardware faults or unintended algorithm selection. Signals include PadLock hardware self-tests, alignment stress tests, `/proc/crypto` priority inspection, and 32-bit/64-bit build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/padlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/pcrypt.h -->
# sources/distributed-fs/ceph-client/include/crypto/pcrypt.h

Purpose: declares the per-request wrapper used by pcrypt to parallelize crypto requests through padata.

Important APIs, types, and flow: `struct pcrypt_request` embeds `struct padata_priv` and a flexible request-private context tail. Helpers return the private context after the wrapper, cast a pcrypt request to its padata object, and recover the wrapper from a padata callback.

State and persistence: state is per request and lasts only through padata scheduling and completion.

Dependencies and integration: depends on padata and crypto request users. It integrates with pcrypt template code that splits encryption/authentication work across CPUs.

Risks and test signals: risks include context-size under-allocation, padata callback casting mistakes, and CPU hotplug interactions. Signals include pcrypt crypto self-tests, parallel workload stress, CPU hotplug under active requests, and request completion ordering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/pcrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/pkcs7.h -->
# sources/distributed-fs/ceph-client/include/crypto/pkcs7.h

Purpose: declares the kernel PKCS#7 message parsing and verification interface.

Important APIs, types, and flow: `pkcs7_parse_message()` decodes DER data to a `pkcs7_message`; `pkcs7_free_message()` releases it. Accessors retrieve content data or message digest. Verification APIs supply detached data, verify signatures at a given usage time, and validate trust against a keyring.

State and persistence: parsed messages hold allocated decoded ASN.1/signature/content state until freed. Trust decisions use keyring state but this header declares no persistence.

Dependencies and integration: depends on kernel keyrings, public-key verification, ASN.1/PKCS#7 parser implementation, and consumers such as module signing, firmware signing, and IMA.

Risks and test signals: risks include DER parser robustness, detached-content lifetime, certificate-chain policy, time validity, and digest mismatch handling. Signals include PKCS#7 signature vectors, malformed ASN.1 fuzzing, keyring trust tests, detached data tests, expired/not-yet-valid certificate tests, and digest extraction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/pkcs7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/poly1305.h -->
# sources/distributed-fs/ceph-client/include/crypto/poly1305.h

Purpose: defines public Poly1305 constants, state structures, and incremental MAC API.

Important APIs, types, and flow: constants define 16-byte block and digest sizes and 32-byte one-time key size. `poly1305_key`, `poly1305_core_key`, `poly1305_state`, `poly1305_block_state`, and `poly1305_desc_ctx` separate nonce, clamped core key, accumulator, block buffering, and pending bytes. `poly1305_init()`, `poly1305_update()`, and `poly1305_final()` implement incremental MAC processing.

State and persistence: all state is caller-owned and contains one-time MAC key material and accumulator state. No persistence exists; contexts should be zeroized by users when appropriate.

Dependencies and integration: used by shash implementations and AEAD constructions such as ChaCha20-Poly1305. Internal core functions are declared separately in `internal/poly1305.h`.

Risks and test signals: nonce/key reuse is catastrophic, and partial-block buffering must match the spec. Signals include RFC Poly1305 and ChaCha20-Poly1305 vectors, split-update boundary tests, empty-message tests, architecture/generic parity, and key zeroization review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/public_key.h -->
# sources/distributed-fs/ceph-client/include/crypto/public_key.h

Purpose: declares the kernel public-key subtype, signature container, keyring restriction policies, query API, and signature verification entry points.

Important APIs, types, and flow: `struct public_key` stores key payload, length, algorithm IDs, key identifier, and extension flags for CA/digital signature/key-cert-sign use. `struct public_key_signature` stores signature bytes, digest bytes, encoding, hash algorithm, public-key algorithm, and key IDs. Free helpers release both structures. Restriction functions gate keyring links by signatures, trusted keys/keyrings, CA flags, or digital-signature usage. `query_asymmetric_key()`, `verify_signature()`, and `public_key_verify_signature()` drive verification; a stub returns `-ENOPKG` when public-key crypto is disabled.

State and persistence: keys may be persisted in kernel keyrings; structures here represent allocated runtime payloads. Signature and digest buffers are owned by parsed data until freed.

Dependencies and integration: integrates with asymmetric key subtype, kernel keyrings, PKCS#7/X.509 parsers, and crypto signature/akcipher implementations.

Risks and test signals: risks include key usage flag enforcement, trust-chain bypass, algorithm-name mismatches, and optional Kconfig stubs. Signals include keyring restriction tests, X.509/PKCS#7 verification, invalid digest/signature tests, disabled-public-key Kconfig builds, and CA/digitalSignature extension policy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/public_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/rng.h -->
# sources/distributed-fs/ceph-client/include/crypto/rng.h

Purpose: exposes the public crypto API for RNG algorithms and standard RNG byte generation.

Important APIs, types, and flow: `struct rng_alg` provides `generate`, optional `seed`, seed size, and base algorithm metadata. `struct crypto_rng` wraps the transform. `crypto_stdrng_get_bytes()` calls `__crypto_stdrng_get_bytes()` when standard RNG support is enabled or returns `-EOPNOTSUPP` otherwise. Helpers allocate/free RNG transforms, access algorithm metadata, generate bytes with optional source/additional input, get bytes without source input, reset/seed a transform, and query seed size.

State and persistence: RNG/DRBG state is transform-local and may include entropy and reseed counters in implementation code. No persistence is declared here.

Dependencies and integration: depends on generic crypto allocation and is consumed by key generation, DRBG, and callers needing crypto API RNG rather than the core random subsystem.

Risks and test signals: risks include using unseeded transforms, ignoring `-EOPNOTSUPP`, weak seeding, and generate buffer length handling. Signals include RNG/DRBG known-answer tests, reseed tests, disabled Kconfig builds, concurrent generate calls, and failure-injection for seed/generate callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/rng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/scatterwalk.h -->
# sources/distributed-fs/ceph-client/include/crypto/scatterwalk.h

Purpose: defines scatterlist walking and copy helpers used by crypto code to process segmented buffers safely.

Important APIs, types, and flow: inline helpers initialize walks at an SG entry or byte position, clamp available bytes to page boundaries and remaining segment length, expose current SG lists, map/unmap current pages, advance within chained SGs, flush destination dcache pages, and mark source/destination completion. Copy helpers move bytes between linear buffers and scatterwalks or SG lists, map-and-copy fixed ranges, and fast-forward an SG view with `scatterwalk_ffwd()`.

State and persistence: `struct scatter_walk` state is transient traversal state over caller-owned SGs. No persistence exists.

Dependencies and integration: depends on scatterlists, highmem/page mapping, chain markers, and cache maintenance. It is central to skcipher, ahash, AEAD, and compression walk code.

Risks and test signals: off-by-one page/segment advancement, incorrect dcache flushing, and SG chain handling can corrupt data or leak stale cache contents. Signals include crypto self-tests with highly fragmented SGs, unaligned offsets, highmem pages, chained SG lists, in-place transforms, and KASAN/KMSAN coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/scatterwalk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/serpent.h -->
# sources/distributed-fs/ceph-client/include/crypto/serpent.h

Purpose: declares Serpent block cipher constants, context, key setup, and block encrypt/decrypt primitives.

Important APIs, types, and flow: constants define key size range, expanded-key words, and 16-byte block size. `struct serpent_ctx` stores the expanded key. `__serpent_setkey()` initializes a context directly; `serpent_setkey()` adapts setkey to a crypto transform; `__serpent_encrypt()` and `__serpent_decrypt()` process one block.

State and persistence: expanded key state is transform/context-local and sensitive. No persistence exists.

Dependencies and integration: used by Serpent cipher drivers and templates that invoke block primitives.

Risks and test signals: risks include accepting zero-length keys if caller-side validation is absent, key schedule mistakes, and endian differences in optimized versions. Signals include Serpent known-answer vectors for all key lengths, transform setkey tests, generic vs optimized parity, and weak alignment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/serpent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sha1.h -->
# sources/distributed-fs/ceph-client/include/crypto/sha1.h

Purpose: exposes direct SHA-1 and HMAC-SHA1 incremental and one-shot helpers.

Important APIs, types, and flow: constants define digest/block/state sizes and initial hash words. `sha1_state`, `sha1_block_state`, and `sha1_ctx` hold incremental state; `sha1_init()`, `sha1_update()`, `sha1_final()`, and `sha1()` process messages. HMAC structs and helpers mirror the MD5 pattern with prepared inner/outer keys, raw-key initialization, update, final, and one-shot APIs.

State and persistence: caller-owned contexts hold hash state and HMAC key material. No persistence exists.

Dependencies and integration: used by legacy protocols, Kerberos variants, and direct HMAC users outside the generic crypto API. Exposes the zero-message SHA-1 digest constant.

Risks and test signals: SHA-1 is collision-broken and should be limited to legacy compatibility or HMAC contexts where still accepted. Signals include SHA-1/HMAC-SHA1 vectors, incremental split tests, empty-message digest checks, raw/prepared key equivalence, and policy review of new call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sha2.h -->
# sources/distributed-fs/ceph-client/include/crypto/sha2.h

Purpose: declares direct SHA-224, SHA-256, SHA-384, SHA-512, and HMAC helpers plus internal shared SHA-2 block contexts.

Important APIs, types, and flow: constants define digest/block sizes and initial vectors for SHA-2 variants. `crypto_sha256_state`, `sha256_state`, `sha512_state`, block-state structs, and internal `__sha256_ctx`/`__sha512_ctx` share update logic. Public contexts and APIs provide init/update/final/one-shot helpers for SHA-224/256/384/512 and HMAC variants. `sha256_finup_2x()` can finalize two SHA-256 messages from a common context, with `sha256_finup_2x_is_optimized()` reporting optimized support.

State and persistence: caller-owned contexts contain hash or HMAC key state. No persistence exists; HMAC contexts are sensitive.

Dependencies and integration: direct SHA-2 helpers are used by protocol and crypto code needing low-overhead hashing or HMAC without transform allocation. Optimized implementations may be architecture-specific.

Risks and test signals: risks include shared internal update-state mistakes, length-counter overflow, HMAC key preprocessing bugs, and optimized two-message finalization divergence. Signals include NIST SHA-2 and HMAC vectors, empty-message constants, incremental split tests, 2x finup parity, large-message length tests, and generic vs optimized comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sha2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sha3.h -->
# sources/distributed-fs/ceph-client/include/crypto/sha3.h

Purpose: declares direct SHA-3 and SHAKE sponge contexts, initialization, update, finalize/squeeze, and one-shot helpers.

Important APIs, types, and flow: constants define SHA3 digest and block sizes, SHAKE defaults, and 200-byte Keccak state size. `sha3_state` stores the sponge state; `__sha3_ctx` tracks byte index and block size; `sha3_ctx` adds digest size and finalization; `shake_ctx` supports extendable-output squeezing. Inline initializers set domain suffixes and sizes for SHA3-224/256/384/512 and SHAKE128/256. APIs update, finalize SHA-3, squeeze SHAKE output, and run one-shot variants.

State and persistence: caller-owned contexts hold sponge state and are explicitly zeroized by provided inline helpers. No persistence exists.

Dependencies and integration: integrates with hash users needing direct SHA-3/SHAKE primitives and with ML-DSA or other modern crypto implementations.

Risks and test signals: risks include domain-separation suffix mistakes, squeeze-after-update misuse, state zeroization, and block-size calculations. Signals include FIPS SHA-3/SHAKE vectors, variable-length SHAKE output tests, split-update tests, zeroization review, and generic/optimized parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sha3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sig.h -->
# sources/distributed-fs/ceph-client/include/crypto/sig.h

Purpose: exposes the public crypto API for stateless-style public-key signature algorithms.

Important APIs, types, and flow: `struct sig_alg` provides key-size, digest-size, max-size, sign, verify, set-public-key, set-private-key, optional init/exit, and base metadata callbacks. `struct crypto_sig` wraps the transform and exit callback. Helpers allocate/free transforms, query algorithm sizes, sign digests/messages, verify signatures, and load public or private keys.

State and persistence: key material is stored in transform contexts after setkey. Sign/verify buffers are caller-owned. No persistence exists.

Dependencies and integration: builds on generic crypto transforms and is consumed by public-key infrastructure, RSA/ML-DSA providers, and signature templates.

Risks and test signals: risks include key/digest/signature size reporting drift, private-key operation exposure, and algorithms with message-vs-digest semantic differences. Signals include sign/verify known-answer tests, invalid key and signature sizes, public-only verify paths, private-key sign paths, and query integration with asymmetric keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/skcipher.h -->
# sources/distributed-fs/ceph-client/include/crypto/skcipher.h

Purpose: exposes the public symmetric-key cipher API for asynchronous skcipher, synchronous skcipher, and lightweight lskcipher algorithms.

Important APIs, types, and flow: flags describe continuation/final state. `struct skcipher_request` carries cryptlen, IV, source/destination SGs, base request, and private context. `struct skcipher_alg_common`, `skcipher_alg`, and `lskcipher_alg` describe algorithm metadata and operations including setkey, encrypt/decrypt, export/import, and state size. Helpers allocate/free transforms, query names, IV/block/chunk/state/alignment/key sizes, set flags and keys, execute encrypt/decrypt, export/import mode state, perform lskcipher linear-buffer operations, allocate/free/zero requests, set callbacks, and set crypt buffers.

State and persistence: transform contexts store keys and mode state; request contexts and IV buffers are caller-owned. Export/import serializes runtime continuation state to caller buffers but no filesystem persistence exists.

Dependencies and integration: central to block/stream mode crypto, AF_ALG, dm-crypt/fs encryption users, and hardware drivers. Internal helpers in `internal/skcipher.h` implement registration and SG walking.

Risks and test signals: risks include IV reuse, request/transform mismatch, SG length errors, sync vs async allocation misuse, export/import state truncation, and lskcipher continuation flag errors. Signals include crypto manager skcipher tests, SG fragmentation, in-place/out-of-place operations, export/import continuation, zero-length and non-block-multiple handling per mode, and hardware async completion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/skcipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sm3.h -->
# sources/distributed-fs/ceph-client/include/crypto/sm3.h

Purpose: declares direct SM3 hash constants, context, and incremental/one-shot APIs.

Important APIs, types, and flow: constants define digest/block sizes and initial vector words. `sm3_block_state` and `sm3_ctx` hold incremental state, byte count, and partial block. `sm3_init()`, `sm3_update()`, `sm3_final()`, and `sm3()` implement hashing.

State and persistence: caller-owned context only; no persistence.

Dependencies and integration: used by SM2/SM4-related protocols and generic hash users requiring SM3.

Risks and test signals: risks include endian and padding differences from SHA-style code. Signals include SM3 standard vectors, split-update tests, empty-message tests, and optimized/generic parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sm3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sm4.h -->
# sources/distributed-fs/ceph-client/include/crypto/sm4.h

Purpose: declares SM4 block cipher constants, context, key expansion tables, and block primitive.

Important APIs, types, and flow: constants define 16-byte key/block sizes and 32 round-key words. `struct sm4_ctx` stores encryption and decryption round keys. Extern tables expose FK, CK, and S-box constants. `sm4_expandkey()` prepares round keys from a raw key; `sm4_crypt_block()` encrypts/decrypts one block with a selected round-key array.

State and persistence: round keys live in caller-owned/transform context and are sensitive. No persistence exists.

Dependencies and integration: used by SM4 crypto drivers and mode templates.

Risks and test signals: risks include key schedule endian handling, encrypt/decrypt round-key ordering, and table access side-channel concerns. Signals include SM4 known-answer vectors, mode self-tests, optimized/generic parity, and key zeroization review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/sm4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/streebog.h -->
# sources/distributed-fs/ceph-client/include/crypto/streebog.h

Purpose: defines Streebog/GOST R 34.11-2012 digest constants and state structures.

Important APIs, types, and flow: constants define 256-bit and 512-bit digest sizes and 64-byte block size. `struct streebog_uint512` stores 512-bit values as 64 bytes; `struct streebog_state` tracks hash state, checksum/sigma state, byte count, and partial block buffer.

State and persistence: caller-owned hash state only; no persistence.

Dependencies and integration: consumed by Streebog hash implementations under the crypto API or direct helper code.

Risks and test signals: risks include byte-order handling in 512-bit counters/checksums and finalization differences between 256/512 variants. Signals include GOST known-answer vectors, split-update tests, empty-message tests, and export/import state checks if wrapped by shash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/streebog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/twofish.h -->
# sources/distributed-fs/ceph-client/include/crypto/twofish.h

Purpose: declares Twofish block cipher constants, context, and key setup entry points.

Important APIs, types, and flow: constants define 16- to 32-byte key sizes and 16-byte block size. `struct twofish_ctx` stores key-dependent S-box words and subkeys. `__twofish_setkey()` prepares a direct context; `twofish_setkey()` adapts setkey to a crypto transform.

State and persistence: expanded key state is transform/context-local and sensitive. No persistence exists.

Dependencies and integration: used by Twofish cipher implementations and block-mode templates.

Risks and test signals: risks include key-size validation, key schedule generation, and optimized/generic divergence. Signals include Twofish known-answer vectors for 128/192/256-bit keys, mode self-tests, invalid key lengths, and key zeroization review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/twofish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/utils.h -->
# sources/distributed-fs/ceph-client/include/crypto/utils.h

Purpose: provides small shared crypto utility helpers for XOR operations and constant-time memory comparison.

Important APIs, types, and flow: `__crypto_xor()` is the external implementation for XORing two sources into a destination. `crypto_xor()` XORs a buffer in place, using word-sized operations when possible and falling back to byte operations. `crypto_xor_cpy()` XORs two input buffers into an output buffer. `crypto_memneq()` delegates to `__crypto_memneq()` to compare buffers without early-exit timing leakage.

State and persistence: stateless; all operations are caller-buffer based.

Dependencies and integration: used broadly by block modes, MACs, and verification code. Depends on unaligned access helpers and constant-time comparison implementation.

Risks and test signals: overlapping buffers, alignment, and size-zero behavior matter for XOR; comparison must remain constant-time. Signals include XOR unit tests for aligned/unaligned/overlapping buffers, KMSAN/KASAN tests, and timing-sensitive review of `crypto_memneq()` call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/xts.h -->
# sources/distributed-fs/ceph-client/include/crypto/xts.h

Purpose: defines the XTS block size and a shared key-verification helper.

Important APIs, types, and flow: `XTS_BLOCK_SIZE` is 16 bytes. `xts_verify_key()` rejects keys when the caller-provided key length is not exactly twice the underlying cipher key size or when the two halves are identical, enforcing the XTS requirement for independent data and tweak keys.

State and persistence: stateless; reads caller key bytes and transform metadata only.

Dependencies and integration: depends on skcipher transform helpers and is used by XTS mode setkey implementations.

Risks and test signals: accepting equal key halves weakens XTS, and wrong split-size logic breaks AES-XTS and other XTS ciphers. Signals include XTS setkey tests for equal halves, odd/short/long key lengths, AES-XTS vectors, and fs/dm encryption setkey coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/xts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/cxl.h -->
# sources/distributed-fs/ceph-client/include/cxl/cxl.h

Purpose: defines core CXL device-state, register-map, DPA partition, and device-state allocation contracts shared by CXL memory and Type-2 drivers.

Important APIs, types, and flow: `enum cxl_devtype` distinguishes vendor-specific Type-2 device memory from class memory Type-3 devices. `struct cxl_regs` groups mapped component, device, PMU, RCH, and RCD register block pointers. Register-map structs describe DVSEC-harvested offsets/sizes and the active register type. `struct cxl_dpa_perf` and `cxl_dpa_partition` model DPA resources, QoS/access coordinates, and RAM/PMEM mode. `struct cxl_dev_state` owns the device pointer, memdev, register maps, parsed device registers, DVSEC offset, RCD/media readiness flags, DPA resource tree, partitions, serial/type, mailbox, and optional features state. `devm_cxl_dev_state_create()` enforces that driver-specific structs embed `cxl_dev_state` at offset zero and delegates to `_devm_cxl_dev_state_create()`.

State and persistence: runtime state is devm-managed per CXL device. DPA resources and partitions model device capacity during the driver lifetime; no direct persistence is handled here.

Dependencies and integration: depends on Linux resources, NUMA/access coordinates, CXL mailbox/features, memdev objects, PCI DVSEC discovery, and register mapping code.

Risks and test signals: risks include wrong register-block offsets, Type-2 embedding contract violations, DPA partition/resource overlap, and optional feature-state Kconfig assumptions. Signals include CXL probe tests, DVSEC/register-map validation, Type-2 driver compile/runtime tests, DPA partition creation tests, and mailbox/no-mailbox device coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/cxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/einj.h -->
# sources/distributed-fs/ceph-client/include/cxl/einj.h

Purpose: declares the optional ACPI APEI EINJ CXL protocol error-injection interface.

Important APIs, types, and flow: when `CONFIG_ACPI_APEI_EINJ_CXL` is enabled, APIs expose available CXL error types through seq_file, inject errors for a downstream-port PCI device, inject RCH errors by RCRB base, and report initialization state. Disabled stubs return `-ENXIO` or `false`.

State and persistence: state is owned by the EINJ implementation; this header only exposes availability and injection entry points. No persistence exists.

Dependencies and integration: depends on ACPI APEI EINJ, PCI devices, seq_file, and CXL error handling paths.

Risks and test signals: error injection is inherently disruptive and must be gated by capability and initialization checks. Signals include disabled-Kconfig stub behavior, debugfs/sysfs available-type output, valid/invalid port injection, RCH path tests, and CXL RAS/CPER event observation after injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/einj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/event.h -->
# sources/distributed-fs/ceph-client/include/cxl/event.h

Purpose: defines CXL event, CPER event, protocol-error section, RAS capability, and work-queue handoff structures for CXL error handling.

Important APIs, types, and flow: packed record structs mirror CXL 3.x event formats: common headers, media headers, generic events, general media, DRAM, health info, memory module, and memory sparing records. `union cxl_event` and `cxl_event_record_raw` carry typed event payloads with UUIDs. CPER structures capture event record headers, device IDs, serial numbers, and protocol-error sections matching UEFI layouts, including agent type, RCRB/SBDF addressing, device ID, serial, capability, DVSEC length, error length, and RAS registers. Work APIs register/unregister GHES work items and retrieve queued CPER event/protocol-error data, with disabled stubs returning zero or `-EOPNOTSUPP`; protocol errors can be validated, converted to work data, and handled.

State and persistence: structures represent firmware-reported records and queued work data. Actual queues are implementation-owned; no persistence is declared here.

Dependencies and integration: depends on UUIDs, workqueues, ACPI APEI GHES/PCIEAER, CPER, CXL RAS, and CXL mem/event consumers.

Risks and test signals: packed ABI layout must match CXL/UEFI specs exactly; validation bits and endianness are critical. Signals include `sizeof`/offset checks, GHES CPER injection, protocol-error validation tests, disabled-Kconfig builds, event-type decoding, and RAS header-log propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/features.h -->
# sources/distributed-fs/ceph-client/include/cxl/features.h

Purpose: declares kernel-known CXL feature UUIDs and device feature-state setup helpers.

Important APIs, types, and flow: UUID macros identify patrol scrub, ECS, soft/hard PPR, cacheline sparing, row sparing, bank sparing, and rank sparing features. `enum cxl_features_capability` distinguishes no feature command support, read-only support, and read-write support. `struct cxl_features_state` links to `cxl_dev_state` and holds a counted array of feature entries plus user-visible feature count. Enabled builds expose `to_cxlfs()`, `devm_cxl_setup_features()`, and `devm_cxl_setup_fwctl()`; disabled builds return NULL or `-EOPNOTSUPP`.

State and persistence: feature discovery state is devm-managed per CXL device. Feature settings may affect device firmware through other code, but this header does not persist them.

Dependencies and integration: depends on UUID support, fwctl, CXL feature UAPI, `cxl_dev_state`, mailbox capability, and memdev setup.

Risks and test signals: UUID typos, counted-array sizing, and Kconfig stubs can hide or mis-expose device controls. Signals include CXL feature discovery tests, fwctl registration, read-only/read-write capability checks, disabled-Kconfig builds, and feature UUID matching against device mailbox responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/mailbox.h -->
# sources/distributed-fs/ceph-client/include/cxl/mailbox.h

Purpose: defines the CXL mailbox command descriptor and mailbox context used to send management commands to devices.

Important APIs, types, and flow: `struct cxl_mbox_cmd` contains opcode, input/output payload pointers, input/output sizes, minimum expected output, polling parameters for background commands, and hardware return code. `struct cxl_mailbox` owns host device, enabled and kernel-exclusive command bitmaps, payload size, mutex, `rcuwait`, transport callback `mbox_send`, and feature capability. `cxl_mailbox_init()` initializes the mailbox context for a host.

State and persistence: mailbox state is per device and runtime-only. Command payloads are caller-owned; return code and output size are updated by transport/command execution.

Dependencies and integration: depends on CXL mem UAPI command IDs, feature capability enum, mutex/rcuwait synchronization, and device-specific mailbox transports.

Risks and test signals: risks include payload size validation, command exclusivity enforcement, polling timeout handling, mailbox serialization, and return-code propagation. Signals include mailbox command unit tests, background command polling tests, concurrent ioctl/kernel command attempts, disabled command rejection, and malformed payload-size tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/cxl/mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/Makefile -->
# sources/distributed-fs/ceph-client/include/drm/Makefile

Purpose: defines the DRM header self-containment and kernel-doc validation build target.

Important APIs, types, and flow: `hdrtest-files` discovers all `*.h` headers under the DRM include directory. When `CONFIG_DRM_HEADER_TEST` is enabled, each header is transformed into a `.hdrtest` target. The command invokes the C compiler in syntax-only mode with the target header included twice to catch missing guards/self-contained include failures, then runs `kernel-doc -none` with optional `-Werror` under `CONFIG_WERROR` or `CONFIG_DRM_WERROR`, and touches the generated target.

State and persistence: no runtime state. Build artifacts are `.hdrtest` files in the object tree.

Dependencies and integration: integrates with Kbuild, `$(CC)`, `$(PYTHON3)`, `$(KERNELDOC)`, DRM header tree, and Kconfig options.

Risks and test signals: risks include shell discovery missing generated headers, false positives from non-self-contained headers, and Werror changing CI strictness. Signals include `CONFIG_DRM_HEADER_TEST=y` builds, header guard failures from double include, kernel-doc warnings, and matrix builds with DRM warning-as-error enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/amd/isp.h -->
# sources/distributed-fs/ceph-client/include/drm/amd/isp.h

Purpose: declares AMD ISP platform data and buffer allocation/free helpers shared between AMD GPU/ISP components.

Important APIs, types, and flow: `struct isp_platform_data` passes an AMD device pointer, ASIC type, and base RMMIO size to ISP platform code. User-buffer helpers import/allocate around a DMA-BUF-like object and return an opaque buffer object plus GPU address. Kernel-buffer helpers allocate/free device-accessible memory and return opaque object, GPU address, and CPU mapping.

State and persistence: buffer state is represented by opaque `buf_obj` handles managed by implementation code. Allocations are runtime-only and must be released with the matching free helper.

Dependencies and integration: depends on Linux device and resource-size types, AMD ASIC typing, DMA-BUF/GPU memory management implementation, and DRM AMD drivers.

Risks and test signals: risks include mismatched alloc/free paths, stale GPU addresses, CPU mapping lifetime, and imported user-buffer pinning. Signals include ISP probe tests, user buffer import/free tests, kernel buffer allocation/free leak checks, IOMMU/DMA mapping tests, and ASIC-type dispatch coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/amd/isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/amd_asic_type.h -->
# sources/distributed-fs/ceph-client/include/drm/amd_asic_type.h

Purpose: enumerates AMD GPU ASIC family identifiers and quirk mapping data used by AMD DRM drivers.

Important APIs, types, and flow: `enum amd_asic_type` lists GPU families from older Southern Islands parts through IP discovery, ending at `CHIP_LAST`. `amdgpu_asic_name[]` maps types to printable names. `struct amdgpu_asic_type_quirk` maps a PCI device/revision pair to the real ASIC type when discovery needs correction.

State and persistence: no runtime state is stored here, aside from extern name table data defined elsewhere.

Dependencies and integration: used by amdgpu/radeon-style code, firmware selection, feature masks, and platform data such as AMD ISP setup.

Risks and test signals: enum value stability matters because tables and logs depend on it; quirk omissions can select wrong IP blocks. Signals include PCI ID probe tests, ASIC name output, firmware loading by family, quirk table coverage for revised devices, and compile checks for `CHIP_LAST`-sized arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/amd_asic_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/analogix_dp.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/analogix_dp.h

Purpose: declares the platform interface for Analogix DisplayPort/eDP bridge core drivers.

Important APIs, types, and flow: `enum analogix_dp_devtype` identifies Exynos and Rockchip variants, with `is_rockchip()` grouping Rockchip DP/eDP devices. `struct analogix_dp_plat_data` passes device type, panel, encoder, connector, skip-connector flag, and platform callbacks for power, attach, and mode retrieval. APIs probe the core, bind/unbind it to a DRM device, suspend/resume, start/stop CRC capture, translate AUX to platform data, and retrieve the DP AUX object.

State and persistence: bridge state is owned by `struct analogix_dp_device` allocated by probe and bound to DRM components. No persistence exists.

Dependencies and integration: depends on DRM CRTC/panel/bridge/connector/DP AUX infrastructure and platform-specific power/attach hooks.

Risks and test signals: risks include connector ownership confusion when `skip_connector` is set, platform callback ordering, suspend/resume power sequencing, and AUX lifetime. Signals include DRM bridge bind/unbind tests, hotplug/mode enumeration, panel attach tests, Rockchip/Exynos variant coverage, CRC capture, and suspend/resume display recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/analogix_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/aux-bridge.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/aux-bridge.h

Purpose: declares optional helper bridges for DisplayPort AUX and HPD bridge auxiliary devices.

Important APIs, types, and flow: with `CONFIG_DRM_AUX_BRIDGE`, `drm_aux_bridge_register()` registers an AUX bridge under a parent device; otherwise it is a no-op success. With `CONFIG_DRM_AUX_HPD_BRIDGE`, devm helpers allocate/add an HPD bridge auxiliary device, a non-devm register helper creates a bridge device from parent and device node, and `drm_aux_hpd_bridge_notify()` reports connector status changes. Disabled stubs return NULL/0 or do nothing.

State and persistence: state is auxiliary-device and devm-managed bridge objects in implementation code. No persistence exists.

Dependencies and integration: depends on DRM connector status, auxiliary bus, device tree nodes, and DP bridge users.

Risks and test signals: disabled stubs returning success can hide missing bridge functionality unless callers account for Kconfig. Signals include AUX/HPD bridge registration tests, devm cleanup on probe failure, hotplug notify behavior, device-tree binding tests, and disabled-Kconfig build/runtime coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/aux-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_dp.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/dw_dp.h

Purpose: declares the platform interface for DesignWare DisplayPort bridge binding.

Important APIs, types, and flow: an anonymous enum defines single-, dual-, and quad-pixel modes. `struct dw_dp_plat_data` passes maximum link rate and pixel mode. `dw_dp_bind()` binds a DesignWare DP controller to a device and DRM encoder using the platform data, returning an opaque `dw_dp` handle.

State and persistence: DP controller state is owned by the returned `struct dw_dp` implementation object. No persistence exists.

Dependencies and integration: depends on Linux devices, DRM encoders, and platform-specific DesignWare DP driver code.

Risks and test signals: risks include unsupported pixel-mode values, link-rate negotiation mismatch, and encoder lifetime coupling. Signals include bridge bind tests, mode-setting at each pixel mode, link training at configured maximum rate, invalid platform data handling, and DRM component teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_dp.h -->
