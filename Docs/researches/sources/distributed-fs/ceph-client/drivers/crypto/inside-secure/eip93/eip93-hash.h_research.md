# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-hash.h

## Purpose
Defines EIP93 hash transform/request/export structures and declares hash algorithm templates plus the result callback.

## Important APIs, Types, and Functions
`struct eip93_hash_ctx` stores the EIP93 device, algorithm flags, and precomputed HMAC ipad/opad buffers. `struct eip93_hash_reqctx` contains DMA-aligned SA records/state, DMA addresses, finalize/partial flags, byte counters, a 64-byte cache, and a list of queued full hash blocks. `struct mkt_hash_block` stores one DMA-mapped 64-byte block. `struct eip93_hash_export_state` is the crypto API export/import format.

The header declares `eip93_hash_handle_result()` and extern templates for MD5, SHA1, SHA224, SHA256, and HMAC variants.

## Control Flow
`eip93-hash.c` allocates the request context through `crypto_ahash_set_reqsize_dma()`, fills these structures during update/final, and the EIP93 core calls the result handler when a hash LAST descriptor completes.

## State and Persistence
The export state stores hash length, EIP93 byte counters, intermediate digest, and cached partial block for in-memory suspend/resume of a hash request. DMA fields are transient and valid only during active hardware submission.

## Dependencies and Integration Points
Includes SHA2 sizing constants and EIP93 core/register definitions. The structs are tightly coupled to EIP93 SA record/state layout and CRYPTO DMA alignment requirements.

## Risks
Structure layout matters for DMA alignment and hardware interpretation. Changing fields before the aligned SA record block or altering buffer sizes can break DMA or export/import compatibility. Only SHA256-sized state buffers are stored, which matches the supported hashes but constrains extension.

## Test Signals
Compile with `CONFIG_CRYPTO_MANAGER_EXTRA_TESTS`, exercise export/import on every declared algorithm, and run with DMA alignment/debug instrumentation.
