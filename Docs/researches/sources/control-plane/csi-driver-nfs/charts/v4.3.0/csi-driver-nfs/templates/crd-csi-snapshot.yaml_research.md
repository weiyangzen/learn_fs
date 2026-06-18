# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This v4.3.0 template installs the snapshot CRDs when the external snapshotter is enabled. It predates the later separate `customResourceDefinitions.enabled` value gate.

## Important APIs, Types, and Functions
It emits `apiextensions.k8s.io/v1` CRDs for `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent`, with `v1` storage schemas and deprecated non-served `v1beta1` schemas. It includes the upstream approval and controller-gen annotations but does not include Helm's `resource-policy: keep` annotation in this version.

## Control Flow, State, and Persistence
The only gate is `externalSnapshotter.enabled`, so enabling the snapshot controller also attempts to create cluster-wide CRDs. CRDs persist as Kubernetes API extensions, but without the Helm keep annotation their uninstall/upgrade lifecycle is more tightly tied to the release than v4.13.x.

## Dependencies and Integration Points
The CRDs are consumed by the v4.3.0 snapshot controller, snapshot RBAC, and controller-side `csi-snapshotter` sidecar. They must be present before the snapshot controller becomes ready.

## Risks and Test Signals
Risks include CRD ownership conflicts when a cluster already has snapshot CRDs, less flexible CRD lifecycle control than v4.13.x, and snapshot controller crash loops if CRDs fail to apply. Signals are `helm template` with `externalSnapshotter.enabled`, server-side dry-run, CRD discovery, and a dynamic snapshot readiness test.
