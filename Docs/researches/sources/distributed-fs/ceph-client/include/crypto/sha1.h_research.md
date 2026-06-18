# sources/distributed-fs/ceph-client/include/crypto/sha1.h

Purpose: exposes direct SHA-1 and HMAC-SHA1 incremental and one-shot helpers.

Important APIs, types, and flow: constants define digest/block/state sizes and initial hash words. `sha1_state`, `sha1_block_state`, and `sha1_ctx` hold incremental state; `sha1_init()`, `sha1_update()`, `sha1_final()`, and `sha1()` process messages. HMAC structs and helpers mirror the MD5 pattern with prepared inner/outer keys, raw-key initialization, update, final, and one-shot APIs.

State and persistence: caller-owned contexts hold hash state and HMAC key material. No persistence exists.

Dependencies and integration: used by legacy protocols, Kerberos variants, and direct HMAC users outside the generic crypto API. Exposes the zero-message SHA-1 digest constant.

Risks and test signals: SHA-1 is collision-broken and should be limited to legacy compatibility or HMAC contexts where still accepted. Signals include SHA-1/HMAC-SHA1 vectors, incremental split tests, empty-message digest checks, raw/prepared key equivalence, and policy review of new call sites.
