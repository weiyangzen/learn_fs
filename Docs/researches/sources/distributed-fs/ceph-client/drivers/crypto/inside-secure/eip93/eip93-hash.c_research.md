# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.c

## Purpose
Implements EIP93 asynchronous hash and HMAC algorithms for MD5, SHA1, SHA224, and SHA256.

## Important APIs, Types, and Functions
Exports `eip93_hash_handle_result()` for result dispatch. Crypto API callbacks include `eip93_hash_init()`, `eip93_hash_update()`, `eip93_hash_final()`, `eip93_hash_finup()`, `eip93_hash_digest()`, `eip93_hash_export()`, `eip93_hash_import()`, and HMAC `eip93_hash_hmac_setkey()`. Algorithm templates are defined for plain and HMAC variants.

`__eip93_hash_init()` programs hash SA records and creates a second HMAC SA record so CMD_HMAC is enabled only on the final block. `eip93_send_hash_req()` maps data blocks, fills descriptors, allocates an async IDR only for the last descriptor, and starts DMA.

## Control Flow
Initialization seeds `sa_state` digest constants and, for HMAC, prepends the precomputed ipad block to request data. Update accumulates data in 64-byte blocks, allocates `mkt_hash_block` nodes, and submits full blocks. With `complete_req`, the last queued full block gets the async IDR and returns `-EINPROGRESS`; otherwise finup can queue intermediate blocks and let final submit the completing descriptor. Final handles the EIP93 zero-length hash limitation in software for plain hashes, sets `finalize`, maps SA state/record when needed, and submits the trailing data buffer as the last descriptor. Completion unmaps state, swaps non-MD5 digest words to CPU order, copies results, frees SA records and block DMA mappings, and completes the ahash request.

## State and Persistence
Per-transform state is `struct eip93_hash_ctx`, including flags and HMAC ipad/opad. Per-request state is DMA-aligned `struct eip93_hash_reqctx`, including SA records, SA state, block list, cached partial block, length counters, and finalize/partial flags. Export/import persists a hash operation into an in-memory `eip93_hash_export_state`, not to disk.

## Dependencies and Integration Points
Uses `eip93_set_sa_record()` and `eip93_hmac_setkey()` from common code, EIP93 ring descriptor APIs, Linux ahash crypto API, digest constants from crypto headers, and result dispatch from `eip93-main.c`.

## Risks
Hardware cannot handle zero-length plain hashes, requiring software constants; HMAC zero-length goes through hardware because ipad data exists. The block list is submitted in reverse list order after `list_add()`, which preserves original input order but is easy to break if list handling changes. DMA unmap sizes are fixed at `SHA256_BLOCK_SIZE` for full blocks. HMAC finalization depends on using a duplicate SA record only for the last descriptor. Async IDR allocation is not visibly checked in the submission helper.

## Test Signals
Run ahash KATs for zero-length and multi-block MD5/SHA1/SHA224/SHA256 and HMAC variants, export/import mid-stream, finup versus update+final equivalence, keys longer than block size, SHA224 partial digest handling, and request cancellation/removal stress under DMA debug.
