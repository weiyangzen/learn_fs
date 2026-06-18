# sources/distributed-fs/ceph-client/crypto/md5.c

Purpose: registers library-backed MD5 and HMAC-MD5 shash algorithms with crypto API state export/import compatibility.

Important APIs, types, and functions: exports `md5_zero_message_hash`. `crypto_md5_*` wrappers call `md5_init()`, `md5_update()`, `md5_final()`, and `md5()`. `crypto_hmac_md5_*` wrappers call `hmac_md5_preparekey()`, `hmac_md5_init()`, `hmac_md5_update()`, `hmac_md5_final()`, and `hmac_md5()`. Internal helpers `__crypto_md5_export()`, `__crypto_md5_import()`, and core variants implement shash state format.

Control flow: module init registers two algorithms: `md5` and `hmac(md5)`. Normal hash requests delegate to the library. Export copies the library context after subtracting the partial-block byte count and stores that partial count as one appended byte. Import restores the context and re-adds the partial count. HMAC import also restores the outer state from the tfm key.

State and persistence: per-request state lives in `struct md5_ctx` or `struct hmac_md5_ctx`; HMAC key state lives in the tfm context. Exported state is caller-owned and transient. The zero-message digest is static exported data.

Dependencies and integration points: depends on `<crypto/md5.h>` and `crypto/internal/hash.h`. Used by legacy protocols and by templates that request `hmac(md5)`.

Risks: MD5 is collision-broken and should be limited to compatibility use. Export/import relies on layout static assertions matching legacy `struct md5_state`. HMAC import must restore `ostate` from the current key or resumed HMACs are wrong.

Test signals: standard MD5 and HMAC-MD5 vectors, zero-message digest users, export/import mid-block and block-aligned states, keyed import after setkey, and algorithm aliases `md5-lib` and `hmac-md5-lib`.
