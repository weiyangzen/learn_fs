# sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr.go

## Purpose
CNI manager that gates pod networking on CNI plugin readiness, monitors health, notifies waiters, and defers GC until ready.

## Important APIs, Types, and Functions
Types: PodNetworkLister, CNIManager, errShutdown. New initializes ocicni plugin and poll goroutine. pollUntilReady, pollContinuously, statusPollFunc handle startup and continuous status. ReadyOrError, Plugin, AddWatcher, Shutdown, GC, doGC expose readiness/plugin lifecycle.

## Control Flow
Startup polls every 500ms until StatusWithContext succeeds, then clears lastError, runs deferred GC, and notifies watchers. Optional continuous monitoring polls every 5s and applies gracePeriod before marking unhealthy. Shutdown cancels context and notifies pending watchers false. GC stores validPodList and runs immediately only when ready.

## State and Persistence
In-memory mutable state protected by RWMutex: lastError, watcher channels, firstFailureTime, validPodList. External state is CNI plugin resources cleaned by GC.

## Dependencies
Depends on github.com/cri-o/ocicni, Kubernetes wait utilities, context/time, logrus.

## Integration Points
Used by CRI-O server to report NetworkReady, block pod creation until CNI ready, expose plugin operations, and clean stale pod network resources.

## Risks and Edge Cases
Watcher channels can receive true right before shutdown by design; continuous monitoring disabled when gracePeriod<=0; health depends on plugin StatusWithContext implementation; GC valid list errors defer cleanup failure.

## Test Signals
cnimgr_test.go exists outside this subset and covers status polling, watchers, shutdown, GC, and grace period behavior.
