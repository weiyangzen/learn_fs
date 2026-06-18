# subset-b-000930 Research

Grouped research report for the requested `sources/distributed-fs/ceph-client/crypto` subset. Each source file has a delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/crypto/Kconfig

Purpose: defines the kernel cryptographic API configuration surface: core crypto framework options, self-test/FIPS controls, public-key algorithms, block ciphers, modes, AEADs, hashes, CRCs, compression, RNGs, userspace AF_ALG interfaces, and architecture/driver crypto submenus.

Important APIs, types, and functions: this is Kconfig data rather than C code. Key symbols include `CRYPTO`, `CRYPTO_ALGAPI`, `CRYPTO_MANAGER`, `CRYPTO_SELFTESTS`, `CRYPTO_FIPS`, front-end families such as `CRYPTO_AEAD`, `CRYPTO_SKCIPHER`, `CRYPTO_HASH`, `CRYPTO_RNG`, `CRYPTO_AKCIPHER`, `CRYPTO_ACOMP`, algorithms such as `CRYPTO_AES`, `CRYPTO_ADIANTUM`, `CRYPTO_AEGIS128`, hash/MAC selections, compression selections, and `CRYPTO_USER_API_*` switches.

Control flow and behavior: selecting `CRYPTO` opens the whole menu and sources `crypto/async_tx/Kconfig`, architecture Kconfigs, driver crypto Kconfig, asymmetric keys, certs, and Kerberos crypto. Many public options select hidden second-level implementation symbols, which then drive object inclusion in the Makefile. `CRYPTO_MANAGER2` is forced when the algorithm API is built in with manager not disabled, ensuring templates and self-test infrastructure are available when needed.

State and persistence: the file persists kernel build configuration, not runtime state. Its selected tristate/bool/string values become `.config` inputs and determine compiled-in or modular crypto code, FIPS metadata strings, jitter entropy tunables, and exposed userspace interfaces.

Dependencies and integration points: it integrates with `crypto/Makefile`, architecture crypto directories, `drivers/crypto`, `certs`, `crypto/asymmetric_keys`, and consumers such as IPsec, fscrypt, dm-crypt, NFS/RxRPC Kerberos, and AF_ALG userspace clients. `select` chains pull in crypto libraries, ASN.1 parsers, MPILIB, compression libraries, and RNG prerequisites.

Risks and correctness concerns: dependency mistakes can expose algorithms without their core API, omit self-tests in FIPS-related builds, or allow obsolete algorithms when not intended. `select` is forceful in Kconfig, so new dependencies must avoid impossible combinations and recursive selections. FIPS options require especially careful alignment with self-tests, module signatures, and DRBG availability.

Test signals: use `olddefconfig`, `allmodconfig`, `allyesconfig`, minimal crypto builds, and FIPS/self-test build matrices. Validate module/object inclusion against `crypto/Makefile`, boot-time algorithm self-tests, AF_ALG socket availability for selected userspace APIs, and architecture submenu coverage with `KMSAN` excluded assembly paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/Makefile -->
# sources/distributed-fs/ceph-client/crypto/Makefile

Purpose: maps crypto Kconfig symbols to built objects and composite modules for the Linux crypto subsystem. It is the build-time contract connecting selected algorithms, templates, API front ends, userspace interfaces, and architecture-sensitive AEGIS NEON objects.

Important APIs, types, and functions: this is kbuild metadata. It defines composite objects such as `crypto.o`, `crypto_algapi.o`, `crypto_skcipher.o`, `crypto_hash.o`, `crypto_acompress.o`, `cryptomgr.o`, `rsa_generic.o`, `ecdsa_generic.o`, `ecdh_generic.o`, `ecrdsa_generic.o`, `jitterentropy_rng.o`, `crc32c-cryptoapi.o`, `crc32-cryptoapi.o`, and `aegis128-y`.

Control flow and behavior: `obj-$(CONFIG_...)` lines include modules or built-ins according to Kconfig. Core front ends build from multiple source files, e.g. `crypto_hash-y := ahash.o shash.o`, `crypto_algapi-y := algapi.o scatterwalk.o proc.o`, and `cryptomgr-y := algboss.o testmgr.o`. Architecture conditionals add AEGIS NEON glue only for ARM/ARM64 when `CONFIG_CRYPTO_AEGIS128_SIMD` is enabled and attach special compiler flags.

State and persistence: the file has no runtime state; it determines build artifacts, module composition, generated ASN.1 dependencies, and compile flags. Its decisions persist in the built kernel tree as object membership and module names.

Dependencies and integration points: it depends directly on Kconfig symbols from `crypto/Kconfig`, generated ASN.1 files, compiler capability macros, and architecture settings. Runtime integration follows from objects included here: AF_ALG modules, algorithm modules, crypto manager, FIPS support, async_tx, asymmetric keys, and Kerberos crypto.

Risks and correctness concerns: mismatched Kconfig and Makefile entries cause selected algorithms to be unavailable or unselected files to build. Composite object omissions are easy to miss for template modules and generated ASN.1 helpers. ARM64 AEGIS flags are sensitive: NEON/AES intrinsics need `-ffreestanding`, crypto CPU features, GCC fixed vector registers, and removal of `-mgeneral-regs-only`.

Test signals: compare every selected Kconfig symbol against an object rule, run representative `make M=crypto` and full kernel builds for ARM, ARM64, x86, and allmodconfig. Verify module aliases load expected objects such as `af_alg`, `algif_hash`, `aegis128`, `adiantum`, and `aes`; test generated ASN.1 dependency rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/acompress.c -->
# sources/distributed-fs/ceph-client/crypto/acompress.c

Purpose: implements the asynchronous compression (`acomp`) crypto API front end, including transform allocation, algorithm registration, request dispatch, virtual/scatterlist conversion, synchronous fallback handling, per-CPU stream context management, and compression scatter-walk helpers.

Important APIs, types, and functions: exported entry points include `crypto_alloc_acomp()`, `crypto_alloc_acomp_node()`, `crypto_acomp_compress()`, `crypto_acomp_decompress()`, `crypto_register_acomp()`, `crypto_unregister_acomp()`, batch registration helpers, stream helpers `crypto_acomp_alloc_streams()`, `_crypto_acomp_lock_stream_bh()`, and walk helpers `acomp_walk_virt()`, `acomp_walk_next_src()`, `acomp_walk_next_dst()`, `acomp_walk_done_src()`, `acomp_walk_done_dst()`, plus `acomp_request_clone()`.

Control flow and behavior: `crypto_acomp_init_tfm()` sets algorithm callbacks and, for async algorithms, allocates a same-name synchronous fallback constrained by `MAX_SYNC_COMP_REQSIZE`. Request entry points reject stack requests on async transforms, direct-dispatch scatterlist or native-virtual requests, and otherwise convert virtual buffers into one-entry scatterlists. Completion wrappers save/restore the original callback and request data so chained fallback or converted requests complete as if submitted directly.

State and persistence: transform state lives in `struct crypto_acomp` and optional fallback `tfm->fb`. Request mutation is transient in `struct acomp_req_chain`, which stores original callback/data and virtual buffer metadata. Stream state persists per CPU in `struct crypto_acomp_streams` until explicitly freed; missing CPU-local contexts are allocated asynchronously by `stream_work`.

Dependencies and integration points: depends on `crypto/internal/acompress.h`, `crypto/scatterwalk.h`, generic `crypto_register_alg()`, proc/netlink reporting, percpu allocation, workqueues, cpumasks, and `compress.h` for scomp integration. Compression algorithms such as deflate/lzo/lz4/zstd register through this front end.

Risks and correctness concerns: virtual-buffer conversion rewrites request source/destination and must restore them exactly, especially across async completion. Stack requests cannot be safely queued to async algorithms. Per-CPU stream fallback to the first possible CPU must avoid unlocked access; cleanup must cancel work before freeing contexts. Walk helpers must handle sleeping, linear buffers, scatterwalk advancement, and zero-length validation consistently.

Test signals: exercise compression/decompression with SG and virtual buffers, async and sync algorithms, stack request rejection, fallback request size limits, callback ordering with `-EINPROGRESS` and `-EBUSY`, CPU hotplug/per-CPU streams, and scatterwalk chunking under preemptible and non-preemptible builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/acompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/adiantum.c -->
# sources/distributed-fs/ceph-client/crypto/adiantum.c

Purpose: implements the `adiantum(streamcipher,blockcipher)` length-preserving skcipher template, designed for storage encryption on CPUs without fast AES. It combines XChaCha12/20, NHPoly1305 hashing, and one 128-bit block-cipher invocation.

Important APIs, types, and functions: major structures are `adiantum_instance_ctx`, `adiantum_tfm_ctx`, `nhpoly1305_ctx`, and `adiantum_request_ctx`. Key functions include `adiantum_setkey()`, `adiantum_hash_header()`, `nhpoly1305_update()`, `nhpoly1305_final()`, `adiantum_hash_message()`, `adiantum_crypt()`, `adiantum_encrypt()`, `adiantum_decrypt()`, `adiantum_init_tfm()`, `adiantum_free_instance()`, `adiantum_supported_algorithms()`, and template `adiantum_create()`.

Control flow and behavior: `adiantum_create()` parses template attributes, grabs a stream cipher and block cipher, validates supported combinations, derives names/priorities, and registers a skcipher instance. `adiantum_setkey()` sets the stream key, derives block/hash subkeys by encrypting zero bytes with XChaCha nonce `1||0`, then initializes AES/block-cipher and Poly1305/NH keys. `adiantum_crypt()` hashes the tweak and left-hand message, transforms the right-hand 16-byte block, runs XChaCha over the bulk, then hashes the output bulk and writes the final right-hand block.

State and persistence: instance state stores crypto spawns; transform state stores child tfms and derived keys. Request state overlays NHPoly1305 state and a child skcipher request to save memory. No disk persistence exists, but the mode is intended for persistent encrypted storage sectors, so deterministic tweak/key handling is critical.

Dependencies and integration points: integrates with the skcipher template API, child skcipher/cipher spawns, `crypto/nh.h`, Poly1305 core, ChaCha/XChaCha constants, scatterwalk helpers, and fscrypt/dm-crypt style callers that need 32-byte tweaks. It imports `CRYPTO_INTERNAL`.

Risks and correctness concerns: the mode requires at least one 16-byte block; scatterlist fast paths must not read beyond mapped pages. NHPoly1305 buffering must produce the same hash independent of SG chunking. Subkey derivation must wipe temporary key material. Template validation must reject unsupported stream ciphers, block sizes, key sizes, and obsolete third hashing parameter.

Test signals: use known-answer tests for `adiantum(xchacha12,aes)` and `adiantum(xchacha20,aes)`, in-place and out-of-place SG layouts, single-page and multi-page paths, minimum length rejection, 32-byte tweak handling, async child cipher errors, and fscrypt/dm-crypt sector-size workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/adiantum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aead.c -->
# sources/distributed-fs/ceph-client/crypto/aead.c

Purpose: provides the generic AEAD crypto API front end: key setup, authsize validation, encrypt/decrypt dispatch, allocation, spawn grabbing, algorithm and template instance registration, proc reporting, and netlink reporting.

Important APIs, types, and functions: exported calls include `crypto_aead_setkey()`, `crypto_aead_setauthsize()`, `crypto_aead_encrypt()`, `crypto_aead_decrypt()`, `crypto_grab_aead()`, `crypto_alloc_aead()`, `crypto_alloc_sync_aead()`, `crypto_has_aead()`, `crypto_register_aead()`, `crypto_unregister_aead()`, batch helpers, and `aead_register_instance()`.

Control flow and behavior: `crypto_aead_setkey()` handles key alignment by copying to an aligned temporary buffer when required, propagates algorithm setkey errors, and manages `CRYPTO_TFM_NEED_KEY`. Encryption/decryption reject unkeyed transforms; decryption also verifies `cryptlen >= authsize`. Transform initialization defaults authsize to `maxauthsize`, sets request size, and installs an exit hook when needed. Registration validates authsize/iv/chunksize bounds and stamps the crypto type.

State and persistence: per-transform state is held by `struct crypto_aead`, including flags, authsize, request size, and algorithm-private context. The file has no persistent storage; registered algorithms persist in the global crypto registry until unregistered.

Dependencies and integration points: depends on `crypto/internal/aead.h`, generic `crypto_alloc_tfm()` and `crypto_register_alg()`, procfs, netlink cryptouser reporting, and template/spawn infrastructure from `algapi.c`. AEAD implementations such as GCM, CCM, ChaCha20-Poly1305, and AEGIS register through this layer.

Risks and correctness concerns: authsize zero is allowed only for algorithms with zero maximum auth size. Unaligned key handling uses `GFP_ATOMIC`, so large or frequent setkey calls can fail under pressure. Registration bounds prevent huge IV/auth/chunk sizes from breaking stack/request assumptions. Forgetting to set `NEED_KEY` on errors can permit unkeyed operations.

Test signals: test unaligned key pointers, invalid auth sizes, decrypt-shorter-than-tag rejection, sync allocation rejecting large request sizes, proc/netlink output, instance registration with missing `free`, and AEAD known-answer tests through both direct kernel API and AF_ALG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis-neon.h -->
# sources/distributed-fs/ceph-client/crypto/aegis-neon.h

Purpose: declares the low-level NEON implementation entry points for AEGIS-128 state initialization, update, chunk encryption/decryption, and final tag generation/verification.

Important APIs, types, and functions: prototypes are `crypto_aegis128_init_neon()`, `crypto_aegis128_update_neon()`, `crypto_aegis128_encrypt_chunk_neon()`, `crypto_aegis128_decrypt_chunk_neon()`, and `crypto_aegis128_final_neon()`. All operate on opaque state/tag buffers to keep the NEON inner file decoupled from the generic `struct aegis_state` definition.

Control flow and behavior: callers in `aegis128-neon.c` enter kernel SIMD context, then call these raw NEON helpers. The final helper uses `authsize == 0` as tag-generation mode and nonzero authsize as verification mode.

State and persistence: the header owns no state. It defines ABI expectations for an 80-byte AEGIS state buffer, 16-byte key/IV inputs, chunk pointers, length parameters, and tag buffers shared between generic and NEON code.

Dependencies and integration points: included by `aegis128-neon.c` and `aegis128-neon-inner.c`; indirectly tied to kbuild flags enabling ARM/ARM64 NEON/AES intrinsics. It is compiled only when SIMD support is selected.

Risks and correctness concerns: prototypes must match the freestanding NEON object exactly. Because state is `void *`, layout mismatches are not type-checked. Tag verification return semantics must remain synchronized with the generic SIMD wrapper.

Test signals: ARM and ARM64 build coverage with `CONFIG_CRYPTO_AEGIS128_SIMD`, module load, KASAN/UBSAN where applicable, and AEGIS known-answer tests comparing generic and NEON outputs for full and partial chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis-neon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis.h -->
# sources/distributed-fs/ceph-client/crypto/aegis.h

Purpose: provides common AEGIS definitions shared by generic and SIMD implementations: block layout, alignment checks, SIMD wrapper prototypes, and a software AES round helper used by the generic AEGIS state update.

Important APIs, types, and functions: defines `AEGIS_BLOCK_SIZE`, `union aegis_block`, forward `struct aegis_state`, `aegis128_have_aes_insn`, `AEGIS_ALIGNED()`, SIMD wrapper declarations, `crypto_aegis_block_xor()`, `crypto_aegis_block_and()`, and `crypto_aegis_aesenc()`.

Control flow and behavior: generic code uses the inline XOR/AND/AESENC helpers for state transitions and block operations. SIMD-capable code uses the declared wrapper functions when runtime SIMD is usable. The AESENC helper implements SubBytes/ShiftRows/MixColumns/table lookup plus key XOR using `aes_enc_tab`.

State and persistence: no independent storage is defined beyond the global `aegis128_have_aes_insn` declaration. `union aegis_block` standardizes in-memory state and tag representation as 16 bytes with little-endian 32/64-bit views.

Dependencies and integration points: depends on `crypto/aes.h` tables, Linux bitops/types, and ARM/ARM64 SIMD implementations. Included by `aegis128-core.c` and `aegis128-neon.c`.

Risks and correctness concerns: the inline software AES round must match the AES round semantics used by AEGIS; endian conversion and byte indexes are correctness-critical. Alignment macros affect fast paths, and `union aegis_block` layout must remain 16 bytes. Prototype drift would break SIMD builds.

Test signals: compile with and without SIMD, compare generic and SIMD known-answer results, run unaligned input/output cases, and validate big/little-endian behavior through crypto self-tests on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis128-core.c -->
# sources/distributed-fs/ceph-client/crypto/aegis128-core.c

Purpose: implements the AEGIS-128 AEAD algorithm, with generic software processing and optional runtime SIMD registration. It handles key/authsize validation, associated-data processing, encryption/decryption, tag generation, tag verification, plaintext wiping on authentication failure, and module registration.

Important APIs, types, and functions: key structures are `struct aegis_state` and `struct aegis_ctx`. Important functions include `aegis128_do_simd()`, `crypto_aegis128_update*()`, `crypto_aegis128_init()`, `crypto_aegis128_process_ad()`, `crypto_aegis128_process_crypt()`, `crypto_aegis128_final()`, `crypto_aegis128_setkey()`, `crypto_aegis128_setauthsize()`, generic and SIMD encrypt/decrypt variants, and module init/exit.

Control flow and behavior: initialization mixes key, IV, and constants through repeated AEGIS updates. Associated data is consumed from scatterlists with partial-block buffering. Encryption/decryption walk payload through `skcipher_walk_aead_*`, processing full and partial blocks. Finalization folds associated-data and ciphertext lengths into the state for seven updates, then XORs state blocks into the tag. Decryption compares supplied tag by XORing into the computed tag; failure wipes produced plaintext before returning `-EBADMSG`.

State and persistence: the transform stores a 16-byte key in `struct aegis_ctx`; each request uses stack-local state and tag buffers. `have_simd` is a read-only-after-init static key enabled only when SIMD algorithm registration succeeds. No state persists beyond transform lifetime.

Dependencies and integration points: depends on AEAD core registration, `skcipher_walk`, scatterwalk, jump labels, kernel SIMD usability checks, and `aegis.h`/SIMD wrappers. It registers `aegis128-generic` and, when supported, `aegis128-simd` with higher priority.

Risks and correctness concerns: authentication failure must not expose plaintext, hence the explicit wipe pass. Partial AD and partial payload block handling are subtle. SIMD and generic paths must be bit-for-bit equivalent. The module exit unregisters SIMD based on current SIMD support; registration/unregistration conditions must match.

Test signals: AEGIS-128 AEAD vectors across auth sizes 8-16, empty AD/plaintext, partial blocks, unaligned buffers, in-place operation, forced generic path, SIMD path, auth failure wipe behavior, and crypto self-tests for both driver names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis128-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis128-neon-inner.c -->
# sources/distributed-fs/ceph-client/crypto/aegis128-neon-inner.c

Purpose: provides the freestanding ARM/ARM64 NEON inner implementation of AEGIS-128, including AES-round acceleration, software AES fallback on ARM64 without AES instructions, chunk encryption/decryption, and tag generation/verification.

Important APIs, types, and functions: defines `struct aegis128_state`, `aegis128_load_state_neon()`, `aegis128_save_state_neon()`, `aegis_aes_round()`, `aegis128_update_neon()`, `preload_sbox()`, and exported NEON functions declared in `aegis-neon.h`.

Control flow and behavior: state is loaded into five `uint8x16_t` vectors. `aegis_aes_round()` uses paired AES instructions when available; ARM64 fallback emulates ShiftRows/SubBytes/MixColumns using table lookups and the AES S-box. Encryption computes keystream `s1 ^ (s2 & s3) ^ s4`, updates with plaintext, and writes ciphertext; decryption derives plaintext before update. Short final chunks use a permutation table to avoid out-of-bounds vector accesses.

State and persistence: state exists only in caller-provided memory, converted to/from vector registers. `aegis128_have_aes_insn` controls the fast AES instruction path. Temporary buffers for short chunks and tag verification are stack-local.

Dependencies and integration points: compiled with special kbuild flags from `crypto/Makefile`, includes ARM/ARM64 NEON headers, uses `crypto_aes_sbox`, and is invoked only through `aegis128-neon.c` under `scoped_ksimd()`.

Risks and correctness concerns: freestanding vector code is compiler- and architecture-sensitive. The GCC ARM64 fallback pins vector registers and preloads S-box tables; flag drift can corrupt ABI assumptions. Short-chunk permutation logic is high risk for off-by-one and stale vector writes. Verification returns a vector-derived mismatch value, so callers must treat any nonzero as failure.

Test signals: ARM32 and ARM64 builds with GCC and Clang, CPUs with and without AES instructions, known-answer tests for all chunk lengths 0-31 and multi-block lengths, unaligned buffers, KASAN where possible, and generic-vs-NEON differential tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis128-neon-inner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis128-neon.c -->
# sources/distributed-fs/ceph-client/crypto/aegis128-neon.c

Purpose: is the ARM/ARM64 SIMD wrapper layer for AEGIS-128. It detects runtime AES/NEON availability and safely enters kernel SIMD context before calling freestanding NEON inner routines.

Important APIs, types, and functions: exports `aegis128_have_aes_insn`, `crypto_aegis128_have_simd()`, `crypto_aegis128_init_simd()`, `crypto_aegis128_update_simd()`, `crypto_aegis128_encrypt_chunk_simd()`, `crypto_aegis128_decrypt_chunk_simd()`, and `crypto_aegis128_final_simd()`.

Control flow and behavior: `crypto_aegis128_have_simd()` returns true on ARM CPUs with AES feature and on ARM64 even without AES instructions because the inner file has an ARM64 table fallback; it sets `aegis128_have_aes_insn` only when hardware AES exists. Each operation wraps the raw NEON call in `scoped_ksimd()` so vector register use is permitted in kernel context.

State and persistence: the global `aegis128_have_aes_insn` is read-only after init and controls inner fallback behavior. No transform/request state is stored here; state buffers are supplied by `aegis128-core.c`.

Dependencies and integration points: depends on architecture CPU feature helpers, `asm/simd.h`, `aegis.h`, and `aegis-neon.h`. It is included in the `aegis128` composite object only for ARM/ARM64 SIMD builds.

Risks and correctness concerns: SIMD use outside valid kernel SIMD context can corrupt user or kernel vector state, so wrapper coverage must remain complete. Runtime feature detection must match the inner implementation’s assumptions. ARM64 fallback availability means SIMD registration can happen without AES instructions, which must remain intentional.

Test signals: boot/module tests on ARM with AES, ARM without AES, ARM64 with and without AES, preemption-heavy crypto workloads, crypto self-tests forcing SIMD driver selection, and comparison with generic `aegis128-generic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aegis128-neon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aes.c -->
# sources/distributed-fs/ceph-client/crypto/aes.c

Purpose: registers the generic AES block cipher backed by `crypto_lib_aes`, plus optional AES-based shash MAC algorithms for CMAC, XCBC-MAC, and CBC-MAC depending on enabled Kconfig symbols.

Important APIs, types, and functions: core cipher callbacks are `crypto_aes_setkey()`, `crypto_aes_encrypt()`, and `crypto_aes_decrypt()`. Optional MAC callbacks include CMAC/XCBC setkey/init/update/final/digest helpers and CBC-MAC setkey/init/update/final/digest helpers. Module init/exit register `alg` and `mac_algs`.

Control flow and behavior: module init registers the `aes` cipher first, then registers any compiled shash MACs; failure unregisters the cipher. AES transform context stores `struct aes_key`. CMAC and XCBC share most runtime callbacks but use different key preparation. CBC-MAC uses encryption-only key material and reinitializes for one-shot digest.

State and persistence: per-transform contexts hold AES key schedules or MAC keys. Per-request shash descriptors hold MAC running state. Registered algorithm aliases persist until module exit; no filesystem state exists.

Dependencies and integration points: depends on `crypto/aes.h`, `crypto/aes-cbc-macs.h`, `crypto/internal/hash.h`, and generic algorithm/shash registration. Kconfig selects AES libraries and optional hash/MAC support. Other templates such as CBC, XTS, CCM, and Adiantum may spawn `aes`.

Risks and correctness concerns: the file assumes key/context alignment fits `CRYPTO_MINALIGN`. Optional MAC registration must track Kconfig; AES cipher registration failure cleanup must be exact. XCBC only permits 128-bit keys. CBC-MAC is not a standalone authenticated mode and should be used only by protocols/templates expecting it.

Test signals: AES ECB known-answer tests, setkey rejection for invalid sizes, CMAC/XCBC/CBC-MAC vectors when enabled, module alias autoloading for `aes`, `aes-lib`, `cmac(aes)`, `xcbc(aes)`, and `cbcmac(aes)`, plus registration rollback failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/af_alg.c -->
# sources/distributed-fs/ceph-client/crypto/af_alg.c

Purpose: implements the PF_ALG userspace socket family core and shared helpers used by hash, skcipher, AEAD, and RNG AF_ALG adapters. It handles type registration, bind/setkey/accept, socket lifecycle, control messages, TX/RX scatterlists, memory accounting, waits, polling, and async request cleanup.

Important APIs, types, and functions: exported helpers include `af_alg_register_type()`, `af_alg_unregister_type()`, `af_alg_release()`, `af_alg_release_parent()`, `af_alg_accept()`, `af_alg_free_sg()`, `af_alg_count_tsgl()`, `af_alg_pull_tsgl()`, `af_alg_wmem_wakeup()`, `af_alg_wait_for_data()`, `af_alg_sendmsg()`, `af_alg_free_resources()`, `af_alg_async_cb()`, `af_alg_poll()`, `af_alg_alloc_areq()`, and `af_alg_get_rsgl()`.

Control flow and behavior: `alg_create()` creates `SOCK_SEQPACKET` PF_ALG sockets. `bind()` looks up or autoloads an `af_alg_type`, allocates a parent algorithm object, and installs it if no accepted children exist. `setsockopt()` configures keys, AEAD authsize, or DRBG entropy before connection. `accept()` creates operation sockets and may use nokey ops until a key is provided. `af_alg_sendmsg()` stores input pages in a chained TX SGL, parses IV/op/assoclen cmsgs, supports `MSG_MORE` and `MSG_SPLICE_PAGES`, and enforces socket send buffer limits. Receive-side helpers pin/extract output iovecs into RX SGLs and async callbacks release resources.

State and persistence: global `alg_types` is protected by `alg_types_sem`. Parent sockets hold algorithm type/private pointers and refcounts; child sockets hold `af_alg_ctx` state such as TX SGL list, IV, operation, used bytes, more/init flags, receive accounting, and at most one inflight AIO request. Pages may be pinned until request cleanup or socket destruction.

Dependencies and integration points: integrates with Linux sockets, net proto registration, module autoloading (`algif-%s`), keyrings for `ALG_SET_KEY_BY_KEY_SERIAL`, LSM hooks, scatterlists, iov iter extraction, poll/wait queues, and per-type modules `algif_hash`, `algif_skcipher`, `algif_aead`, and `algif_rng`.

Risks and correctness concerns: user-controlled lengths and cmsgs require strict validation. Page pin/unpin, send/receive accounting, SGL chaining, and partial pulls are high-risk for leaks or UAFs. Locking across parent/child sockets and nokey refcounts must prevent setkey races with accepted sockets. Only one AIO request per child is allowed; violating cleanup paths can strand `ctx->inflight`.

Test signals: AF_ALG bind/setkey/accept/sendmsg/recvmsg tests, nokey-to-key transition, keyring-based setkey, splice-page input, nonblocking waits, poll readiness, AIO completion, cancellation/error cleanup, large SGL chains, partial receive buffers, module autoload, and memory leak/pin accounting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/af_alg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ahash.c -->
# sources/distributed-fs/ceph-client/crypto/ahash.c

Purpose: implements the asynchronous hash (`ahash`) front end, including scatterlist hash walking, shash-backed ahash transforms, key handling, block-only buffering, virtual-buffer fallback, export/import, transform cloning, registration, and one-shot digest helpers.

Important APIs, types, and functions: exported APIs include `crypto_hash_walk_first()`, `crypto_hash_walk_done()`, `shash_ahash_update()`, `shash_ahash_finup()`, `shash_ahash_digest()`, `crypto_ahash_setkey()`, `crypto_ahash_init()`, `crypto_ahash_update()`, `crypto_ahash_finup()`, `crypto_ahash_digest()`, export/import variants, `crypto_alloc_ahash()`, `crypto_clone_ahash()`, registration helpers, `ahash_request_free()`, and `crypto_hash_digest()`.

Control flow and behavior: transforms can either wrap a shash algorithm or use a native ahash algorithm. Native ahash requests reject queued async stack requests, enforce `NEED_KEY`, and may route virtual-buffer requests through a fallback transform using exported/imported state. Block-only algorithms buffer trailing partial blocks in request context and adjust SG chains before update/finup. Default `finup` composes update plus final through saved callbacks.

State and persistence: transform state records `using_shash`, reqsize, statesize, optional fallback tfm, and key-needed flags. Request context stores shash descriptors, block-only tail buffers, saved callbacks/data, and temporary chained SG entries. Export/import serializes algorithm state for cloning, continuation, and fallback transitions.

Dependencies and integration points: depends on scatterwalk, shash front end, hash common helpers, generic crypto registry, proc/netlink reporting, and consumers such as HMAC, AF_ALG hash, IPsec, fs integrity, and signature code. It shares fallback and spawn infrastructure with `algapi.c`.

Risks and correctness concerns: block-only buffering changes `req->src` and `req->nbytes` and must restore them even across async completion. Fallback requires state sizes bounded by `HASH_MAX_STATESIZE` and algorithms with export_core support. Clone behavior differs for keyed and unkeyed algorithms. Import validation must reject corrupt buffered-length values.

Test signals: shash-backed and native ahash vectors, update/finup/digest equivalence, virtual-buffer fallback, block-only algorithms with all tail lengths, export/import/clone continuation, keyed hash `-ENOKEY`, async completion ordering, stack request rejection, and AF_ALG hash accept-state cloning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ahash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/akcipher.c -->
# sources/distributed-fs/ceph-client/crypto/akcipher.c

Purpose: provides the generic public-key cipher (`akcipher`) front end: allocation, spawn grabbing, registration, instance registration, proc/netlink reporting, transform lifecycle, default unsupported operations, and synchronous encrypt/decrypt wrappers.

Important APIs, types, and functions: exports `crypto_grab_akcipher()`, `crypto_alloc_akcipher()`, `crypto_register_akcipher()`, `crypto_unregister_akcipher()`, `akcipher_register_instance()`, `crypto_akcipher_sync_encrypt()`, and `crypto_akcipher_sync_decrypt()`. Internal helper state is `struct crypto_akcipher_sync_data`.

Control flow and behavior: registration fills missing encrypt/decrypt/private-key callbacks with `-ENOSYS` defaults, stamps the crypto type, and registers the base algorithm. Sync helpers allocate one buffer large enough for request, algorithm request context, and max(input, output), copy input into it, set a single SG for in-place operation, wait for completion, copy output back, and wipe/free the request buffer.

State and persistence: transform-private state belongs to individual algorithms such as RSA. The sync helper uses temporary heap state only. Registered algorithms persist in the global crypto registry until unregistered.

Dependencies and integration points: depends on `crypto/internal/akcipher.h`, scatterlists, crypto wait helpers, generic algorithm/template registration, and cryptouser reporting. Public-key implementations and padding templates register through this layer.

Risks and correctness concerns: synchronous buffer length computation must avoid overflow and must wipe sensitive material. `crypto_akcipher_sync_encrypt()` returns only operation status while decrypt returns output length on success, so callers must honor the API distinction. Default `-ENOSYS` callbacks avoid NULL calls but can hide missing implementation coverage until runtime.

Test signals: RSA encrypt/decrypt/signature padding through akcipher, sync wrapper success and insufficient-output behavior, async completion wait handling, invalid keys returning `-ENOSYS` or algorithm errors, registration with missing callbacks, and netlink/proc reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/akcipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algapi.c -->
# sources/distributed-fs/ceph-client/crypto/algapi.c

Purpose: implements the low-level crypto algorithm registry and template/spawn infrastructure. It validates algorithms, manages registration/unregistration, self-test larvals, template instances, dependency removal, notifier registration, async request queues, counter increment helpers, and boot-time self-test startup.

Important APIs, types, and functions: exported APIs include `crypto_register_alg()`, `crypto_unregister_alg()`, batch helpers, `crypto_register_template()`, `crypto_unregister_template()`, `crypto_lookup_template()`, `crypto_register_instance()`, `crypto_unregister_instance()`, `crypto_grab_spawn()`, `crypto_drop_spawn()`, `crypto_spawn_tfm()`, `crypto_spawn_tfm2()`, notifier helpers, attr parsing helpers, `__crypto_inst_setname()`, queue helpers, `crypto_inc()`, `crypto_alg_extsize()`, `crypto_type_has_alg()`, and `crypto_alg_tested()`.

Control flow and behavior: registration validates module signatures in FIPS mode, names, alignment, blocksize, priority, and duplicate names. With self-tests enabled, an untested algorithm is registered alongside a larval placeholder; `cryptomgr` later reports results through `crypto_alg_tested()`, which marks success/failure and notifies waiters. Templates register separately, create instances with spawns, and dependency trees are walked depth-first when underlying algorithms are removed or superseded.

State and persistence: global crypto algorithm/template lists are protected by `crypto_alg_sem`. Algorithms track refcounts, flags, user spawn lists, larval completions, and module refs. Templates maintain live and dead instance lists plus deferred free work. Async queues store request lists, backlog pointer, length, and max length.

Dependencies and integration points: depends on `internal.h` globals, crypto notifier chain, module refs/signatures, workqueues, rtnetlink-era list locking conventions, `cryptomgr` self-test scheduling, and all crypto front ends/templates that register algorithms or spawn children.

Risks and correctness concerns: registry locking and refcounts are critical; mistakes can produce UAFs during module unload or template removal. Spawn dependency pruning must avoid deleting instances needed by a newly registered replacement. FIPS signature checks panic on invalid modules. Larval/test state must never expose untested algorithms as tested. Queue backlog semantics affect async engine fairness.

Test signals: concurrent register/unregister stress, module unload with dependent templates, self-test pass/fail/`-ECANCELED` paths, FIPS module signature failure behavior, duplicate names/priorities, template instance creation/removal, spawn refcount leaks, async queue full/backlog behavior, and `crypto_inc()` counter vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algboss.c -->
# sources/distributed-fs/ceph-client/crypto/algboss.c

Purpose: implements the crypto manager notifier that instantiates template algorithms on demand and schedules algorithm self-tests in kernel threads.

Important APIs, types, and functions: key structures are `cryptomgr_param` for template instantiation and `crypto_test_param` for self-tests. Main functions are `cryptomgr_probe()`, `cryptomgr_schedule_probe()`, `cryptomgr_test()`, `cryptomgr_schedule_test()`, `cryptomgr_notify()`, and module init/exit registering `cryptomgr_notifier`.

Control flow and behavior: on `CRYPTO_MSG_ALG_REQUEST`, it parses names like `cbc(aes)` into a template name and nested algorithm attributes, builds rtattr arrays, and starts `cryptomgr_probe` to call the template’s `create()` method until success or signal. On `CRYPTO_MSG_ALG_REGISTER`, it starts `cryptomgr_test`, which runs `alg_test()` and reports back through `crypto_alg_tested()`. `CRYPTO_MSG_ALG_LOADED` is ignored.

State and persistence: all operation-specific state is heap-allocated and owned by the spawned kthread. Larval completions bridge async instantiation back to waiters. The module persists only a notifier block.

Dependencies and integration points: depends on crypto notifier chain, template lookup, larval algorithms from `algapi.c`, `testmgr` via `alg_test()`, kthreads, module refcounts, and rtattr-compatible template parameters.

Risks and correctness concerns: parser correctness is important for nested template names; malformed names must not overrun fixed arrays or leak module refs. Kthread creation failures must release larval/module references. Probe loops on `-EAGAIN` must stop on pending signals. Self-tests are optional by Kconfig but are central for FIPS/production confidence.

Test signals: request algorithms such as `cbc(aes)`, nested templates, malformed names, missing templates, kthread failure injection, self-test pass/fail notifications, module unload while work is active, and boot-time self-test scheduling from `algapi.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algboss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_aead.c -->
# sources/distributed-fs/ceph-client/crypto/algif_aead.c

Purpose: implements the AF_ALG userspace adapter for AEAD algorithms, translating socket sendmsg/recvmsg operations into `aead_request`s with TX/RX scatterlists, associated data, IVs, tags, synchronous and AIO completion paths, and nokey handling.

Important APIs, types, and functions: main functions are `aead_sendmsg()`, `_aead_recvmsg()`, `aead_recvmsg()`, `aead_check_key()`, nokey send/recv wrappers, `aead_bind()`, `aead_release()`, `aead_setauthsize()`, `aead_setkey()`, `aead_sock_destruct()`, accept helpers, and `algif_type_aead`.

Control flow and behavior: parent bind allocates a `crypto_aead`; accepted children allocate `af_alg_ctx` and IV storage. Sendmsg delegates to `af_alg_sendmsg()` with the AEAD IV size. Receive waits for data, verifies AAD/tag minimums, computes output length, allocates an async request, maps user output buffers to RX SGLs, pulls the relevant TX SGL bytes, copies AAD to output, sets crypt/ad fields, and runs encrypt/decrypt either synchronously or through AIO. Nokey ops re-check the parent tfm and switch the child out of nokey state once a key is available.

State and persistence: child socket context stores IV, TX SGL list, assoclen, operation direction, used bytes, wait object, and inflight state inherited from AF_ALG. Parent socket stores the AEAD tfm and nokey refcounts.

Dependencies and integration points: depends on `af_alg.c` helpers, AEAD core APIs, socket proto ops, scatterlist copy helpers, and userspace cmsgs `ALG_SET_IV`, `ALG_SET_OP`, and `ALG_SET_AEAD_ASSOCLEN`.

Risks and correctness concerns: AEAD length arithmetic must handle encryption tag expansion and decryption tag consumption without underflow. AAD is copied into output separately, so in-place expectations are subtle. Auth failure `-EBADMSG` must propagate even after partial loop progress. AIO supports only one inflight request per child.

Test signals: AF_ALG AEAD known-answer tests for encrypt/decrypt, AAD-only and empty payload cases, short tag/input rejection, partial receive buffers, nokey accept then setkey, authsize setsockopt, AIO path, in-place userspace buffers, and authentication failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_hash.c -->
# sources/distributed-fs/ceph-client/crypto/algif_hash.c

Purpose: implements the AF_ALG userspace adapter for hash algorithms, supporting streaming sendmsg, digest recvmsg, accepted-state cloning, keyed hash nokey transitions, and hash result buffering.

Important APIs, types, and functions: defines `struct hash_ctx` and functions `hash_alloc_result()`, `hash_free_result()`, `hash_sendmsg()`, `hash_recvmsg()`, `hash_accept()`, `hash_check_key()`, nokey wrappers, `hash_bind()`, `hash_release()`, `hash_setkey()`, `hash_sock_destruct()`, accept helpers, and `algif_type_hash`.

Control flow and behavior: sendmsg extracts user pages into a temporary SG table, initializes the request when starting a new stream, then chooses digest/update/finup depending on whether data continues and `MSG_MORE` is set. Zero-length sends can finalize a pending stream. Recvmsg allocates a digest buffer, finalizes if needed, truncates user length with `MSG_TRUNC`, copies the digest, then frees the result. `accept()` can clone an in-progress hash by exporting state from the existing request and importing it into the new child.

State and persistence: each child socket holds one `ahash_request`, optional result buffer, temporary SG state, wait object, context length, and `more` flag. Parent holds the `crypto_ahash` tfm. Exported hash state is temporary during accept cloning.

Dependencies and integration points: depends on `af_alg.c`, ahash APIs, socket proto ops, iov extraction into SG tables, and keyed hash flags. It registers AF_ALG type name `hash`.

Risks and correctness concerns: result lifetime is subtle: previous non-stream results are discarded on a new request, and errors must free partial results. Export/import during accept must hold the source socket lock while preserving state consistency. Pinned SG pages must always be released. Nokey refcounting must avoid racing parent key updates.

Test signals: AF_ALG hash digest and streaming vectors, `MSG_MORE` boundaries, zero-length send/recv behavior, short receive with `MSG_TRUNC`, accept clone of in-progress HMAC/hash, nokey keyed hashes, nonblocking behavior, and SG extraction error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_rng.c -->
# sources/distributed-fs/ceph-client/crypto/algif_rng.c

Purpose: implements the AF_ALG userspace adapter for RNG algorithms, including normal random generation, optional CAVP test additional-data handling, seeding through setkey, and privileged entropy injection for DRBG validation.

Important APIs, types, and functions: structures are `struct rng_ctx` and `struct rng_parent_ctx`. Main functions include `rng_recvmsg()`, `rng_test_recvmsg()`, `rng_test_sendmsg()`, `rng_bind()`, `rng_release()`, `rng_sock_destruct()`, `rng_accept_parent()`, `rng_setkey()`, optional `rng_setentropy()`, and `algif_type_rng`.

Control flow and behavior: bind allocates a parent context and `crypto_rng`. Accept creates a child context sharing the parent DRNG state; if CAVP entropy was configured, it switches the child socket ops to test mode. Normal recvmsg generates at most 128 bytes per call. Test sendmsg stores additional input for the next generation; test recvmsg passes it to `crypto_rng_generate()` then wipes it.

State and persistence: parent context stores the DRNG pointer and optional entropy buffer. Child context stores DRNG pointer, context length, and one additional-data buffer for test mode. RNG state itself is inside the algorithm tfm and may be shared by multiple accepted sockets.

Dependencies and integration points: depends on AF_ALG core, `crypto/rng.h`, capability checks for `CAP_SYS_ADMIN`, optional `CONFIG_CRYPTO_USER_API_RNG_CAVP`, and userspace `ALG_SET_DRBG_ENTROPY`.

Risks and correctness concerns: output is capped to a stack buffer of 128 bytes; callers must loop for larger reads. CAVP entropy injection is intentionally privileged and test-only. Shared DRNG state across accepted sockets is documented but can surprise users expecting independent streams. Sensitive seed/additional/entropy buffers must be wiped on free.

Test signals: AF_ALG RNG read lengths 0, 1, 128, and larger; setkey seeding; CAVP additional data one-shot consumption; `CAP_SYS_ADMIN` enforcement for entropy; shared-state behavior across accepts; and failure propagation from unseeded RNG implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_skcipher.c -->
# sources/distributed-fs/ceph-client/crypto/algif_skcipher.c

Purpose: implements the AF_ALG userspace adapter for symmetric key ciphers, converting socket input/output buffers into `skcipher_request`s while supporting streaming state export/import, block-size chunking, synchronous and AIO operation, and nokey transitions.

Important APIs, types, and functions: key functions are `skcipher_sendmsg()`, `algif_skcipher_export()`, `algif_skcipher_done()`, `_skcipher_recvmsg()`, `skcipher_recvmsg()`, `skcipher_check_key()`, nokey send/recv wrappers, `skcipher_bind()`, `skcipher_release()`, `skcipher_setkey()`, `skcipher_sock_destruct()`, accept helpers, and `algif_type_skcipher`.

Control flow and behavior: sendmsg delegates to `af_alg_sendmsg()` with cipher IV size. Receive waits until data exists and, when streaming, at least one chunk is available. It allocates a request, maps RX buffers, limits non-final processing to full chunks, pulls TX SGL bytes, sets crypt parameters, imports saved state if continuing, and runs encrypt/decrypt. If `CRYPTO_SKCIPHER_REQ_NOTFINAL` is set, completion exports cipher state into the child context for the next receive.

State and persistence: child `af_alg_ctx` stores IV, TX SGL list, direction, used bytes, optional exported cipher state, wait object, and inflight flag. Parent stores the `crypto_skcipher` tfm. Exported state persists across multiple recvmsg calls on the same child stream.

Dependencies and integration points: depends on AF_ALG core, skcipher API, scatterlists, socket ops, and cmsgs for IV and encrypt/decrypt direction. It registers AF_ALG type name `skcipher`.

Risks and correctness concerns: streaming partial-block handling must never process incomplete chunks unless final. Exported state allocation uses `GFP_ATOMIC` in completion and must be cleaned on import or destruction. Partial user receive buffers affect how much TX data is consumed. AIO allows only one inflight request per child.

Test signals: AF_ALG skcipher vectors for CBC/CTR/XTS-style algorithms, `MSG_MORE` streaming, short receive buffers, non-final state export/import, nokey transition, AIO completion path, invalid partial block rejection, IV sizes, and cleanup of exported state on errors and socket close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/algif_skcipher.c -->
