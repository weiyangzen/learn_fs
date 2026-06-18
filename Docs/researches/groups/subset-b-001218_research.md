# Research: subset-b-001218

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi2.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi2.c

## Purpose
`caamalg_qi2.c` is the DPAA2 Queue Interface v2 CAAM crypto driver implementation. It binds to FSL MC `dpseci` objects, configures DPIO-backed transmit/receive queues, registers kernel Crypto API AEAD, skcipher, and ahash algorithms, and translates each crypto request into a DPAA2 frame-list descriptor carrying CAAM flow context and scatter/gather tables. It is the queue-based counterpart to classic CAAM job-ring drivers, optimized around per-CPU DPIO portals, NAPI polling, and a small `kmem_cache` for request extended descriptors.

## Important APIs, Types, And Functions
Key local types include `struct caam_ctx` for symmetric/AEAD transform state, `struct caam_hash_ctx` and `struct caam_hash_state` for ahash transform/request state, and the header-defined `struct caam_request` that carries frame-list entries, FLC DMA addresses, completion callback, request context, and the operation-specific extended descriptor. `driver_algs`, `driver_aeads`, and `driver_hash` are the registration catalogs for skcipher, AEAD, and ahash algorithms.

Important entry points are `dpaa2_caam_probe()`, `dpaa2_caam_remove()`, and exported `dpaa2_caam_enqueue()`. Symmetric paths are driven by `aead_setkey()`, `gcm_setkey()`, `rfc4106_setkey()`, `rfc4543_setkey()`, `chachapoly_setkey()`, `skcipher_setkey()` and mode-specific wrappers. Request preparation is handled by `aead_edesc_alloc()` and `skcipher_edesc_alloc()`, with completions in `aead_encrypt_done()`, `aead_decrypt_done()`, `skcipher_encrypt_done()`, and `skcipher_decrypt_done()`. The QI2 ahash path mirrors the job-ring hash file with `ahash_set_sh_desc()`, `hash_digest_key()`, `ahash_setkey()`, state-machine functions (`ahash_update_first`, `ahash_update_no_ctx`, `ahash_update_ctx`, `ahash_final_*`, `ahash_finup_*`, `ahash_digest`), export/import, and completion callbacks.

## Control Flow
Probe hard-codes CAAM little-endian behavior for DPAA2, allocates `dpaa2_caam_priv`, creates the 512-byte request cache, sets a 49-bit DMA mask, allocates an MC portal and per-CPU private data, configures DPSECI queues, binds receive queues to DPIO notifications, enables NAPI, initializes debugfs, and registers only algorithms supported by `sec_attr` accelerator counts. Removal unregisters algorithms, tears down debugfs, disables NAPI and DPSECI, frees DPIO stores, MC portal, per-CPU memory, and the cache.

For a crypto request, the setkey/authsize callbacks build CAAM shared descriptors in flow contexts and DMA-sync them. Encrypt/decrypt/update/digest callbacks allocate an edesc from `qi_cache`, map source/destination/IV/context buffers, build DPAA2 SG entries and two frame-list entries, fill `caam_request`, then call `dpaa2_caam_enqueue()`. Enqueue maps the frame-list table, builds a list-format `dpaa2_fd`, checks congestion memory when present, and attempts enqueue on the current CPU's DPIO request FQ. Completion arrives through DPIO notification, NAPI pulls response frames, `dpaa2_caam_process_fd()` converts FD address back to virtual memory, unmaps the frame-list DMA, and calls the saved request callback.

## State And Persistence Behavior
State is runtime-only. Per-device state persists from probe to remove in `dpaa2_caam_priv`, including DPSECI attributes, queue IDs, DPIO notification contexts, congestion notification memory, per-CPU stores, debugfs root, and cleanup mask. Per-transform state persists across operations in `caam_ctx` or `caam_hash_ctx`, including key material, descriptor/FLC memory, DMA addresses, algorithm metadata, authsize, and optional XTS fallback. Per-request state lives in `caam_request`, operation edescs, and ahash partial buffers/context; it is freed or unmapped in completion/error paths. There is no disk persistence.

## Dependencies And Integration Points
The file depends on DPAA2 MC/DPIO/FD APIs (`dpseci_*`, `dpaa2_io_service_*`, `dpaa2_fd_*`, `dpaa2_fl_*`), CAAM descriptor constructors from `caamalg_desc.h` and `caamhash_desc.h`, SG conversion helpers from `sg_sw_qm2.h`, CAAM error decoding, Linux DMA mapping, NAPI/netdev dummy devices, IOMMU translation, and the kernel Crypto API registration interfaces. It exposes `dpaa2_caam_enqueue()` for other QI2 CAAM users and registers as an FSL MC driver matching `obj_type = "dpseci"`.

## Risks
The request cache has a fixed `CAAM_QI_MEMCACHE_SIZE` of 512 bytes; edesc paths explicitly reject too many SG entries or IV bytes, so high-fragmentation callers can receive `-ENOMEM`. DMA mapping and unmapping are dense and mode-specific; regressions can leak mappings, reuse stale IV/context DMA, or double-free edescs. XTS fallback behavior depends on SEC era and IV high-half checks. The congestion gate can return `-EBUSY`, so callers must honor backlog flags. Algorithm registration is partially successful by design, which means remove paths must track `registered` flags accurately. The ahash state machine stores function pointers in exported state, which is normal for in-kernel ahash export/import but makes version/layout compatibility important.

## Test Signals
Useful signals include successful probe logs, `algorithms registered in /proc/crypto`, `hash algorithms registered in /proc/crypto`, and expected algorithm names under `/proc/crypto` with `-caam-qi2` driver names. Crypto selftests should cover AES CBC/CTR/RFC3686/XTS, DES/3DES conditional on hardware, GCM/RFC4106/RFC4543, chacha20, chacha20-poly1305, authenc variants, and SHA/MD5 HMAC/unkeyed hashes. Error tests should exercise fragmented SG lists, zero-length skcipher requests, XTS fallback cases, congestion/backlog behavior, invalid auth sizes, invalid key lengths, and probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi2.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi2.h

## Purpose
`caamalg_qi2.h` defines the DPAA2 CAAM QI2 driver contracts shared by the implementation and other CAAM code. It captures device-private DPSECI/DPIO state, per-CPU receive queue state, operation-specific extended descriptor layouts, flow-context storage, operation direction enums, and the `caam_request` envelope passed to `dpaa2_caam_enqueue()`.

## Important APIs, Types, And Functions
`struct dpaa2_caam_priv` is the per-device anchor: DPSECI object ID/version/attributes, SEC capabilities, queue attributes, congestion notification memory and DMA address, device/MC/IOMMU handles, per-CPU private data, debugfs root, and cleanup CPU mask. `struct dpaa2_caam_priv_per_cpu` stores NAPI, dummy netdev, request/response FQIDs, notification context, dequeue store, backpointer, and selected DPIO service.

`struct aead_edesc`, `struct skcipher_edesc`, and `struct ahash_edesc` describe operation-specific software descriptors containing DMA metadata and inline DPAA2 SG tables. `struct caam_flc` stores FLC words plus a shared descriptor. `enum optype` indexes encrypt/decrypt flow contexts. `struct caam_request` is the generic queue request with two frame-list entries, mapped FLC, callback, opaque context, operation edesc, and an embedded fallback skcipher request. The only declared function is `int dpaa2_caam_enqueue(struct device *dev, struct caam_request *req)`.

## Control Flow
The header itself has no executable control flow, but it determines the lifecycle used in `caamalg_qi2.c`: probe allocates/fills `dpaa2_caam_priv` and per-CPU state; setkey paths fill `caam_flc`; request paths allocate one of the edesc layouts and fill `caam_request`; enqueue maps `fd_flt`; completion uses the callback/context/edesc fields to unmap resources and complete the Crypto API request.

## State And Persistence Behavior
All structures are volatile kernel memory. `dpaa2_caam_priv` persists for the bound DPSECI device lifetime, per-CPU structures persist while the device is enabled, transform flow contexts persist for a crypto transform lifetime, and edesc/request fields persist for a single in-flight operation. DMA addresses in these structures are only valid while the corresponding mapping remains active.

## Dependencies And Integration Points
The header includes Crypto API skcipher internals, DPAA2 IO/FD definitions, Linux thread/netdevice support, `dpseci.h`, and CAAM descriptor construction definitions. It bridges the Linux Crypto API, DPAA2 queue manager frame-list format, and CAAM shared descriptor format. The flexible SG arrays in edesc structures assume callers allocate enough trailing storage, which `caamalg_qi2.c` does via `qi_cache_zalloc()`.

## Risks
Structure layout matters for DMA and cache alignment. `caam_flc` is explicitly aligned to `CRYPTO_DMA_ALIGN`, and `caam_request.fd_flt` is aligned because hardware consumes its DMA image. Mis-sizing the fixed 512-byte cache user structures or changing flexible array assumptions can break SG construction. The embedded fallback skcipher request means request-size calculations must include fallback request size for XTS transforms.

## Test Signals
Compile-time coverage should catch missing DPAA2/CAAM type definitions and structure users. Runtime signals are indirect: successful QI2 probe/enqueue/completion paths validate the layout. Stressing multi-SG AEAD/skcipher/hash operations, XTS fallback, and congestion/backlog behavior exercises the fields declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash.c

## Purpose
`caamhash.c` implements classic job-ring CAAM asynchronous hash support for the Linux Crypto API. It registers unkeyed hashes and keyed HMAC/XCBC/CMAC variants, builds shared descriptors for update/final/digest operations, maintains per-request hash continuation state, maps scatterlists into SEC4 SG tables, submits job descriptors to CAAM job rings, and completes requests through either direct job-ring completion or crypto-engine backlog finalization.

## Important APIs, Types, And Functions
`struct caam_hash_ctx` is per-transform state holding four shared descriptors, key storage, DMA addresses, directions, job-ring device, context length, and `alginfo`. `struct caam_hash_state` is per-request state holding DMA addresses, partial input buffer, CAAM context bytes, state-machine function pointers, current edesc, and completion callback. `struct ahash_edesc` contains a job descriptor and optional SEC4 SG table.

Descriptor setup functions include `ahash_set_sh_desc()`, `axcbc_set_sh_desc()`, and `acmac_set_sh_desc()`, all using constructors from `caamhash_desc.c`. Key handling is in `hash_digest_key()`, `ahash_setkey()`, `axcbc_setkey()`, and `acmac_setkey()`. Submission and cleanup helpers include `ahash_edesc_alloc()`, `ahash_edesc_add_src()`, `ahash_enqueue_req()`, `ahash_do_one_req()`, `ahash_unmap*()`, and completion callbacks `ahash_done*()`. Registration uses `driver_hash[]`, `caam_hash_alloc()`, `caam_hash_cra_init()`, `caam_algapi_hash_init()`, and `caam_algapi_hash_exit()`.

## Control Flow
Module initialization checks the CAAM MDHA block and digest-size capability, then registers HMAC forms for all templates and unkeyed forms for non-AES digest templates. Transform init allocates a job ring, determines context length and DMA directions by algorithm and era, maps shared descriptor/key memory, sets request size, and creates descriptors immediately for unkeyed hashes.

Each request begins at `ahash_init()`, which installs first-operation handlers. `update` buffers partial blocks until a full block is available; first updates use `sh_desc_update_first`, later updates import prior CAAM context with `sh_desc_update`. `final` and `finup` either digest buffered data directly or import context plus remaining data. `digest` creates a one-shot descriptor. Completion unmaps context/source/buffer/SG mappings, copies digest output from `state->caam_ctx` when needed, frees the edesc, and completes through the direct ahash callback or crypto engine depending on backlog.

## State And Persistence Behavior
Shared descriptors and optional key/split-key material persist for the transform lifetime and are DMA-mapped once. Per-request state tracks buffered tail data, CAAM running context, and which function should handle the next operation. Export/import copies buffer, context, buffer length, and function pointers into `caam_export_state`. No persistent storage is used outside kernel memory and hardware queues.

## Dependencies And Integration Points
This file depends on CAAM job-ring APIs (`caam_jr_alloc`, `caam_jr_enqueue`, `caam_jr_free`), crypto-engine ahash backlog support, descriptor constructors from `caamhash_desc.h`, SEC4 SG helpers, split-key generation, CAAM error decoding, Linux scatterwalk/DMA APIs, and Crypto API ahash registration. Hardware capability probing reads CAAM perfmon/version registers from `caam_drv_private`.

## Risks
The hash state machine is sensitive to block-size tail handling, especially XCBC/CMAC keeping the last full block buffered for finalization semantics. DMA direction varies by era and algorithm; wrong direction or missed unmap can corrupt context or leak mappings. `hash_digest_key()` submits a synchronous job and waits for completion, so setkey can block. Error paths must free edescs and unmap partially mapped SG/context buffers. Export/import containing function pointers is kernel-internal and should not be treated as stable serialized data.

## Test Signals
Expected runtime signals are registered algorithms such as `sha256-caam`, `hmac-sha256-caam`, `xcbc-aes-caam`, and `cmac-aes-caam`. Crypto selftests should cover one-shot digest, multi-update, final without update, finup, export/import continuation, HMAC keys larger than block size, AES XCBC/CMAC key validation, MDHA LP256 capability limits, backlog paths, fragmented SG inputs, and zero-length messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.c

## Purpose
`caamhash_desc.c` contains shared descriptor constructors for CAAM hash operations. It centralizes the descriptor command sequences used by both the classic job-ring ahash implementation and the DPAA2 QI2 ahash implementation.

## Important APIs, Types, And Functions
The exported functions are `cnstr_shdsc_ahash()` for MDHA class-2 hashes/HMACs and `cnstr_shdsc_sk_hash()` for symmetric-key hash algorithms implemented with class-1 AES XCBC/CMAC. Both take a descriptor buffer, `struct alginfo`, operation state (`OP_ALG_AS_*`), digest/context sizes, and other mode-specific metadata. `cnstr_shdsc_ahash()` also accepts `import_ctx` and SEC era because pre-era-6 HMAC uses split keys while era 6+ can use descriptor key protocol generation.

## Control Flow
`cnstr_shdsc_ahash()` initializes a serial shared descriptor, conditionally loads or derives HMAC key material for all states except update, optionally imports previous class-2 context, appends the class-2 operation, calculates variable input length, consumes message bytes from the sequence input FIFO, and stores digest/context bytes to sequence output. `cnstr_shdsc_sk_hash()` initializes a save-context descriptor, emits a shared-state skip jump, loads immediate or DMA key material depending on INIT versus UPDATE/FINAL and XCBC versus CMAC, optionally restores class-1 context, runs the class-1 operation, consumes message bytes, stores context, and for XCBC INIT saves K1 back to key memory.

## State And Persistence Behavior
The functions do not own runtime state; they write command words into caller-provided descriptor buffers. Persistent behavior is encoded in descriptor sharing semantics: skip jumps avoid reloading shared key/context after the descriptor has been shared, and `HDR_SAVECTX` supports class-1 context reuse. Key and context DMA addresses referenced through `alginfo` remain caller-owned.

## Dependencies And Integration Points
The constructors depend on `desc_constr.h` helpers such as `init_sh_desc`, `append_jump`, `append_key_as_imm`, `append_proto_dkp`, `append_seq_load`, `append_operation`, `append_seq_fifo_load`, and `append_seq_store`. They integrate with `caamhash.c` and `caamalg_qi2.c`, which choose descriptor state variants and DMA-sync the generated descriptors before hardware use.

## Risks
Descriptor length and command ordering are hardware-contract sensitive. Incorrect `import_ctx`, digest size, context length, era, or `alginfo` key fields will produce descriptors that either fail in hardware or compute incorrect hashes. The era split between precomputed split-key loading and DKP must remain aligned with CAAM hardware support. XCBC has extra key-save behavior for INIT that must match the caller's key DMA mapping direction.

## Test Signals
Descriptor-level confidence comes from ahash Crypto API selftests across HMAC SHA/MD5, unkeyed SHA/MD5, XCBC-AES, and CMAC-AES on both first/update/final and digest paths. Debug descriptor dumps and CAAM status decoding help diagnose bad command sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.h

## Purpose
`caamhash_desc.h` declares descriptor size constants and shared descriptor constructor APIs for CAAM hash operations. It is the small interface layer used by both job-ring and QI2 hash implementations.

## Important APIs, Types, And Functions
The descriptor length constants (`DESC_AHASH_BASE`, `DESC_AHASH_UPDATE_LEN`, `DESC_AHASH_UPDATE_FIRST_LEN`, `DESC_AHASH_FINAL_LEN`, `DESC_AHASH_DIGEST_LEN`) describe expected command-space needs in CAAM command-size units. `is_xcbc_aes()` identifies AES-XCBC algorithm selectors. The external constructors are `cnstr_shdsc_ahash()` and `cnstr_shdsc_sk_hash()`.

## Control Flow
The only local executable logic is `is_xcbc_aes()`, which masks an algorithm type against `OP_ALG_ALGSEL_MASK | OP_ALG_AAI_MASK` and compares it to AES plus XCBC-MAC. The rest of the header establishes compile-time contracts for implementation files.

## State And Persistence Behavior
There is no mutable state. The constants influence static descriptor buffer sizing in callers, and the helper provides a pure classification of an algorithm word.

## Dependencies And Integration Points
The header assumes CAAM descriptor and operation macros are already available through included CAAM compatibility/descriptor headers in the including source. It is included by `caamhash.c`, `caamhash_desc.c`, and `caamalg_qi2.c`.

## Risks
If descriptor length constants fall behind constructor changes, callers may under-allocate descriptor buffers. If `is_xcbc_aes()` masks the wrong bits, XCBC paths may use CMAC-style key/context handling or vice versa.

## Test Signals
Build coverage detects missing declarations and many sizing mismatches. Runtime validation comes from successful XCBC/CMAC/HMAC/hash selftests and absence of CAAM descriptor length/status errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.c

## Purpose
`caampkc.c` implements CAAM public-key cryptography support for RSA through the kernel akcipher API. It registers an async `rsa-caam` implementation when PKHA hardware is available, parses public/private keys, supports CAAM RSA private key forms 1/2/3, builds per-request job descriptors containing PDBs and SG pointers, submits jobs to CAAM job rings, and handles completion/unmapping.

## Important APIs, Types, And Functions
Request cleanup is split across `rsa_io_unmap()`, `rsa_pub_unmap()`, and `rsa_priv_f{1,2,3}_unmap()`. Completion callbacks are `rsa_pub_done()` and `rsa_priv_f_done()`. `rsa_edesc_alloc()` normalizes input length by stripping leading zeros or adding zero padding, maps source/destination SGs, builds optional SEC4 SG tables, and stores the edesc in request context. PDB setup functions are `set_rsa_pub_pdb()`, `set_rsa_priv_f1_pdb()`, `set_rsa_priv_f2_pdb()`, and `set_rsa_priv_f3_pdb()`.

Crypto API operations are `caam_rsa_enc()`, `caam_rsa_dec()`, and private-form dispatch helpers. Key handling uses `caam_rsa_set_pub_key()`, `caam_rsa_set_priv_key()`, `caam_rsa_set_priv_key_form()`, `caam_read_raw_data()`, `caam_read_rsa_crt()`, and `caam_rsa_free_key()`. Transform lifetime is managed by `caam_rsa_init_tfm()` and `caam_rsa_exit_tfm()`. Module hooks are `caam_pkc_init()` and `caam_pkc_exit()`.

## Control Flow
Initialization checks PKHA availability from perfmon or version registers and skips registration if encryption/decryption is unavailable. It allocates a zero buffer used for left-padding short RSA inputs, then registers the akcipher engine algorithm. Transform init allocates a job ring and maps the zero padding buffer. Key set parses ASN.1 RSA keys into raw fields, strips leading zeros from positive integers, validates modulus length up to 4096 bits, allocates key buffers, and chooses the best private form available.

Encrypt/decrypt validate key presence and destination length, allocate an edesc, map key fields into the selected PDB, initialize a CAAM RSA descriptor, and submit directly to the job ring or through crypto-engine when backlog is requested. Completion decodes CAAM errors, unmaps key/PDB/source/destination/SG DMA, frees the edesc, and completes the akcipher request directly or through `crypto_finalize_akcipher_request()`.

## State And Persistence Behavior
Global state consists of `zero_buffer` and `init_done`. Per-transform state in `caam_rsa_ctx` holds parsed key buffers, job-ring device, and mapped padding DMA. Per-request state in `caam_rsa_req_ctx` stores stripped/padded source SG information, edesc pointer, and completion callback. Key buffers are freed with `kfree_sensitive()` where private material is involved; public `e`/`n` use regular `kfree()`.

## Dependencies And Integration Points
The file depends on CAAM job-ring APIs, crypto-engine akcipher support, RSA parser helpers, CAAM PDB definitions and descriptor constructors from `caampkc.h`, SEC4 SG helpers, DMA mapping, scatterwalk helpers, and CAAM error decoding. It registers a single akcipher algorithm named `rsa` with driver name `rsa-caam`.

## Risks
RSA input normalization is subtle: oversized inputs strip leading zeros; shorter inputs use DMA-mapped zero padding in the SG table. Bugs can alter numeric values or PDB lengths. PDB setup maps many key buffers with multi-label unwind paths, making unmap symmetry critical. `akcipher_do_one_req()` always calls `rsa_pub_unmap()` on enqueue failure even though backlog requests may be private operations, which is a code path worth reviewing carefully against engine usage. CRT handling must zero-pad dP/dQ/qInv to factor lengths and avoid accepting zero-only fields. Hardware capability checks differ before and after era 10.

## Test Signals
Signals include `caam pkc algorithms registered in /proc/crypto` and an `rsa-caam` entry. Tests should cover public encrypt/private decrypt with form1, form2, and form3 keys; leading-zero modulus/key fields; leading-zero ciphertext/plaintext inputs; short input padding; fragmented source/destination SGs; too-small destination buffers; invalid key lengths over 4096 bits; missing PKHA hardware; backlog and direct completion paths; and removal after failed registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.h

## Purpose
`caampkc.h` defines the RSA public-key crypto data structures and descriptor constructor declarations used by the CAAM PKC implementation. It documents the CAAM-supported RSA private key representations and the per-transform/per-request/per-edesc state layouts.

## Important APIs, Types, And Functions
`enum caam_priv_key_form` enumerates `FORM1` `(n,d)`, `FORM2` `(p,q,d)`, and `FORM3` `(p,q,dP,dQ,qInv)`. `struct caam_rsa_key` stores raw key component buffers, temporary buffers for CAAM private operations, component sizes, and selected private form. `struct caam_rsa_ctx` stores the key, job-ring device, and DMA address of the shared zero-padding buffer. `struct caam_rsa_req_ctx` stores source fixup SG state, edesc pointer, and the selected completion callback. `struct rsa_edesc` stores SG counts, mapped counts, SEC4 SG metadata, backlog flag, one RSA PDB union, and trailing hardware descriptor words.

The declared descriptor constructors are `init_rsa_pub_desc()`, `init_rsa_priv_f1_desc()`, `init_rsa_priv_f2_desc()`, and `init_rsa_priv_f3_desc()`.

## Control Flow
The header has no runtime control flow, but its form enum drives `caam_rsa_dec()` dispatch and completion unmapping. The PDB union layout lets each operation allocate one edesc and then initialize the matching descriptor form in `caampkc.c`.

## State And Persistence Behavior
The structures describe volatile kernel memory. `caam_rsa_key` persists for a crypto transform until a new key is installed or the transform exits. `caam_rsa_req_ctx` and `rsa_edesc` persist only for one in-flight akcipher request. DMA addresses in PDBs and SG tables are valid only while mapped.

## Dependencies And Integration Points
The header includes CAAM compatibility and PDB definitions. It is consumed by `caampkc.c` and by RSA descriptor construction code that supplies the declared `init_rsa_*_desc()` functions. It integrates CAAM PDB formats with Linux akcipher request state.

## Risks
The documentation has a duplicated `@dp` tag where one entry refers to `dq`, so readers must rely on field names. Layout changes to `rsa_edesc` can break allocation math in `rsa_edesc_alloc()`, which places `sec4_sg` after `hw_desc`. Private key buffers require sensitive free handling in implementation. The form enum must stay aligned with PDB setup and unmap dispatch.

## Test Signals
Compile coverage verifies structure and constructor users. Runtime coverage comes from RSA selftests across all private key forms, SG fragmentation, padding, and cleanup paths. Memory sanitizers or DMA debug are useful for catching PDB/SG layout or unmap mistakes tied to these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.h -->
