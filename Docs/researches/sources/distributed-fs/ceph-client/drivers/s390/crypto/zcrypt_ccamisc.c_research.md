# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.c

## Purpose
`zcrypt_ccamisc.c` implements exported helper routines for CCA secure-key handling used by the s390 zcrypt core and pkey consumers. It builds CCA CPRBX request/reply buffers, sends them through `zcrypt_send_cprb()`, validates CCA AES DATA, AES CIPHER, and ECC token formats, derives protected keys, queries CCA facility state, and scans AP queues for CCA-capable APQNs matching master-key constraints.

## Important APIs, Types, And Functions
The externally visible functions are `cca_check_secaeskeytoken()`, `cca_check_secaescipherkey()`, `cca_check_sececckeytoken()`, `cca_genseckey()`, `cca_clr2seckey()`, `cca_sec2protkey()`, `cca_gencipherkey()`, `cca_clr2cipherkey()`, `cca_cipher2protkey()`, `cca_ecc2protkey()`, `cca_query_crypto_facility()`, `cca_get_info()`, `cca_findcard2()`, `zcrypt_ccamisc_init()`, and `zcrypt_ccamisc_exit()`. Internal helpers include `alloc_and_prep_cprbmem()`, `free_cprbmem()`, `prep_xcrb()`, and `_ip_cprb_helper()`. The file relies heavily on token layouts from `zcrypt_ccamisc.h`, AP queue status from `zcrypt_api.h`, and type-6 CPRB dispatch from `zcrypt_msgtype6.h`.

## Control Flow
Most operations allocate one contiguous buffer for request CPRB, request parameter block, reply CPRB, and reply parameter block. The request CPRB is initialized as a T2 CPRBX, `prep_xcrb()` wraps it in an `ica_xcRB`, `zcrypt_send_cprb()` submits it, and reply code/reason code checks gate parsing of the returned parameter block. Key-generation/import functions build different CCA service requests: `KG` for random AES DATA keys, `CM` for clear AES DATA import, `US` for secure-to-protected unwrap, `GK` for AES CIPHER generation, multi-step `IP` for AES CIPHER import, `AU` for AES CIPHER/ECC protected-key export, and `FQ` for facility queries. `cca_get_info()` issues `STATICSA` and `STATICSB` facility queries, while `cca_findcard2()` iterates the preallocated device-status table and filters queues by online state, CCA function bit, card/domain, hardware type, and master-key verification patterns.

## State And Persistence
The file owns two module-lifetime resources: `cprb_mempool` for no-allocation or short-term CPRB buffers, and `dev_status_mem` for serialized APQN scans. Sensitive request buffers are scrubbed before freeing when clear key material or derived protected key material may be present. No persistent on-disk state exists; observable state is AP queue status and adapter master-key state returned by firmware.

## Dependencies And Integration Points
This code integrates with the AP bus through `zcrypt_send_cprb()`, with pkey through exported secure/protected key helpers, with debug via `ZCRYPT_DBF_*`, and with zcrypt status calls through `zcrypt_device_status_ext()` and `zcrypt_device_status_mask_ext()`. It assumes CCA CPRB formats and CCA service function semantics.

## Risks And Test Signals
Primary risks are structure packing/length mismatches, unchecked firmware reply shape beyond local plausibility tests, endian/alignment sensitivity in embedded CCA fields, buffer-size mismatches in caller-supplied key buffers, and serialization bottlenecks around `dev_status_mem_mutex`. Good test signals include invalid token rejection, correct `-EINVAL`/`-EIO`/`-EBUSY` mapping, CPRB mempool operation under `ZCRYPT_XFLAG_NOMEMALLOC`, successful key generation/import/unwrap on CCA APQNs, master-key filtering in `cca_findcard2()`, and memory-scrub paths for clear-key operations.
