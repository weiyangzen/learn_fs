<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.hh -->
# sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.hh

## Purpose
`RecyclePolicy.hh` declares the cleanup policy object used by `Recycle`. It defines supported config keys, runtime atomic settings, quota-stat hooks, and policy methods for applying, storing, dumping, and evaluating cleanup thresholds.

## Important APIs and types
- `RecyclePolicy` derives from `eos::common::LogId` and declares `Recycle` as a friend so the recycler can access policy internals.
- Public methods are `ApplyConfig(FsView*)`, virtual `StoreConfig()`, `Config(key, value, msg)`, `RefreshWatermarks()`, `IsWithinLimits()`, virtual `GetQuotaStats()`, and `Dump(delim)`.
- Static key constants define the serialized config contract: keep time, ratio, collect time, remove time, dry-run, enforce, and enable.
- Runtime atomics include `mEnabled`, `mEnforced`, `mKeepTimeSec`, `mSpaceKeepRatio`, `mDryRun`, `mCollectInterval`, `mRemoveInterval`, `mLowSpaceWatermark`, and `mLowInodeWatermark`.
- `IN_TEST_HARNESS` can expose internals publicly for unit tests.

## Control flow and state model
The class is intentionally small and mostly atomic so the recycler thread and config commands can share policy state with minimal locking. `StoreConfig()` and `GetQuotaStats()` are virtual, which enables the existing tests to mock persistence and quota input while exercising parsing and watermark logic.

## Persistence behavior
Persistence is abstracted behind `StoreConfig()` but implemented in the `.cc` file as FsView global config. The header makes the serialized keys stable public constants, so command handlers and tests can refer to the same strings.

## Dependencies and integration points
The declaration depends on MGM namespace definitions, common logging/mapping, namespace `IView`, and atomics. It forward declares `FsView`. It is owned by `Recycle`, called by recycle command handling, and uses quota statistics keyed by `SpaceQuota` tags in the implementation.

## Risks and test signals
Using `std::atomic<double>` for ratio state is straightforward but still requires platform support assumptions. Interval atomics use `std::chrono::seconds`, so any code compiling this header depends on atomic support for that trivially copyable representation. The public key constants and virtual hooks are good test seams; existing `RecyclePolicyTests` already mock the two virtual methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.hh -->
