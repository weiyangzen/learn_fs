## sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.hh

Purpose: declares the balancer statistics cache. It defines `BalancePair` and `VectBalanceFs`, then exposes `FsBalancerStats` as a `LogId`-derived helper for group deviation caching and node transfer slot accounting.

Important APIs/types: constructor binds a space name and initializes `mLastTs`; `UpdateInfo(FsView*, double)`, `NeedsUpdate(seconds)`, `GetTxEndpoints()`, `TakeTxSlot()`, `FreeTxSlot()`, and `HasTxSlot()`. The class stores `mGrpToMaxDev` as group to `(deviation, steady_clock timestamp)`, `mGrpToPrioritySets` as group to `FsPrioritySets`, and `mNodeNumTx` as node identifier to active transfer count.

Integration: depends on `mgm/fsview/FsView.hh` for `FsBalanceInfo` and priority sets, and is consumed by `FsBalancer`. Constants `sGrpDevUpdThreshold=0.25` and `sGrpUpdTimeThreshold=10` minutes define cache refresh sensitivity. Risks include coarse refresh constants and private state becoming public under `IN_TEST_HARNESS`. Tests should construct synthetic `FsView` results or harness-access maps to verify endpoint ordering, cache invalidation, and slot-limit behavior.
