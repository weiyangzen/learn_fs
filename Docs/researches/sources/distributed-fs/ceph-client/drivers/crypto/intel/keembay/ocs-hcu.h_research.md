# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.h

## Purpose
This header defines the public low-level OCS HCU interface for the Keem Bay hash front end. It declares device/context structures, supported algorithms, DMA-list APIs, hash/HMAC APIs, and the IRQ handler.

## Important APIs, Types, And Functions
- Constants: `OCS_HCU_DMA_BIT_MASK` enforces 32-bit DMA addressing; `OCS_HCU_HW_KEY_LEN` defines the maximum hardware HMAC key register vector.
- `enum ocs_hcu_algo` enumerates SHA256, SHA224, SHA384, SHA512, and SM3 hardware algorithm IDs.
- `struct ocs_hcu_dev` holds device list linkage, device pointer, MMIO base, crypto engine, IRQ state, and error flag.
- `struct ocs_hcu_idata` stores message length and digest/intermediate chain data.
- `struct ocs_hcu_hash_ctx` pairs algorithm selection with intermediate data.
- Public APIs cover DMA list allocation/free/add, streaming hash update/finup/final, one-shot digest, hardware HMAC, and IRQ handling.

## Control Flow
The front end initializes `struct ocs_hcu_dev` during platform probe and embeds `struct ocs_hcu_hash_ctx` in each request context. It then uses the declared APIs to build DMA lists and advance/finalize hardware hash state.

## State And Persistence
The header declares state containers but owns no storage. Intermediate state can be copied/exported by higher layers through `struct ocs_hcu_hash_ctx`.

## Dependencies And Integration Points
It depends on DMA mapping types and SHA512 digest size. It is consumed by both `ocs-hcu.c` and `keembay-ocs-hcu-core.c`.

## Risks
- Consumers must respect the 32-bit DMA mask and initialize completions/IRQ state before invoking low-level operations.
- `struct ocs_hcu_idata` always allocates SHA512-sized digest storage, which is safe for smaller algorithms but requires correct digest-size validation on output.

## Test Signals
- Compile coverage of both HCU objects.
- Runtime coverage for every declared public operation through the Crypto API front end.
