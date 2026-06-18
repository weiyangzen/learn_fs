# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu2.c

Purpose: SPU2 message-format implementation for Broadcom crypto hardware. It hides SPU2 fixed metadata/optional metadata layout behind the same common API exposed by `spu.h`, translating software cipher/hash enums into SPU2 control words and building little-endian FMD/OMD headers.

Important APIs and functions: translation helpers `spu2_cipher_mode_xlate()`, `spu2_cipher_xlate()`, `spu2_hash_mode_xlate()`, and `spu2_hash_xlate()`; debug decoders `spu2_dump_fmd_ctrl*()`, `spu2_dump_omd()`, and `spu2_dump_msg_hdr()`; control writers `spu2_fmd_ctrl0_write()` through `spu2_fmd_ctrl3_write()`; public helpers `spu2_ctx_max_payload()`, `spu2_payload_length()`, `spu2_response_hdr_len()`, `spu2_hash_pad_len()`, `spu2_gcm_ccm_pad_len()`, `spu2_assoc_resp_len()`, `spu2_aead_ivlen()`, `spu2_hash_type()`, `spu2_digest_size()`, `spu2_create_request()`, `spu2_cipher_req_init()`, `spu2_cipher_req_finish()`, `spu2_request_pad()`, `spu2_status_process()`, `spu2_ccm_update_iv()`, and `spu2_wordalign_padlen()`.

Control flow: AEAD/hash/cipher request creation adjusts ordering for GCM and CCM, translates generic enums, handles RFC4543 and zero-payload GCM as hash-only, writes FMD ctrl words, then serializes hash key, cipher key, and IV into OMD. The skcipher path initializes FMD/OMD at setkey time and updates encrypt/decrypt, IV, and payload length at request time.

State and persistence: no persistent storage. It writes caller-provided request buffers and can mutate parameter structures: RFC4543/GCM hash-only moves cipher key into hash key fields, and `spu2_ccm_update_iv()` shortens and shifts the IV buffer because SPU2 does not want CCM flags/length bytes.

Dependencies and integration points: uses `spu.h`, `spu2.h`, `util.h`, Linux endian helpers, and `linux/string_choices.h` for logging. It integrates with the common Broadcom crypto request path and status handling.

Risks: SPU2 uses little-endian FMD while SPU-M uses big-endian headers; payload length is effectively infinite except CCM but still encoded in ctrl3; RFC4543 changes key ownership and payload/assoc interpretation; status length is controlled by a hardware register default; `spu2_cipher_req_finish()` ORs payload length into ctrl3, so stale bits would matter if reused incorrectly.

Test signals: Crypto API tests for GCM/CCM ordering, RFC4106/RFC4543, zero-length GCM payloads, skcipher IV update, CCM IV rewriting, invalid tag status, and descriptor dumps matching expected FMD fields.
