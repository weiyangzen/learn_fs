<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/generic.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/generic.go

Purpose: generated generic informer lookup for Rook Ceph v1 resources. It lets callers request a `GenericInformer` by `GroupVersionResource` instead of using typed methods.

Important APIs/types/functions: `GenericInformer`, `genericInformer`, `Informer`, `Lister`, and `(*sharedInformerFactory).ForResource`. The switch maps every known Ceph v1 resource plural, including `cephnfses` and `cephnvmeofgateways`, to its typed informer.

Control flow: `ForResource` switches on the requested resource. On a match it constructs `genericInformer{resource: resource.GroupResource(), informer: typed.Informer()}`. `Lister` wraps the shared indexer with `cache.NewGenericLister`. Unknown resources return `fmt.Errorf("no informer found for %v", resource)`.

State and persistence behavior: no state beyond the referenced informer and group resource. The generic lister reads from the same cache owned by the shared factory.

Dependencies and integration points: depends on Rook Ceph v1 scheme group version and client-go cache generic listers. Dynamic controller code and generic utilities use this path when they cannot compile against a typed lister.

Risks: the switch must be regenerated when resources are added or plural names change. Unknown-resource support is explicitly not implemented, so callers need a different dynamic informer for CRDs outside the generated set.

Test signals: table tests for every supported `GroupVersionResource`, error behavior for unknown resources, and confirmation that generic listers share cache state with typed informers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/generic.go -->
