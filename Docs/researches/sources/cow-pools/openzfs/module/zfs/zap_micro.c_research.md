# File Research: sources/cow-pools/openzfs/module/zfs/zap_micro.c

## Summary
Implements micro-ZAP handling: compact single-block ZAP objects, their in-memory B-tree index, conversion to fat-ZAP, byte swapping, entry insertion, and normalization-conflict checks.

## Main Responsibilities
- Computes the effective maximum micro-ZAP block size, including `large_microzap` gating.
- Byteswaps on-disk micro-ZAP blocks.
- Builds and maintains an in-memory B-tree of micro-ZAP entries keyed by hash and collision differentiator.
- Opens ZAP dmu buffers as either micro-ZAP or fat-ZAP objects.
- Creates micro-ZAP blocks and upgrades them to fat-ZAP when needed.
- Adds entries and detects Unicode normalization conflicts.

## Key APIs
- `zap_get_micro_max_size()`
- `mzap_byteswap()`
- `mzap_open()`
- `mzap_upgrade()`
- `mzap_create_impl()`
- `mze_find()`, `mze_destroy()`
- `mze_canfit_fzap_leaf()`
- `mzap_normalization_conflict()`
- `mzap_addent()`

## Important Behavior
Micro-ZAP entries are indexed in memory using only the upper 32 bits of the ZAP hash plus the on-disk `mze_cd` collision differentiator. `mze_find()` walks all same-hash entries and calls `zap_match()` to handle exact or normalized matching.

`mzap_upgrade()` copies the old micro-ZAP block, optionally changes object block size, destroys the micro index, initializes fat-ZAP state, and reinserts every micro-ZAP entry with its original collision differentiator.

`mzap_create_impl()` creates a micro-ZAP header by default, but immediately upgrades when fat-ZAP-only flags are requested.

## State and Synchronization
Most mutating operations assert the ZAP rwlock is held as writer. `mzap_open()` installs `zap_t` as the DMU buffer user and handles races by freeing the loser object if another opener already installed one.

## Risks
The upgrade path assumes reinsertion cannot fail; failure would lose entries, so it uses `VERIFY0()`. Hash/collision ordering depends on `mze_cd` matching physical storage. Large micro-ZAP support must stay aligned with block-size limits, send/receive expectations, and the `uint16_t` chunk id limit.
