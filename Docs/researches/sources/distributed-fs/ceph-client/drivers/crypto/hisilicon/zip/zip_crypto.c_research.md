# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_crypto.c

## Purpose
This file registers HiSilicon ZIP hardware as asynchronous compression algorithms for the Crypto API. It supports hardware deflate compression/decompression and lz4 compression, with software fallback for initialization failures and lz4 decompression.

## Important APIs, Types, And Functions
Exported-to-module functions are `hisi_zip_register_to_crypto()` and `hisi_zip_unregister_from_crypto()`. The async compression algorithms are `hisi_zip_acomp_deflate` and `hisi_zip_acomp_lz4`. Internal request state is split across `struct hisi_zip_ctx`, two `struct hisi_zip_qp_ctx` entries for compression and decompression queues, per-queue `struct hisi_zip_req_q` arrays plus bitmaps, and per-request `struct hisi_zip_req`.

Descriptor operations are abstracted by `struct hisi_zip_sqe_ops`, currently implemented by `hisi_zip_ops` for SQE type 3. `hisi_zip_fill_sqe()` writes source/destination addresses, input/output lengths, SGL buffer type, request type, 16K window size, request pointer tag, and SQE type. Completion uses `GET_REQ_FROM_SQE()` to recover the request pointer.

## Control Flow
Algorithm init creates two QPs using `zip_create_qps()`, initializes request queues, creates SGL pools sized at `q_depth << 1`, and sets QP completion callbacks. A compression request allocates a free request ID from the bitmap, maps source and destination scatterlists into hardware SGLs using the shared HiSilicon SGL helper, fills an SQE, and submits it with `hisi_qp_send()`. Completion checks status, unmaps both SGLs, updates `acomp_req->dlen` from produced length, completes the request, and frees the request ID.

If QP creation or resource setup fails in init, the context sets `fallback = true` and init still succeeds. Fallback requests use `ACOMP_FBREQ_ON_STACK()` and call the software Crypto API algorithm. LZ4 decompression always falls back through `hisi_zip_decompress()`.

## State And Persistence
Global algorithm registration is tracked by `zip_algs_lock` and `zip_available_devs`. Per-transform state owns QPs, bitmaps, request arrays, SGL pools, and the fallback flag. Per-device DFX counters count sends, receives, send-busy events, and bad descriptors. No state persists across module unload.

## Dependencies And Integration Points
The file depends on Crypto API `acompress`, HiSilicon QM queue submission, HiSilicon SGL pool helpers, DMA mapping through those helpers, and ZIP capability checks in `zip_main.c`. It registers algorithms only if `hisi_zip_alg_support()` finds the relevant hardware bits.

## Risks
Request pointer tags are split into two 32-bit SQE fields; this assumes pointer round-trip is valid for the target architecture. Request queue exhaustion returns `-EAGAIN`. Hardware status `HZIP_NC_ERR` is treated as non-fatal, so callers must interpret produced data correctly. The fallback path uses stack fallback requests and copies only `dlen`; callback semantics must match the async caller expectation. Resource cleanup must match init failure stages to avoid leaking QPs, bitmaps, or SGL pools.

## Test Signals
Run Crypto API acomp tests for deflate compress/decompress and lz4 compress; check lz4 decompression fallback. Exercise zero or missing src/dst/slen/dlen rejection, request bitmap exhaustion, too many SGL entries via `sgl_sge_nr`, hardware nonzero status, `HZIP_NC_ERR`, and init fallback when QP allocation fails. Debugfs DFX counters should reflect send/receive/busy/error paths.
