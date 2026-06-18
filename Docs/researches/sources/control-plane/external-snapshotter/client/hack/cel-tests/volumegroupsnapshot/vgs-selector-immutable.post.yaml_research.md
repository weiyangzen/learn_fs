# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 11 lines, 267 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (selector), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

## Control Flow
- `run-cel-tests.sh` discovers this YAML with `find cel-tests -name *.yaml` and submits it with `kubectl apply --dry-run=server` for standalone cases.
- For `.pre.yaml` files the script applies the pre-state, applies the matching `.post.yaml`, then deletes the post-state to verify update-time CEL validation.
- The fixture relies on API server CRD schema/CEL behavior, not local parsing.

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
- Expected validation substring: `selector is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
