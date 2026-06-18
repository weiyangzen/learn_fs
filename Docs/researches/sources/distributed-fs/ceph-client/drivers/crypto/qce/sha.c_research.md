<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.c

Purpose: implements QCE SHA1/SHA256 and HMAC-SHA1/HMAC-SHA256 ahash algorithms with streaming state, DMA result dumps, export/import, and HMAC key preprocessing.

Important APIs and functions: `qce_ahash_init()` seeds standard digest IV and flags. `qce_ahash_update()` buffers incomplete blocks, chains prior buffered bytes with current SG data, holds back one final block, and enqueues hardware work for block-aligned chunks. `qce_ahash_final()` sends the held buffer as the last block or returns zero-message hashes. `qce_ahash_digest()` handles one-shot requests. `qce_ahash_done()` reads result digest and byte count, restores request fields, and completes. `qce_ahash_hmac_setkey()` hashes long HMAC keys using QCE itself.

Control flow: hardware submissions map source SGs plus a result buffer SG, prepare DMA, issue pending, and program registers through `qce_start()`. Register setup in `common.c` uses first/last flags, digest, byte counts, and auth key fields. Registration creates templates from `ahash_def[]`.

State and persistence: request context persists buffer, temporary SG chain, digest, byte counts, total count, first/last flags, original request fields, auth key pointer, and result SG. Transform context stores padded HMAC key. Export/import serializes enough request state for pause/resume.

Dependencies and integration: QCE core queue, DMA helpers, common register setup, SHA constants, crypto wait helpers for long HMAC key hashing, and zero-message hash constants.

Risks and test signals: update logic intentionally holds back a block on exact multiples to let final set last-block state. Using `sg_dma_len()` before DMA mapping in length traversal is suspicious because update has not mapped yet. Test streaming chunk boundaries, exact block multiples, zero-length final/digest, import/export, HMAC long keys, DMA-map errors, and concurrent queued requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.c -->
