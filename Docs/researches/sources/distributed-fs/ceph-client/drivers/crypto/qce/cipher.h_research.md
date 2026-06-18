<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/cipher.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/cipher.h

Purpose: declares QCE skcipher transform/request context structures and the skcipher algorithm-ops export.

Important types: `struct qce_cipher_ctx` holds the raw encryption key, key length, and optional fallback skcipher for AES modes. `struct qce_cipher_reqctx` holds operation flags, IV pointer/size, SG counts, result SG, destination SG table, source/destination SG pointers, crypt length, and trailing fallback request.

Control flow and integration: skcipher code fills request context before queueing; shared register setup in `common.c` reads flags, key, IV, and crypt length. `to_cipher_tmpl()` maps a crypto skcipher transform back to its `qce_alg_template`. `skcipher_ops` is consumed by QCE core registration and dispatch.

State and persistence: transform context persists keys and fallback; request context is transient but its result SG and destination table remain live until DMA completion.

Dependencies: QCE common/core headers, Linux crypto skcipher APIs, scatterlists, and AES/DES key size constraints.

Risks and test signals: fallback request is deliberately last and request-size code depends on that layout. Test AES fallback paths, DES/3DES no-fallback paths, IV update after completion, and DMA cleanup for both in-place and split source/destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/cipher.h -->
