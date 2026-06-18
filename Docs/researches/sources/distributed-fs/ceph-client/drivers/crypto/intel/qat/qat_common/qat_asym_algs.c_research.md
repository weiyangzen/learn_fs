# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_asym_algs.c

## Purpose
`qat_asym_algs.c` implements QAT public-key Crypto API algorithms for RSA (`akcipher`) and Diffie-Hellman (`kpp`). It manages DMA key material, builds PKE firmware parameter tables, handles scatterlist alignment/padding, submits PKE requests, completes async operations, and registers algorithms once per active device set.

## Important APIs, Types, And Functions
Key types are `qat_rsa_ctx`, `qat_dh_ctx`, and `qat_asym_request`, with RSA/DH input/output parameter table structures. Important functions include `qat_alg_send_asym_message()`, `qat_alg_asym_callback()`, `qat_dh_compute_value()`, `qat_dh_set_secret()`, `qat_dh_cb()`, `qat_rsa_enc()`, `qat_rsa_dec()`, `qat_rsa_setkey()`, `qat_rsa_setkey_crt()`, `qat_rsa_cb()`, and function-ID selectors for RSA/DH key sizes. Public registration APIs are `qat_asym_algs_register()` and `qat_asym_algs_unregister()`.

## Control Flow
RSA transform init obtains a QAT instance and sets request size. Key setup parses public/private keys, strips leading zeros, allocates coherent buffers for `n`, `e`, `d`, and optional CRT fields, and selects CRT mode when all CRT components are present. RSA encrypt/decrypt validates key presence, destination length, source length, chooses a PKE function ID by modulus size and CRT/non-CRT mode, pads non-full-size scatterlist input into aligned temporary memory, maps source/output buffers and parameter tables, fills a PKE request, and submits on the PKE ring. Completion unmaps everything, copies aligned output back if needed, sets `dst_len`, and completes the request.

DH init obtains a QAT instance and allocates fallback KPP. `set_secret` decodes DH params; unsupported prime lengths fall back to software. Supported paths allocate coherent `p`, optional `g`, and private `xa`. Public/shared-secret operations build PKE tables for base `g` or peer public value, use optimized G=2 function IDs when possible, align input/output buffers, submit, and complete similarly to RSA.

## State And Persistence Behavior
RSA context persists DMA key components and CRT mode for the transform. DH context persists `p`, optional `g`, `xa`, G=2 flag, fallback transform, and instance. Per-request `qat_asym_request` persists aligned temporary buffers, DMA parameter tables, firmware request, callbacks, and request pointers until completion. Registration uses a mutex and active-device counter.

## Dependencies And Integration Points
The file depends on Crypto API RSA/KPP internals, DH/RSA parsers, FIPS flag header, QAT PKE firmware ABI, QAT transport/backlog, DMA mapping, scatterwalk helpers, and `qat_crypto` instance selection. It integrates with the PKE response callback registered on PKE rings.

## Risks
Key-size support is limited to specific RSA/DH bit lengths. DMA cleanup paths are dense and must avoid leaking sensitive buffers. RSA CRT setup silently falls back to non-CRT if any CRT component allocation/validation fails, while private exponent remains required. Request contexts are manually 64-byte aligned using extra request size. Fallback paths for DH must mirror request flags and output lengths.

## Test Signals
RSA encrypt/decrypt selftests across 512/1024/1536/2048/3072/4096-bit keys, private CRT and non-CRT keys, short inputs, too-small outputs, fragmented SGLs, and malformed keys are important. DH tests should cover supported and unsupported prime sizes, G=2 optimized public-key generation, peer shared secret, fallback, and PKE error status.
