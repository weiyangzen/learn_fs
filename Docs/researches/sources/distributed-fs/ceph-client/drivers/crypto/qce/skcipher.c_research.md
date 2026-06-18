<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/skcipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/skcipher.c

Purpose: implements QCE skcipher algorithms for AES ECB/CBC/CTR/XTS and DES/3DES ECB/CBC with DMA staging and AES software fallbacks.

Important APIs and functions: `qce_skcipher_setkey()` stores AES keys, rejects XTS identical halves, and configures fallback; DES/3DES setkey functions verify keys and reject 3DES duplicate key components. `qce_skcipher_crypt()` validates lengths, handles zero-length no-op, selects fallback for AES-192 and unsuitable XTS lengths, then enqueues. `qce_skcipher_async_req_handle()` builds a destination SG table with an appended result dump, maps source/destination, submits DMA, and calls `qce_start()`. `qce_skcipher_done()` terminates DMA, unmaps/frees, checks status, and copies the returned counter IV to the request IV.

Control flow: registration builds one template per entry in `skcipher_def[]`; AES algorithms get fallback transforms and larger request contexts, while DES/3DES do not. Hardware register setup in `common.c` uses flags and transform key material.

State and persistence: transform context stores key bytes, key length, and fallback skcipher. Request context stores IV pointer, SG state, result SG/table, crypt length, flags, and fallback request. Module parameter `aes_sw_max_len` controls XTS fallback threshold.

Dependencies and integration: QCE core queue, DMA helpers, common register setup, crypto skcipher fallback API, DES/AES key validation, and module parameter configuration.

Risks and test signals: error path returns `-rctx->dst_nents` for invalid dst count, which turns a negative error into a positive value. AES-192 setkey stores fallback key but leaves hardware key copy empty by design because requests must fallback. Test AES/DES/3DES vectors, CTR IV update, XTS sector-size constraints and module parameter, AES-192 fallback, invalid key rejection, in-place/diff-dst SGs, DMA-map failures, and status error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/skcipher.c -->
