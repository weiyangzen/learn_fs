# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/crd-csi-snapshot.yaml

Purpose: conditionally installs CSI snapshot CRDs required for external snapshotting support.

Important APIs and types: rendered only when both `.Values.externalSnapshotter.enabled` and `.Values.externalSnapshotter.customResourceDefinitions.enabled` are true. Defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs in `snapshot.storage.k8s.io`, with v1 served/storage versions and deprecated v1beta1 schemas marked `served: false`. CRDs carry `helm.sh/resource-policy: keep`.

Control flow: Helm template emits three large CRD YAML documents. Kubernetes API server registers namespaced `VolumeSnapshot` and cluster-scoped class/content resources. Snapshot controller and CSI snapshotter sidecar then reconcile these APIs.

State and persistence: creates cluster-scoped CRDs that persist after Helm uninstall because of the keep policy. Snapshot custom resources and their status subresources become persistent Kubernetes API objects.

Dependencies and integration: integrates with `csi-snapshot-controller.yaml`, controller sidecar snapshotter in `csi-nfs-controller.yaml`, and external-snapshotter CRD schemas.

Risks: CRDs are large copied schemas and can drift from external-snapshotter releases. Helm does not manage CRD upgrades cleanly, and keep policy leaves resources behind. v1beta1 is present but not served, which can break old clients expecting beta APIs.

Test signals: Helm render/install, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, snapshot controller readiness, and snapshot E2E tests.
