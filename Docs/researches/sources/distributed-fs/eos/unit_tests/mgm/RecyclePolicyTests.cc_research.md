# sources/distributed-fs/eos/unit_tests/mgm/RecyclePolicyTests.cc

## Purpose
Tests recycle-bin policy enforcement and configuration parsing. It validates watermark derivation from quota stats, within-limit checks, and accepted/rejected policy config values.

## Important APIs, types, and functions
The tests use a `MockRecyclePolicy` overriding `GetQuotaStats()` and `StoreConfig()`. Covered members include `RefreshWatermarks`, `IsWithinLimits`, `Config`, `mEnforced`, `mLowInodeWatermark`, `mLowSpaceWatermark`, `mSpaceKeepRatio`, `mKeepTimeSec`, `mCollectInterval`, `mRemoveInterval`, and `mDryRun`.

## Control flow
No-limit and quota-limit tests feed quota maps using `SpaceQuota` keys and assert derived low watermarks and limit status. Config tests toggle enforcement, keep time, ratio, collection/removal intervals, dry-run mode, invalid values, and reset behavior.

## State and persistence
State is in-memory atomic policy fields. `StoreConfig()` is mocked; production policy changes persist to MGM configuration.

## Dependencies and integration points
Depends on Google Test/Mock, recycle policy internals, quota key constants, and maps. It integrates with recycle cleanup scheduling and quota-aware retention.

## Risks and test signals
The tests cover important policy toggles. Risks include floating-point ratio comparisons, enforcement state interactions after invalid config, quota maps missing some keys, and mocked persistence hiding storage failures beyond `StoreConfig()` returning false.
