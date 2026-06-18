# sources/control-plane/external-snapshotter/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml

## Purpose
Defines the `volumesnapshots.snapshot.storage.k8s.io` CRD for `snapshot.storage.k8s.io` with namespaced `VolumeSnapshot` resources and OpenAPI/CEL validation for snapshot API admission.

Source size: 351 lines, 22409 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `apiextensions.k8s.io/v1` `CustomResourceDefinition` named `volumesnapshots.snapshot.storage.k8s.io`.
- CRD versions: v1 served=True storage=True, v1beta1 served=False storage=False.
- Names: plural `volumesnapshots`, singular `volumesnapshot`, kind `VolumeSnapshot`, list kind `VolumeSnapshotList`.
- Validation density: 4 CEL validation blocks and 4 `required` schema markers observed.

## Control Flow
- Applied by cluster administrators before controllers start; the API server stores and validates `VolumeSnapshot` custom resources.
- The schema constrains `spec.source` alternatives, optional class name handling, status shape, object metadata, and conversion/storage for served versions.
- Snapshot controllers and CSI sidecars subsequently watch these resources through generated clientsets, informers, and listers.

## State and Persistence
- Persists `VolumeSnapshot` custom resources in the Kubernetes API server/etcd under `snapshot.storage.k8s.io`.
- Status subresources and controller-managed fields are persisted by the controller rather than by this YAML itself.
- CEL immutability and one-of rules become admission-time state transition constraints.

## Dependencies and Integration Points
- Kubernetes apiextensions v1 CRD machinery.
- Generated snapshot API Go types and controller-gen output.
- External snapshotter controllers, webhook/conversion components, and Kubernetes storage clients.

## Risks and Edge Cases
- Any schema or CEL mismatch can reject valid snapshots, accept invalid restore sources, or break controller assumptions.
- CRD version/storage flags must stay aligned with generated API types and conversion webhooks.
- Large schemas are easy to drift from API structs unless `update-crd.sh` is rerun after type changes.

## Test Signals
- Exercised indirectly by `client/hack/run-cel-tests.sh` and the `client/hack/cel-tests/volumesnapshot` fixtures in this work item.
- Regeneration path is `client/hack/update-crd.sh` using controller-gen.
