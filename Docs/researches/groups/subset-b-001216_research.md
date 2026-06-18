# subset-b-001216 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.c

Purpose: SPU-M message-format implementation for Broadcom crypto hardware. It translates the common software-facing SPU parameters from `spu.h` into big-endian SPU-M request headers and provides helpers for payload limits, response parsing, padding, status handling, and CCM IV formatting.

Important APIs and functions: exports `hash_alg_name` and `aead_alg_name`; `spum_dump_msg_hdr()` decodes MH/SCTX/BDESC/BD fields for packet debug; `spum_ns2_ctx_max_payload()` and `spum_nsp_ctx_max_payload()` cap chunk sizes; `spum_payload_length()` reads response BD size; `spum_hash_pad_len()`, `spum_gcm_ccm_pad_len()`, `spum_assoc_resp_len()`, and `spum_digest_size()` implement hardware-specific sizing; `spum_create_request()` builds full AEAD/hash/cipher headers; `spum_cipher_req_init()` and `spum_cipher_req_finish()` split skcipher setup-time and request-time header work; `spum_request_pad()` materializes GCM/CCM, hash, and STATUS padding; `spum_status_process()` maps hardware status into `SPU_INVALID_ICV` or `-EBADMSG`; `spum_ccm_update_iv()` writes CCM B0 fields and plaintext length.

Control flow: caller computes common `spu_request_opts`, cipher/hash/AEAD parameters, then calls the sizing helpers and header builders. `spum_create_request()` computes auth/cipher lengths and offsets, writes the SPUHEADER, appends auth key, cipher key, IV, BDESC, and BD, and returns the exact header length. The skcipher fast path prebuilds stable SCTX/key fields at setkey time and later updates inbound/outbound, IV, BDESC, and BD size per request.

State and persistence: no durable storage. State is encoded into caller-provided DMA-able header buffers and into mutable `cipher_parms->iv_buf` for XTS and CCM. Debug output depends on global debug flags from `util.h`.

Dependencies and integration points: includes `spu.h`, `spum.h`, `cipher.h`, and `util.h`; uses Linux endian helpers, SHA constants, Crypto API naming, and the Broadcom request construction path used by the mailbox/DMA driver.

Risks: header length arithmetic assumes key and IV lengths are word-aligned where SCTX word counts are incremented by `/ 4`; BD size is 16-bit; AEAD decrypt subtracts digest size from cipher/auth lengths; RFC4543 overrides offsets in a special path; CCM may need word padding before ICV; XTS mutates IV state for SPU-M by zeroing the hardware IV and placing the tweak in payload. Status parsing is endian-specific.

Test signals: kernel crypto selftests for CBC/ECB/CTR/XTS, GCM, CCM, RFC4543/GMAC, HMAC/hash chunking, invalid ICV, empty hashes, and multi-chunk payloads should cover this file. Useful debug signals are packet header dumps, `SPU response STATUS`, and matching request/response payload lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.h

Purpose: common SPU abstraction header shared by SPU-M and SPU2 implementations. It defines hardware-independent cipher/hash/AEAD enums, request parameter structures, common sizing constants, inline helpers, and the public function contract each SPU backend implements.

Important APIs and types: `enum spu_cipher_alg`, `spu_cipher_mode`, `spu_cipher_type`, `hash_alg`, `hash_mode`, `hash_type`, and `aead_type`; `struct spu_request_opts`, `spu_cipher_parms`, `spu_hash_parms`, and `spu_aead_parms`; constants such as `SPU_RX_STATUS_LEN`, `SPU_PAD_LEN_MAX`, `SPU_MAX_PAYLOAD_INF`, `SPU_XTS_TWEAK_SIZE`, and CCM B0 masks; inline `spu_req_incl_icv()` and `spu_real_db_size()`. It declares the full SPU-M function surface and includes the common name arrays.

Control flow: higher-level cipher code works in these generic enum and parameter types, then dispatches through SPU-M or SPU2-specific functions. The inline helpers are used before request construction to decide whether decrypting GCM/CCM must carry ICV separately and to compute total data-block size.

State and persistence: this header owns no runtime state but defines mutable parameter buffers (`key_buf`, `iv_buf`) that backend implementations may read or update.

Dependencies and integration points: depends on Linux types, scatterlists, and crypto SHA constants. It is the compatibility layer between Broadcom crypto driver code and the two SPU hardware formats.

Risks: enum aliases intentionally share values, for example ECB/NONE and several AES/hash type constants. Callers must interpret values in context. Adding algorithms requires keeping `HASH_ALG_LAST`, name arrays, backend translation functions, and hardware masks consistent.

Test signals: build coverage for both SPU-M and SPU2, crypto selftests across every advertised enum combination, and compile-time detection of prototype drift between headers and implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.c

Purpose: SPU2 message-format implementation for Broadcom crypto hardware. It hides SPU2 fixed metadata/optional metadata layout behind the same common API exposed by `spu.h`, translating software cipher/hash enums into SPU2 control words and building little-endian FMD/OMD headers.

Important APIs and functions: translation helpers `spu2_cipher_mode_xlate()`, `spu2_cipher_xlate()`, `spu2_hash_mode_xlate()`, and `spu2_hash_xlate()`; debug decoders `spu2_dump_fmd_ctrl*()`, `spu2_dump_omd()`, and `spu2_dump_msg_hdr()`; control writers `spu2_fmd_ctrl0_write()` through `spu2_fmd_ctrl3_write()`; public helpers `spu2_ctx_max_payload()`, `spu2_payload_length()`, `spu2_response_hdr_len()`, `spu2_hash_pad_len()`, `spu2_gcm_ccm_pad_len()`, `spu2_assoc_resp_len()`, `spu2_aead_ivlen()`, `spu2_hash_type()`, `spu2_digest_size()`, `spu2_create_request()`, `spu2_cipher_req_init()`, `spu2_cipher_req_finish()`, `spu2_request_pad()`, `spu2_status_process()`, `spu2_ccm_update_iv()`, and `spu2_wordalign_padlen()`.

Control flow: AEAD/hash/cipher request creation adjusts ordering for GCM and CCM, translates generic enums, handles RFC4543 and zero-payload GCM as hash-only, writes FMD ctrl words, then serializes hash key, cipher key, and IV into OMD. The skcipher path initializes FMD/OMD at setkey time and updates encrypt/decrypt, IV, and payload length at request time.

State and persistence: no persistent storage. It writes caller-provided request buffers and can mutate parameter structures: RFC4543/GCM hash-only moves cipher key into hash key fields, and `spu2_ccm_update_iv()` shortens and shifts the IV buffer because SPU2 does not want CCM flags/length bytes.

Dependencies and integration points: uses `spu.h`, `spu2.h`, `util.h`, Linux endian helpers, and `linux/string_choices.h` for logging. It integrates with the common Broadcom crypto request path and status handling.

Risks: SPU2 uses little-endian FMD while SPU-M uses big-endian headers; payload length is effectively infinite except CCM but still encoded in ctrl3; RFC4543 changes key ownership and payload/assoc interpretation; status length is controlled by a hardware register default; `spu2_cipher_req_finish()` ORs payload length into ctrl3, so stale bits would matter if reused incorrectly.

Test signals: Crypto API tests for GCM/CCM ordering, RFC4106/RFC4543, zero-length GCM payloads, skcipher IV update, CCM IV rewriting, invalid tag status, and descriptor dumps matching expected FMD fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.h

Purpose: SPU2-specific hardware message definition header. It defines SPU2 cipher/hash numeric encodings, FMD layout, FMD control-word masks, response status constants, and public prototypes for the SPU2 backend.

Important APIs and types: `enum spu2_cipher_type`, `spu2_cipher_mode`, `spu2_hash_type`, `spu2_hash_mode`, and `spu2_ret_md_opts`; `struct SPU2_FMD` with four little-endian 64-bit control words; constants `FMD_SIZE`, `SPU2_REQ_FIXED_LEN`, `SPU2_HEADER_ALLOC_LEN`, `SPU2_MAX_PAYLOAD`, `SPU2_INVALID_ICV`; masks for ctrl0 cipher/hash/protocol/order, ctrl1 key/IV/tag/return fields, ctrl2 AAD/payload offsets, and ctrl3 payload/TLS length.

Control flow: `spu2.c` writes these masks into FMD ctrl words, appends OMD after the FMD, and later decodes response FMD/status according to these definitions.

State and persistence: no runtime state. This file defines binary ABI expectations between driver memory and SPU2 hardware.

Dependencies and integration points: depends on common SPU enums and MAX key/IV sizes from surrounding Broadcom headers. It is included by SPU2 implementation and indirectly by the common driver dispatch code.

Risks: mask widths and shifts are hardware-contract critical; many fields exceed 32 bits and require 64-bit constants and casts; `SPU2_RET_IV_LEN` uses zero to mean 16 bytes; `SPU2_HEADER_ALLOC_LEN` references the generic request fixed length, so allocation assumptions must match both SPU families.

Test signals: compile tests for 64-bit mask use, request header dumps for FMD ctrl fields, invalid ICV mapping, and hardware/crypto selftests that exercise returned metadata, IV, AAD2, and payload flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spum.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spum.h

Purpose: SPU-M-specific hardware message definition header. It defines the big-endian SPU-M request/response layout, status values, header sizes, payload limits, SCTX/BDESC/BD structures, and bit masks used by `spu.c`.

Important APIs and types: `struct MHEADER`, `SCTX`, `BDESC_HEADER`, `BD_HEADER`, and `SPUHEADER`; request/response sizing constants such as `SPU_REQ_FIXED_LEN`, `SPU_HEADER_ALLOC_LEN`, `SPU_RESP_HDR_LEN`, and `SPU_HASH_RESP_HDR_LEN`; payload caps `SPUM_NS2_MAX_PAYLOAD` and `SPUM_NSP_MAX_PAYLOAD`; status masks `SPU_STATUS_ERROR_FLAG` and `SPU_STATUS_INVALID_ICV`; MH flag bits and SCTX word masks for cipher/hash algorithm, mode, type, inbound/order, ICV, IV, and BD suppression.

Control flow: SPU-M builders in `spu.c` fill `SPUHEADER`, append variable SCTX key/IV material, then append `BDESC_HEADER` and `BD_HEADER`. Response parsing uses the fixed response header lengths and status masks.

State and persistence: no runtime state; the definitions describe serialized DMA message state.

Dependencies and integration points: included by `spu.c`; relies on Linux endian types and common max key/IV sizes from the Broadcom crypto driver.

Risks: all structures are big-endian hardware formats; field sizes are small, especially 16-bit BD payload lengths and 8-bit SCTX word count. Allocation sizing must remain in sync with max key sizes and RC4 legacy assumptions.

Test signals: packet dump comparison against expected MH/SCTX/BDESC/BD words, large payload chunking around 64 KiB and 8 KiB NSP limits, BD suppression hash responses, and invalid ICV status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/spum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.c

Purpose: utility implementation for the Broadcom SPU crypto driver. It provides scatterlist slicing/copy helpers, counter arithmetic, software hash fallback/helper execution, debugfs statistics, algorithm-name formatting, and CCM integer formatting.

Important APIs and functions: `spu_sg_at_offset()`, `sg_copy_part_to_buf()`, `sg_copy_part_from_buf()`, `spu_sg_count()`, and `spu_msg_sg_add()` manage scatterlist offsets and fragments; `add_to_ctr()` increments a 128-bit big-endian counter; `do_shash()` runs synchronous kernel shash with optional key; `__dump_sg()` is DEBUG-only packet dumping; `spu_alg_name()` maps common SPU enum pairs to Crypto API names; `spu_setup_debugfs()` and `spu_free_debugfs()` manage a debugfs stats file; `format_value_ccm()` writes a 32-bit value into a variable-length CCM field.

Control flow: request-building code calls SG helpers while assembling DMA messages. Hash setup can call `do_shash()` for software precomputation. Debugfs read walks `iproc_priv` counters and, for SPU-M, reads per-SPU FIFO high-water registers.

State and persistence: persistent state is external in `iproc_priv`, atomic counters, debugfs dentries, and mapped hardware registers. This file allocates transient buffers for debugfs reads and shash descriptors.

Dependencies and integration points: uses Linux scatterlist, Crypto API shash, debugfs, ioread32, `cipher.h`, `spu.h`, and `util.h`. It is shared by SPU-M/SPU2 code and higher-level Broadcom crypto paths.

Risks: `spu_msg_sg_add()` updates caller SG pointers and skip state and is sensitive to partial-entry math; `do_shash()` currently calls update with `data1` unconditionally, so callers must pass a valid pointer when `data1_len` is nonzero; debugfs stats are bounded by a fixed 2048-byte buffer and can truncate; `format_value_ccm()` only represents up to 32-bit values even if `len` is larger.

Test signals: SG split/copy tests across offsets and zero lengths, counter carry tests, shash known-answer tests, debugfs read under active counters, and CCM value formatting for 2/3/4-byte lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.h

Purpose: public utility header for the Broadcom SPU crypto driver. It declares utility helpers and defines debug logging macros that compile to active packet/flow logging only under `DEBUG`.

Important APIs and types: external debug controls `flow_debug_logging`, `packet_debug_logging`, and `debug_logging_sleep`; macros `flow_log`, `flow_dump`, `packet_log`, `packet_dump`, and `dump_sg`; prototypes for scatterlist helpers, counter increment, `do_shash()`, `spu_alg_name()`, debugfs setup/teardown, and `format_value_ccm()`.

Control flow: implementation files include this header and use logging macros inline. With `DEBUG` defined, logs check runtime flags, print or hex dump, and optionally sleep; without `DEBUG`, static inline no-op stubs remove the logging cost.

State and persistence: no state is owned here, but the declared debug flags affect global runtime logging and timing.

Dependencies and integration points: includes Linux kernel/delay headers and `spu.h`; bridges utility functions to SPU-M/SPU2 and broader Broadcom driver code.

Risks: enabling debug with `debug_logging_sleep` can materially affect crypto timing and throughput; packet dumps may expose key material because header dump paths print keys and IVs; macro availability depends on compile-time `DEBUG`, not just runtime flags.

Test signals: compile with and without `CONFIG_CRYPTO_DEV_BCM_SPU_DEBUG`/`DEBUG`, verify no-op logging builds, and validate that debugfs/stat helpers are available only through their declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/Kconfig

Purpose: Kconfig menu for Freescale/NXP CAAM crypto drivers. It controls the main CAAM controller backend, job-ring backend, Crypto API registrations, QI/DPAA2 variants, public-key/RNG/PRNG/blob-generation support, debug output, and job-ring interrupt coalescing settings.

Important symbols: `CRYPTO_DEV_FSL_CAAM_COMMON`, `CRYPTO_DEV_FSL_CAAM_CRYPTO_API_DESC`, and `CRYPTO_DEV_FSL_CAAM_AHASH_API_DESC` are shared descriptor/common libraries; `CRYPTO_DEV_FSL_CAAM` enables the platform controller; `CRYPTO_DEV_FSL_CAAM_JR` enables job rings; `CRYPTO_DEV_FSL_CAAM_CRYPTO_API`, `_QI`, `_AHASH_API`, `_PKC_API`, `_RNG_API`, `_PRNG_API`, `_BLOB_GEN`, and `_RNG_TEST` select feature modules; `CRYPTO_DEV_FSL_DPAA2_CAAM` enables DPAA2 DPSECI support.

Control flow: build configuration gates which objects the Makefile links and which algorithms later register with the Crypto API. Nested `if` blocks require the CAAM controller and job-ring backend before most service APIs can be enabled.

State and persistence: no runtime state; persistent effect is kernel build configuration.

Dependencies and integration points: depends on SoC architecture symbols, `FSL_MC_DPIO`, `NETDEVICES`, `FSL_DPAA`, Crypto API symbols, hwrng, and job-ring/crypto-engine infrastructure.

Risks: defaults enable many APIs when CAAM/JR are selected; QI needs DPAA and NET; interrupt coalescing thresholds can force timeouts if set at or above ring size; blob generation is a silent bool selected by other users rather than a user-visible menu.

Test signals: configuration matrix builds for platform CAAM, JR-only APIs, QI, DPAA2, COMPILE_TEST, and RNG test; verify selected crypto dependencies and produced modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/Makefile

Purpose: CAAM driver build recipe. It maps Kconfig symbols to controller, job-ring, descriptor, Crypto API, RNG, public-key, blob, queue-interface, debugfs, and DPAA2 object files.

Important build targets: `error.o`, `caam.o`, `caam_jr.o`, `caamalg_desc.o`, `caamhash_desc.o`, `ctrl.o`, `jr.o`, `key_gen.o`, `caamalg.o`, `caamalg_qi.o`, `caamhash.o`, `caamrng.o`, `caamprng.o`, `caampkc.o`, `pkc_desc.o`, `blob_gen.o`, `qi.o`, `debugfs.o`, `dpaa2_caam.o`, `caamalg_qi2.o`, `dpseci.o`, and `dpseci-debugfs.o`.

Control flow: `obj-*` lines create modules or built-ins based on configuration. Composite objects (`caam-y`, `caam_jr-y`, `dpaa2_caam-y`) collect feature objects under the main module target. Debug builds add `-DDEBUG`; all builds define an empty `VERSION`.

State and persistence: no runtime state; affects build graph and compilation flags.

Dependencies and integration points: synchronized with `Kconfig` symbols and source files in this directory. `caamalg.c` is included only in `caam_jr` when `CRYPTO_DEV_FSL_CAAM_CRYPTO_API` is enabled.

Risks: object inclusion order determines which features are present in each module; stale Kconfig/Makefile mapping can produce missing symbols. Debug flag changes can expose verbose dumps and alter timing.

Test signals: all relevant Kconfig combinations should link, especially CAAM_JR with/without Crypto API, blob generation, debugfs, QI, and DPAA2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/blob_gen.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/blob_gen.c

Purpose: CAAM blob encapsulation/decapsulation helper exported for trusted keys and CAAM blob consumers. It allocates a job ring, validates hardware blob support, builds a CAAM job descriptor for blob protocol operations, maps input/output DMA buffers, submits the job, waits synchronously, and returns the generated or decoded blob data.

Important APIs and functions: `struct caam_blob_priv` wraps a job-ring device; `struct caam_blob_job_result` carries completion and error; `caam_blob_job_done()` translates CAAM status and completes waiters; `check_caam_state()` reads controller mode-of-operation; `caam_process_blob()` performs encap/decap and is exported; `caam_blob_gen_init()` obtains a job ring and checks `blob_present`; `caam_blob_gen_exit()` releases it.

Control flow: caller initializes `caam_blob_priv`, then calls `caam_process_blob(info, encap)`. The function validates key modifier length, computes protocol op and output length, handles protected-key black blob/EKT overhead, allocates a descriptor, DMA maps input and output, warns if using insecure test key mode, appends key modifier, seq in/out pointers, and blob operation, enqueues to CAAM JR, waits for completion on `-EINPROGRESS`, updates `info->output_len`, unmaps DMA, and frees the descriptor.

State and persistence: persistent state is the allocated CAAM job ring in `caam_blob_priv`. Per-call state is descriptor memory, DMA mappings, and completion result. Blob contents are written to caller-provided output buffers.

Dependencies and integration points: includes CAAM descriptor construction, job-ring, error, register, and SoC blob headers; exports symbols to trusted key and CAAM blob users; depends on controller `blob_present` and secure/trusted mode for production key uniqueness.

Risks: decapsulation subtracts `CAAM_BLOB_OVERHEAD` from `input_len`, so short inputs are dangerous unless callers validate; protected-key encap uses bidirectional DMA for input because CAAM writes protected key material back through the input buffer path; descriptor sizing must track appended commands; insecure mode falls back to a test key with only a warning.

Test signals: trusted-key blob KATs, encap/decap round trips for normal and protected keys, invalid key modifier length, short blob input rejection, no-blob hardware returning `-ENODEV`, DMA mapping failure unwinds, and secure-mode warning visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/blob_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg.c

Purpose: CAAM job-ring Crypto API backend for skcipher and AEAD algorithms. It registers CAAM-backed cipher/authenticated-encryption implementations, manages per-transform shared descriptors and DMA mappings, builds per-request job descriptors, submits jobs directly or through `crypto_engine`, handles completions, and unregisters algorithms on exit.

Important APIs and types: `struct caam_alg_entry` stores CAAM class1/class2 algorithm selectors plus RFC3686/geniv/nodkp flags; `struct caam_aead_alg` and `caam_skcipher_alg` wrap engine algorithms and registration state; `struct caam_ctx` holds shared descriptors, key buffers, DMA addresses, alginfo, authsize, fallback/protected-key state, and job-ring device; request contexts hold `aead_edesc` or `skcipher_edesc`. Key/setup functions include `aead_set_sh_desc()`, `gcm_set_sh_desc()`, `rfc4106_set_sh_desc()`, `rfc4543_set_sh_desc()`, `chachapoly_set_sh_desc()`, `aead_setkey()`, `gcm_setkey()`, `rfc4106_setkey()`, `rfc4543_setkey()`, `chachapoly_setkey()`, `skcipher_setkey()`, `paes_skcipher_setkey()`, and `xts_skcipher_setkey()`. Request functions include `aead_edesc_alloc()`, `skcipher_edesc_alloc()`, `init_*_job()`, `aead_enqueue_req()`, `aead_do_one_req()`, `skcipher_do_one_req()`, `aead_crypt()`, `gcm_crypt()`, `chachapoly_crypt()`, and `skcipher_crypt()`. Lifecycle functions are `caam_init_common()`, `caam_cra_init()`, `caam_aead_init()`, `caam_algapi_init()`, and `caam_algapi_exit()`.

Control flow: transform initialization allocates a CAAM job ring, maps the contiguous context region containing shared descriptors and key material, sets `alginfo`, and optionally allocates XTS fallback. Setkey validates user keys, copies or derives split keys, syncs DMA, chooses inline versus pointer keys, and constructs encrypt/decrypt shared descriptors. Each request allocates an extended descriptor, maps source/destination SGs and IV/link tables, initializes a job descriptor pointing at the shared descriptor, submits directly to the job ring unless backlog is requested, and later completion callbacks translate CAAM status, unmap DMA, update IV for skcipher, free descriptors, and complete through either Crypto API or crypto-engine.

State and persistence: per-transform state persists in `caam_ctx` for the lifetime of the Crypto API tfm: shared descriptors, DMA addresses, key material, authsize, fallback cipher, protected-key blob metadata, and job-ring ownership. Per-request state persists until callback completion in `aead_edesc` or `skcipher_edesc`. Driver-wide algorithm arrays track which entries were registered.

Dependencies and integration points: depends on CAAM descriptor constructors (`caamalg_desc.h`), job-ring API (`jr.h`), SEC4 scatter/gather conversion, key generation, CAAM register feature detection, Linux Crypto API internals for AEAD/skcipher/engine, trusted-key protected-key headers, DMA mapping, DES/AES/XTS/GCM/ChaChaPoly helpers, and hardware capability registers.

Risks: descriptor buffer limits are tight and require `desc_inline_query()` and `DESC_*_JOB_IO_LEN` to remain accurate; SG mapping/unmapping paths differ for in-place versus out-of-place and zero-length AEAD data; backlog requests use crypto-engine completion while direct submissions complete directly; XTS falls back for unsupported eras or key sizes; protected-key/PAES mode maps extra descriptor space and protected-key DMA; authenc key extraction and DKP/split-key handling vary by CAAM era; registration filters must match hardware feature bits for AES/DES/MD/GCM/ChaCha20/Poly1305; debug hex dumps can expose key material when DEBUG is enabled.

Test signals: `/proc/crypto` registration on hardware with varied CHA capabilities; kernel crypto selftests for all registered skcipher and AEAD names including RFC4106, RFC4543, RFC7539, authenc HMAC with AES/DES/3DES/CBC/CTR, geniv variants, PAES, and XTS fallback; SG stress with multi-entry, in-place/out-of-place, zero-length, and auth-tag failure cases; DMA API debug; module unload/reload; hardware era matrix for DKP, GCM, XTS, ChaCha20, Poly1305, and MD LP256 digest limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg.c -->
