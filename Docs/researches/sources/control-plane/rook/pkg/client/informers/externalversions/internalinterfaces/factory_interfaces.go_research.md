<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/internalinterfaces/factory_interfaces.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/internalinterfaces/factory_interfaces.go

Purpose: generated small interface package used to connect resource informer packages to the top-level factory without import cycles.

Important APIs/types/functions: `NewInformerFunc`, `SharedInformerFactory`, and `TweakListOptionsFunc`. `NewInformerFunc` receives a versioned Rook client and resync period and returns `cache.SharedIndexInformer`.

Control flow: resource informer wrappers pass their default constructor to `SharedInformerFactory.InformerFor`; tweak functions are invoked by per-resource list/watch closures before API calls.

State and persistence behavior: this file owns no state. It defines contracts implemented by `externalversions.sharedInformerFactory` and consumed by generated resource informers.

Dependencies and integration points: imports the Rook versioned clientset, Kubernetes `metav1.ListOptions`, `runtime.Object`, and client-go cache types. It is a core generated boundary between packages.

Risks: changing these interfaces breaks all generated informer packages. Since the shared interface only exposes `Start` and `InformerFor`, extra top-level factory behavior remains intentionally hidden from resource packages.

Test signals: compile-time conformance of `sharedInformerFactory`, successful resource informer construction, and list-option tweak propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/internalinterfaces/factory_interfaces.go -->
