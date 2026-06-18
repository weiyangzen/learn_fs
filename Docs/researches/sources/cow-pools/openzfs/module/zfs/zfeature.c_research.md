# File Research: sources/cow-pools/openzfs/module/zfs/zfeature.c

## Summary
Implements SPA feature-flag persistence, compatibility checks, enablement, refcount changes, and enabled-TXG tracking.

## Main Responsibilities
- Checks active feature support for read or write opens.
- Retrieves feature refcounts from the in-memory cache or MOS ZAP objects.
- Enables features and their dependencies.
- Updates feature refcounts in syncing context.
- Creates feature ZAP objects during pool creation or upgrade.
- Tracks activation/deactivation of MOS features.
- Records feature enable TXG when the `enabled_txg` feature is active.

## Key APIs
- `spa_features_check()`
- `feature_get_refcount()`
- `feature_get_refcount_from_disk()`
- `feature_sync()`
- `feature_enable_sync()`
- `spa_feature_create_zap_objects()`
- `spa_feature_enable()`
- `spa_feature_incr()`, `spa_feature_decr()`
- `spa_feature_is_enabled()`, `spa_feature_is_active()`
- `spa_feature_enabled_txg()`

## Important Behavior
Enabled features are stored in either `features_for_read` or `features_for_write` depending on readonly compatibility, plus descriptions in `feature_descriptions`. Refcount zero means enabled but inactive; nonzero means active.

`feature_enable_sync()` recursively enables dependencies, stores the description, initializes the refcount, optionally records the enabling TXG, handles encryption errata cleanup for `bookmark_v2`, and upgrades the error log when `head_errlog` is enabled.

## State and Synchronization
Refcount updates require syncing context and hold `spa_feat_stats_lock`. The in-memory `spa_feat_refcount_cache` is kept in sync with on-disk ZAP state for normal registered features.

## Risks
Feature refcounts are on-disk compatibility state; incorrect increments or decrements can make pools appear unsupported or writable when they are not. `feature_sync()` is also used by `zhack`, which can pass pseudo-features with `SPA_FEATURE_NONE`.
