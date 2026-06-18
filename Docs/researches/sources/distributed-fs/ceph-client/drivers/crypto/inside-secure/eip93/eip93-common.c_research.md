# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.c

## Purpose
Provides the core shared EIP93 descriptor, scatterlist, SA record, DMA, result cleanup, and HMAC precomputation logic used by skcipher, AEAD, and hash frontends.

## Important APIs, Types, and Functions
Public functions are `eip93_parse_ctrl_stat_err()`, `eip93_put_descriptor()`, `eip93_get_descriptor()`, `check_valid_request()`, `eip93_set_sa_record()`, `eip93_send_req()`, `eip93_unmap_dma()`, `eip93_handle_result()`, and `eip93_hmac_setkey()`.

Private ring helpers advance command/result read/write pointers. Scatterlist helpers create/free bounce SGs and validate 4-byte/block alignment. `eip93_scatter_combine()` splits mapped scatterlists into one or more EIP93 descriptors. `eip93_hmac_setkey()` computes ipad/opad digests using the EIP93 hash algorithms through the Linux ahash API.

## Control Flow
Request validation computes total source/destination sizes, derives SG entry counts, and creates bounce buffers when alignment or AEAD multi-entry constraints cannot be met. Submission builds SA state from the request IV, handles RFC3686 IV layout, handles 32-bit CTR overflow by splitting work with a second state, maps SA state and SGs, allocates a 16-bit async IDR entry, and calls `eip93_scatter_combine()`. Each descriptor is placed into CDR/RDR under the ring write lock; if rings are full, it sleeps briefly and retries. Writing `EIP93_REG_PE_CD_COUNT` starts DMA.

Completion unmaps SGs, copies bounce-buffer output back to the original destination, converts non-MD5 auth tags to host order, unmaps/copies final IV state, and frees per-request state. Hardware control/status errors are translated to Linux errors such as `-EBADMSG`, `-EIO`, `-EACCES`, or `-EINVAL`.

## State and Persistence
The file manages ring pointer state inside `struct eip93_ring`, IDR mappings from hardware-visible IDs to `crypto_async_request`, transient bounce buffers, DMA mappings, and per-request SA state. No durable persistence exists. SA records supplied by frontends are transform state but are programmed here.

## Dependencies and Integration Points
Depends on `eip93-regs.h` bitfields, `eip93-main.h` ring/device definitions, and the Linux DMA/scatterlist/crypto APIs. It is invoked by AEAD/skcipher frontends and by HMAC setup in both AEAD and hash code.

## Risks
Ring full handling is a busy sleep/retry loop with no timeout, so hardware stalls can pin callers. `idr_alloc()` return is not checked before being packed into the descriptor user ID. Bounce buffer allocation uses `GFP_KERNEL | GFP_DMA`, which can fail under pressure and may constrain memory placement. The CTR overflow split path uses 32-bit DMA address fields and hardware state assumptions. Error cleanup paths must match every DMA map and bounce allocation, making DMA API debug testing important.

## Test Signals
Use DMA API debug, KASAN, and crypto stress vectors for multi-SG in-place/out-of-place requests, unaligned offsets, AEAD tag conversion, CTR counter wrap near `0xffffffff`, ring saturation, hardware auth failure, and simulated DMA mapping failures.
