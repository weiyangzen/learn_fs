# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.c

## Purpose
This file registers HiSilicon SEC v2/v3 hardware acceleration with the Linux Crypto API for asynchronous skcipher and AEAD transforms. It bridges `crypto_skcipher` and `crypto_aead` requests into SEC queue-manager SQEs, handles DMA mapping of scatterlists or small packet buffers, validates hardware result descriptors, and falls back to software transforms when a request is unsupported, too large, or cannot safely be submitted to hardware.

## Important APIs, Types, And Functions
The exported entry points are `sec_register_to_crypto(struct hisi_qm *qm)` and `sec_unregister_from_crypto(struct hisi_qm *qm)`, called by `sec_main.c` through `hisi_qm_alg_register()` and `hisi_qm_alg_unregister()`. Registration is guarded by `sec_algs_lock` and `sec_available_devs`, so Crypto API algorithms are registered only once while multiple SEC devices may exist.

Core local types include `struct sec_skcipher` and `struct sec_aead`, wrappers around Crypto API algorithm descriptors plus hardware capability masks. `struct sec_req`, `struct sec_ctx`, `struct sec_qp_ctx`, and resource types are defined in `sec.h` and are used here to store per-request SQEs, DMA resources, queue IDs, fallback transforms, and algorithm state.

The key setup path is `sec_skcipher_setkey()` for AES, SM4, 3DES, CTR/CBC/ECB/XTS modes, and `sec_aead_setkey()` for CCM/GCM plus authenc HMAC-SHA CBC modes. `sec_skcipher_soft_crypto()` and `sec_aead_soft_crypto()` are software fallback paths. Descriptor builders are split by algorithm and hardware generation: `sec_skcipher_bd_fill()` and `sec_aead_bd_fill()` build type2 descriptors; `sec_skcipher_bd_fill_v3()` and `sec_aead_bd_fill_v3()` build type3 descriptors. `sec_process()` is the common submit path.

## Control Flow
Crypto API init allocates queue pairs through `sec_create_qps()`, creates per-queue request/resource pools, allocates DMA key/IV/MAC buffers, and chooses type2 or type3 `sec_req_op` callbacks from the QM hardware version. Request submission validates lengths and modes, decides whether pbuffer optimization is usable, assigns a request ID, maps buffers, copies IV state, fills an SQE, and sends it with `hisi_qp_send()`.

Completion flows through `sec_req_cb()` for type2 or `sec_req_cb3()` for type3. Type2 completions recover the request from the SQ message ring/tag index, while type3 completions carry a request pointer in the descriptor tag. Both parse done/ICV/flag/error fields, unmap buffers, update debug counters, and call the skcipher or AEAD callback. Backlogged requests are drained after each completion.

## State And Persistence
State is in memory only. Per-transform state includes keys in coherent DMA buffers, fallback tfms, algorithm mode, request operation table, queue contexts, and preallocated pbuffer/IV/MAC/SGL resources sized by queue depth. Request IDs are tracked by per-QP IDR and freed on completion or fallback cleanup. Global registration state is the `sec_available_devs` counter. Sensitive key buffers are cleared with `memzero_explicit()` before DMA free.

## Dependencies And Integration Points
The file depends on the Linux Crypto API, DMA mapping, IDR, scatterlist helpers, and HiSilicon QM APIs. It uses the shared HiSilicon SGL pool exported from `hisi_acc_sg_buf_map_to_hw_sgl()`. It integrates with `sec_main.c` through algorithm capability bitmaps from `sec_get_alg_bitmap()` and queue allocation from `sec_create_qps()`.

## Risks
The main risks are DMA lifetime errors, request ID leaks on rare failure paths, invalid descriptor bit programming, and fallback behavior mismatch. AEAD has extra risk around CCM IV dimension validation, GCM minimum tag size, MAC extraction/copyback, and decrypt ICV handling. Small-packet pbuffer mode shares one DMA buffer for input/output, so copy sizing must stay consistent with authsize and associated data. Type2/type3 split raises compatibility risk when capability probing or QM version checks are wrong.

## Test Signals
Useful signals are Crypto API self-tests for `ecb/cbc/ctr/xts(aes)`, `cbc/ctr/xts(sm4)`, `ecb/cbc(des3_ede)`, `ccm/gcm(aes)`, `ccm/gcm(sm4)`, and authenc HMAC-SHA CBC algorithms. Exercise zero length, non-block-size CBC, XTS minimum length, oversized input fallback, small pbuffer requests, in-place and out-of-place scatterlists, backlog under full SQ, ICV failure on AEAD decrypt, and hardware v2/v3 descriptor paths. Runtime debug counters `send_cnt`, `recv_cnt`, and `done_flag_cnt` should move consistently with completed requests.
