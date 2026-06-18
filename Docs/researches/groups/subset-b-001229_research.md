# Research report: subset-b-001229

Grouped research for the Inside Secure / SafeXcel crypto driver files under `sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/`. Each section preserves the original source path for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.c

## Purpose
Implements the EIP93 AEAD/authenc crypto API algorithms. It binds Linux `aead_request` operations for `authenc(hmac(...),cbc(...))` and `authenc(hmac(...),rfc3686(ctr(aes)))` families to the EIP93 descriptor path shared with skcipher code.

## Important APIs, Types, and Functions
The exported integration function is `eip93_aead_handle_result()`, called by `eip93-main.c` when a result descriptor with `EIP93_DESC_AEAD` and `EIP93_DESC_LAST` is consumed. Crypto API entry points are `eip93_aead_setkey()`, `eip93_aead_setauthsize()`, `eip93_aead_encrypt()`, and `eip93_aead_decrypt()`. Context is `struct eip93_crypto_ctx` from `eip93-cipher.h`; request state is `struct eip93_cipher_reqctx`.

`eip93_aead_setkey()` parses `crypto_authenc_keys`, validates DES/3DES/AES keys, strips RFC3686 nonce material when needed, programs the SA record with `eip93_set_sa_record()`, and precomputes HMAC inner/outer digests through `eip93_hmac_setkey()`. The file defines the registered `struct eip93_alg_template` instances for HMAC-MD5/SHA1/SHA224/SHA256 combined with CBC AES, RFC3686 AES, CBC DES, and CBC 3DES.

## Control Flow
Algorithm registration is performed indirectly by `eip93-main.c` through the global templates. At transform initialization, `eip93_aead_cra_init()` sets request size, copies template flags/type, stores the EIP93 device pointer, and allocates one SA record. Per request, encrypt/decrypt sets direction flags, verifies the request AAD length against the cached association length, maps the SA record, fills request context sizes and scatterlist pointers, and calls `eip93_aead_send_req()`. That validates scatterlists through `check_valid_request()` and forwards to `eip93_send_req()`.

Completion is reversed: `eip93_aead_handle_result()` unmaps request DMA, copies saved IV state through `eip93_handle_result()`, and completes the Linux AEAD request with the parsed hardware status.

## State and Persistence
Persistent transform state includes flags, block size, auth size, cached AAD length, RFC3686 nonce, and the allocated SA record. `ctx->set_assoc` causes the first request after setkey/init to program `HASH_CRYPT_OFFSET`; later requests must keep the same `assoclen`. Hardware-visible state is transient DMA mapping of the SA record plus per-request `sa_state` allocated by the common path. There is no filesystem or cross-boot persistence.

## Dependencies and Integration Points
Depends on Linux crypto AEAD/authenc helpers, AES/DES validation helpers, HMAC/hash support from `eip93-common.c`/`eip93-hash.c`, and descriptor submission from `eip93-common.c`. Templates are discovered by `eip93-main.c`, which registers only algorithms supported by hardware option bits.

## Risks
The cached AAD length means a transform rejects later requests whose AAD size differs, which is stricter than many software AEAD implementations. `eip93_aead_cra_exit()` unconditionally unmaps `ctx->sa_record_base`; if no successful request mapped it, this depends on DMA API tolerance for a zero/old DMA address. Direction bits are set on decrypt by mutating the shared SA record and are reset only by later `setkey()`/`eip93_set_sa_record()`, so encrypt-after-decrypt on the same transform deserves test attention. AEAD multi-segment requests commonly force bounce buffers in the common path.

## Test Signals
Exercise crypto self-tests for every registered authenc algorithm, including RFC3686 nonce sizing, authsize truncation, decrypt authentication failure mapping to `-EBADMSG`, mixed in-place/out-of-place scatterlists, unaligned AAD/payload, repeated requests with same AAD length, and a deliberate AAD length change on the same transform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.h

## Purpose
Declares the EIP93 AEAD/authenc algorithm templates and the AEAD result callback used by the EIP93 core.

## Important APIs, Types, and Functions
The header exports `eip93_aead_handle_result(struct crypto_async_request *async, int err)` and many `extern struct eip93_alg_template` declarations. The declared templates cover HMAC-MD5/SHA1/SHA224/SHA256 with CBC AES, CTR/RFC3686 AES, CBC DES, CBC 3DES, and null-cipher authenc variants.

## Control Flow
`eip93-main.c` includes this header to populate its algorithm array and to dispatch result descriptors with AEAD flags. The concrete template definitions for most listed combinations are in `eip93-aead.c`; consumers do not allocate or mutate these declarations directly outside registration.

## State and Persistence
The header owns no runtime state. It exposes global algorithm templates that become bound to an `eip93_device` during registration.

## Dependencies and Integration Points
Requires `struct eip93_alg_template` from `eip93-main.h`, indirectly available through the include graph in the C files. It integrates AEAD definitions into the common EIP93 registration and interrupt completion path.

## Risks
Some extern declarations are broader than the definitions in the listed `eip93-aead.c` view, especially CTR/null authenc names. Build coverage must ensure every declared symbol is either defined in the compilation unit or intentionally excluded by Kconfig/source selection.

## Test Signals
Build/link the EIP93 driver with all declared AEAD templates enabled, then check `/proc/crypto` for expected driver names and run AEAD self-tests for registered algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aes.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aes.h

## Purpose
Declares EIP93 AES skcipher algorithm templates.

## Important APIs, Types, and Functions
Exports `eip93_alg_ecb_aes`, `eip93_alg_cbc_aes`, `eip93_alg_ctr_aes`, and `eip93_alg_rfc3686_aes` as `struct eip93_alg_template` globals. These templates are defined in `eip93-cipher.c`.

## Control Flow
The EIP93 platform driver includes this header and registers the AES templates if hardware option bits advertise AES and compatible AES key sizes. Per-request behavior is implemented by common skcipher callbacks in `eip93-cipher.c`.

## State and Persistence
No runtime state is owned here. The declared template objects are global descriptors whose `eip93` pointer is set during registration.

## Dependencies and Integration Points
Depends on `struct eip93_alg_template` from `eip93-main.h` through including C files. Integrates AES modes into the driver-wide algorithm list.

## Risks
The header is intentionally declaration-only; missing or mismatched definitions would surface as link failures. Runtime risk comes from registration-time key-size adjustment for hardware AES capabilities in `eip93-main.c`.

## Test Signals
Compile/link EIP93 with AES enabled, verify ECB/CBC/CTR/RFC3686 AES driver names, and run aligned and unaligned skcipher test vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.c

## Purpose
Implements EIP93 skcipher support for AES, DES, and 3DES in ECB/CBC/CTR/RFC3686 modes. It is the non-AEAD symmetric cipher frontend to the shared EIP93 descriptor machinery.

## Important APIs, Types, and Functions
The result callback `eip93_skcipher_handle_result()` is exported for `eip93-main.c`. Crypto API callbacks include `eip93_skcipher_cra_init()`, `eip93_skcipher_cra_exit()`, `eip93_skcipher_setkey()`, `eip93_skcipher_encrypt()`, and `eip93_skcipher_decrypt()`. Algorithm templates are defined for `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `rfc3686(ctr(aes))`, `ecb/cbc(des)`, and `ecb/cbc(des3_ede)`.

## Control Flow
Transform initialization allocates one SA record and stores the EIP93 device pointer/type. `setkey()` validates the key using crypto library helpers, extracts an RFC3686 nonce when applicable, programs `sa_cmd` words through `eip93_set_sa_record()`, and copies the key into the SA record. Encrypt/decrypt sets request flags, with decrypt also setting `EIP93_SA_CMD_DIRECTION_IN` in the SA record. `eip93_skcipher_crypt()` rejects zero length as a no-op, enforces block alignment for ECB/CBC, maps the SA record, fills the request context, and submits through `eip93_skcipher_send_req()` and `eip93_send_req()`.

## State and Persistence
Persistent transform state is the allocated SA record, block size, RFC3686 nonce, type, and EIP93 pointer. Per-request state is `struct eip93_cipher_reqctx`, including scatterlists, DMA addresses, descriptor flags, IV size, and per-request SA state allocated in the common layer. No state survives transform destruction.

## Dependencies and Integration Points
Depends on Linux AES/DES validation helpers, DMA mapping, `eip93-common.c` for SA record generation and request submission, and `eip93-main.c` for registration/completion. AES templates use `CRYPTO_ALG_NEED_FALLBACK` and kernel-driver-only flags for AES modes.

## Risks
Like AEAD, `cra_exit()` unmaps the last SA record DMA address unconditionally. Decrypt mutates the shared SA record direction bit, so encrypting later with the same transform may rely on setkey or fresh SA setup to clear it. CTR mode handles non-block-size lengths, but ECB/CBC reject unaligned sizes. Descriptor submission busy-waits in the common path if the ring is full.

## Test Signals
Run AES/DES/3DES known-answer tests for encrypt/decrypt, RFC3686 nonce handling, zero-length no-op, CBC/ECB unaligned length rejection, CTR partial-block operation, and repeated encrypt/decrypt ordering on a single transform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.h

## Purpose
Defines shared transform and request context structures for EIP93 skcipher and AEAD operations, plus the common cipher request API used across EIP93 files.

## Important APIs, Types, and Functions
`struct eip93_crypto_ctx` stores the device pointer, algorithm flags, SA record pointer/DMA address, block size, RFC3686 nonce, AEAD auth and association sizes, `set_assoc`, and algorithm type. `struct eip93_cipher_reqctx` stores descriptor flags, direction/mode flags, sizes, SA/state DMA addresses, scatterlist pointers, mapped entry counts, and optional CTR-overflow state.

Declared functions include `check_valid_request()`, `eip93_unmap_dma()`, `eip93_skcipher_handle_result()`, `eip93_send_req()`, and `eip93_handle_result()`.

## Control Flow
AEAD and skcipher frontends fill `eip93_cipher_reqctx`, then call `check_valid_request()` and `eip93_send_req()`. The interrupt path calls the relevant result handler, which uses `eip93_unmap_dma()` and `eip93_handle_result()` before completing the crypto request.

## State and Persistence
The structures describe in-memory crypto transform/request state only. DMA addresses are valid only between submission and completion. The same transform context can be reused across requests and therefore carries key/SA/AAD-related state.

## Dependencies and Integration Points
Includes `eip93-main.h` for device, algorithm type, flags, descriptors, and SA state definitions. It is the coupling point between `eip93-aead.c`, `eip93-cipher.c`, `eip93-common.c`, and `eip93-main.c`.

## Risks
The request context owns pointers to either caller scatterlists or bounce scatterlists, so cleanup must compare against original request lists correctly. DMA address fields are not self-validating; unmap paths assume successful map paths and descriptor completion ordering.

## Test Signals
Look for DMA API debug warnings under skcipher and AEAD stress tests, especially in-place, out-of-place, unaligned, and multi-SG requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.c

## Purpose
Provides the core shared EIP93 descriptor, scatterlist, SA record, DMA, result cleanup, and HMAC precomputation logic used by skcipher, AEAD, and hash frontends.

## Important APIs, Types, and Functions
Public functions are `eip93_parse_ctrl_stat_err()`, `eip93_put_descriptor()`, `eip93_get_descriptor()`, `check_valid_request()`, `eip93_set_sa_record()`, `eip93_send_req()`, `eip93_unmap_dma()`, `eip93_handle_result()`, and `eip93_hmac_setkey()`.

Private ring helpers advance command/result read/write pointers. Scatterlist helpers create/free bounce SGs and validate 4-byte/block alignment. `eip93_scatter_combine()` splits mapped scatterlists into one or more EIP93 descriptors. `eip93_hmac_setkey()` computes ipad/opad digests using the EIP93 hash algorithms through the Linux ahash API.

## Control Flow
Request validation computes total source/destination sizes, derives SG entry counts, and creates bounce buffers when alignment or AEAD multi-entry constraints cannot be met. Submission builds SA state from the request IV, handles RFC3686 IV layout, handles 32-bit CTR overflow by splitting work with a second state, maps SA state and SGs, allocates a 16-bit async IDR entry, and calls `eip93_scatter_combine()`. Each descriptor is placed into CDR/RDR under the ring write lock; if rings are full, it sleeps briefly and retries. Writing `EIP93_REG_PE_CD_COUNT` starts DMA.

Completion unmaps SGs, copies bounce-buffer output back to the original destination, converts non-MD5 auth tags to host order, unmaps/copies final IV state, and frees per-request state. Hardware control/status errors are translated to Linux errors such as `-EBADMSG`, `-EIO`, `-EACCES`, or `-EINVAL`.

## State and Persistence
The file manages ring pointer state inside `struct eip93_ring`, IDR mappings from hardware-visible IDs to `crypto_async_request`, transient bounce buffers, DMA mappings, and per-request SA state. No durable persistence exists. SA records supplied by frontends are transform state but are programmed here.

## Dependencies and Integration Points
Depends on `eip93-regs.h` bitfields, `eip93-main.h` ring/device definitions, and the Linux DMA/scatterlist/crypto APIs. It is invoked by AEAD/skcipher frontends and by HMAC setup in both AEAD and hash code.

## Risks
Ring full handling is a busy sleep/retry loop with no timeout, so hardware stalls can pin callers. `idr_alloc()` return is not checked before being packed into the descriptor user ID. Bounce buffer allocation uses `GFP_KERNEL | GFP_DMA`, which can fail under pressure and may constrain memory placement. The CTR overflow split path uses 32-bit DMA address fields and hardware state assumptions. Error cleanup paths must match every DMA map and bounce allocation, making DMA API debug testing important.

## Test Signals
Use DMA API debug, KASAN, and crypto stress vectors for multi-SG in-place/out-of-place requests, unaligned offsets, AEAD tag conversion, CTR counter wrap near `0xffffffff`, ring saturation, hardware auth failure, and simulated DMA mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.h

## Purpose
Declares shared EIP93 helper APIs for descriptor rings, SA record programming, hardware error parsing, and HMAC precomputation.

## Important APIs, Types, and Functions
Exports `eip93_get_descriptor()`, `eip93_put_descriptor()`, `eip93_set_sa_record()`, `eip93_parse_ctrl_stat_err()`, and `eip93_hmac_setkey()`. These form the public surface of `eip93-common.c`.

## Control Flow
Frontend files use `eip93_set_sa_record()` during key setup. The main result path uses `eip93_get_descriptor()` while draining RDR/CDR. AEAD and hash key setup call `eip93_hmac_setkey()`. Hardware status parsing is centralized through `eip93_parse_ctrl_stat_err()`.

## State and Persistence
The header owns no state. Its functions operate on caller-provided `struct eip93_device`, `struct eip93_descriptor`, and `struct sa_record` objects.

## Dependencies and Integration Points
Assumes the including translation unit has EIP93 core and register structures visible. It is the API boundary between common EIP93 mechanics and the algorithm-specific frontends.

## Risks
Because prototypes use low-level device/descriptor pointers, misuse can corrupt ring state or misprogram hardware. There are no compile-time annotations for lock ownership around descriptor get/put; callers must hold the appropriate locks.

## Test Signals
Build with sparse/lockdep where possible and run descriptor submission/completion tests under concurrent crypto requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-des.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-des.h

## Purpose
Declares EIP93 DES and 3DES skcipher algorithm templates.

## Important APIs, Types, and Functions
Exports `eip93_alg_ecb_des`, `eip93_alg_cbc_des`, `eip93_alg_ecb_des3_ede`, and `eip93_alg_cbc_des3_ede` as `struct eip93_alg_template` globals. Definitions live in `eip93-cipher.c`.

## Control Flow
`eip93-main.c` includes the header to register DES/3DES templates when the EIP93 option register advertises TDES support. Requests then run through the common skcipher callbacks.

## State and Persistence
No state is held in this header. Template objects become bound to a device pointer during registration.

## Dependencies and Integration Points
Relies on `struct eip93_alg_template` from the EIP93 core. Integrates legacy DES modes into the EIP93 algorithm list.

## Risks
DES/3DES are legacy algorithms and may be disabled or policy-restricted in some deployments. Runtime behavior depends on key validation in `eip93-cipher.c`.

## Test Signals
Compile/link with TDES-capable hardware flags, run DES/3DES KATs, and verify weak-key rejection behavior through crypto self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.c

## Purpose
Implements EIP93 asynchronous hash and HMAC algorithms for MD5, SHA1, SHA224, and SHA256.

## Important APIs, Types, and Functions
Exports `eip93_hash_handle_result()` for result dispatch. Crypto API callbacks include `eip93_hash_init()`, `eip93_hash_update()`, `eip93_hash_final()`, `eip93_hash_finup()`, `eip93_hash_digest()`, `eip93_hash_export()`, `eip93_hash_import()`, and HMAC `eip93_hash_hmac_setkey()`. Algorithm templates are defined for plain and HMAC variants.

`__eip93_hash_init()` programs hash SA records and creates a second HMAC SA record so CMD_HMAC is enabled only on the final block. `eip93_send_hash_req()` maps data blocks, fills descriptors, allocates an async IDR only for the last descriptor, and starts DMA.

## Control Flow
Initialization seeds `sa_state` digest constants and, for HMAC, prepends the precomputed ipad block to request data. Update accumulates data in 64-byte blocks, allocates `mkt_hash_block` nodes, and submits full blocks. With `complete_req`, the last queued full block gets the async IDR and returns `-EINPROGRESS`; otherwise finup can queue intermediate blocks and let final submit the completing descriptor. Final handles the EIP93 zero-length hash limitation in software for plain hashes, sets `finalize`, maps SA state/record when needed, and submits the trailing data buffer as the last descriptor. Completion unmaps state, swaps non-MD5 digest words to CPU order, copies results, frees SA records and block DMA mappings, and completes the ahash request.

## State and Persistence
Per-transform state is `struct eip93_hash_ctx`, including flags and HMAC ipad/opad. Per-request state is DMA-aligned `struct eip93_hash_reqctx`, including SA records, SA state, block list, cached partial block, length counters, and finalize/partial flags. Export/import persists a hash operation into an in-memory `eip93_hash_export_state`, not to disk.

## Dependencies and Integration Points
Uses `eip93_set_sa_record()` and `eip93_hmac_setkey()` from common code, EIP93 ring descriptor APIs, Linux ahash crypto API, digest constants from crypto headers, and result dispatch from `eip93-main.c`.

## Risks
Hardware cannot handle zero-length plain hashes, requiring software constants; HMAC zero-length goes through hardware because ipad data exists. The block list is submitted in reverse list order after `list_add()`, which preserves original input order but is easy to break if list handling changes. DMA unmap sizes are fixed at `SHA256_BLOCK_SIZE` for full blocks. HMAC finalization depends on using a duplicate SA record only for the last descriptor. Async IDR allocation is not visibly checked in the submission helper.

## Test Signals
Run ahash KATs for zero-length and multi-block MD5/SHA1/SHA224/SHA256 and HMAC variants, export/import mid-stream, finup versus update+final equivalence, keys longer than block size, SHA224 partial digest handling, and request cancellation/removal stress under DMA debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.h

## Purpose
Defines EIP93 hash transform/request/export structures and declares hash algorithm templates plus the result callback.

## Important APIs, Types, and Functions
`struct eip93_hash_ctx` stores the EIP93 device, algorithm flags, and precomputed HMAC ipad/opad buffers. `struct eip93_hash_reqctx` contains DMA-aligned SA records/state, DMA addresses, finalize/partial flags, byte counters, a 64-byte cache, and a list of queued full hash blocks. `struct mkt_hash_block` stores one DMA-mapped 64-byte block. `struct eip93_hash_export_state` is the crypto API export/import format.

The header declares `eip93_hash_handle_result()` and extern templates for MD5, SHA1, SHA224, SHA256, and HMAC variants.

## Control Flow
`eip93-hash.c` allocates the request context through `crypto_ahash_set_reqsize_dma()`, fills these structures during update/final, and the EIP93 core calls the result handler when a hash LAST descriptor completes.

## State and Persistence
The export state stores hash length, EIP93 byte counters, intermediate digest, and cached partial block for in-memory suspend/resume of a hash request. DMA fields are transient and valid only during active hardware submission.

## Dependencies and Integration Points
Includes SHA2 sizing constants and EIP93 core/register definitions. The structs are tightly coupled to EIP93 SA record/state layout and CRYPTO DMA alignment requirements.

## Risks
Structure layout matters for DMA alignment and hardware interpretation. Changing fields before the aligned SA record block or altering buffer sizes can break DMA or export/import compatibility. Only SHA256-sized state buffers are stored, which matches the supported hashes but constrains extension.

## Test Signals
Compile with `CONFIG_CRYPTO_MANAGER_EXTRA_TESTS`, exercise export/import on every declared algorithm, and run with DMA alignment/debug instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.c

## Purpose
Implements the EIP93 platform driver: device probing, descriptor ring allocation, hardware initialization, interrupt handling, result dispatch, and crypto algorithm registration.

## Important APIs, Types, and Functions
Core routines include `eip93_register_algs()`, `eip93_unregister_algs()`, `eip93_handle_result_descriptor()`, `eip93_irq_handler()`, `eip93_initialize()`, `eip93_desc_init()`, `eip93_cleanup()`, `eip93_crypto_probe()`, and `eip93_crypto_remove()`. It exposes inline IRQ helpers `eip93_irq_enable()`, `eip93_irq_disable()`, and `eip93_irq_clear()`.

The static `eip93_algs[]` array collects templates from AES, DES, AEAD, and hash files.

## Control Flow
Probe allocates `struct eip93_device`, maps MMIO, requests the IRQ, allocates and initializes one command ring and one result ring, initializes tasklet/spinlocks/IDR, reads hardware option bits, resets/configures the packet engine, enables RDR threshold interrupts, and registers supported algorithms. Removal unregisters algorithms and disables/cleans hardware.

At runtime, the IRQ handler detects RDR threshold interrupts, disables that interrupt, and schedules a tasklet. The tasklet drains result descriptors. It waits until hardware marks descriptor ownership and length ready, acknowledges RD count, stops at `EIP93_DESC_LAST`, resolves the async request through the 16-bit IDR, parses hardware errors, and calls the result handler matching `EIP93_DESC_SKCIPHER`, `EIP93_DESC_AEAD`, or `EIP93_DESC_HASH`.

## State and Persistence
Maintains MMIO base, IRQ, rings, tasklet, spinlocks, and an IDR mapping descriptor user IDs to active crypto requests. Ring memory is DMA coherent and device-managed. No persistent storage is used.

## Dependencies and Integration Points
Depends on platform device/OF infrastructure, Linux crypto registration APIs, EIP93 register definitions, and algorithm templates from sibling EIP93 files. Device tree compatibles include several `inside-secure,safexcel-eip93*` variants.

## Risks
The result drain loop busy-waits for descriptor ownership bits with no timeout. IDR lookup/removal assumes a valid ID stored by submitters. The driver uses 32-bit DMA addresses in descriptors and casts coherent base DMA to `u32`, so it depends on suitable DMA addressing. Requesting a threaded IRQ with only a primary handler and `IRQF_ONESHOT` is unusual but functional if supported. Algorithm template globals are mutated with the device pointer during registration.

## Test Signals
Probe/remove on each compatible, interrupt storm and ring saturation tests, crypto self-tests under concurrent requests, IDR exhaustion behavior, DMA mask/address tests on 64-bit systems, and hardware error injection for auth/pad/ext errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.h

## Purpose
Defines EIP93 core constants, algorithm/mode/descriptor flags, device/ring structures, and algorithm template type shared by all EIP93 driver files.

## Important APIs, Types, and Functions
Key constants include `EIP93_RING_NUM`, `EIP93_RING_BUSY`, `EIP93_CRA_PRIORITY`, algorithm flags (`EIP93_ALG_*`, `EIP93_HASH_*`), mode flags (`EIP93_MODE_*`), direction flags, and descriptor flags (`EIP93_DESC_*`). Helper macros classify flags, such as `IS_AES()`, `IS_HMAC()`, `IS_CTR()`, and `IS_ENCRYPT()`.

Types include `struct eip93_device`, `struct eip93_desc_ring`, `struct eip93_ring`, `enum eip93_alg_type`, and `struct eip93_alg_template`.

## Control Flow
The flags defined here are set by algorithm templates and per-request frontends, then consumed by common SA record generation, descriptor submission, result dispatch, and algorithm support filtering.

## State and Persistence
`struct eip93_device` is the driver instance. `struct eip93_ring` owns command/result rings, lock state, a tasklet, and the async IDR. Template objects are global descriptors patched with the active device pointer during registration.

## Dependencies and Integration Points
Includes Linux crypto internal headers for AEAD/hash/skcipher algorithm structures and interrupt support. It is the central include for EIP93 sibling files.

## Risks
Macros encode overlapping bit ranges and must stay synchronized with `eip93-regs.h` and template flags. The 16-bit crypto IDR field limits active tracked requests to `EIP93_RING_NUM - 1` in current code. `EIP93_RING_SA_STATE_DMA()` casts DMA addresses to 32-bit, reflecting descriptor limitations.

## Test Signals
Compile-time coverage of all templates, sparse checks for bitfield usage, and runtime tests that combine every algorithm/mode/direction flag path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-regs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-regs.h

## Purpose
Defines the EIP93 packet engine register map, bitfields, SA record layout, SA state layout, and descriptor layout used by the EIP93 driver.

## Important APIs, Types, and Functions
Register definitions cover direct packet engine registers, command/result ring registers, packet engine config/status, endian and clock control, option/revision registers, interrupt registers, SA command words, and state offsets. Important bitfields include ownership/ready bits, extended error codes, ring sizes/counts, clock enables, algorithm option bits, interrupt masks, SA cipher/hash/mode/opcode fields, and copy/HMAC controls.

The hardware-facing packed structures are `struct sa_record`, `struct sa_state`, and `struct eip93_descriptor`.

## Control Flow
`eip93-main.c` uses these definitions for initialization, interrupt control, option detection, and result draining. `eip93-common.c`, `eip93-cipher.c`, `eip93-aead.c`, and `eip93-hash.c` use SA command fields and descriptor fields to program work for the packet engine.

## State and Persistence
No software state is held in the header. The packed structures define DMA-visible state exchanged with hardware: SA records contain command words, keys, digest state, SPI/sequence fields, and nonce; SA state stores IV, byte count, and intermediate digest; descriptors carry control/status, source/destination/SA/state addresses, user ID, and length.

## Dependencies and Integration Points
Uses Linux `BIT`, `GENMASK`, and `FIELD_PREP` bit helpers through including C files. It is tightly coupled to the EIP93 hardware manual and must match hardware endianness/address expectations.

## Risks
Packed structure layout and bit constants are hardware ABI. Typos or field-width mistakes can cause silent crypto corruption, DMA faults, or incorrect error reporting. `EIP93_REG_INT_MASK_STAT` and `EIP93_REG_INT_CLR` share offset `0x204`, so read/write semantics must remain clear. Descriptor address fields are 32-bit.

## Test Signals
Validate with hardware probe logs, register readback tests, crypto KATs across every mode, endian configuration tests, and hardware error injection to confirm `eip93_parse_ctrl_stat_err()` mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.c

## Purpose
Implements the main SafeXcel EIP97/EIP197 crypto engine driver. It handles platform and PCI probing, hardware detection/configuration, EIP197 context cache and firmware setup, descriptor ring setup, request queueing, interrupt-driven result completion, algorithm registration, and module init/exit.

## Important APIs, Types, and Functions
Major initialization functions include `eip197_trc_cache_init()`, `eip197_load_firmwares()`, `safexcel_hw_setup_cdesc_rings()`, `safexcel_hw_setup_rdesc_rings()`, `safexcel_hw_init()`, `safexcel_configure()`, `safexcel_init_register_offsets()`, and `safexcel_probe_generic()`. Runtime queue/completion functions include `safexcel_dequeue()`, `safexcel_try_push_requests()`, `safexcel_rdesc_check_errors()`, `safexcel_complete()`, `safexcel_invalidate_cache()`, and `safexcel_handle_result_descriptor()`. Probe/remove paths are `safexcel_probe()`, `safexcel_remove()`, `safexcel_pci_probe()`, and `safexcel_pci_remove()`.

The static `safexcel_algs[]` array collects skcipher, AEAD, ahash, SHA3, SMx, Chacha/Poly, CCM/GCM, and authenc templates from other driver files. `max_rings` is a module parameter.

## Control Flow
Platform probe maps MMIO, enables optional clocks, sets a 64-bit DMA mask, and calls the generic probe. PCI probe maps BARs, performs dev-board reset/MSI setup when applicable, enables bus mastering, and also calls the generic probe. Generic probe creates the DMA context pool, detects EIP97 versus EIP197 and endianness, probes EIP206/EIP96/EIP201 blocks, records hardware capabilities, configures descriptor sizes/ring counts, allocates rings/workqueues/IRQ data, requests per-ring IRQs, initializes hardware, and registers only algorithms whose `algo_mask` is supported by hardware.

At runtime, algorithm-specific send functions enqueue requests into per-ring crypto queues. `safexcel_dequeue()` pulls requests, calls each context’s `send()` method to emit command/result descriptors, records pending request counts, writes RDR/CDR prepared counts, and programs RDR interrupt coalescing. Ring IRQs acknowledge RDR threshold events and wake a threaded handler. The thread calls `safexcel_handle_result_descriptor()`, which retrieves the request stored for the first result descriptor, dispatches to the algorithm context’s `handle_result()`, completes the crypto request if requested, acknowledges processed descriptors, updates ring busy/request state, and schedules a workqueue refill.

## State and Persistence
Driver instance state is in `struct safexcel_crypto_priv`: MMIO base, clocks, per-device data, register offsets, probed hardware config, flags, DMA context pool, ring selection counter, and ring array. Each ring holds descriptor rings, a request pointer table for RDR entries, a crypto queue, locks, busy/request counters, saved request/backlog when resources run out, IRQ number, and a single-thread workqueue. Firmware is loaded into hardware program memory at probe time but not persisted by the driver.

## Dependencies and Integration Points
Depends on Linux platform/OF, PCI, firmware loader, DMA pool, workqueue, interrupt, and crypto registration APIs. Integrates with sibling SafeXcel algorithm files through `struct safexcel_context` callbacks and `safexcel_alg_template` declarations in `safexcel.h`. Firmware paths include `inside-secure/eip197b`, `inside-secure/eip197d`, `inside-secure/eip197_minifw`, and legacy root names for EIP197B.

## Risks
TRC cache probing writes classification RAM and assumes sane physical RAM sizing. Firmware startup polling has a small bounded poll count and falls back to mini firmware only for supported cases. DSE reset waits in a tight loop for thread status. Fatal RDR errors are logged but the ring is not reinitialized in this path. PCI probe allocates `priv` with `kzalloc_obj()` and several early error paths return without freeing it. The PCI remove path destroys workqueues but does not clear IRQ affinity hints, unlike platform remove. Correct operation depends on algorithm `send()`/`handle_result()` callbacks managing descriptor resources exactly.

## Test Signals
Probe/remove both DT and PCI paths, test EIP97 and EIP197 variants, firmware present/missing/minifw fallback, multiple `max_rings` values, MSI/MSI-X on dev board, crypto self-tests for capability-filtered algorithms, ring saturation and backlog handling, fatal RDR status injection, DMA API debug, and suspend-like remove while queues are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.h

## Purpose
Defines the SafeXcel EIP97/EIP197 register map, descriptor formats, context record layout, token encoding, hardware capability flags, driver state structures, helper prototypes, and algorithm template declarations.

## Important APIs, Types, and Functions
The header contains version constants for HIA/EIP blocks, register base macros for EIP197 and EIP97, CDR/RDR register offsets, DFE/DSE/AIC/PE/TRC/ICE bitfields, context-control encodings, token opcodes/instructions, firmware constants, and algorithm capability flags.

Important hardware-facing structures are `struct safexcel_context_record`, `struct result_data_desc`, `struct safexcel_result_desc`, `struct safexcel_token`, `struct safexcel_control_data_desc`, and `struct safexcel_command_desc`. Driver structures include `struct safexcel_desc_ring`, `struct safexcel_config`, `struct safexcel_ring`, `struct safexcel_priv_data`, `struct safexcel_register_offsets`, `struct safexcel_hwconfig`, `struct safexcel_crypto_priv`, `struct safexcel_context`, `struct safexcel_ahash_export_state`, and `struct safexcel_alg_template`.

Prototypes include queue/completion helpers, ring pointer helpers, descriptor allocation helpers, request mapping helpers, and `safexcel_hmac_setkey()`.

## Control Flow
`safexcel.c` uses register macros and structures to probe hardware, configure rings, process interrupts, and register algorithms. Algorithm-specific C files use `struct safexcel_context` callbacks and descriptor helper prototypes to build command/result descriptors, attach requests to result descriptors, and process completion.

## State and Persistence
The header defines all in-memory state containers for the SafeXcel core. `struct safexcel_crypto_priv` is per device, `struct safexcel_ring` is per hardware ring, and `struct safexcel_context` is per crypto transform. `struct safexcel_ahash_export_state` is an in-memory crypto API export/import format. No filesystem persistence is defined.

## Dependencies and Integration Points
Includes Linux crypto AEAD/hash/skcipher headers and SHA sizing constants. It is the central contract between `safexcel.c`, ring helpers, cipher/hash/AEAD algorithm files, and hardware firmware/register programming.

## Risks
Many bitfields and packed descriptors are hardware ABI and sensitive to layout, endian, and bus-width alignment. `struct safexcel_context` embeds callback pointers used by the core queue and result paths; a missing or wrong callback in an algorithm file can break request processing. The extern algorithm list is broad, so Kconfig/source selection must provide matching definitions. Register offset macros rely on correctly detected EIP97/EIP197 offsets.

## Test Signals
Build all SafeXcel objects together, run sparse/endianness checks, verify descriptor size/offset calculations on different hardware data widths, inspect `/proc/crypto` against hardware `algo_flags`, run ahash export/import tests, and use DMA/debug instrumentation on descriptor rings and context records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.h -->
