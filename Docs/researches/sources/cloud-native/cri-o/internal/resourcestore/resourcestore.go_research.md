# sources/cloud-native/cri-o/internal/resourcestore/resourcestore.go

Purpose: tracks recently-created resources by name until another CRI-O path retrieves them, while notifying waiters and cleaning up stale unused resources.

Important APIs/types/functions: `ResourceStore`, `Resource`, `IdentifiableCreatable`, `New`, `NewWithTimeout`, `Close`, `Get`, `Put`, `Delete`, `WatcherForResource`, `SetStageForResource`, `StageUnknown`, and the cleanup goroutine.

Control flow: construction starts `cleanupStaleResources`. `Put` creates or fills a placeholder and notifies watchers. `Get` removes a fully-put resource, calls `SetCreated`, and returns its ID. `WatcherForResource` creates placeholders for in-progress resources and returns the current stage. Cleanup marks put resources stale on one tick and reaps them on the next, running their cleaner outside the mutex.

State and persistence behavior: state is in-memory map plus watcher channels. Cleanup side effects are delegated to `ResourceCleaner`; no store state survives process restart.

Dependencies and integration points: uses CRI-O logging, logrus, mutexes, timers, and caller-supplied resource/cleanup implementations. It coordinates duplicate or retried create requests.

Risks: watcher sends occur while holding the mutex but channels are buffered by one. Placeholders must be deleted if never put and only staged, or they can leak. Cleanup timing is between one and two timeout intervals.

Test signals: tests cover put/get, duplicate put failure, `SetCreated`, multiple watcher notification, stale cleanup invocation, no cleanup before put, and stage creation/update.
