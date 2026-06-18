# subset-b-001230 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_cipher.c Research

## Purpose
`safexcel_cipher.c` registers and implements the Inside Secure/Marvell EIP197/EIP96 symmetric cipher and AEAD Crypto API algorithms. It covers skcipher AES/DES/3DES/SM4/ChaCha20 modes, combined `authenc(hmac(...),...)` AEAD modes, XTS, GCM, CCM, ChaCha20-Poly1305, SM4+SM3 fallbacks, and IPsec wrappers such as RFC4106 GCM, RFC4543 GMAC, and RFC4309 CCM. The file translates Linux Crypto API requests into Safexcel command/result descriptors, token streams, context records, DMA mappings, and completion callbacks.

## Important APIs, Types, and Functions
The main per-transform state is `struct safexcel_cipher_ctx`, which embeds `struct safexcel_context`, the driver-private pointer, cipher mode and algorithm selectors, AEAD flags, IV/counter handling fields, key storage, HMAC/XCM hash metadata, and an optional AEAD fallback transform. Per-request state is `struct safexcel_cipher_req`, carrying encrypt/decrypt direction, result descriptor count, invalidation state, and mapped source/destination entry counts.

`safexcel_skcipher_iv()`, `safexcel_skcipher_token()`, `safexcel_aead_iv()`, and `safexcel_aead_token()` build the EIP197 token program. They handle inline IVs, RFC3686 nonces, ChaCha counters, CBC IVs, ESP IV skipping, CCM B0 construction, AAD hashing, ICV append/retrieve/verify, GCM/CCM `enc(Y0)`, and GMAC no-crypto cases.

`safexcel_skcipher_aes_setkey()`, `safexcel_skcipher_aesctr_setkey()`, `safexcel_skcipher_aesxts_setkey()`, DES/3DES/SM4 setkey helpers, `safexcel_aead_setkey()`, `safexcel_aead_gcm_setkey()`, `safexcel_aead_ccm_setkey()`, and ChaCha-Poly setkey helpers validate keys, expand AES keys where needed, extract RFC nonces, precompute GHASH or HMAC state, and mark cached contexts for invalidation when key material changes.

`safexcel_context_control()` is the central hardware context word builder. It selects crypto algorithm, mode, key size, hash/HMAC/XCM digest mode, and operation type according to `struct safexcel_cipher_ctx` and request direction. `safexcel_send_req()` maps scatterlists, writes command descriptors, writes result descriptors, attaches request tracking to the first result descriptor, and rolls descriptor write pointers and DMA maps back on failure.

`safexcel_queue_req()` allocates the context record, chooses a ring, optionally schedules a TRC-cache invalidation, enqueues the Crypto API request, and starts ring work. `safexcel_skcipher_send()`, `safexcel_aead_send()`, `safexcel_skcipher_handle_result()`, and `safexcel_aead_handle_result()` are the `safexcel_context` callbacks used by the common ring engine.

The many `struct safexcel_alg_template` instances expose the actual Crypto API algorithms, including `ecb(aes)`, `cbc(aes)`, `rfc3686(ctr(aes))`, DES/3DES ECB/CBC, AES-XTS, AES-GCM/CCM, AES/3DES/DES authenc variants with MD5/SHA1/SHA2, ChaCha20, RFC7539 ChaCha20-Poly1305 and ESP, SM4 ECB/CBC/CTR, SM4 authenc SHA1/SM3, and IPsec GCM/CCM variants.

## Control Flow
For skcipher requests, Crypto API `encrypt` or `decrypt` calls `safexcel_queue_req()`. The queue path selects or reuses a hardware ring and context record, marks invalidation if the context cache is stale, enqueues the async request, and schedules ring work. The send callback either emits an invalidate descriptor or calls `safexcel_send_req()`. That function maps input/output scatterlists, preserves CBC decrypt IVs before in-place overwrite, copies key and HMAC state into the context record, emits command descriptors over source SG segments, emits result descriptors over destination SG segments, and programs the first descriptor with context control and tokens.

Completion drains the expected result descriptors, checks hardware errors through `safexcel_rdesc_check_errors()`, completes the hardware ring, unmaps DMA, updates CBC encrypt IV from the final ciphertext block, and completes the Crypto API request. If the request was an invalidation, `safexcel_handle_inv_result()` either frees the context during transform exit or requeues the original request on a selected ring.

AEAD control flow is similar but adjusts source/destination lengths for associated data and authentication tags. Encrypt adds the digest to output; decrypt consumes the tag and verifies it. CCM, GCM, ESP, and GMAC change token sequencing and association length handling. The small/unsupported ChaCha-Poly and SM4-SM3 edge cases use fallback AEAD transforms rather than hardware.

## State and Persistence
Persistent state lives in each Crypto API transform context: selected algorithm/mode, expanded or raw key material, nonce, precomputed HMAC ipad/opad or GHASH state in the embedded `safexcel_context`, and the DMA-backed hardware context record. Request-local state tracks descriptor counts and DMA mapping counts so completion can unmap exactly what was mapped. Hardware context records are allocated from `priv->context_pool` and invalidated before reuse or exit when `EIP197_TRC_CACHE` is active.

No filesystem state is persisted. The relevant long-lived state is kernel memory, DMA mappings, hardware descriptor rings, and the registered Crypto API algorithm table.

## Dependencies and Integration Points
This file depends on the Safexcel core in `safexcel.h`, ring helpers in `safexcel_ring.c`, shared descriptor helpers such as `safexcel_add_cdesc()`, `safexcel_add_rdesc()`, `safexcel_rdr_req_set()`, `safexcel_complete()`, and `safexcel_invalidate_cache()`, and hash support through `safexcel_hmac_setkey()`. It integrates with Linux Crypto API `skcipher` and `aead`, DMA mapping, scatterlist helpers, AES/DES/SM4/ChaCha/GCM/CCM/Authenc validators, and fallback allocation through `crypto_alloc_aead()`.

## Risks and Edge Cases
Descriptor and DMA rollback is high risk: every failure path must undo command descriptors, result descriptors, and SG mappings consistently. AEAD length arithmetic is sensitive because assoclen, digest size, ESP IV skip, and decrypt tag removal interact. Several hardware limitations are handled explicitly: zero-length input gets a dummy descriptor, EIP96 SM4 blocksize errors are checked in software, ChaCha-Poly and SM4-SM3 use fallback for zero or small corner cases, and TRC-cache invalidation is required after key/state changes. Unaligned nonce loads through pointer casts and endianness conversions are correctness-sensitive. The XTS path rejects short data but still relies on correct key split and tweak-key placement.

## Test Signals
Useful tests are Crypto API self-tests and tcrypt vectors for all registered algorithm names and driver names, including in-place and out-of-place SG lists, multi-SG boundaries, zero-length and AAD-only AEAD cases, CBC IV update semantics, authentication failure on decrypt, RFC4106/RFC4309 assoclen validation, SM4 blocksize rejection, XTS short input rejection, and fallback-triggering ChaCha-Poly/SM4-SM3 cases. Runtime signals include hardware result descriptor errors, DMA mapping failures, invalidation warnings during transform exit, and request completion status under ring pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_hash.c Research

## Purpose
`safexcel_hash.c` implements Inside Secure/Marvell Safexcel asynchronous hash and MAC algorithms for the Linux Crypto API. It supports plain MD5, SHA1, SHA224, SHA256, SHA384, SHA512, SM3, SHA3 variants, HMAC variants for those hashes, AES CBC-MAC, XCBC, and CMAC. It translates `ahash_request` operations into Safexcel descriptor/token programs, handles partial-block caching and hash continuation, and supplies fallback paths where the hardware cannot support streaming, import/export, or zero-length SHA3/HMAC-SHA3 cases.

## Important APIs, Types, and Functions
`struct safexcel_ahash_ctx` holds per-transform state: embedded `safexcel_context`, selected hardware hash algorithm, key size, CBC/XCBC flags, fallback state, AES key schedule pointer for XCBC/CMAC, fallback `crypto_ahash`, prehash `crypto_shash`, and shash descriptor. `struct safexcel_ahash_req` is request-local DMA-aligned state containing flags for finish/HMAC/invalidation/fallback quirks, mapped SG/result/cache DMA addresses, digest type, state and block sizes, current hash state, total and processed lengths, and two cache buffers.

`safexcel_hash_token()` builds a four-token hash program: consume input through the hash engine, optionally pad CBC-MAC to a block boundary, insert output digest, then NOP. `safexcel_context_control()` programs the hardware context for initial hash, continuation, HMAC, XCM MACs, precomputed digest state, digest counters, and no-finish operations.

`safexcel_ahash_cache()`, `safexcel_ahash_update()`, `safexcel_ahash_final()`, `safexcel_ahash_finup()`, `safexcel_ahash_export()`, and `safexcel_ahash_import()` implement the Crypto API request lifecycle. `safexcel_ahash_send_req()` maps cache/current SG data into command descriptors, emits one result descriptor for the digest state, and updates `processed`. `safexcel_handle_req_result()` unmaps DMA, performs HMAC outer-pass continuation when needed, copies final digests, and moves deferred cache bytes.

HMAC key support is split across `safexcel_hmac_init_pad()`, `safexcel_hmac_init_iv()`, `__safexcel_hmac_setkey()`, and exported `safexcel_hmac_setkey()`, which is also used by cipher AEAD setkey code. CBC-MAC/XCBC/CMAC setkey paths precompute AES-based key material for XCM digest operation. SHA3 and HMAC-SHA3 use `safexcel_sha3_*` and `safexcel_hmac_sha3_*` wrappers with `crypto_alloc_ahash()` fallback.

## Control Flow
`init` functions zero request state, set algorithm selectors, digest mode, digest size, state size, block size, and HMAC starting state. `update` first tries to cache data until enough bytes exist for a hardware block. If the cache overflows or this is the last request, it enqueues the request to the Safexcel ring. The send callback either emits a cache invalidation descriptor or constructs command descriptors over cached bytes plus SG bytes. For non-final updates, the code keeps one block cached so final padding remains correct.

On completion, the result descriptor is checked, DMA mappings are undone, and the hardware-produced digest state is kept in `req->state`. Final HMAC may require a second internal hash pass when the hardware cannot perform the direct HMAC finish, so completion rewrites request state with opad and re-enqueues without completing the original request. Final plain hashes copy the digest from request state to `areq->result`.

Zero-length hashes are handled in software for MD5/SHA1/SHA2/SM3 using known constants. Zero-length CBC-MAC/XCBC/CMAC and zero-length HMAC have special synthetic states or padding. SHA3 update/final/export/import routes to fallback because hardware is only used for single non-empty digest/finup style flows.

## State and Persistence
The transform context persists hardware context records, HMAC ipad/opad state, fallback transforms, and AES key schedules. Request state persists rolling hash state, byte counters, deferred block cache, and DMA addresses between update/final calls. Context records are DMA pool allocations and may require TRC-cache invalidation when continuation state or HMAC outer state changes. No filesystem state is persisted.

## Dependencies and Integration Points
The file integrates with Linux `ahash`, `shash`, AES helper APIs, HMAC constants, scatterlist copying, DMA mapping, and Safexcel ring/core functions. It exports `safexcel_hmac_setkey()` to the cipher/AEAD file so combined authenc algorithms can reuse the same HMAC precompute logic. SHA3/HMAC-SHA3 fallback depends on generic Crypto API implementations of the same algorithm names.

## Risks and Edge Cases
Partial-block caching and length accounting are the main correctness risks: `len`, `processed`, `cache`, and `cache_next` must stay consistent across update/final/import/export. HMAC continuation has hardware-specific limitations, including fake outer passes, zero-length HMAC padding, digest counters with a 32-bit hardware limit, and TRC invalidation when state changes. CBC-MAC/XCBC/CMAC have custom padding and AES subkey transformations where endianness matters. SHA3 fallback state is subtle because some operations begin on hardware but update/export/import force fallback. DMA rollback must cover cache, SG, result mapping, and descriptor write pointers.

## Test Signals
Use Crypto API self-tests and known-answer tests for plain hashes, HMACs, SM3, SHA3, CBC-MAC, XCBC, and CMAC. Important cases include zero-length digest and HMAC, repeated small updates, updates crossing block size, import/export after partial updates, long inputs near digest counter limits, multi-SG requests, callback completion after requeued HMAC outer pass, SHA3 fallback after update/export/import, and context invalidation under repeated setkey or continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_ring.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_ring.c Research

## Purpose
`safexcel_ring.c` provides descriptor ring allocation and pointer management for the Safexcel EIP197/EIP97 crypto driver. It owns the low-level command descriptor ring (CDR), command shadow token ring, and result descriptor ring (RDR) helpers used by cipher, hash, and other Safexcel algorithm files.

## Important APIs, Types, and Functions
`safexcel_init_ring_descriptors()` allocates coherent DMA memory for CDR, CDR shadow token storage, and RDR using offsets from `priv->config`. It initializes read/write pointers and pre-populates each command descriptor's `atok_lo`/`atok_hi` fields with the DMA address of its shadow token area.

`safexcel_select_ring()` round-robins requests over the configured hardware rings using `atomic_inc_return(&priv->ring_used)`.

Internal helpers `safexcel_ring_next_cwptr()` and `safexcel_ring_next_rwptr()` reserve the next command or result slot, detect ring-full conditions, update write pointers with wraparound, and return `ERR_PTR(-ENOMEM)` when no descriptor is available. `safexcel_ring_next_rptr()` consumes the next result descriptor and returns `ERR_PTR(-ENOENT)` when the ring is empty. `safexcel_ring_curr_rptr()`, `safexcel_ring_first_rdr_index()`, and `safexcel_ring_rdr_rdesc_index()` expose read pointer/index information to the core request tracking code.

`safexcel_ring_rollback_wptr()` backs up a write pointer after partially constructed requests fail. `safexcel_add_cdesc()` fills a command descriptor with segment flags, data DMA address, packet length, context pointer, and first-descriptor control options. `safexcel_add_rdesc()` fills a result descriptor with destination DMA address, segment flags, result token size, and pessimistic error defaults that hardware clears on success.

## Control Flow
Probe/setup calls `safexcel_init_ring_descriptors()` for each ring. Algorithm send paths reserve one command descriptor per input segment through `safexcel_add_cdesc()` and one result descriptor per output segment through `safexcel_add_rdesc()`. If any reservation fails, the caller rolls back already reserved descriptors with `safexcel_ring_rollback_wptr()`. Completion paths consume descriptors with `safexcel_ring_next_rptr()`.

## State and Persistence
All state is in DMA-coherent ring memory and in-memory read/write pointers inside `struct safexcel_desc_ring`. The ring keeps separate command shadow write pointers because token memory is parallel to command descriptors. State persists only while the driver/device instance is alive.

## Dependencies and Integration Points
The file depends on descriptor layouts and constants from `safexcel.h`, DMA allocation APIs, and bit helpers for 64-bit DMA addresses. It is a shared integration point for Safexcel cipher/hash request builders and core completion code.

## Risks and Edge Cases
Ring-full checks rely on pointer arithmetic over byte-addressed descriptor regions. Offsets must match hardware descriptor sizes supplied by `priv->config`, or pointer wrap and index calculations become wrong. `safexcel_add_cdesc()` deliberately forces first packet length to at least one byte because EIP97 can hang on zero-length input; callers must still use dummy-safe buffers. Rollback must be called the exact number of successful reservations.

## Test Signals
Stress tests should exercise ring wraparound, full-ring backpressure, multi-segment requests, descriptor rollback after induced result-ring exhaustion, empty result-ring reads, zero-length request paths, and mixed cipher/hash traffic over multiple rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/Kconfig Research

## Purpose
This Kconfig fragment is the Intel crypto driver menu aggregator. It includes the per-driver Kconfig files for Intel Keem Bay, IXP4xx, QAT, and IAA crypto support.

## Important APIs, Types, and Functions
There are no C APIs or runtime functions. The important entries are four `source` directives:
`drivers/crypto/intel/keembay/Kconfig`, `drivers/crypto/intel/ixp4xx/Kconfig`, `drivers/crypto/intel/qat/Kconfig`, and `drivers/crypto/intel/iaa/Kconfig`.

## Control Flow
During Kconfig processing, this file pulls child menu/config definitions into the Intel crypto subtree. The IAA option researched in this subset is reachable only because this file sources `drivers/crypto/intel/iaa/Kconfig`.

## State and Persistence
It contributes build configuration symbols to the kernel `.config`. It has no runtime state.

## Dependencies and Integration Points
It integrates with the kernel Kconfig build system and the parent `drivers/crypto` Kconfig hierarchy. Its child entries control which Intel crypto driver directories the Makefile can build.

## Risks and Edge Cases
If a child Kconfig path is wrong or omitted, its driver options disappear from configuration even if source code exists. Ordering is simple and has no visible dependency logic here.

## Test Signals
Run `make menuconfig`/`olddefconfig` and verify Intel crypto options appear. Build coverage should confirm that enabling `CRYPTO_DEV_IAA_CRYPTO` reaches the IAA Makefile path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/Makefile Research

## Purpose
This Makefile routes enabled Intel crypto driver builds into their subdirectories.

## Important APIs, Types, and Functions
There are no runtime APIs. Build rules add `keembay/` and `ixp4xx/` unconditionally to `obj-y`, add `qat/` when `CONFIG_CRYPTO_DEV_QAT` is enabled, and add `iaa/` when `CONFIG_CRYPTO_DEV_IAA_CRYPTO` is enabled.

## Control Flow
Kbuild evaluates the object lists after configuration. If IAA crypto is selected, Kbuild descends into `drivers/crypto/intel/iaa/` and evaluates that directory's Makefile.

## State and Persistence
The file affects build artifacts only. It has no runtime state.

## Dependencies and Integration Points
It depends on symbols defined in child Kconfig files and integrates with the parent `drivers/crypto` Kbuild traversal.

## Risks and Edge Cases
The directory inclusion is symbol-sensitive. A mismatch between Kconfig symbol names and Makefile conditionals would silently skip a selected driver. Here, IAA uses `CONFIG_CRYPTO_DEV_IAA_CRYPTO`, matching the researched IAA Kconfig.

## Test Signals
Enable and disable `CONFIG_CRYPTO_DEV_IAA_CRYPTO` and check that `drivers/crypto/intel/iaa/iaa_crypto.o` is or is not built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Kconfig Research

## Purpose
This Kconfig file defines configuration switches for the Intel Analytics Accelerator (IAA) compression accelerator crypto driver and its optional statistics support.

## Important APIs, Types, and Functions
`CONFIG_CRYPTO_DEV_IAA_CRYPTO` is a tristate option titled `Support for Intel(R) IAA Compression Accelerator`. It depends on `CRYPTO_DEFLATE` and `INTEL_IDXD`, defaults to `n`, and builds module `iaa_crypto` when selected as a module. `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS` is a bool option depending on IAA crypto and enables per-device, per-workqueue, and global driver statistics.

## Control Flow
Configuration selection controls whether the IAA directory is entered by the Intel Makefile and whether `iaa_crypto_stats.o` is added by the IAA Makefile. Runtime code in `iaa_crypto_main.c` also compiles against stats update functions that are either real functions or inline no-ops depending on the stats symbol.

## State and Persistence
The selected symbols persist in kernel `.config` and govern built-in/module output. They have no direct runtime storage, although enabling stats adds runtime counters and debugfs files in companion code.

## Dependencies and Integration Points
The driver requires the Intel IDXD bus/workqueue infrastructure and the Crypto API deflate implementation. The dependency on `CRYPTO_DEFLATE` is important because the IAA driver registers an acomp `deflate` implementation and uses generic deflate fallback for some decompression errors.

## Risks and Edge Cases
Missing `INTEL_IDXD` prevents the driver from binding to IAA workqueues. Missing `CRYPTO_DEFLATE` would break fallback and algorithm integration, so it is correctly enforced. Stats are optional, so code paths must remain valid with no-op stats functions.

## Test Signals
Kconfig tests should verify dependency enforcement, module name `iaa_crypto`, stats object inclusion only when requested, and successful builds for built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Makefile Research

## Purpose
This Makefile builds the Intel IAA crypto module and sets include paths and symbol namespace defaults required for IDXD integration.

## Important APIs, Types, and Functions
`ccflags-y` adds the IDXD driver include path and defines `DEFAULT_SYMBOL_NAMESPACE` as `"IDXD"`. `obj-$(CONFIG_CRYPTO_DEV_IAA_CRYPTO) := iaa_crypto.o` creates the module or built-in object. `iaa_crypto-y` is composed from `iaa_crypto_main.o` and `iaa_crypto_comp_fixed.o`. `iaa_crypto-$(CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS)` conditionally adds `iaa_crypto_stats.o`.

## Control Flow
Kbuild evaluates this file only when the parent Intel Makefile descends into `iaa/`. The composite object is linked from the listed translation units. Stats functions resolve either to compiled stats code or inline no-ops from the stats header depending on configuration.

## State and Persistence
The Makefile affects build artifacts and symbol namespace metadata. It has no runtime state.

## Dependencies and Integration Points
It integrates with `drivers/dma/idxd` headers and the IDXD exported symbol namespace. It connects Kconfig symbols to actual objects.

## Risks and Edge Cases
The namespace define and `MODULE_IMPORT_NS("IDXD")` in the C file must remain aligned with IDXD exports. Missing `iaa_crypto_comp_fixed.o` would leave the fixed Huffman mode unregistered. Missing stats object when stats are enabled would break debugfs/stat update linkage.

## Test Signals
Build with IAA enabled/disabled and stats enabled/disabled. Inspect `modinfo iaa_crypto` and link output for expected objects and IDXD namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto.h Research

## Purpose
`iaa_crypto.h` is the shared internal header for the Intel IAA crypto compression driver. It defines hardware operation flags, completion constants, compression-mode limits, fixed-deflate metadata, workqueue/device state structures, AECS table layout, compression mode registration APIs, and per-transform Crypto API context.

## Important APIs, Types, and Functions
Important constants include IAA decompress flags (`IAA_DECOMP_ENABLE`, `IAA_DECOMP_FLUSH_OUTPUT`, `IAA_DECOMP_CHECK_FOR_EOB`, `IAA_DECOMP_STOP_ON_EOB`, `IAA_DECOMP_SUPPRESS_OUTPUT`), compress flags (`IAA_COMP_FLUSH_OUTPUT`, `IAA_COMP_APPEND_EOB`), `IAA_COMPLETION_TIMEOUT`, known error/status codes, `IAA_COMP_MODES_MAX`, fixed header constants, and aggregate `IAA_COMP_FLAGS`/`IAA_DECOMP_FLAGS`.

`struct iaa_wq` represents an IDXD workqueue bound to crypto. It tracks list membership, the underlying `idxd_wq`, reference count, remove flag, parent `iaa_device`, and optional stats counters. `struct iaa_device` groups IDXD device state, per-mode DMA tables, workqueue list/count, and optional stats counters. `struct wq_table_entry` is the per-CPU workqueue selection table.

`struct aecs_comp_table_record` models the IAA Analytics Engine Configuration and State compression table, including CRC/checksum fields, output accumulator, literal/length symbols, and distance symbols. `struct iaa_compression_mode` stores global mode definition tables plus optional per-device init/free hooks. `struct iaa_device_compression_mode` stores per-device DMA-coherent AECS state.

The exported APIs are `iaa_aecs_init_fixed()`, `iaa_aecs_cleanup_fixed()`, `add_iaa_compression_mode()`, and `remove_iaa_compression_mode()`. `struct iaa_compression_ctx` is the Crypto API transform context, containing compression mode, verification setting, async mode, and interrupt mode. The header also declares global `iaa_devices` and `iaa_devices_lock`.

## Control Flow
`iaa_crypto_comp_fixed.c` registers a global fixed compression mode through `add_iaa_compression_mode()`. `iaa_crypto_main.c` copies those mode tables into per-device DMA AECS tables when IDXD workqueues probe, uses `iaa_compression_ctx` during acomp operations, and references `iaa_wq`/`iaa_device` to select hardware resources.

## State and Persistence
The header defines only in-memory kernel state. Global compression modes persist while the module is loaded; per-device modes persist while IAA devices/workqueues are bound; per-transform contexts persist while a Crypto API transform exists.

## Dependencies and Integration Points
It depends on Linux Crypto API headers, IDXD core and UAPI headers, list/mutex users in the C files, and hardware descriptor definitions from IDXD. It is the contract between the fixed-mode table file, main IAA driver, and stats code.

## Risks and Edge Cases
`IAA_COMP_MODES_MAX` is only two, so new modes can fail registration if slots are exhausted. `struct aecs_comp_table_record` is packed and hardware-facing; layout or alignment changes can break DMA programming. Reference and remove fields in `iaa_wq` are central to hot-remove safety. Optional stats fields are present in structures regardless of stats object linkage, so update functions must be valid in both configurations.

## Test Signals
Compile tests should cover stats on/off. Runtime tests should validate mode registration/removal ordering, per-device AECS DMA allocation, hot-remove with active references, and fixed mode availability in the acomp `deflate` algorithm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_comp_fixed.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_comp_fixed.c Research

## Purpose
`iaa_crypto_comp_fixed.c` defines the static fixed-Huffman DEFLATE tables used by Intel IAA hardware and registers the `"fixed"` compression mode with the IAA crypto core.

## Important APIs, Types, and Functions
`fixed_ll_sym[286]` and `fixed_d_sym[30]` encode the RFC1951 fixed Huffman literal/length and distance tables in the format expected by IAA AECS compression state. `init_fixed_mode()` initializes per-device AECS state by clearing CRC/checksum fields, writing a fixed-block header (`FIXED_HDR | bfinal`) into `output_accum`, and setting `num_output_accum_bits` to `FIXED_HDR_SIZE`.

`iaa_aecs_init_fixed()` calls `add_iaa_compression_mode("fixed", ...)` with the fixed tables and init callback. `iaa_aecs_cleanup_fixed()` removes that mode through `remove_iaa_compression_mode("fixed")`.

## Control Flow
Module init in `iaa_crypto_main.c` calls `iaa_aecs_init_fixed()` before registering the IDXD subdriver. Later, each probed IAA device copies the global fixed tables into a DMA-coherent per-device `aecs_comp_table_record` and calls `init_fixed_mode()`. Module cleanup calls `iaa_aecs_cleanup_fixed()` after unregistering the IDXD driver.

## State and Persistence
The static tables are read-only kernel data. The registered compression mode persists globally while the module is loaded and no IAA devices are active during add/remove. Per-device copies are allocated and freed by main driver code.

## Dependencies and Integration Points
The file includes `idxd.h` and `iaa_crypto.h` for AECS structures, mode registration APIs, and constants. It is required by `iaa_crypto_main.c` because the exposed acomp algorithm uses `IAA_MODE_FIXED`.

## Risks and Edge Cases
The table values are hardware-specific and not self-validating. Any transcription error would produce invalid compressed output or verification failures. `init_fixed_mode()` assumes `num_output_accum_bits` is initially zeroed by the allocator before computing the byte offset. Mode registration must happen before devices are added, matching the lock/order restrictions in `add_iaa_compression_mode()`.

## Test Signals
Compression known-answer tests should verify fixed-Huffman DEFLATE output can be decompressed by generic deflate. Compression verification mode should catch CRC or table mistakes. Module load/unload tests should confirm fixed mode registration and removal succeed with no active devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_comp_fixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_main.c Research

## Purpose
`iaa_crypto_main.c` is the main Intel Analytics Accelerator crypto driver. It binds to IDXD IAX workqueues, creates a per-CPU workqueue selection table, registers a Crypto API async compression algorithm named `deflate` with driver name `deflate-iaa`, builds IAA hardware descriptors for compression/decompression, optionally verifies compressed output by hardware decompression and CRC comparison, exposes sysfs controls, and handles module/probe/remove lifecycle.

## Important APIs, Types, and Functions
Global state includes `nr_iaa`, CPU/node counts, `cpus_per_iaa`, per-CPU `wq_table`, global `iaa_devices`, `iaa_devices_lock`, `iaa_crypto_enabled`, `iaa_crypto_registered`, `iaa_verify_compress`, and sync-mode flags `async_mode`/`use_irq`.

Sysfs driver attributes are `verify_compress` and `sync_mode`. They are writable only while IAA crypto is disabled. `set_iaa_sync_mode()` maps strings to operation flags, although the `"async"` branch currently sets the same flags as `"sync"`, making the `async_mode && !use_irq` display branch unreachable from the store path.

Compression mode APIs `add_iaa_compression_mode()` and `remove_iaa_compression_mode()` manage global compression modes before devices exist. `init_device_compression_mode()` allocates per-device DMA-coherent AECS tables and copies mode Huffman tables into them. Workqueue/device helpers include `save_iaa_wq()`, `remove_iaa_wq()`, `iaa_wq_get()`, `iaa_wq_put()`, `alloc_wq_table()`, `rebalance_wq_table()`, and `wq_table_next_wq()`.

The data path is implemented by `iaa_comp_acompress()` and `iaa_comp_adecompress()`. They select a workqueue for the current CPU, take a workqueue reference, map source and destination SG lists, call `iaa_compress()` or `iaa_decompress()`, handle synchronous or asynchronous completion, unmap DMA, and release the workqueue. `check_completion()` polls completion records and maps hardware status to Linux errors. `iaa_desc_complete()` handles interrupt-driven asynchronous completions. `deflate_generic_decompress()` is a software fallback for selected decompression analytics errors.

`iaa_register_compression_device()` registers `iaa_acomp_fixed_deflate`; `iaa_crypto_probe()` binds an IDXD workqueue, initializes global tables on the first workqueue, saves/rebalances workqueues, registers the Crypto API algorithm, and enables the driver. `iaa_crypto_remove()` quiesces and removes a workqueue, waits for references through remove flags, disables the driver on last removal, and frees the per-CPU table.

## Control Flow
Module init counts CPUs and NUMA nodes, registers the fixed compression mode, registers the IDXD subdriver, creates sysfs attributes, and initializes debugfs stats if available. Probe accepts only enabled IAX devices with matching workqueue driver names, enables the IDXD workqueue, creates the global workqueue table on first bind, initializes per-device compression modes, rebalances CPU-to-workqueue mappings, registers the acomp algorithm on first workqueue, and marks `iaa_crypto_enabled`.

Compression requests enter through Crypto API acomp. The driver rejects disabled state or missing source data, selects a workqueue via the per-CPU table, maps a single source and destination SG entry, fills an IAX compress descriptor with source, destination, AECS table, completion address, and flags, submits it to IDXD, and either polls or returns `-EINPROGRESS` depending on context mode. If verification is enabled, it remaps buffers in reverse directions, submits a suppress-output decompression descriptor, and compares CRCs.

Decompression mirrors compression but builds an IAX decompress descriptor. If hardware returns an analytics error, the synchronous and IRQ completion paths can fall back to generic deflate decompression. Remove flow quiesces the workqueue first, then removes it from selection structures while preserving active references until `iaa_wq_put()`.

## State and Persistence
Runtime state is fully in kernel memory: global mode registry, per-device mode DMA tables, per-workqueue reference/remove state, per-CPU workqueue arrays, Crypto API registration state, sysfs-controllable defaults, and optional stats counters. Per-transform `iaa_compression_ctx` snapshots verification and sync-mode defaults at transform init; changing sysfs attributes later does not alter existing transform contexts.

## Dependencies and Integration Points
The file depends on IDXD core APIs for workqueue enable/disable, descriptor allocation/submission/freeing, completion callbacks, and workqueue private data. It depends on `iaa_crypto.h` for structures and flags, `iaa_crypto_comp_fixed.c` for fixed-mode registration, optional `iaa_crypto_stats` for counters/debugfs, Linux DMA mapping and scatterlist APIs, sysfs driver attributes, module lifecycle, and Crypto API `acompress`.

## Risks and Edge Cases
The data path only accepts SG mappings that collapse to one DMA segment; multi-segment inputs return `-EIO`, which is a functional limitation tests must capture. DMA unmap direction changes during verification are delicate. Async mode without IRQ appears unselectable because `set_iaa_sync_mode("async")` sets `async_mode = false`; if intentional, the mode description is stale, and if not, async polling mode is broken. `check_completion()` disables global IAA crypto on completion timeout, affecting all users. Hot-remove safety depends on `iaa_wq_get()`/`iaa_wq_put()` reference ordering and `remove` flags. The compression mode registry refuses add/remove while devices exist, so module ordering is strict. Per-transform contexts snapshot global sysfs settings, which may surprise users expecting live changes.

## Test Signals
Test module load/unload, IDXD workqueue probe/remove, first/last workqueue registration, sysfs writes before and after enable, sync/async_irq behavior, compression/decompression known-answer tests, verification CRC mismatch handling, hardware buffer overflow mapping to `-E2BIG` or `-EOVERFLOW`, software fallback on analytics decompression errors, completion timeout disabling, single-vs-multi-SG behavior, CPU hotplug/NUMA selection assumptions, stats on/off builds, and hot-remove during in-flight async acomp requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_main.c -->
