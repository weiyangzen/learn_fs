<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystem.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystem.go

Purpose: generated shared informer and lister binding for the `CephFilesystem` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephFilesystemInformer` exposes `Informer()` and `Lister()`. `NewCephFilesystemInformer` delegates to `NewFilteredCephFilesystemInformer`; `NewFilteredCephFilesystemInformer` builds a `cache.SharedIndexInformer`; `cephFilesystemInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephFilesystemLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephFilesystems(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephFilesystem{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephFilesystem`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephFilesystems()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephFilesystems`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystem.go -->
