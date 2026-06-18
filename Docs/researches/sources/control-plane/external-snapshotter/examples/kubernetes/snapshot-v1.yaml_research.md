# sources/control-plane/external-snapshotter/examples/kubernetes/snapshot-v1.yaml

## Purpose
example manifest for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-demo-v1`.

Source size: 9 lines, 208 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-demo-v1`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='csi-hostpath-snapclass-v1'`.

## Control Flow
- Used as a sample resource for manual Kubernetes workflows and e2e-style validation of snapshot, restore, class, PVC, or group snapshot behavior.
- Users apply it after CRDs/controllers are installed and after replacing driver-specific names where needed.
- The object is reconciled by Kubernetes storage controllers and external-snapshotter controllers.

## State and Persistence
- No local persistence; applying the manifest creates or updates Kubernetes API objects.
- Object state lives in the API server and is reconciled by controllers after admission.
- For CEL fixtures, state is temporary test state created by server-side dry run or by pre/post transaction setup.

## Dependencies and Integration Points
- Kubernetes API server and the relevant built-in or CRD API group.
- External snapshotter CRDs/controllers when the object uses snapshot or group snapshot APIs.
- `kubectl`/kustomize for application and validation.

## Risks and Edge Cases
- Field drift against CRD schemas can make the fixture or deployment fail admission.
- Name, namespace, driver, and selector values are often test-specific and may not be valid in arbitrary clusters.
- Expected-failure fixtures are sensitive to exact validation error text.

## Test Signals
- Acts as documentation-by-example; acceptance depends on matching CRDs, StorageClass, SnapshotClass, CSI driver, and PVC state.
- Invalid examples are intended to demonstrate admission/schema rejection.
