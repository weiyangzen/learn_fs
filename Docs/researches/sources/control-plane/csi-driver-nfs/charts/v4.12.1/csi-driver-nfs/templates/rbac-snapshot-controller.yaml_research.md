# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template provides the optional standalone snapshot controller's service account, cluster permissions, and leader-election permissions.

## APIs, Control Flow, and State
It renders only when `externalSnapshotter.enabled` is true. It grants snapshot-controller access to PVs, PVCs, events, `VolumeSnapshotClass`, `VolumeSnapshotContent`, `VolumeSnapshot`, status subresources, and release-namespace leases. It optionally grants Node reads if `externalSnapshotter.enabledDistributedSnapshotting` is set.

## Dependencies and Integration Points
The RBAC is consumed by `csi-snapshot-controller.yaml` and requires the snapshot CRDs to exist. It integrates with Kubernetes lease state for leader election and writes snapshot status state into the Kubernetes API.

## Risks and Test Signals
The optional distributed snapshotting value is undeclared in defaults, so enabling it depends on caller-provided values. Test render output for that flag, `kubectl auth can-i` for all snapshot verbs, and end-to-end snapshot deletion policy behavior. This file is unchanged from 4.12.0.
