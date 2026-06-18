# Group Research: subset-b-000381

Source files: 151

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-class-empty-string.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-class-empty-string.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 11 lines, 247 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (selector), `spec.volumeGroupSnapshotClassName=''`.

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
- Expected validation substring: `volumeGroupSnapshotClassName must not be the empty string when set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-class-empty-string.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 250 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (volumeGroupSnapshotContentName), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
- Expected validation substring: `volumeGroupSnapshotContentName is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 242 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (volumeGroupSnapshotContentName), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-to-selector.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-to-selector.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 11 lines, 272 bytes.

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
- Expected validation substring: `volumeGroupSnapshotContentName is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-to-selector.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-to-selector.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-to-selector.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 242 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (volumeGroupSnapshotContentName), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-content-to-selector.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-no-class.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-no-class.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a standalone dry-run fixture expected to be accepted.

Source size: 10 lines, 212 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (selector).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-no-class.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-immutable.post.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 11 lines, 272 bytes.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-to-content.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-to-content.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 242 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (volumeGroupSnapshotContentName), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
- Expected validation substring: `selector is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-to-content.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-to-content.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-to-content.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 11 lines, 272 bytes.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-selector-to-content.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-content.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-content.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a standalone dry-run fixture expected to be accepted.

Source size: 9 lines, 242 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (volumeGroupSnapshotContentName), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-content.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-no-selector-no-content.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-no-selector-no-content.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 8 lines, 199 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (object), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
- Expected validation substring: `exactly one of selector and volumeGroupSnapshotContentName must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-no-selector-no-content.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-selector-and-content.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-selector-and-content.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 12 lines, 318 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (selector, volumeGroupSnapshotContentName), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
- Expected validation substring: `exactly one of selector and volumeGroupSnapshotContentName must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-selector-and-content.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-selector.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-selector.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`. It is a standalone dry-run fixture expected to be accepted.

Source size: 11 lines, 272 bytes.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshot/vgs-with-selector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-deletionpolicy-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-deletionpolicy-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 204 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`.

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
- Expected validation substring: `deletionPolicy: Invalid value: "string": deletionPolicy is immutable once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-deletionpolicy-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-deletionpolicy-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-deletionpolicy-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 204 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-deletionpolicy-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-parameters-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-parameters-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 205 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`.

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
- Expected validation substring: `parameters: Invalid value: "object": parameters are immutable once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-parameters-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-parameters-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-parameters-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 203 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotclass/vgs-class-parameters-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-class-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-class-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 18 lines, 468 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `Invalid value: "string": volumeGroupSnapshotClassName is immutable once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-class-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-class-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-class-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 18 lines, 467 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-pre'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-class-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-driver-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-driver-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 17 lines, 430 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpathafter.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `spec.driver: Invalid value: "string": driver is immutable once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-driver-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-driver-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-driver-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 17 lines, 425 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-driver-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-mutate-deletionpolicy.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-mutate-deletionpolicy.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to be accepted.

Source size: 18 lines, 468 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Delete'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-mutate-deletionpolicy.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-mutate-deletionpolicy.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-mutate-deletionpolicy.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to succeed.

Source size: 18 lines, 468 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-mutate-deletionpolicy.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ok.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ok.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a standalone dry-run fixture expected to be accepted.

Source size: 14 lines, 320 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ok.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-name-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-name-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 18 lines, 476 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `spec.volumeGroupSnapshotRef: Invalid value: "object": volumeGroupSnapshotRef.name and volumeGroupSnapshotRef.namespace are immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-name-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-name-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-name-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 18 lines, 468 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-name-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-namespace-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-namespace-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 18 lines, 476 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `spec.volumeGroupSnapshotRef: Invalid value: "object": volumeGroupSnapshotRef.name and volumeGroupSnapshotRef.namespace are immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-namespace-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-namespace-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-namespace-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 18 lines, 468 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-namespace-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-only-name.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-only-name.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 13 lines, 297 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandles), `spec.volumeGroupSnapshotRef` (name).

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
- Expected validation substring: `both volumeGroupSnapshotRef.name and volumeGroupSnapshotRef.namespace must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-only-name.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-only-namespace.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-only-namespace.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 13 lines, 287 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandles), `spec.volumeGroupSnapshotRef` (namespace).

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
- Expected validation substring: `both volumeGroupSnapshotRef.name and volumeGroupSnapshotRef.namespace must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-only-namespace.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 19 lines, 522 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace, uid).

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
- Expected validation substring: `Invalid value: "object": volumeGroupSnapshotRef.uid is immutable once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 19 lines, 522 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace, uid).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-set-from-empty.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-set-from-empty.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to be accepted.

Source size: 19 lines, 522 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace, uid).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-set-from-empty.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-set-from-empty.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-set-from-empty.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to succeed.

Source size: 18 lines, 476 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotClassName='class-post'`, `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-ref-uid-set-from-empty.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-both-volume-and-groupsnapshot.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-both-volume-and-groupsnapshot.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 19 lines, 458 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles, volumeHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `exactly one of volumeHandles and groupSnapshotHandles must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-both-volume-and-groupsnapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-empty.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-empty.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 12 lines, 290 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (object), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `exactly one of volumeHandles and groupSnapshotHandles must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-empty.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 18 lines, 448 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `groupSnapshotHandles is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 17 lines, 425 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-to-volume.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-to-volume.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 14 lines, 320 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `groupSnapshotHandles is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-to-volume.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-to-volume.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-to-volume.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 17 lines, 425 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-groupsnapshot-to-volume.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-immutable.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 15 lines, 334 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `volumeHandles is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-immutable.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 14 lines, 320 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-to-groupsnapshot.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-to-groupsnapshot.post.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction post-state expected to fail server-side validation.

Source size: 17 lines, 425 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (groupSnapshotHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- Expected validation substring: `volumeHandles is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-to-groupsnapshot.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-to-groupsnapshot.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-to-groupsnapshot.pre.yaml

## Purpose
CEL admission test fixture for `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 14 lines, 320 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta2` `VolumeGroupSnapshotContent` named `new-groupsnapshotcontent-demo`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandles), `spec.volumeGroupSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumegroupsnapshotcontent/vgsc-source-volume-to-groupsnapshot.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-empty-class.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-empty-class.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 9 lines, 195 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName=''`.

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
- Expected validation substring: `volumeSnapshotClassName must not be the empty string when set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-empty-class.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-no-class.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-no-class.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a standalone dry-run fixture expected to be accepted.

Source size: 8 lines, 165 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-no-class.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-not-empty-class.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-not-empty-class.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a standalone dry-run fixture expected to be accepted.

Source size: 9 lines, 205 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='class-name'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-not-empty-class.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-empty.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-empty.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 8 lines, 163 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (object), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- Expected validation substring: `exactly one of volumeSnapshotContentName and persistentVolumeClaimName must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-empty.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-multiple.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-multiple.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 10 lines, 258 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName, volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- Expected validation substring: `exactly one of volumeSnapshotContentName and persistentVolumeClaimName must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-multiple.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc-annotate.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc-annotate.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction post-state expected to be accepted.

Source size: 11 lines, 233 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='this-is-a-test'`, annotations `p`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc-annotate.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc-annotate.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc-annotate.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction pre-state; paired post apply is expected to succeed.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc-annotate.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 211 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- Expected validation substring: `persistentVolumeClaimName is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-pvc.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-vsc.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-vsc.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- Expected validation substring: `persistentVolumeClaimName is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-vsc.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-vsc.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-vsc.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc-to-vsc.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a standalone dry-run fixture expected to be accepted.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-pvc.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-pvc.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (persistentVolumeClaimName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- Expected validation substring: `volumeSnapshotContentName is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-pvc.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-pvc.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-pvc.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-pvc.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc-annotate.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc-annotate.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction post-state expected to be accepted.

Source size: 11 lines, 233 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`, annotations `p`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc-annotate.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc-annotate.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc-annotate.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction pre-state; paired post apply is expected to succeed.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc-annotate.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 9 lines, 211 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- Expected validation substring: `Invalid value: "string": volumeSnapshotContentName is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vsc-to-vsc.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vscontent.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vscontent.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`. It is a standalone dry-run fixture expected to be accepted.

Source size: 9 lines, 209 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-test`.
- Important fields: `spec.source` (volumeSnapshotContentName), `spec.volumeSnapshotClassName='this-is-a-test'`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshot/vs-source-vscontent.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-empty-source.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-empty-source.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 12 lines, 253 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (object), `spec.volumeSnapshotRef` (name, namespace).

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
- Expected validation substring: `exactly one of volumeHandle and snapshotHandle must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-empty-source.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-multiple-source.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-multiple-source.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 14 lines, 312 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (snapshotHandle, volumeHandle), `spec.volumeSnapshotRef` (name, namespace).

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
- Expected validation substring: `exactly one of volumeHandle and snapshotHandle must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-multiple-source.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok-with-snapshothandle.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok-with-snapshothandle.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a standalone dry-run fixture expected to be accepted.

Source size: 13 lines, 282 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (snapshotHandle), `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok-with-snapshothandle.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction post-state expected to be accepted.

Source size: 15 lines, 311 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.volumeSnapshotRef` (name, namespace), annotations `test`.

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction pre-state; paired post apply is expected to succeed.

Source size: 13 lines, 280 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a standalone dry-run fixture expected to be accepted.

Source size: 13 lines, 280 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-ok.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-source-no-name.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-source-no-name.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 12 lines, 262 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.volumeSnapshotRef` (namespace).

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
- Expected validation substring: `both spec.volumeSnapshotRef.name and spec.volumeSnapshotRef.namespace must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-source-no-name.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-source-no-namespace.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-source-no-namespace.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a standalone dry-run fixture expected to fail server-side validation.

Source size: 12 lines, 251 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.volumeSnapshotRef` (name).

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
- Expected validation substring: `both spec.volumeSnapshotRef.name and spec.volumeSnapshotRef.namespace must be set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-source-no-namespace.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-immutable.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 14 lines, 316 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (snapshotHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- Expected validation substring: `snapshotHandle is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-immutable.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 14 lines, 308 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (snapshotHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-to-volumehandle.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-to-volumehandle.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 14 lines, 313 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- Expected validation substring: `snapshotHandle is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-to-volumehandle.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-to-volumehandle.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-to-volumehandle.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 14 lines, 308 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (snapshotHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcesnapshothandle-to-volumehandle.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-immutable.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-immutable.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 14 lines, 314 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- Expected validation substring: `volumeHandle is immutable`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-immutable.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-immutable.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-immutable.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 14 lines, 306 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-immutable.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-to-snapshothandle.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-to-snapshothandle.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 14 lines, 317 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (snapshotHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- Expected validation substring: `volumeHandle is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-to-snapshothandle.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-to-snapshothandle.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-to-snapshothandle.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 14 lines, 306 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumehandle-to-snapshothandle.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumemode.post.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumemode.post.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction post-state expected to fail server-side validation.

Source size: 13 lines, 280 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.volumeSnapshotRef` (name, namespace).

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
- Expected validation substring: `sourceVolumeMode is required once set`.
- Absence or presence of `.err`/`.tx_err` determines whether the runner treats failure as success.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumemode.post.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumemode.pre.yaml -->
# sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumemode.pre.yaml

## Purpose
CEL admission test fixture for `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`. It is a transaction pre-state; paired post apply is expected to fail.

Source size: 14 lines, 306 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotContent` named `new-snapshotcontent-test`.
- Important fields: `spec.deletionPolicy='Retain'`, `spec.driver='hostpath.csi.k8s.io'`, `spec.source` (volumeHandle), `spec.sourceVolumeMode='Block'`, `spec.volumeSnapshotRef` (name, namespace).

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
- No adjacent expected-error file for this exact YAML, so the runner expects admission success unless it is a paired pre-state.
- Paired `.pre.yaml`/`.post.yaml` files exercise update/immutability transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/cel-tests/volumesnapshotcontent/vsc-sourcevolumemode.pre.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/run-cel-tests.sh -->
# sources/control-plane/external-snapshotter/client/hack/run-cel-tests.sh

## Purpose
Runs server-side admission/CEL validation fixtures under `client/hack/cel-tests`.

Source size: 112 lines, 2772 bytes.

## Important APIs, Types, and Functions
- Shell functions: `exec_case`, `exec_tx_case`.
- External commands/helpers: `find`, `grep`, `kubectl`.

## Control Flow
- Parses optional `-v/--verbose` and rejects unknown arguments.
- `exec_case` dry-runs each YAML with `kubectl apply --dry-run=server` and compares success/failure to adjacent `.err` files.
- `exec_tx_case` applies each `.pre.yaml`, applies the matching `.post.yaml`, checks `.tx_err` expectations, deletes the post resource, and counts successes/failures.
- Exits non-zero if any fixture outcome differs from expectation.

## State and Persistence
- Writes temporary `.out` files beside fixtures.
- Transaction tests create real API objects for the pre-state and clean up using the post manifest.
- Counters are process-local.

## Dependencies and Integration Points
- kubectl connected to a cluster with snapshot CRDs installed.
- Fixture `.err` and `.tx_err` files containing expected validation substrings.
- Bash, find, grep, and server-side Kubernetes dry-run support.

## Risks and Edge Cases
- Exact error text matching can be brittle across Kubernetes versions.
- Transaction cleanup uses the post manifest and may leave pre-state if apply/delete paths fail unexpectedly.
- The first loop includes `.pre.yaml` and `.post.yaml` as standalone YAMLs before transaction tests, which is intentional but can surprise maintainers.

## Test Signals
- The script is the executable test harness for all CEL fixtures in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/run-cel-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/tools.go -->
# sources/control-plane/external-snapshotter/client/hack/tools.go

## Purpose
Go source file in package `tools`.

Source size: 23 lines, 810 bytes.

## Important APIs, Types, and Functions
- Go package `tools`.
- Key imports: `k8s.io/code-generator`.

## Control Flow
- Control flow follows the declared functions and methods listed above.
- The file integrates with neighboring package code through imports and exported declarations.

## State and Persistence
- State behavior depends on the declared types and functions; no separate durable store is visible in this file.
- Kubernetes-related packages generally persist through API server objects rather than local files.

## Dependencies and Integration Points
- Key imports listed above.
- Neighboring packages in the external-snapshotter module.

## Risks and Edge Cases
- Generated files should not be edited manually.
- Caller behavior must respect cache/client-go contracts.

## Test Signals
- Compile-time package tests are the baseline signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/update-crd.sh -->
# sources/control-plane/external-snapshotter/client/hack/update-crd.sh

## Purpose
Regenerates CRD YAML from API type definitions using controller-gen.

Source size: 45 lines, 1279 bytes.

## Important APIs, Types, and Functions
- External commands/helpers: `controller-gen`, `find`, `go`, `mktemp`, `which`.

## Control Flow
- Computes `SCRIPT_ROOT` as the client directory.
- Looks for `controller-gen`; if absent, installs controller-gen v0.15.0 in a temporary Go module.
- Runs `controller-gen crd paths=${SCRIPT_ROOT}/apis/...`.

## State and Persistence
- Writes generated CRD manifests under controller-gen default output paths in the client tree.
- Uses a temporary directory for tool bootstrap and removes it afterward.

## Dependencies and Integration Points
- Go toolchain, controller-gen v0.15.0, API marker comments under `client/apis`.

## Risks and Edge Cases
- `set -o errexit` is commented out, so some failures may not abort as strictly as expected.
- Generated CRDs must be reviewed for schema/CEL drift before release.

## Test Signals
- Diff of generated CRDs and CEL test execution provide validation.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/update-crd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/update-generated-code.sh -->
# sources/control-plane/external-snapshotter/client/hack/update-generated-code.sh

## Purpose
Regenerates deepcopy helpers, clientsets, informers, and listers for external-snapshotter API packages.

Source size: 34 lines, 1151 bytes.

## Important APIs, Types, and Functions
- External commands/helpers: `go`.

## Control Flow
- Computes `SCRIPT_ROOT` as the client directory.
- Sources `${GOPATH}/src/k8s.io/code-generator/kube_codegen.sh`.
- Runs `kube::codegen::gen_helpers` and `kube::codegen::gen_client` with watch support and the module output package.

## State and Persistence
- Writes generated Go files under `client/` based on API definitions.
- No runtime persistence; this is a developer maintenance script.

## Dependencies and Integration Points
- GOPATH checkout of k8s.io/code-generator, Go toolchain, boilerplate file, API packages.

## Risks and Edge Cases
- Requires the expected GOPATH layout, which can fail in module-only environments.
- Generated output must stay in sync with CRDs and API type changes.

## Test Signals
- Compile/tests after regeneration plus git diff review are the main signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/hack/update-generated-code.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/factory.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/factory.go

## Purpose
Generated shared informer factory for all external-snapshotter API groups and versions.

Source size: 269 lines, 9681 bytes.

## Important APIs, Types, and Functions
- Go package `externalversions`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `SharedInformerOption`, `sharedInformerFactory`, `SharedInformerFactory`.
- Functions/methods: `WithCustomResyncConfig`, `WithTweakListOptions`, `WithNamespace`, `WithTransform`, `NewSharedInformerFactory`, `NewFilteredSharedInformerFactory`, `NewSharedInformerFactoryWithOptions`, `Start`, `Shutdown`, `WaitForCacheSync`, `InformerFor`, `Groupsnapshot`, `Snapshot`.
- Key imports: `reflect`, `sync`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/volumegroupsnapshot`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/volumesnapshot`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/runtime/schema`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Factory options set namespace, list-option tweaks, per-type resync periods, and object transforms.
- `InformerFor` memoizes informers by Go reflect type under a mutex.
- `Start` launches each requested informer once, `WaitForCacheSync` waits only for started informers, and `Shutdown` prevents further starts and waits for goroutines.

## State and Persistence
- Maintains in-memory maps of informer type to shared index informer and started state.
- Caches Kubernetes objects in client-go informers; persisted source of truth remains the Kubernetes API server.
- The wait group tracks running informer goroutines until stop channels close.

## Dependencies and Integration Points
- Versioned external-snapshotter clientset, generated group informers, Kubernetes runtime/schema, client-go cache, sync/time/reflect.

## Risks and Edge Cases
- Calling `WaitForCacheSync` before `Start` can miss newly created informers.
- Transforms and tweak functions apply across factory-created informers and can hide fields or filter resources unexpectedly.
- Shutdown blocks until stop channels close.

## Test Signals
- Generated-code behavior is normally covered by client-go generator conventions and downstream controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/factory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/generic.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/generic.go

## Purpose
Generated generic informer router mapping GroupVersionResource values to typed snapshot and group snapshot informers.

Source size: 93 lines, 4899 bytes.

## Important APIs, Types, and Functions
- Go package `externalversions`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `GenericInformer`, `genericInformer`.
- Functions/methods: `Informer`, `Lister`, `ForResource`.
- Key imports: `fmt`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta2`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumesnapshot/v1`, `k8s.io/apimachinery/pkg/runtime/schema`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `ForResource` switches over known `SchemeGroupVersion.WithResource(...)` values.
- On match it returns a `genericInformer` wrapping the typed informer and group resource.
- Unknown resources return an explicit error.

## State and Persistence
- No durable state; wrappers reference factory-managed informers and their shared caches.
- Generic listers read from informer indexers.

## Dependencies and Integration Points
- Generated API packages for volumesnapshot v1 and volumegroupsnapshot v1/v1beta1/v1beta2, schema, client-go cache.

## Risks and Edge Cases
- New CRD versions/resources must be regenerated here or generic access will fail.
- Resource plural strings must match CRDs exactly.

## Test Signals
- Downstream callers can assert `ForResource` returns informers for each known GVR and errors for unknown resources.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/generic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/internalinterfaces/factory_interfaces.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/internalinterfaces/factory_interfaces.go

## Purpose
Generated internal informer interfaces used to avoid import cycles between factory and typed informer packages.

Source size: 40 lines, 1449 bytes.

## Important APIs, Types, and Functions
- Go package `internalinterfaces`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `NewInformerFunc`, `SharedInformerFactory`, `TweakListOptionsFunc`.
- Key imports: `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Declares callback signatures and a minimal factory interface.
- Typed informers receive this interface so they can call back into the shared factory without depending on concrete factory types.

## State and Persistence
- No runtime state; this is compile-time interface glue.

## Dependencies and Integration Points
- Versioned clientset, metav1 list options, runtime object, client-go cache, time.

## Risks and Edge Cases
- Interface changes require regenerating all informer packages together.
- Incorrect tweak signatures would break list/watch filtering across generated informers.

## Test Signals
- Compile-time type checking is the primary signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/internalinterfaces/factory_interfaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/interface.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/interface.go

## Purpose
Generated version or group facade exposing typed informer accessors for snapshot resources.

Source size: 62 lines, 2398 bytes.

## Important APIs, Types, and Functions
- Go package `volumegroupsnapshot`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `Interface`, `group`.
- Functions/methods: `New`, `V1`, `V1beta1`, `V1beta2`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/volumegroupsnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/volumegroupsnapshot/v1beta1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/volumegroupsnapshot/v1beta2`.

## Control Flow
- Constructs a lightweight group/version struct with factory, namespace, and tweak-list options.
- Accessor methods return resource-specific informer structs for snapshots, classes, and contents.
- Top-level group interfaces expose versioned subinterfaces.

## State and Persistence
- No independent persistence; methods bind caller requests to factory-owned informer caches.
- Namespace and tweak functions are carried into each resource informer.

## Dependencies and Integration Points
- Internal informer interfaces, versioned subpackages, and client-go informer cache machinery.

## Risks and Edge Cases
- Accessor drift would prevent controllers from wiring a generated informer for a resource/version.
- Namespaces and list filters must be passed consistently to namespaced informers.

## Test Signals
- Compile and controller startup provide coverage; generated code is convention-driven.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/interface.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/interface.go

## Purpose
Generated version or group facade exposing typed informer accessors for snapshot resources.

Source size: 59 lines, 2481 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `Interface`, `version`.
- Functions/methods: `New`, `VolumeGroupSnapshots`, `VolumeGroupSnapshotClasses`, `VolumeGroupSnapshotContents`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`.

## Control Flow
- Constructs a lightweight group/version struct with factory, namespace, and tweak-list options.
- Accessor methods return resource-specific informer structs for snapshots, classes, and contents.
- Top-level group interfaces expose versioned subinterfaces.

## State and Persistence
- No independent persistence; methods bind caller requests to factory-owned informer caches.
- Namespace and tweak functions are carried into each resource informer.

## Dependencies and Integration Points
- Internal informer interfaces, versioned subpackages, and client-go informer cache machinery.

## Risks and Edge Cases
- Accessor drift would prevent controllers from wiring a generated informer for a resource/version.
- Namespaces and list filters must be passed consistently to namespaced informers.

## Test Signals
- Compile and controller startup provide coverage; generated code is convention-driven.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshot.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshot.go

## Purpose
Generated typed informer for `volumegroupsnapshot` resources.

Source size: 102 lines, 4688 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotInformer`, `volumeGroupSnapshotInformer`.
- Functions/methods: `NewVolumeGroupSnapshotInformer`, `NewFilteredVolumeGroupSnapshotInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshotclass.go

## Purpose
Generated typed informer for `volumegroupsnapshotclass` resources.

Source size: 101 lines, 4692 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotClassInformer`, `volumeGroupSnapshotClassInformer`.
- Functions/methods: `NewVolumeGroupSnapshotClassInformer`, `NewFilteredVolumeGroupSnapshotClassInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshotcontent.go

## Purpose
Generated typed informer for `volumegroupsnapshotcontent` resources.

Source size: 101 lines, 4735 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotContentInformer`, `volumeGroupSnapshotContentInformer`.
- Functions/methods: `NewVolumeGroupSnapshotContentInformer`, `NewFilteredVolumeGroupSnapshotContentInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1/volumegroupsnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/interface.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/interface.go

## Purpose
Generated version or group facade exposing typed informer accessors for snapshot resources.

Source size: 59 lines, 2486 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `Interface`, `version`.
- Functions/methods: `New`, `VolumeGroupSnapshots`, `VolumeGroupSnapshotClasses`, `VolumeGroupSnapshotContents`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`.

## Control Flow
- Constructs a lightweight group/version struct with factory, namespace, and tweak-list options.
- Accessor methods return resource-specific informer structs for snapshots, classes, and contents.
- Top-level group interfaces expose versioned subinterfaces.

## State and Persistence
- No independent persistence; methods bind caller requests to factory-owned informer caches.
- Namespace and tweak functions are carried into each resource informer.

## Dependencies and Integration Points
- Internal informer interfaces, versioned subpackages, and client-go informer cache machinery.

## Risks and Edge Cases
- Accessor drift would prevent controllers from wiring a generated informer for a resource/version.
- Namespaces and list filters must be passed consistently to namespaced informers.

## Test Signals
- Compile and controller startup provide coverage; generated code is convention-driven.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshot.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshot.go

## Purpose
Generated typed informer for `volumegroupsnapshot` resources.

Source size: 102 lines, 4738 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotInformer`, `volumeGroupSnapshotInformer`.
- Functions/methods: `NewVolumeGroupSnapshotInformer`, `NewFilteredVolumeGroupSnapshotInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1beta1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshotclass.go

## Purpose
Generated typed informer for `volumegroupsnapshotclass` resources.

Source size: 101 lines, 4742 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotClassInformer`, `volumeGroupSnapshotClassInformer`.
- Functions/methods: `NewVolumeGroupSnapshotClassInformer`, `NewFilteredVolumeGroupSnapshotClassInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1beta1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshotcontent.go

## Purpose
Generated typed informer for `volumegroupsnapshotcontent` resources.

Source size: 101 lines, 4785 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotContentInformer`, `volumeGroupSnapshotContentInformer`.
- Functions/methods: `NewVolumeGroupSnapshotContentInformer`, `NewFilteredVolumeGroupSnapshotContentInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1beta1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta1/volumegroupsnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/interface.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/interface.go

## Purpose
Generated version or group facade exposing typed informer accessors for snapshot resources.

Source size: 59 lines, 2486 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `Interface`, `version`.
- Functions/methods: `New`, `VolumeGroupSnapshots`, `VolumeGroupSnapshotClasses`, `VolumeGroupSnapshotContents`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`.

## Control Flow
- Constructs a lightweight group/version struct with factory, namespace, and tweak-list options.
- Accessor methods return resource-specific informer structs for snapshots, classes, and contents.
- Top-level group interfaces expose versioned subinterfaces.

## State and Persistence
- No independent persistence; methods bind caller requests to factory-owned informer caches.
- Namespace and tweak functions are carried into each resource informer.

## Dependencies and Integration Points
- Internal informer interfaces, versioned subpackages, and client-go informer cache machinery.

## Risks and Edge Cases
- Accessor drift would prevent controllers from wiring a generated informer for a resource/version.
- Namespaces and list filters must be passed consistently to namespaced informers.

## Test Signals
- Compile and controller startup provide coverage; generated code is convention-driven.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshot.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshot.go

## Purpose
Generated typed informer for `volumegroupsnapshot` resources.

Source size: 102 lines, 4738 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotInformer`, `volumeGroupSnapshotInformer`.
- Functions/methods: `NewVolumeGroupSnapshotInformer`, `NewFilteredVolumeGroupSnapshotInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta2`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1beta2`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshotclass.go

## Purpose
Generated typed informer for `volumegroupsnapshotclass` resources.

Source size: 101 lines, 4742 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotClassInformer`, `volumeGroupSnapshotClassInformer`.
- Functions/methods: `NewVolumeGroupSnapshotClassInformer`, `NewFilteredVolumeGroupSnapshotClassInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta2`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1beta2`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshotcontent.go

## Purpose
Generated typed informer for `volumegroupsnapshotcontent` resources.

Source size: 101 lines, 4785 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotContentInformer`, `volumeGroupSnapshotContentInformer`.
- Functions/methods: `NewVolumeGroupSnapshotContentInformer`, `NewFilteredVolumeGroupSnapshotContentInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta2`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumegroupsnapshot/v1beta2`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumegroupsnapshot/v1beta2/volumegroupsnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/interface.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/interface.go

## Purpose
Generated version or group facade exposing typed informer accessors for snapshot resources.

Source size: 46 lines, 1622 bytes.

## Important APIs, Types, and Functions
- Go package `volumesnapshot`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `Interface`, `group`.
- Functions/methods: `New`, `V1`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/volumesnapshot/v1`.

## Control Flow
- Constructs a lightweight group/version struct with factory, namespace, and tweak-list options.
- Accessor methods return resource-specific informer structs for snapshots, classes, and contents.
- Top-level group interfaces expose versioned subinterfaces.

## State and Persistence
- No independent persistence; methods bind caller requests to factory-owned informer caches.
- Namespace and tweak functions are carried into each resource informer.

## Dependencies and Integration Points
- Internal informer interfaces, versioned subpackages, and client-go informer cache machinery.

## Risks and Edge Cases
- Accessor drift would prevent controllers from wiring a generated informer for a resource/version.
- Namespaces and list filters must be passed consistently to namespaced informers.

## Test Signals
- Compile and controller startup provide coverage; generated code is convention-driven.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/interface.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/interface.go

## Purpose
Generated version or group facade exposing typed informer accessors for snapshot resources.

Source size: 59 lines, 2346 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `Interface`, `version`.
- Functions/methods: `New`, `VolumeSnapshots`, `VolumeSnapshotClasses`, `VolumeSnapshotContents`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`.

## Control Flow
- Constructs a lightweight group/version struct with factory, namespace, and tweak-list options.
- Accessor methods return resource-specific informer structs for snapshots, classes, and contents.
- Top-level group interfaces expose versioned subinterfaces.

## State and Persistence
- No independent persistence; methods bind caller requests to factory-owned informer caches.
- Namespace and tweak functions are carried into each resource informer.

## Dependencies and Integration Points
- Internal informer interfaces, versioned subpackages, and client-go informer cache machinery.

## Risks and Edge Cases
- Accessor drift would prevent controllers from wiring a generated informer for a resource/version.
- Namespaces and list filters must be passed consistently to namespaced informers.

## Test Signals
- Compile and controller startup provide coverage; generated code is convention-driven.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshot.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshot.go

## Purpose
Generated typed informer for `volumesnapshot` resources.

Source size: 90 lines, 3845 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeSnapshotInformer`, `volumeSnapshotInformer`.
- Functions/methods: `NewVolumeSnapshotInformer`, `NewFilteredVolumeSnapshotInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumesnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumesnapshot/v1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshotclass.go

## Purpose
Generated typed informer for `volumesnapshotclass` resources.

Source size: 89 lines, 3855 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeSnapshotClassInformer`, `volumeSnapshotClassInformer`.
- Functions/methods: `NewVolumeSnapshotClassInformer`, `NewFilteredVolumeSnapshotClassInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumesnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumesnapshot/v1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshotcontent.go

## Purpose
Generated typed informer for `volumesnapshotcontent` resources.

Source size: 89 lines, 3896 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeSnapshotContentInformer`, `volumeSnapshotContentInformer`.
- Functions/methods: `NewVolumeSnapshotContentInformer`, `NewFilteredVolumeSnapshotContentInformer`, `defaultInformer`, `Informer`, `Lister`.
- Key imports: `context`, `time`, `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumesnapshot/v1`, `github.com/kubernetes-csi/external-snapshotter/client/v8/clientset/versioned`, `github.com/kubernetes-csi/external-snapshotter/client/v8/informers/externalversions/internalinterfaces`, `github.com/kubernetes-csi/external-snapshotter/client/v8/listers/volumesnapshot/v1`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/runtime`, `k8s.io/apimachinery/pkg/watch`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Standalone constructors build a `cache.NewSharedIndexInformer` around a ListWatch.
- List and Watch functions apply optional `tweakListOptions` before calling the versioned clientset.
- `defaultInformer`, `Informer`, and `Lister` connect the typed informer to the shared factory and generated lister.

## State and Persistence
- Informer state is an in-memory cache/indexer populated by Kubernetes list/watch.
- The API server remains the persistent source of truth.
- Namespace scoping and tweak filters constrain which objects enter the cache.

## Dependencies and Integration Points
- Generated API type package, versioned clientset, generated lister package, metav1/runtime/watch, client-go cache.

## Risks and Edge Cases
- Incorrect resource client method or namespace handling would break controller watches.
- Objects returned from listers must be treated read-only because they point into the shared cache.

## Test Signals
- Generated by informer-gen; runtime coverage comes from controllers that call `.Informer()` and `.Lister()`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/informers/externalversions/volumesnapshot/v1/volumesnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/expansion_generated.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/expansion_generated.go

## Purpose
Generated empty lister expansion interfaces for future custom methods on snapshot listers.

Source size: 35 lines, 1324 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotListerExpansion`, `VolumeGroupSnapshotNamespaceListerExpansion`, `VolumeGroupSnapshotClassListerExpansion`, `VolumeGroupSnapshotContentListerExpansion`.

## Control Flow
- Declares no-op expansion interfaces compiled into generated lister interfaces.
- Developers can add custom methods in separate non-generated expansion files if needed.

## State and Persistence
- No runtime state or persistence.

## Dependencies and Integration Points
- Go type system only; no imports in most expansion files.

## Risks and Edge Cases
- Regeneration should preserve extension points; custom expansion methods belong outside generated output.

## Test Signals
- Compile-time interface embedding is the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/expansion_generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshot.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshot.go

## Purpose
Generated cache lister for `volumegroupsnapshot` resources.

Source size: 70 lines, 3194 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotLister`, `volumeGroupSnapshotLister`, `VolumeGroupSnapshotNamespaceLister`, `volumeGroupSnapshotNamespaceLister`.
- Functions/methods: `NewVolumeGroupSnapshotLister`, `VolumeGroupSnapshots`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Top-level `List` scans all namespaces in the indexer.
- Namespace accessor returns a namespace lister whose `List` uses `cache.ListAllByNamespace` and whose `Get` uses `namespace/name` keys.
- Missing objects return typed Kubernetes NotFound errors.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshotclass.go

## Purpose
Generated cache lister for `volumegroupsnapshotclass` resources.

Source size: 48 lines, 2083 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotClassLister`, `volumeGroupSnapshotClassLister`.
- Functions/methods: `NewVolumeGroupSnapshotClassLister`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans the shared indexer with a label selector.
- `Get` resolves cluster-scoped objects by name and returns a Kubernetes NotFound error when absent.
- Returned objects are pointers from the informer cache and must be treated read-only.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshotcontent.go

## Purpose
Generated cache lister for `volumegroupsnapshotcontent` resources.

Source size: 48 lines, 2119 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotContentLister`, `volumeGroupSnapshotContentLister`.
- Functions/methods: `NewVolumeGroupSnapshotContentLister`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans all cached objects with a selector.
- `Get` resolves cluster-scoped content objects by name and returns NotFound on cache miss.
- The lister is constructed with `New...Lister(indexer)`.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1/volumegroupsnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/expansion_generated.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/expansion_generated.go

## Purpose
Generated empty lister expansion interfaces for future custom methods on snapshot listers.

Source size: 35 lines, 1329 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotListerExpansion`, `VolumeGroupSnapshotNamespaceListerExpansion`, `VolumeGroupSnapshotClassListerExpansion`, `VolumeGroupSnapshotContentListerExpansion`.

## Control Flow
- Declares no-op expansion interfaces compiled into generated lister interfaces.
- Developers can add custom methods in separate non-generated expansion files if needed.

## State and Persistence
- No runtime state or persistence.

## Dependencies and Integration Points
- Go type system only; no imports in most expansion files.

## Risks and Edge Cases
- Regeneration should preserve extension points; custom expansion methods belong outside generated output.

## Test Signals
- Compile-time interface embedding is the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/expansion_generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshot.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshot.go

## Purpose
Generated cache lister for `volumegroupsnapshot` resources.

Source size: 70 lines, 3249 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotLister`, `volumeGroupSnapshotLister`, `VolumeGroupSnapshotNamespaceLister`, `volumeGroupSnapshotNamespaceLister`.
- Functions/methods: `NewVolumeGroupSnapshotLister`, `VolumeGroupSnapshots`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta1`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Top-level `List` scans all namespaces in the indexer.
- Namespace accessor returns a namespace lister whose `List` uses `cache.ListAllByNamespace` and whose `Get` uses `namespace/name` keys.
- Missing objects return typed Kubernetes NotFound errors.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshotclass.go

## Purpose
Generated cache lister for `volumegroupsnapshotclass` resources.

Source size: 48 lines, 2123 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotClassLister`, `volumeGroupSnapshotClassLister`.
- Functions/methods: `NewVolumeGroupSnapshotClassLister`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta1`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans the shared indexer with a label selector.
- `Get` resolves cluster-scoped objects by name and returns a Kubernetes NotFound error when absent.
- Returned objects are pointers from the informer cache and must be treated read-only.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshotcontent.go

## Purpose
Generated cache lister for `volumegroupsnapshotcontent` resources.

Source size: 48 lines, 2159 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotContentLister`, `volumeGroupSnapshotContentLister`.
- Functions/methods: `NewVolumeGroupSnapshotContentLister`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta1`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans all cached objects with a selector.
- `Get` resolves cluster-scoped content objects by name and returns NotFound on cache miss.
- The lister is constructed with `New...Lister(indexer)`.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta1/volumegroupsnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/expansion_generated.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/expansion_generated.go

## Purpose
Generated empty lister expansion interfaces for future custom methods on snapshot listers.

Source size: 35 lines, 1329 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotListerExpansion`, `VolumeGroupSnapshotNamespaceListerExpansion`, `VolumeGroupSnapshotClassListerExpansion`, `VolumeGroupSnapshotContentListerExpansion`.

## Control Flow
- Declares no-op expansion interfaces compiled into generated lister interfaces.
- Developers can add custom methods in separate non-generated expansion files if needed.

## State and Persistence
- No runtime state or persistence.

## Dependencies and Integration Points
- Go type system only; no imports in most expansion files.

## Risks and Edge Cases
- Regeneration should preserve extension points; custom expansion methods belong outside generated output.

## Test Signals
- Compile-time interface embedding is the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/expansion_generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshot.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshot.go

## Purpose
Generated cache lister for `volumegroupsnapshot` resources.

Source size: 70 lines, 3249 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotLister`, `volumeGroupSnapshotLister`, `VolumeGroupSnapshotNamespaceLister`, `volumeGroupSnapshotNamespaceLister`.
- Functions/methods: `NewVolumeGroupSnapshotLister`, `VolumeGroupSnapshots`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta2`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Top-level `List` scans all namespaces in the indexer.
- Namespace accessor returns a namespace lister whose `List` uses `cache.ListAllByNamespace` and whose `Get` uses `namespace/name` keys.
- Missing objects return typed Kubernetes NotFound errors.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshotclass.go

## Purpose
Generated cache lister for `volumegroupsnapshotclass` resources.

Source size: 48 lines, 2123 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotClassLister`, `volumeGroupSnapshotClassLister`.
- Functions/methods: `NewVolumeGroupSnapshotClassLister`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta2`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans the shared indexer with a label selector.
- `Get` resolves cluster-scoped objects by name and returns a Kubernetes NotFound error when absent.
- Returned objects are pointers from the informer cache and must be treated read-only.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshotcontent.go

## Purpose
Generated cache lister for `volumegroupsnapshotcontent` resources.

Source size: 48 lines, 2159 bytes.

## Important APIs, Types, and Functions
- Go package `v1beta2`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeGroupSnapshotContentLister`, `volumeGroupSnapshotContentLister`.
- Functions/methods: `NewVolumeGroupSnapshotContentLister`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumegroupsnapshot/v1beta2`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/listers`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans all cached objects with a selector.
- `Get` resolves cluster-scoped content objects by name and returns NotFound on cache miss.
- The lister is constructed with `New...Lister(indexer)`.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumegroupsnapshot/v1beta2/volumegroupsnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/expansion_generated.go -->
# sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/expansion_generated.go

## Purpose
Generated empty lister expansion interfaces for future custom methods on snapshot listers.

Source size: 35 lines, 1264 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeSnapshotListerExpansion`, `VolumeSnapshotNamespaceListerExpansion`, `VolumeSnapshotClassListerExpansion`, `VolumeSnapshotContentListerExpansion`.

## Control Flow
- Declares no-op expansion interfaces compiled into generated lister interfaces.
- Developers can add custom methods in separate non-generated expansion files if needed.

## State and Persistence
- No runtime state or persistence.

## Dependencies and Integration Points
- Go type system only; no imports in most expansion files.

## Risks and Edge Cases
- Regeneration should preserve extension points; custom expansion methods belong outside generated output.

## Test Signals
- Compile-time interface embedding is the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/expansion_generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshot.go -->
# sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshot.go

## Purpose
Generated cache lister for `volumesnapshot` resources.

Source size: 99 lines, 3722 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeSnapshotLister`, `volumeSnapshotLister`, `VolumeSnapshotNamespaceLister`, `volumeSnapshotNamespaceLister`.
- Functions/methods: `NewVolumeSnapshotLister`, `List`, `VolumeSnapshots`, `List`, `Get`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumesnapshot/v1`, `k8s.io/apimachinery/pkg/api/errors`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/tools/cache`.

## Control Flow
- Top-level `List` scans all namespaces in the indexer.
- Namespace accessor returns a namespace lister whose `List` uses `cache.ListAllByNamespace` and whose `Get` uses `namespace/name` keys.
- Missing objects return typed Kubernetes NotFound errors.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshotclass.go -->
# sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshotclass.go

## Purpose
Generated cache lister for `volumesnapshotclass` resources.

Source size: 68 lines, 2455 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeSnapshotClassLister`, `volumeSnapshotClassLister`.
- Functions/methods: `NewVolumeSnapshotClassLister`, `List`, `Get`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumesnapshot/v1`, `k8s.io/apimachinery/pkg/api/errors`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans the shared indexer with a label selector.
- `Get` resolves cluster-scoped objects by name and returns a Kubernetes NotFound error when absent.
- Returned objects are pointers from the informer cache and must be treated read-only.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshotclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshotcontent.go -->
# sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshotcontent.go

## Purpose
Generated cache lister for `volumesnapshotcontent` resources.

Source size: 68 lines, 2502 bytes.

## Important APIs, Types, and Functions
- Go package `v1`.
- Generated file marked `DO NOT EDIT`; source of truth is API type/code-generator input.
- Types/interfaces: `VolumeSnapshotContentLister`, `volumeSnapshotContentLister`.
- Functions/methods: `NewVolumeSnapshotContentLister`, `List`, `Get`.
- Key imports: `github.com/kubernetes-csi/external-snapshotter/client/v8/apis/volumesnapshot/v1`, `k8s.io/apimachinery/pkg/api/errors`, `k8s.io/apimachinery/pkg/labels`, `k8s.io/client-go/tools/cache`.

## Control Flow
- `List` scans all cached objects with a selector.
- `Get` resolves cluster-scoped content objects by name and returns NotFound on cache miss.
- The lister is constructed with `New...Lister(indexer)`.

## State and Persistence
- Reads from the shared informer cache/indexer only.
- No writes or durable persistence; authoritative state remains in the Kubernetes API server.
- Object pointers are cache-owned read-only views of Kubernetes state.

## Dependencies and Integration Points
- Generated API type package, Kubernetes api/errors, labels, client-go cache.

## Risks and Edge Cases
- Cache staleness can affect controller decisions until informers resync or receive watch updates.
- Callers must not mutate returned objects without deep-copying.
- Resource names in NotFound errors must match API resources for good diagnostics.

## Test Signals
- Generated by lister-gen; exercised by controllers using listers after cache sync.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/client/listers/volumesnapshot/v1/volumesnapshotcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cloudbuild.yaml -->
# sources/control-plane/external-snapshotter/cloudbuild.yaml

## Purpose
Cloud Build pipeline for building external-snapshotter container images.

Source size: 47 lines, 2334 bytes.

## Important APIs, Types, and Functions
- Cloud Build config with 1 steps.

## Control Flow
- Cloud Build executes configured build steps in order using repository source context.
- Steps build command images such as csi-snapshotter, snapshot-controller, and conversion webhook and publish tagged outputs.
- Dockerfiles under `cmd/*` provide per-binary image definitions.

## State and Persistence
- No repository runtime state; build artifacts are container images in the configured registry.
- Build substitutions/tags determine image names and versions.

## Dependencies and Integration Points
- Google Cloud Build, Docker/build tooling, command Dockerfiles, repository Go binaries.

## Risks and Edge Cases
- Tag/substitution drift can publish images under unexpected names.
- Dockerfile or binary path mismatches fail builds late in the pipeline.

## Test Signals
- Successful Cloud Build execution and runnable images are the validation signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/csi-snapshotter/Dockerfile -->
# sources/control-plane/external-snapshotter/cmd/csi-snapshotter/Dockerfile

## Purpose
Container image definition for the `csi-snapshotter` external-snapshotter binary.

Source size: 7 lines, 226 bytes.

## Important APIs, Types, and Functions
- Base stages: `FROM gcr.io/distroless/static:latest`.
- Copy steps: `COPY ${binary} csi-snapshotter`.
- Runtime directives: `ENTRYPOINT ["/csi-snapshotter"]`.

## Control Flow
- Build context provides a prebuilt binary or staged artifact.
- The image copies the command binary into the runtime filesystem and sets process/user directives.
- Kubernetes Deployment manifests run this image as the controller or sidecar container.

## State and Persistence
- No runtime persistence is declared by the Dockerfile.
- Container state is ephemeral; Kubernetes objects and CSI driver state are external.

## Dependencies and Integration Points
- Container base image, built Go command binary, image build system/cloudbuild, Kubernetes deployment manifests.

## Risks and Edge Cases
- Binary path/name must match the command built by release tooling.
- Base image and user settings affect CVE profile and runtime permissions.

## Test Signals
- Image build success and command startup in Kubernetes are the relevant signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/csi-snapshotter/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main.go -->
# sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main.go

## Purpose
Main entrypoint for the CSI external-snapshotter sidecar that talks to a CSI driver and reconciles VolumeSnapshotContent operations.

Source size: 376 lines, 14754 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Functions/methods: `main`, `buildConfig`, `supportsControllerCreateSnapshot`, `supportsGroupControllerCreateVolumeGroupSnapshot`.
- Key imports: `context`, `flag`, `fmt`, `net/http`, `os`, `os/signal`, `strings`, `sync`, `time`, `google.golang.org/grpc`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/labels`, ...

## Control Flow
- Parses feature gates, logging, common CSI sidecar flags, retry, metrics, leader election, and node-deployment options.
- Builds Kubernetes and snapshot clientsets, shared informer factories, optional node-local content filtering, and event schemes.
- Connects to the CSI endpoint, discovers driver name, probes readiness, verifies snapshot capability, optionally checks group snapshot capability, then constructs sidecar controllers.
- Starts metrics/health endpoints, leader election or direct controller loops, informer factories, and worker queues until shutdown.

## State and Persistence
- Maintains process-local clients, gRPC connection, metrics manager, informer caches, workqueues, and controller goroutines.
- Persists desired/observed snapshot state through Kubernetes snapshot CRs and CSI driver calls.
- Node deployment mode filters content by the managed-by label derived from `NODE_NAME`.

## Dependencies and Integration Points
- CSI protobuf/gRPC APIs, csi-lib-utils config/connection/rpc/metrics/leader election, Kubernetes client-go, generated snapshot client/informers, sidecar controller, snapshotter, group snapshotter.

## Risks and Edge Cases
- Requires a reachable CSI endpoint and driver support for create/delete snapshot or exits.
- Leader election conflicts with node-deployment mode by design.
- Feature gate and driver capability mismatches can leave group snapshot functionality disabled or warning-only.

## Test Signals
- Companion `main_test.go` covers capability probing helper behavior with mock CSI responses.
- Integration coverage requires a Kubernetes cluster and CSI driver.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main_test.go -->
# sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main_test.go

## Purpose
Unit tests for the CSI snapshotter command entrypoint support checks and mock CSI server setup.

Source size: 164 lines, 4555 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Functions/methods: `Test_supportsControllerCreateSnapshot`, `createMockServer`.
- Key imports: `context`, `fmt`, `testing`, `github.com/container-storage-interface/spec/lib/go/csi`, `github.com/golang/mock/gomock`, `github.com/kubernetes-csi/csi-lib-utils/connection`, `github.com/kubernetes-csi/csi-lib-utils/metrics`, `github.com/kubernetes-csi/csi-test/v5/driver`, `github.com/kubernetes-csi/csi-test/v5/utils`, `google.golang.org/grpc`.

## Control Flow
- Creates a mock CSI driver and gRPC connection.
- Programs expected `ControllerGetCapabilities` responses with gomock.
- Calls support-detection helpers and compares errors/results for capability, error, empty, and absent-capability cases.

## State and Persistence
- Test state is in-memory mock server state plus a local gRPC connection; no Kubernetes API state is written.
- Mock expectations are consumed once per test case and verified by gomock at teardown.

## Dependencies and Integration Points
- CSI protobuf APIs, csi-test mock driver, gomock, csi-lib-utils connection and metrics helpers, Go testing package.

## Risks and Edge Cases
- Tests cover snapshot capability detection but not the full `main` startup path.
- Mock server lifecycle must stop and close connections to avoid leaked goroutines.

## Test Signals
- This file is itself the test signal for `supportsControllerCreateSnapshot`.
- Cases include success, gRPC error, missing capability, nil capability, and empty capability list.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-controller/Dockerfile -->
# sources/control-plane/external-snapshotter/cmd/snapshot-controller/Dockerfile

## Purpose
Container image definition for the `snapshot-controller` external-snapshotter binary.

Source size: 7 lines, 225 bytes.

## Important APIs, Types, and Functions
- Base stages: `FROM gcr.io/distroless/static:latest`.
- Copy steps: `COPY ${binary} snapshot-controller`.
- Runtime directives: `ENTRYPOINT ["/snapshot-controller"]`.

## Control Flow
- Build context provides a prebuilt binary or staged artifact.
- The image copies the command binary into the runtime filesystem and sets process/user directives.
- Kubernetes Deployment manifests run this image as the controller or sidecar container.

## State and Persistence
- No runtime persistence is declared by the Dockerfile.
- Container state is ephemeral; Kubernetes objects and CSI driver state are external.

## Dependencies and Integration Points
- Container base image, built Go command binary, image build system/cloudbuild, Kubernetes deployment manifests.

## Risks and Edge Cases
- Binary path/name must match the command built by release tooling.
- Base image and user settings affect CVE profile and runtime permissions.

## Test Signals
- Image build success and command startup in Kubernetes are the relevant signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-controller/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-controller/main.go -->
# sources/control-plane/external-snapshotter/cmd/snapshot-controller/main.go

## Purpose
Main entrypoint for the cluster-level snapshot controller that reconciles VolumeSnapshot, VolumeSnapshotContent, and optionally group snapshot APIs.

Source size: 383 lines, 14849 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Types/interfaces: `promklog`.
- Functions/methods: `ensureCustomResourceDefinitionsExist`, `main`, `buildConfig`, `Println`.
- Key imports: `context`, `flag`, `fmt`, `math`, `net`, `net/http`, `os`, `os/signal`, `strings`, `sync`, `time`, `k8s.io/client-go/informers/core/v1`, ...

## Control Flow
- Parses kubeconfig, logging, feature gates, worker counts, retry, leader election, metrics, distributed snapshotting, and volume-mode conversion flags.
- Builds clients and informer factories, optionally includes node informers, registers metrics and snapshot types, and constructs the common snapshot controller.
- Waits for required CRDs to exist with exponential backoff before running.
- Runs controller workers either under leader election or directly, starts informers/metrics HTTP server, and handles shutdown signals.

## State and Persistence
- Uses informer caches, workqueues, metrics, leader-election leases, and Kubernetes API writes to reconcile snapshot object status and bindings.
- The API server stores CRDs and snapshot objects; this process stores only transient cache/queue state.
- Distributed snapshotting adds node informer state for node-local volume handling.

## Dependencies and Integration Points
- Kubernetes client-go, generated snapshot client/informers, common-controller package, csi-lib-utils leader election, external-snapshotter metrics/features.

## Risks and Edge Cases
- Startup fails if CRDs are absent beyond `retry-crd-interval-max`.
- RBAC must allow list/watch/update on all snapshot and related core resources.
- Preventing volume-mode conversion is security-sensitive and should stay enabled unless deliberately changed.

## Test Signals
- CRD presence check is deterministic but needs API-server integration for full coverage.
- Controller behavior is tested in package-level controller tests outside this file.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-controller/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-conversion-webhook/Dockerfile -->
# sources/control-plane/external-snapshotter/cmd/snapshot-conversion-webhook/Dockerfile

## Purpose
Container image definition for the `snapshot-conversion-webhook` external-snapshotter binary.

Source size: 7 lines, 246 bytes.

## Important APIs, Types, and Functions
- Base stages: `FROM gcr.io/distroless/static:latest`.
- Copy steps: `COPY ${binary} snapshot-conversion-webhook`.
- Runtime directives: `ENTRYPOINT ["/snapshot-conversion-webhook"]`.

## Control Flow
- Build context provides a prebuilt binary or staged artifact.
- The image copies the command binary into the runtime filesystem and sets process/user directives.
- Kubernetes Deployment manifests run this image as the controller or sidecar container.

## State and Persistence
- No runtime persistence is declared by the Dockerfile.
- Container state is ephemeral; Kubernetes objects and CSI driver state are external.

## Dependencies and Integration Points
- Container base image, built Go command binary, image build system/cloudbuild, Kubernetes deployment manifests.

## Risks and Edge Cases
- Binary path/name must match the command built by release tooling.
- Base image and user settings affect CVE profile and runtime permissions.

## Test Signals
- Image build success and command startup in Kubernetes are the relevant signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-conversion-webhook/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-conversion-webhook/main.go -->
# sources/control-plane/external-snapshotter/cmd/snapshot-conversion-webhook/main.go

## Purpose
Main entrypoint for the HTTPS snapshot conversion webhook server.

Source size: 82 lines, 2135 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Functions/methods: `main`.
- Key imports: `context`, `crypto/tls`, `flag`, `k8s.io/component-base/logs`, `k8s.io/component-base/logs/api/v1`, `k8s.io/klog/v2`, `github.com/kubernetes-csi/csi-lib-utils/standardflags`, `github.com/kubernetes-csi/external-snapshotter/v8/pkg/webhook`.

## Control Flow
- Parses TLS certificate, private key, and port flags with logging setup.
- Validates required TLS paths, creates a cert watcher, configures `tls.Config.GetCertificate`, and starts the webhook server with a cancellable context.
- The server handles conversion requests through the `pkg/webhook` package.

## State and Persistence
- Maintains process-local TLS watcher and HTTP server state.
- No Kubernetes objects are persisted by this file directly; it serves conversion traffic from the API server.

## Dependencies and Integration Points
- Go TLS/context/flag, component-base logging, csi-lib-utils standardflags, external-snapshotter webhook package.

## Risks and Edge Cases
- Missing or unreadable cert/key files are fatal.
- Webhook Deployment/Service/CA bundle must match the serving cert or API conversion fails.

## Test Signals
- Operational test is API-server conversion through the deployed webhook example.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/cmd/snapshot-conversion-webhook/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/kustomization.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/kustomization.yaml

## Purpose
deployment manifest for `kustomize.config.k8s.io/v1beta1` `Kustomization` named `unnamed`.

Source size: 7 lines, 175 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `kustomize.config.k8s.io/v1beta1` `Kustomization` named `unnamed`.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/rbac-csi-snapshotter.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/rbac-csi-snapshotter.yaml

## Purpose
deployment manifest for `v1` `ServiceAccount` named `csi-snapshotter`.

Source size: 93 lines, 3099 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `v1` `ServiceAccount` named `csi-snapshotter`.
- Contains 5 YAML documents; document kinds: ServiceAccount, ClusterRole, ClusterRoleBinding, Role, RoleBinding.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/rbac-csi-snapshotter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/rbac-external-provisioner.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/rbac-external-provisioner.yaml

## Purpose
deployment manifest for `v1` `ServiceAccount` named `csi-provisioner`.

Source size: 100 lines, 2880 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `v1` `ServiceAccount` named `csi-provisioner`.
- Important fields: namespace `default`.
- Contains 5 YAML documents; document kinds: ServiceAccount, ClusterRole, ClusterRoleBinding, Role, RoleBinding.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/rbac-external-provisioner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/setup-csi-snapshotter.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/setup-csi-snapshotter.yaml

## Purpose
deployment manifest for `rbac.authorization.k8s.io/v1` `ClusterRoleBinding` named `csi-snapshotter-provisioner-role`.

Source size: 121 lines, 3391 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `rbac.authorization.k8s.io/v1` `ClusterRoleBinding` named `csi-snapshotter-provisioner-role`.
- Contains 4 YAML documents; document kinds: ClusterRoleBinding, RoleBinding, Service, StatefulSet.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/csi-snapshotter/setup-csi-snapshotter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/kustomization.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/kustomization.yaml

## Purpose
deployment manifest for `kustomize.config.k8s.io/v1beta1` `Kustomization` named `unnamed`.

Source size: 6 lines, 148 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `kustomize.config.k8s.io/v1beta1` `Kustomization` named `unnamed`.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml

## Purpose
deployment manifest for `v1` `ServiceAccount` named `snapshot-controller`.

Source size: 103 lines, 3354 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `v1` `ServiceAccount` named `snapshot-controller`.
- Important fields: namespace `kube-system`.
- Contains 5 YAML documents; document kinds: ServiceAccount, ClusterRole, ClusterRoleBinding, Role, RoleBinding.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml

## Purpose
deployment manifest for `apps/v1` `Deployment` named `snapshot-controller`.

Source size: 44 lines, 1832 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `apps/v1` `Deployment` named `snapshot-controller`.
- Important fields: `spec.minReadySeconds=35`, `spec.replicas=2`, `spec.selector` (matchLabels), `spec.strategy` (rollingUpdate, type), `spec.template` (metadata, spec), namespace `kube-system`.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/create-cert.sh -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/create-cert.sh

## Purpose
Creates example TLS material for the snapshot conversion webhook deployment.

Source size: 128 lines, 3579 bytes.

## Important APIs, Types, and Functions
- Shell functions: `usage`.
- External commands/helpers: `base64`, `kubectl`, `mktemp`, `openssl`.

## Control Flow
- Generates a CA and serving certificate/key with OpenSSL for the webhook service DNS names.
- Creates or updates Kubernetes TLS/CA secrets expected by the webhook example.
- Feeds the generated CA to the webhook example patching flow.

## State and Persistence
- Creates local certificate files and Kubernetes Secret state for the example namespace.
- Certificate validity and SANs determine API-server trust.

## Dependencies and Integration Points
- openssl, kubectl, Kubernetes cluster access, webhook example namespace/service naming.

## Risks and Edge Cases
- Example certificates are for development/demo use and must not be reused as production PKI.
- Service DNS names, namespace, and CA bundle must match the webhook manifest.

## Test Signals
- Successful webhook TLS handshake and API conversion calls validate the output.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/create-cert.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/patch-ca-bundle.sh -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/patch-ca-bundle.sh

## Purpose
Patches the webhook example manifest or live configuration with the generated CA bundle.

Source size: 12 lines, 406 bytes.

## Important APIs, Types, and Functions
- External commands/helpers: `kubectl`.

## Control Flow
- Reads CA certificate material, base64-encodes or injects it, and patches the webhook configuration.
- Updates the `caBundle` field so the Kubernetes API server trusts the conversion webhook service.

## State and Persistence
- Mutates webhook configuration YAML or Kubernetes API state depending on invocation.
- No controller state is stored locally beyond generated cert files.

## Dependencies and Integration Points
- kubectl/sed/base64 tooling, generated CA certificate, webhook example manifest.

## Risks and Edge Cases
- Incorrect CA bundle breaks CRD conversion requests.
- Patching assumptions can drift if webhook YAML structure changes.

## Test Signals
- API-server conversion through the webhook and successful `kubectl apply` of CRDs validate the patch.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/patch-ca-bundle.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/webhook.yaml -->
# sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/webhook.yaml

## Purpose
deployment manifest for `apps/v1` `Deployment` named `snapshot-conversion-webhook-deployment`.

Source size: 48 lines, 1587 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `apps/v1` `Deployment` named `snapshot-conversion-webhook-deployment`.
- Important fields: `spec.replicas=1`, `spec.selector` (matchLabels), `spec.template` (metadata, spec), namespace `default`, labels `app.kubernetes.io/name`.
- Contains 2 YAML documents; document kinds: Deployment, Service.

## Control Flow
- Consumed by `kubectl apply` or kustomize overlays to install snapshotter components, service accounts, RBAC, deployments, and webhook resources.
- Controllers then use in-cluster service accounts to watch snapshot CRDs and coordinate with CSI sidecars.
- Manifest ordering matters around CRDs, RBAC, Deployments, Services, and webhook CA bundle injection.

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
- Validated operationally by deploying the external-snapshotter manifests into a Kubernetes cluster.
- Kustomize references and RBAC verbs are primary integration signals.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/webhook.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/groupsnapshot-v1beta1.yaml -->
# sources/control-plane/external-snapshotter/examples/kubernetes/groupsnapshot-v1beta1.yaml

## Purpose
example manifest for `groupsnapshot.storage.k8s.io/v1beta1` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.

Source size: 13 lines, 379 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta1` `VolumeGroupSnapshot` named `new-groupsnapshot-demo`.
- Important fields: `spec.source` (selector), `spec.volumeGroupSnapshotClassName='csi-hostpath-groupsnapclass'`.

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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/groupsnapshot-v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/groupsnapshotclass-v1beta1.yaml -->
# sources/control-plane/external-snapshotter/examples/kubernetes/groupsnapshotclass-v1beta1.yaml

## Purpose
example manifest for `groupsnapshot.storage.k8s.io/v1beta1` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`.

Source size: 7 lines, 181 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `groupsnapshot.storage.k8s.io/v1beta1` `VolumeGroupSnapshotClass` named `csi-hostpath-groupsnapclass`.

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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/groupsnapshotclass-v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/invalid-snapshot-v1.yaml -->
# sources/control-plane/external-snapshotter/examples/kubernetes/invalid-snapshot-v1.yaml

## Purpose
example manifest for `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-demo-v1`.

Source size: 10 lines, 339 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshot` named `new-snapshot-demo-v1`.
- Important fields: `spec.source` (persistentVolumeClaimName, volumeSnapshotContentName), `spec.volumeSnapshotClassName='csi-hostpath-snapclass-v1'`.

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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/invalid-snapshot-v1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/pvc.yaml -->
# sources/control-plane/external-snapshotter/examples/kubernetes/pvc.yaml

## Purpose
example manifest for `v1` `PersistentVolumeClaim` named `hpvc`.

Source size: 12 lines, 193 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `v1` `PersistentVolumeClaim` named `hpvc`.
- Important fields: `spec.accessModes` (1 item list), `spec.resources` (requests), `spec.storageClassName='csi-hostpath-sc'`.

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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/restore.yaml -->
# sources/control-plane/external-snapshotter/examples/kubernetes/restore.yaml

## Purpose
example manifest for `v1` `PersistentVolumeClaim` named `hpvc-restore`.

Source size: 16 lines, 309 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `v1` `PersistentVolumeClaim` named `hpvc-restore`.
- Important fields: `spec.accessModes` (1 item list), `spec.dataSource` (apiGroup, kind, name), `spec.resources` (requests), `spec.storageClassName='csi-hostpath-sc'`.

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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/snapshot-v1.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/snapshot-v1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/snapshotclass-v1.yaml -->
# sources/control-plane/external-snapshotter/examples/kubernetes/snapshotclass-v1.yaml

## Purpose
example manifest for `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named `csi-hostpath-snapclass-v1`.

Source size: 7 lines, 164 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named `csi-hostpath-snapclass-v1`.

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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/snapshotclass-v1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/storageclass.yaml -->
# sources/control-plane/external-snapshotter/examples/kubernetes/storageclass.yaml

## Purpose
example manifest for `storage.k8s.io/v1` `StorageClass` named `csi-hostpath-sc`.

Source size: 8 lines, 185 bytes.

## Important APIs, Types, and Functions
- Kubernetes API object: `storage.k8s.io/v1` `StorageClass` named `csi-hostpath-sc`.

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
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/examples/kubernetes/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/hack/verify-vendor.sh -->
# sources/control-plane/external-snapshotter/hack/verify-vendor.sh

## Purpose
Verifies vendored dependencies are in sync with module metadata.

Source size: 39 lines, 1459 bytes.

## Important APIs, Types, and Functions
- External commands/helpers: `go`.

## Control Flow
- Runs Go vendoring verification logic from the repository hack tooling.
- Fails when `vendor/` differs from `go.mod`/`go.sum` expectations.

## State and Persistence
- May create temporary files during verification but should not persist changes in a clean run.
- Dependency state is represented by module files and vendor contents.

## Dependencies and Integration Points
- Go toolchain and repository module/vendor layout.

## Risks and Edge Cases
- Vendoring checks can be sensitive to Go version and environment.
- Failure indicates dependency drift that should be regenerated, not ignored.

## Test Signals
- CI can run this script as a presubmit signal.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/hack/verify-vendor.sh -->
