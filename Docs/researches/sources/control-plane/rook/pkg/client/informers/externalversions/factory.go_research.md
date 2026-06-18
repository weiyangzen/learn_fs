<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/factory.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/factory.go

Purpose: generated top-level shared informer factory for the Rook versioned clientset. It owns informer caching, lifecycle, namespace/filter options, custom resyncs, and transform functions.

Important APIs/types/functions: `SharedInformerOption`, `sharedInformerFactory`, `WithCustomResyncConfig`, `WithTweakListOptions`, `WithNamespace`, `WithTransform`, `NewSharedInformerFactory`, `NewFilteredSharedInformerFactory`, `NewSharedInformerFactoryWithOptions`, `Start`, `Shutdown`, `WaitForCacheSync`, `InformerFor`, the public `SharedInformerFactory` interface, and `Ceph()`.

Control flow: construction initializes maps and applies functional options. `InformerFor` locks, reuses an informer by `reflect.TypeOf(obj)` when present, selects custom or default resync, invokes the resource-specific constructor, applies the optional transform, stores the informer, and returns it. `Start` locks and runs all not-yet-started informers in goroutines. `Shutdown` sets a flag and waits for started goroutines to exit after their stop channel closes. `WaitForCacheSync` snapshots started informers and waits on each cache.

State and persistence behavior: mutable state includes client, namespace, tweak function, default/custom resyncs, transform, informer map, started map, wait group, mutex, and shutdown flag. All state is in-memory process state; persistence is Kubernetes API state watched by informers.

Dependencies and integration points: integrates the generated Rook clientset with client-go `cache.SharedIndexInformer`, `runtime.Object`, `schema.GroupVersionResource`, and the Ceph group informer package. Controllers use this factory to share watches and reduce API server connections.

Risks: informers created after `Start` require another `Start` call; `Start` races with immediate `WaitForCacheSync` if callers do not follow the documented lifecycle. Transform functions affect every informer and can strip fields expected by reconcilers. Wrong custom resync keys silently fall back to the default.

Test signals: lifecycle tests for start idempotency, shutdown blocking/unblocking, informer reuse by type, custom resync application, transform application, namespaced/tweaked factory options, and cache sync reporting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/factory.go -->
