<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.h

Purpose: declares QCE AEAD context structures and the algorithm operations handle used by the QCE core.

Important types: `struct qce_aead_ctx` stores encryption key, authentication key, RFC4309 CCM salt, key lengths, authsize, fallback-needed flag, and fallback AEAD transform. `struct qce_aead_reqctx` stores operation flags, IV pointer/size, source and destination SG state, result and AAD SG entries, allocated SG tables, crypt/assoc lengths, allocated formatted AAD, CCM nonce/result buffers, RFC4309 IV, and trailing fallback request.

Control flow and integration: `to_aead_tmpl()` recovers the enclosing `qce_alg_template` from a registered AEAD transform. `aead_ops` is exported to `core.c` so QCE can register/unregister AEAD algorithms and dispatch queued requests by type.

State and persistence: context fields persist across transform lifetime, especially fallback and key material. Request context fields are per-request and include resources that completion/error paths must free.

Dependencies: shared QCE `common.h`/`core.h`, crypto AEAD APIs, scatterlists, and QCE nonce/key constants.

Risks and test signals: the trailing fallback request requirement affects request-size calculation. Dynamic `adata` and SG tables must be consistently initialized and released. Test fallback request sizing, CCM/RFC4309 IV construction, and all diff-dst/in-place SG table branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.h -->
