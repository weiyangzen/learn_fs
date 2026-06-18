<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/interface.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/interface.go

Purpose: generated version-level informer interface for every `ceph.rook.io/v1` resource. It is the typed menu used by controllers after selecting the Ceph API group and version.

Important APIs/types/functions: `Interface` declares resource methods including `CephBlockPools`, `CephBlockPoolRadosNamespaces`, `CephBucketNotifications`, `CephBucketTopics`, `CephCOSIDrivers`, `CephClients`, `CephClusters`, `CephFilesystems`, `CephFilesystemMirrors`, `CephFilesystemSubVolumeGroups`, `CephNFSes`, `CephNVMeOFGateways`, object-store realm/store/account/user/zone/zonegroup methods, and `CephRBDMirrors`. `version` stores the shared factory, namespace, and tweak function.

Control flow: `New` returns a `version` value. Each method constructs the small per-resource informer wrapper with identical factory/namespace/tweak state; actual informer allocation is deferred until `Informer()` is called on that wrapper.

State and persistence behavior: no local cache or persistence is stored here. The shared factory owns informer caches, started flags, and synchronization state.

Dependencies and integration points: depends on `internalinterfaces.SharedInformerFactory` to avoid cycles and on the sibling generated per-resource informer files. Top-level factories reach this through `Ceph().V1()`.

Risks: omitted methods make resources unavailable to typed controllers; stale method names such as `CephNFSes` or `CephNVMeOFGateways` break generated client compatibility. Because wrappers are cheap, callers must still use the shared factory lifecycle correctly.

Test signals: compile coverage for every generated resource method, generic factory resource lookup, and controller informer construction across all Rook Ceph v1 CRDs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/interface.go -->
