# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_base.go

Purpose: defines the sidecar controller object, constructor, informer wiring, workqueue worker loop, driver filtering, and local cache initialization for snapshot and optional group-snapshot content processing.

Important APIs/types/functions: `csiSnapshotSideCarController`, `NewCSISnapshotSideCarController`, `Run`, `enqueueContentWork`, `contentWorker`, `processNextItem`, `syncContentByKey`, `isDriverMatch`, `deleteContentInCacheStore`, and `initializeCaches`. The struct owns Kubernetes clients, event recorder, listers, sync predicates, workqueues, cache stores, CSI handler, feature flags, and group snapshot listers/queues.

Control flow: the constructor configures event broadcasting, the content workqueue, snapshot content/class informers, and optionally group snapshot informers. Add/delete events enqueue immediately; update events for `VolumeSnapshotContent` pass through `utils.ShouldEnqueueContentChange` to avoid loops from sidecar-owned status/finalizer updates. `Run` waits for informers, seeds local stores from listers, launches worker goroutines, and optionally attaches worker goroutines to a wait group for leader-election release-on-exit. Each queue item is fetched by key, resolved from the informer, filtered by driver/class, cached by resource version, and reconciled through `syncContent`.

State and persistence: this file maintains only runtime state: rate-limited queue contents and cache stores keyed by object identity. Durable state remains in the API server through the operation file. Deleted objects are removed from the local cache after informer not-found resolution.

Dependencies and integration: integrates client-go informers, workqueue, event recorder, feature gates, snapshot/group snapshot generated clients and listers, CSI snapshotter/group snapshotter interfaces, and utility cache functions. It shares the same controller type with group snapshot methods in neighboring files.

Risks and test signals: risks include skipped objects when class-driver metadata is stale or missing, group snapshot cache initialization not applying the same driver filter as normal content, non-reentrant worker assumptions with multiple workers, and stale cache resource-version parse failures. Tests cover resource-version ordering and parse errors through `StoreObjectUpdate`; broader informer/worker behavior is mostly integration-tested elsewhere.
