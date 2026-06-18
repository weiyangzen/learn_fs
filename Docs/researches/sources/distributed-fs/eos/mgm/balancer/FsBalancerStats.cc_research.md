## sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.cc

Purpose: implements cached balancer statistics used by `FsBalancer` to decide which groups and filesystems are transfer endpoints. `UpdateInfo()` asks `FsView` for groups whose deviation exceeds the configured threshold, compares them against `mGrpToMaxDev`, refreshes group priority sets when deviation changes enough or ten minutes have elapsed, and removes groups that are no longer unbalanced.

Important APIs: `NeedsUpdate()` rate-limits refreshes by `mLastTs`; `GetTxEndpoints()` extracts source and destination sets, preferring `mPrioHigh` to `mHigh` and `mPrioLow` to `mLow`; `HasTxSlot()`, `TakeTxSlot()`, and `FreeTxSlot()` maintain per-node in-flight transfer counts behind `mMutex`.

State and persistence: there is no persistent storage; all state is in-memory caches derived from `FsView`. Dependency signals are `FsView::GetUnbalancedGroups()` and `FsView::GetFsToBalance()`. Risks include mixing `system_clock` for update intervals with `steady_clock` for group refresh age, stale priority sets until update thresholds trigger, and node slot entries staying present at zero. Test signals should cover group add/update/remove, priority fallback, refresh interval boundaries, mutex-protected slot increments/decrements, and missing node IDs.
