# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.h

## Purpose
This header defines algorithm-level constants, operation enums, context layouts, and Crypto API lifecycle prototypes for the CPT VF algorithm implementation.

## Important APIs and types
Constants define maximum key sizes and request types. Enums cover request type, major opcodes, cipher types, MAC types, and AES key lengths. Hardware context/control types include `union otx2_cpt_encr_ctrl`, `struct otx2_cpt_fc_enc_ctx`, `union otx2_cpt_fc_hmac_ctx`, `struct otx2_cpt_fc_ctx`, and `union otx2_cpt_offset_ctrl`. Crypto transform contexts are `struct otx2_cpt_enc_ctx`, `struct otx2_cpt_req_ctx`, `struct otx2_cpt_sdesc`, and `struct otx2_cpt_aead_ctx`. Public functions are `otx2_cpt_crypto_init()` and `otx2_cpt_crypto_exit()`.

## Control flow
There is no executable control flow. The structures are filled by `otx2_cptvf_algs.c` during setkey and request construction, then passed through `otx2_cpt_reqmgr.h` and `otx2_cptvf_reqmgr.c` into CPT instructions.

## State and persistence
Transform contexts persist for the life of a Crypto API tfm and hold keys, fallback tfms, shash state, CN10K errata context, PCI device, and algorithm metadata. Request contexts are per-operation and contain request info, control word, hardware flexicrypto context, and fallback request storage.

## Dependencies and integration points
The header depends on Crypto API hash/skcipher/aead types, common CPT definitions, and CN10K CPT helper state. It is included by VF main for crypto registration and by algorithm implementation for all request construction.

## Risks and edge cases
Bitfield layout in `otx2_cpt_encr_ctrl` and `otx2_cpt_offset_ctrl` depends on endian configuration. Key buffers combine authentication and encryption key material, so setkey code must respect max lengths and offsets. `struct otx2_cpt_req_ctx` contains a union of fallback request types, so request-size setup must match the algorithm class.

## Test signals
Signals include successful build across endian configurations, correct setkey behavior for all supported key sizes, valid hardware context bytes in request dumps, AEAD HMAC pad generation, fallback request storage sizing, and crypto selftests for all declared algorithm modes.
