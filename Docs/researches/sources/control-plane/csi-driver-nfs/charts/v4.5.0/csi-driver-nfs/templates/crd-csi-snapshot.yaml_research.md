# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose

This template installs the CSI snapshot CRDs for v4.5.0. It emits `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs for the `snapshot.storage.k8s.io` API group, preserving the v1 snapshot API and deprecated v1beta1 schemas.

## APIs, control flow, and state

Unlike v4.4.0, rendering is gated by both `.Values.externalSnapshotter.enabled` and `.Values.externalSnapshotter.customResourceDefinitions.enabled`. Each CRD includes Helm annotation `"helm.sh/resource-policy": keep`, so Helm should leave the CRD behind during uninstall. The CRD schemas model snapshot desired state and controller-observed status: `VolumeSnapshot.spec.source`, class selection, binding status, readiness, restore size, errors, `VolumeSnapshotClass.driver/deletionPolicy/parameters`, and `VolumeSnapshotContent` binding/source/status fields.

## Dependencies and integration points

The CRDs integrate with the API server, the optional snapshot-controller, the `csi-snapshotter` sidecar, and snapshot RBAC. The new `customResourceDefinitions.enabled` value lets cluster operators use a platform-provided snapshot API while still enabling the snapshot controller if desired.

## Risks and test signals

The double gate is safer but can surprise upgrades from v4.4.0: disabling the controller disables CRD rendering too, and setting `customResourceDefinitions.enabled=false` assumes CRDs already exist. `resource-policy: keep` prevents accidental CRD removal but can leave stale CRD versions after chart uninstall. Test `helm template` for all enabled/disabled combinations, validate server-side application of all three CRDs, check Helm uninstall behavior in a disposable cluster, and verify snapshot resource validation and status updates.
