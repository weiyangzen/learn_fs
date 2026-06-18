# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.h

Purpose: common SPU abstraction header shared by SPU-M and SPU2 implementations. It defines hardware-independent cipher/hash/AEAD enums, request parameter structures, common sizing constants, inline helpers, and the public function contract each SPU backend implements.

Important APIs and types: `enum spu_cipher_alg`, `spu_cipher_mode`, `spu_cipher_type`, `hash_alg`, `hash_mode`, `hash_type`, and `aead_type`; `struct spu_request_opts`, `spu_cipher_parms`, `spu_hash_parms`, and `spu_aead_parms`; constants such as `SPU_RX_STATUS_LEN`, `SPU_PAD_LEN_MAX`, `SPU_MAX_PAYLOAD_INF`, `SPU_XTS_TWEAK_SIZE`, and CCM B0 masks; inline `spu_req_incl_icv()` and `spu_real_db_size()`. It declares the full SPU-M function surface and includes the common name arrays.

Control flow: higher-level cipher code works in these generic enum and parameter types, then dispatches through SPU-M or SPU2-specific functions. The inline helpers are used before request construction to decide whether decrypting GCM/CCM must carry ICV separately and to compute total data-block size.

State and persistence: this header owns no runtime state but defines mutable parameter buffers (`key_buf`, `iv_buf`) that backend implementations may read or update.

Dependencies and integration points: depends on Linux types, scatterlists, and crypto SHA constants. It is the compatibility layer between Broadcom crypto driver code and the two SPU hardware formats.

Risks: enum aliases intentionally share values, for example ECB/NONE and several AES/hash type constants. Callers must interpret values in context. Adding algorithms requires keeping `HASH_ALG_LAST`, name arrays, backend translation functions, and hardware masks consistent.

Test signals: build coverage for both SPU-M and SPU2, crypto selftests across every advertised enum combination, and compile-time detection of prototype drift between headers and implementation files.
