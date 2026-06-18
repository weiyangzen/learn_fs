# File Research: sources/block-storage/linux-dm/drivers/md/bcache/features.c

## Purpose
Converts bcache superblock feature bits into human-readable compatibility, read-only compatibility, and incompatibility strings.

## Main Interfaces
- Feature table with the incompat feature `BCH_FEATURE_INCOMPAT_LOG_LARGE_BUCKET_SIZE` rendered as `large_bucket`.
- `bch_print_cache_set_feature_compat()`.
- `bch_print_cache_set_feature_ro_compat()`.
- `bch_print_cache_set_feature_incompat()`.

## Control Flow
The `compose_feature_string(type)` macro iterates the feature table, filters by compatibility class, prints each known feature name, and surrounds enabled features with brackets. The three public functions bind that macro to compat, ro-compat, or incompat feature namespaces.

## State And Synchronization
No locking. It reads `c->cache->sb` feature fields and writes into the caller-provided buffer.

## Integration Points
Depends on feature macros from `features.h` and superblock/cache-set definitions from `bcache_ondisk.h` and `bcache.h`. Used by sysfs or diagnostics that expose cache-set feature flags.

## Notable Behaviors
- Unknown feature bits are not rendered here; only entries in `feature_list` are printed.
- The output format uses bracketed names for enabled known features and bare names for disabled known features.

## Risks And Review Focus
- `snprintf(out, buf + size - out, ...)` relies on careful pointer arithmetic; callers must pass a valid positive buffer size.
- Any new feature bit needs an entry in `feature_list` to be visible through this formatter.
