# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
Optionally installs external-snapshotter CRDs for the v4.9.0 chart.

## Important APIs, Types, And Functions
Defines CRDs for namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. The schemas include v1 storage versions, deprecated v1beta1 compatibility schemas, source one-of constraints, status subresources, and printer columns.

## Control Flow
Helm emits all CRDs only when both snapshotter and CRD installation flags are true. Kubernetes stores the definitions and validates subsequent snapshot API objects against the OpenAPI schemas.

## State And Persistence
CRDs persist as cluster API extensions and use `helm.sh/resource-policy: keep`. The resources they enable store snapshot requests, classes, content handles, status, readiness, restore size, and errors.

## Dependencies And Integration Points
Requires snapshot controller and csi-snapshotter sidecar compatible with the v1 snapshot APIs. Integrates with RBAC and the optional snapshot controller deployment in this chart.

## Risks And Edge Cases
Byte-identical to the v4.7.0 and v4.8.0 CRD templates here, so CRD versions do not advance in v4.9.0. CRD ownership by Helm can conflict with cluster-level snapshot installations, and keep policy leaves resources after uninstall.

## Test Signals
`helm template` with snapshot CRDs enabled, Kubernetes server-side dry-run, and end-to-end `VolumeSnapshot` creation and restore checks.
