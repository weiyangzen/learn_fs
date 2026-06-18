# sources/control-plane/rook/pkg/operator/ceph/cluster/dependents.go

Purpose: discovers custom resources in a namespace that depend on a `CephCluster` and therefore should block cluster deletion until removed.

Important APIs and functions: `cephClusterDependentListKinds` enumerates list kinds for pools, mirrors, filesystems, object stores/users/zones/zonegroups/realms, NFS, clients, bucket topics/notifications, subvolume groups, and RADOS namespaces. `CephClusterDependents` lists each kind using an unstructured list and returns a `dependents.DependentList`. `listKindToSingularKind` trims the `List` suffix for display/reporting.

Control flow: for each configured list kind, it sets group/version/kind to the Rook Ceph API, calls the controller-runtime client in the target namespace, records list errors, and adds each object's name under the singular kind. After scanning all kinds, it aggregates any errors while still returning whatever dependents were found.

State and persistence behavior: read-only. It builds an in-memory dependent list and does not mutate Kubernetes objects or status directly; callers use the result to report deletion blocking.

Dependencies and integration points: uses `clusterd.Context.Client`, unstructured Kubernetes objects, Rook Ceph API scheme metadata, controller-runtime namespace filtering, Rook util aggregate errors, and `pkg/util/dependents`.

Risks: the list kind table is a deletion safety boundary. Missing a dependent CRD kind can allow cluster deletion while resources still exist. Some entries in the table are not suffixed with `List` (`CephBucketTopic`, `CephBucketNotification`, `CephFilesystemSubVolumeGroup`, `CephBlockPoolRadosNamespace`), so `listKindToSingularKind` returns the same string and correctness depends on controller-runtime accepting those kind names for list objects. Errors are aggregated but partial results can still be used by callers.

Test signals: `dependents_test.go` covers many listed kinds and namespace isolation, but error aggregation is noted as TODO and not currently exercised.
