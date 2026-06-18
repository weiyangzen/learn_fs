# sources/distributed-fs/ceph-client/include/crypto/md5.h

Purpose: exposes compact non-crypto-API MD5 and HMAC-MD5 helper contexts and one-shot functions for kernel users that need direct primitives.

Important APIs, types, and flow: constants define digest, block, state, and initial hash values. `md5_state`, `md5_block_state`, and `md5_ctx` hold incremental hash state; `md5_init()`, `md5_update()`, `md5_final()`, and `md5()` implement incremental and one-shot hashing. `hmac_md5_key` stores prepared inner/outer block keys; `hmac_md5_ctx` combines key and hash context. HMAC helpers prepare keys, initialize from prepared or raw key, update, finalize, and perform one-shot HMAC.

State and persistence: state is caller-owned contexts containing hash and key material. No persistence exists; HMAC contexts should be treated as sensitive.

Dependencies and integration: depends on kernel crypto type definitions and is used by protocol code needing low-overhead MD5/HMAC-MD5. It also exposes the zero-message digest constant.

Risks and test signals: MD5 is cryptographically broken for collision resistance, so use should be limited to legacy/non-adversarial protocols. Signals include RFC MD5/HMAC-MD5 vectors, incremental vs one-shot parity, empty-message hash, raw/prepared key equivalence, and zeroization review for HMAC keys.
