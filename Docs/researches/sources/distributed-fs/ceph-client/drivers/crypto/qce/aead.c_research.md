<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.c

Purpose: implements QCE AEAD algorithms for authenc HMAC+CBC DES/3DES/AES and AES-CCM/RFC4309 CCM using DMA scatterlist staging plus shared QCE register programming.

Important APIs and functions: `qce_aead_crypt()` sets encrypt/decrypt flags, computes payload length, handles zero-length and fallback cases, validates CBC and RFC4309 constraints, and enqueues. `qce_aead_async_req_handle()` prepares IV/nonce/AAD, builds source and destination SG tables, maps DMA, submits BAM transfers, and calls `qce_start()`. `qce_aead_done()` terminates DMA, unmaps/free SG tables, checks status, copies/generated tags on encrypt, and verifies non-CCM tags on decrypt. Setkey paths parse authenc keys or CCM salt and mark AES-192/weak 3DES fallback.

Control flow: CCM with AAD creates a formatted padded AAD buffer and may replace source/destination SGs. Non-CCM appends the shared result buffer to destination for result dump. Completion copies the tag from either QCE result dump or the CCM side buffer. Registration builds `qce_alg_template` instances from `aead_def[]` and links them in `aead_algs`.

State and persistence: transform context stores encryption/auth keys, RFC4309 salt, authsize, fallback AEAD, and `need_fallback`. Request context owns dynamic AAD allocation, SG tables, result SG, nonce buffers, lengths, flags, and fallback request.

Dependencies and integration: QCE core queue, `qce_dma_prep_sgs()`, `qce_start()` AEAD register setup, crypto authenc/CCM helpers, DMA mapping, scatterwalk, and fallback AEAD algorithms.

Risks and test signals: `rctx->adata` is allocated for CCM AAD but not visibly freed in completion/error paths, a leak risk. Error cleanup differs by CCM/non-CCM and diff-dst/in-place. Decrypt length subtracts authsize and can underflow if caller validation is insufficient. Test authenc and CCM vectors, RFC4309 assoclen 16/20 checks, zero-length fallback, AES-192 fallback, weak 3DES fallback, in-place/diff-dst, AAD/non-AAD CCM, decrypt tag failure `-EBADMSG`, and DMA-map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.c -->
