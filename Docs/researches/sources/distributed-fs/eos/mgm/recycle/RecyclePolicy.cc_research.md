<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.cc -->
# sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.cc

## Purpose
`RecyclePolicy.cc` implements the persistent runtime policy for recycle-bin cleanup. It parses/stores recycle config, exposes formatted dumps, obtains recycle quota statistics, computes low watermarks, and decides whether cleanup can stop because usage has dropped below configured limits.

## Important APIs and functions
- `ApplyConfig(FsView*)` reads the `"recycle"` global config string, tokenizes space-separated `key=value` pairs, tolerates missing values as empty strings, and applies each with `Config()`.
- `StoreConfig()` serializes enable/enforce/keep-time/ratio/collect/remove/dry-run fields back to `FsView::gFsView.SetGlobalConfig("recycle", ...)`.
- `Config(key, value, msg)` parses and applies one key. Supported keys are `recycle-keep-time`, `recycle-ratio`, `recycle-collect-time`, `recycle-remove-time`, `recycle-dry-run`, `recycle-enforce`, and `recycle-enable`; unknown keys are ignored.
- `Dump(delim)` reports current atomic state and watermarks.
- `GetQuotaStats()` returns group/project quota values for `Recycle::gRecyclingPrefix` and `Quota::gProjectId`.
- `RefreshWatermarks()` reads used/max logical bytes and files, skips updates while below the configured ratio, otherwise sets low watermarks to `(ratio - 0.1) * max`.
- `IsWithinLimits()` checks current recycle quota stats against low watermarks and returns true once either inode or space usage is below its low watermark; with no ratio or no stats, it returns false so time-based cleanup may continue.

## Control flow
On recycler startup, `Recycle::Recycler()` calls `ApplyConfig()` to populate atomics from stored FsView config. User config commands call `RecyclePolicy::Config()` through `Recycle::Config()`, which updates a value, logs a dump, and immediately stores the full config string. During cleanup, `RefreshWatermarks()` is called before collection/removal when a ratio is configured; `RemoveEntries()` periodically calls `IsWithinLimits()` and stops deleting when usage is low enough.

## State and persistence
Runtime state is stored in atomics: enabled, enforced, keep time, space keep ratio, dry-run, collect interval, remove interval, low-space watermark, and low-inode watermark. Persistent state is the serialized global `"recycle"` config in FsView. Quota usage is external state read from the quota subsystem.

## Dependencies and integration points
The policy depends on `Recycle` constants, `Quota::GetGroupStatistics`, `SpaceQuota` tag values, `XrdMgmOfs`, `FsView`, and common tokenization/logging. It is owned by the `Recycle` instance and is tested with a mock subclass overriding `GetQuotaStats()` and `StoreConfig()`.

## Risks and edge cases
- `Config()` returns true on empty values before key validation. This is useful for tolerant parsing but can hide malformed config entries.
- Numeric parsing catches all exceptions and returns clear messages, but range checks are mostly performed by `Recycle::Config()`, not here. Direct callers of `RecyclePolicy::Config()` can set unusual intervals or ratios.
- `RefreshWatermarks()` uses `999999999` as a denominator fallback for zero max values; this avoids division by zero but can produce surprising ratio behavior for zero-quota configurations.
- `IsWithinLimits()` returns true if either inode or space watermark is under-run, not necessarily both. This matches the implementation but should be intentional for cleanup stop policy.
- Unknown keys are silently ignored, which helps compatibility but can hide operator typos in raw config.

## Test signals
`sources/distributed-fs/eos/unit_tests/mgm/RecyclePolicyTests.cc` covers no-limit behavior, above/below watermark transitions, valid config parsing, invalid numeric parsing, dry-run toggles, and explicit enforce disable. Additional tests should cover enable key validation, unknown key behavior, empty-value behavior, zero max quota stats, and direct ratio range assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.cc -->
