# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-snapshot-controller.yaml

Purpose: conditionally deploys the external snapshot-controller used for CSI snapshot lifecycle reconciliation.

Important APIs and types: rendered when `.Values.externalSnapshotter.enabled` is true. Creates an `apps/v1` Deployment with configurable name, replicas, labels, annotations, priority, resources, image, and service account. Uses leader election in the release namespace and `minReadySeconds: 15`.

Control flow: controller pod runs the snapshot-controller image, watches snapshot CRDs, and coordinates `VolumeSnapshot`/`VolumeSnapshotContent` lifecycle independently of the NFS controller sidecar snapshotter.

State and persistence: creates Deployment/Pods and leader-election state in Kubernetes. It manages snapshot API objects created by users.

Dependencies and integration: requires snapshot CRDs, RBAC/service account templates, image values, and optional controller affinity/tolerations inherited from chart values.

Risks: the template reuses `.Values.controller.affinity`, `runOnControlPlane`, `runOnMaster`, and tolerations rather than externalSnapshotter-specific placement values, which couples controller placement settings. If CRDs are disabled or already incompatible, pods may fail readiness.

Test signals: Deployment rollout, snapshot-controller logs, CRD availability, and snapshot create/delete E2E.
