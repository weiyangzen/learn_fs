# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs.c

## Purpose
`qat_algs.c` implements QAT symmetric Crypto API algorithms: AES CBC, AES CTR, AES XTS, and authenc HMAC(SHA1/SHA256/SHA512)-CBC-AES AEAD. It builds QAT lookaside firmware requests, DMA content descriptors, maps scatterlists into QAT buffer lists, handles async completions, updates IVs, supports backlog submission, and registers algorithms once across active devices.

## Important APIs, Types, And Functions
Key context types are `qat_alg_cd`, `qat_alg_aead_ctx`, and `qat_alg_skcipher_ctx`. Important setup helpers include `qat_alg_do_precomputes()`, `qat_alg_init_common_hdr()`, `qat_alg_aead_init_enc_session()`, `qat_alg_aead_init_dec_session()`, `qat_alg_skcipher_init_com()`, `qat_alg_skcipher_init_enc()`, `qat_alg_skcipher_init_dec()`, `qat_alg_validate_key()`, and key-management functions for AEAD/skcipher/XTS. Runtime functions include `qat_alg_aead_enc()`, `qat_alg_aead_dec()`, `qat_alg_skcipher_encrypt()`, `qat_alg_skcipher_decrypt()`, XTS wrappers, `qat_alg_callback()`, and completion callbacks. Public registration functions are `qat_algs_register()` and `qat_algs_unregister()`.

## Control Flow
Transform init records hash settings or allocates XTS fallback/tweak ciphers. Setkey obtains a NUMA-local QAT crypto instance, allocates coherent content descriptors, validates AES key length, fills cipher/auth setup blocks, precomputes HMAC inner/outer states, builds firmware request templates, and sets slice chains. AEAD encrypt/decrypt validates block-aligned payloads, maps source/destination SGLs, copies the template, fills opaque pointer, buffer-list DMA addresses, IV, cipher offset/length, and auth params, then submits through the symmetric ring. Skcipher encrypt/decrypt follows the same pattern with cipher-only params and IV handling; CBC/CTR IVs are updated after completion or precomputed for decrypt, XTS may use hardware or fallback for AES-192-XTS.

## State And Persistence Behavior
Per-transform contexts persist content descriptors, physical addresses, firmware templates, selected instance, fallback objects, mode, and hash metadata. Per-request state lives in `struct qat_crypto_request` embedded in the Crypto API request context and contains the firmware request, mapped buffer list, callback, IV copy, and request pointers. Registration state uses a mutex and `active_devs` reference count.

## Dependencies And Integration Points
The file depends on Linux Crypto API internals, HMAC precompute helpers, AES/XTS helpers, QAT transport/backlog code, `qat_crypto` instance selection, firmware LA/hardware headers, DMA, and `qat_bl` SGL conversion. It integrates with QAT service callbacks through `qat_alg_callback()` registered on rings.

## Risks
DMA mapping/unmapping is complex and must match every error/completion path. AEAD only supports CBC payloads aligned to AES block size and authenc key parsing. XTS hardware/fallback split depends on AES-V2 capability and key size; tweak handling must match firmware expectations. IV updates are mode-specific and can corrupt caller state if completion order or error paths are wrong. Registration refcounting must match device bring-up/tear-down.

## Test Signals
Crypto selftests should cover all registered algorithms, all AES key sizes, AEAD encrypt/decrypt success and auth failure, fragmented and in-place/out-of-place SGLs, zero-length skcipher, CTR counter carry, CBC IV update, XTS fallback for 192-bit halves, AES-V2 XTS/CTR paths, backlog/ring-full behavior, and unregister after multiple devices.
