# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.h

## Purpose
Defines shared transform and request context structures for EIP93 skcipher and AEAD operations, plus the common cipher request API used across EIP93 files.

## Important APIs, Types, and Functions
`struct eip93_crypto_ctx` stores the device pointer, algorithm flags, SA record pointer/DMA address, block size, RFC3686 nonce, AEAD auth and association sizes, `set_assoc`, and algorithm type. `struct eip93_cipher_reqctx` stores descriptor flags, direction/mode flags, sizes, SA/state DMA addresses, scatterlist pointers, mapped entry counts, and optional CTR-overflow state.

Declared functions include `check_valid_request()`, `eip93_unmap_dma()`, `eip93_skcipher_handle_result()`, `eip93_send_req()`, and `eip93_handle_result()`.

## Control Flow
AEAD and skcipher frontends fill `eip93_cipher_reqctx`, then call `check_valid_request()` and `eip93_send_req()`. The interrupt path calls the relevant result handler, which uses `eip93_unmap_dma()` and `eip93_handle_result()` before completing the crypto request.

## State and Persistence
The structures describe in-memory crypto transform/request state only. DMA addresses are valid only between submission and completion. The same transform context can be reused across requests and therefore carries key/SA/AAD-related state.

## Dependencies and Integration Points
Includes `eip93-main.h` for device, algorithm type, flags, descriptors, and SA state definitions. It is the coupling point between `eip93-aead.c`, `eip93-cipher.c`, `eip93-common.c`, and `eip93-main.c`.

## Risks
The request context owns pointers to either caller scatterlists or bounce scatterlists, so cleanup must compare against original request lists correctly. DMA address fields are not self-validating; unmap paths assume successful map paths and descriptor completion ordering.

## Test Signals
Look for DMA API debug warnings under skcipher and AEAD stress tests, especially in-place, out-of-place, unaligned, and multi-SG requests.
