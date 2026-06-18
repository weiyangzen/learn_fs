# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.h

## Purpose

`cc_hash.h` defines the shared hash request state and exported hash/SRAM helper interfaces used by the CryptoCell hash implementation and other ccree modules. It is the contract between `cc_hash.c`, buffer mapping code, and AEAD code that needs hash larval and digest-length SRAM addresses.

## Important APIs, Types, And Functions

Constants define HMAC pad words, hardware digest-length sizes for older and newer revisions, maximum digest/block sizes, XCBC derived-key offsets, and `CC_EXPORT_MAGIC` for import/export validation. `struct aeshash_state` mirrors the state shape used for AES-XCBC/CMAC state size accounting. `struct ahash_req_ctx` stores all per-request buffers, DMA addresses, scatterlist state, MLLI metadata, double-buffer counts, and the XCBC update count.

Inline helpers `cc_hash_buf_cnt()`, `cc_hash_buf()`, `cc_next_buf_cnt()`, and `cc_next_buf()` select the current or alternate partial-block buffer based on `buff_index`. Exported functions are `cc_hash_alloc()`, `cc_init_hash_sram()`, `cc_hash_free()`, `cc_digest_len_addr()`, and `cc_larval_digest_addr()`.

## Control Flow

The header has no executable control flow beyond inline buffer selectors. Its definitions are consumed when crypto transforms set request DMA size, when buffer manager code fills partial blocks and MLLI tables, and when hash descriptors load or write state.

## State And Persistence Behavior

`struct ahash_req_ctx` is per asynchronous hash request, not persistent beyond the request unless exported through the crypto API. Its aligned buffers are DMA-facing and include digest result, current digest state, HMAC outer digest, digest byte count, and partial input blocks. The SRAM address helpers refer to device SRAM state initialized elsewhere.

## Dependencies And Integration Points

The header includes `cc_buffer_mgr.h`, so it shares `async_gen_req_ctx`, `mlli_params`, and DMA buffer type definitions. It depends on Linux crypto constants for AES and SHA sizes. It is included by `cc_hash.c`, AEAD setup code, and request/buffer paths that operate on hash request state.

## Risks And Edge Cases

Changing maximum digest or block sizes affects DMA mapping sizes, crypto statesize, and export/import layout. `CC_EXPORT_MAGIC` protects only against obvious format mismatch, not against mode mismatch. The double-buffer helpers assume `buff_index` is always 0 or 1. `xcbc_count` is used to distinguish empty, partial, and full-block MAC finalization cases.

## Test Signals

Compile coverage should catch structure/member contract breaks across `cc_hash.c` and `cc_buffer_mgr.c`. Runtime signals include successful hash export/import, fragmented update/final tests that switch buffers, and AES-XCBC/CMAC tests with empty input, one full block, and partial final blocks.
