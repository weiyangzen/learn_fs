<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectrealm.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectrealm.go

Purpose: generated shared informer and lister binding for the `CephObjectRealm` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephObjectRealmInformer` exposes `Informer()` and `Lister()`. `NewCephObjectRealmInformer` delegates to `NewFilteredCephObjectRealmInformer`; `NewFilteredCephObjectRealmInformer` builds a `cache.SharedIndexInformer`; `cephObjectRealmInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephObjectRealmLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephObjectRealms(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephObjectRealm{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephObjectRealm`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephObjectRealms()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephObjectRealms`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectrealm.go -->
