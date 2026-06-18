<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbucketnotification.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbucketnotification.go

Purpose: generated cache lister for `CephBucketNotification` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephBucketNotificationLister` supports `List(selector)` and `CephBucketNotifications(namespace)`. `cephBucketNotificationLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephBucketNotification]`. `NewCephBucketNotificationLister` constructs the indexer with `cephrookiov1.Resource("cephbucketnotification")`. `CephBucketNotificationNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephBucketNotification`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbucketnotification.go -->
