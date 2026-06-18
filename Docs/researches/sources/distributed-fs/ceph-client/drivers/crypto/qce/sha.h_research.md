<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.h

Purpose: declares QCE hash context structures, bounds, template conversion helper, and ops export.

Important types: `struct qce_sha_ctx` stores the padded HMAC key. `struct qce_sha_reqctx` holds pending buffer, temporary buffer, digest, buflen, flags, original source/nbytes, SG count, byte count, total count, first/last block booleans, temporary chained SG entries, auth key pointer/length, and result SG.

Control flow and integration: SHA algorithm code stores all streaming state in `qce_sha_reqctx`; common register setup reads the same fields when programming SHA/HMAC/CMAC auth segments. `to_ahash_tmpl()` recovers the QCE template from a crypto transform, and `ahash_ops` is exported to core registration.

State and persistence: request context is export/import capable and persists across update/final calls. Transform context persists HMAC key material.

Dependencies: scatterwalk, SHA1/SHA2 constants, QCE common/core headers, and crypto ahash internals.

Risks and test signals: max block/digest sizes are SHA256-bound, so adding SHA512 would require structural changes. Test request-size DMA alignment, export/import state size, HMAC setup, and all update/final paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.h -->
