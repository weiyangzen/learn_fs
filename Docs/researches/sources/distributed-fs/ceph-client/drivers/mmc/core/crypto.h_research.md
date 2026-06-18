# sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.h

## Purpose
Declares MMC inline encryption helpers and no-op stubs when crypto support is disabled.

## Important APIs, Types, And Functions
- Real declarations for `mmc_crypto_set_initial_state()`, `mmc_crypto_setup_queue()`, and `mmc_crypto_prepare_req()` under `CONFIG_MMC_CRYPTO`.
- Empty inline stubs otherwise.

## Control Flow
Core and block paths call helpers unconditionally; the preprocessor selects real or no-op implementations.

## State And Persistence
No header-owned state. Controls whether host/request crypto fields are touched.

## Dependencies And Integration Points
Forward declares host, queue request, and request queue structures; integrates core/block setup with optional `crypto.c`.

## Risks And Edge Cases
No-op stubs must preserve non-crypto behavior. Prototype drift breaks crypto builds.

## Test Signals
Compile with `CONFIG_MMC_CRYPTO=y/n`; encrypted I/O validates real path and ordinary I/O validates stubs.
