# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec.h

## Purpose
`sec2/sec.h` is the private shared header for the newer HiSilicon SEC2 crypto driver. It defines per-request buffers, hardware SGL layout, skcipher/AEAD request state, per-QP resource state, transform context, debug counters, capability table enums, and exported helper prototypes that connect SEC2 crypto code to the shared QM driver.

## Important APIs, types, and functions
Important structures include `struct sec_alg_res`, `struct sec_hw_sge`, `struct sec_hw_sgl`, `struct sec_src_dst_buf`, `struct sec_request_buf`, `struct sec_cipher_req`, `struct sec_aead_req`, `struct sec_req`, `struct sec_req_op`, `struct sec_auth_ctx`, `struct sec_cipher_ctx`, `struct sec_qp_ctx`, `struct sec_ctx`, `struct sec_debug`, and `struct sec_dev`. Capability enums `sec_cap_type` and `sec_cap_table_type` map SEC/QM capability table slots. Helper prototypes are `sec_destroy_qps()`, `sec_create_qps()`, and `sec_get_alg_bitmap()`.

## Control flow
The header defines the operation vector `struct sec_req_op`: request processing maps buffers, fills a SEC SQE, sends it to a QM queue pair, unmaps buffers, and invokes completion callbacks. `struct sec_ctx` chooses queues by separate encrypt/decrypt cyclic counters and stores algorithm type, fallback state, pbuf support, and cipher/auth contexts. `struct sec_qp_ctx` tracks one QM queue pair, request ID allocation, request list, per-queue DMA resources, and SGL pools.

## State and persistence behavior
All state is runtime-only. Per-QP state tracks `hisi_qp`, IDR request IDs, send head, request array, SGL pools, and DMA buffers. Per-transform state tracks keys, IV sizes, fallback crypto transforms, algorithm support flags, and selected request operations. `struct sec_debug` contains atomic counters for send/receive/busy/error/invalid/done statistics. No on-disk persistence exists.

## Dependencies and integration points
The header depends on `linux/hisi_acc_qm.h` for QM queue types and on `sec_crypto.h` for SEC SQE formats. It also depends on Linux crypto skcipher/AEAD/shash types, IDR, spinlocks, atomics, and DMA addresses. It integrates SEC2 with the shared QM implementation in `qm.c`; `struct sec_dev` embeds `struct hisi_qm`.

## Risks and edge cases
Alignment of `struct sec_hw_sgl` is fixed at 64 bytes and must remain hardware-compatible. The union in `struct sec_request_buf` overlays SGL buffers with a 512-byte pbuf, so `use_pbuf` decisions must be correct. The request IDR/list must be protected by the documented locks to prevent completion/use-after-free races. Fallback flags mean behavior can diverge between hardware and software paths. Capability bitmap enums must match hardware tables used by SEC2 main code.

## Test signals
Build coverage with SEC2 enabled, skcipher and AEAD crypto selftests, hardware and fallback path tests, pbuf and SGL path tests, request ID exhaustion, completion error counters, queue creation/destruction, capability bitmap decoding, and reset/stop interaction through embedded `hisi_qm` are the key signals.
