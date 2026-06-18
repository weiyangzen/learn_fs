# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations.go

Purpose: provides typed annotation maps and helpers for applying component-specific annotations to Rook-managed Kubernetes objects.

Important APIs/types/functions: `AnnotationsSpec`, `Annotations`, getters such as `GetMgrAnnotations`, `GetDashboardAnnotations`, `GetMonAnnotations`, `GetOSDAnnotations`, `GetCleanupAnnotations`, `GetCephExporterAnnotations`, `GetCmdReporterAnnotations`, `GetCrashCollectorAnnotations`, `GetClusterMetadataAnnotations`, `mergeAllAnnotationsWithKey`, `ApplyToObjectMeta`, and `Merge`.

Control flow: component getters merge `all` annotations with component-specific entries. `ApplyToObjectMeta` initializes metadata annotations and only fills missing keys. `Merge` returns a new map copying receiver values first and only adding absent keys from the supplied map.

State and persistence: no global state; annotations persist on Kubernetes object metadata after reconciliation.

Dependencies/integration: uses Kubernetes `metav1.ObjectMeta` and `KeyType` constants from `keys.go`.

Risks: comments say supplied attributes override originals, but implementation preserves receiver values on conflicts; since `all.Merge(component)` is used, `all` wins over component-specific keys.

Test signals: `annotations_test.go` covers merge, YAML unmarshalling, apply behavior, nil maps, and component getter behavior.
