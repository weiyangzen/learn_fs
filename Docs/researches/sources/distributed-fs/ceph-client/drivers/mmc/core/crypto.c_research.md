# sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.c

## Purpose
MMC inline encryption glue between block-layer crypto and MMC requests for hosts with crypto capability.

## Important APIs, Types, And Functions
- `mmc_crypto_set_initial_state()` reprograms keys after resets.
- `mmc_crypto_setup_queue()` registers the host crypto profile with a request queue.
- `mmc_crypto_prepare_req()` copies request crypto context and keyslot index into `struct mmc_request`.

## Control Flow
Queue setup registers crypto support. Initial-state/reset paths reprogram keys. Block request preparation attaches crypto metadata before host submission.

## State And Persistence
No key ownership here. It references `host->crypto_profile`, request crypto contexts, and block crypto keyslots. Hardware keyslots persist until reset/reprogramming.

## Dependencies And Integration Points
Depends on `CONFIG_MMC_CRYPTO`, `linux/blk-crypto.h`, MMC host definitions, and MMC queue/request structures.

## Risks And Edge Cases
If reset clears keys and reprogramming is skipped, encrypted I/O can fail or use invalid slots. Non-crypto requests must remain unchanged. Host capability bits must be accurate.

## Test Signals
Build with `MMC_CRYPTO` and `BLK_INLINE_ENCRYPTION`; encrypted I/O across reset/resume; correct keyslot indices; unchanged unencrypted I/O.
