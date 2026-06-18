<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hmac.c -->
# sources/distributed-fs/ceph-client/crypto/hmac.c

Purpose: Implements `hmac` templates for both synchronous hash (`shash`) and asynchronous hash (`ahash`) frontends, wrapping an unkeyed hash algorithm with RFC2104 HMAC processing.

Important APIs/types/functions: `struct hmac_ctx` and `struct ahash_hmac_ctx` store child hash handles plus exported inner and outer pad states. `hmac_setkey()` and `hmac_setkey_ahash()` hash oversized keys, enforce a 112-bit minimum in FIPS mode, build ipad/opad, and export preinitialized hash states. Shash operations include init/update/finup/export/import and core export/import. Ahash operations mirror them with child `ahash_request` forwarding and async finup completion. `hmac_create()` selects ahash or shash based on requested type, while `hmac-shash` forces shash.

Control flow: Template creation grabs an unkeyed child hash, rejects keyed children and invalid digest/state sizes, names the instance, and registers it. Setkey prepares reusable inner/outer states. A digest operation imports the inner state, processes data, finalizes the inner digest, imports the outer state, and hashes the inner digest to produce the HMAC. Ahash finup may complete synchronously or through `hmac_finup_done()`.

State and persistence behavior: Per-transform state stores child transform references and pad-state snapshots for the transform lifetime. Per-request state stores child descriptors/requests. Sensitive request and key-derived buffers are zeroed with stack/request zero helpers or sensitive frees where used.

Dependencies and integration points: Uses `crypto/hmac.h`, internal hash template APIs, Linux FIPS mode, ahash virtual request support, and the crypto template registry. It is foundational for KDFs, Kerberos, IPsec, and many kernel authentication users.

Risks: Underlying hashes requiring keys are deliberately rejected; missing that check would create nested keyed semantics. Exported state sizes must be at least the block size or pad export would overrun. Ahash request sizing is validated because wrapper requests embed child requests. FIPS key-length rejection can break callers that previously used short keys.

Test signals: HMAC known-answer tests for shash and ahash, long-key normalization, export/import and export_core/import_core, async completion paths, invalid child hash rejection, FIPS short-key rejection, clone_tfm behavior, and template lookup for `hmac(sha256)` and `hmac-shash(sha256)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hmac.c -->
