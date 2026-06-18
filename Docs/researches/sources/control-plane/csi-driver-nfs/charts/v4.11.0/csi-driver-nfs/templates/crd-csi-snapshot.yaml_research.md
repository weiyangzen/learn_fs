# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

Purpose: Optional snapshot CRD bundle for chart 4.11.0.

Important APIs/types/functions: Same `apiextensions.k8s.io/v1` CRD set as v4.10.0 for VolumeSnapshot, VolumeSnapshotClass, and VolumeSnapshotContent; gated by `externalSnapshotter.enabled` and `customResourceDefinitions.enabled`; `helm.sh/resource-policy: keep`.

Control flow: When both values are true, renders the CRD OpenAPI schemas, printer columns, status subresources, names, group, and version metadata.

State and persistence: Adds/updates cluster API extensions and persists them after uninstall due to keep policy.

Dependencies and integration points: Required by snapshot class/controller and CSI snapshotter workflows.

Risks: CRD ownership conflicts with cluster-managed CSI snapshot CRDs; kept resources complicate rollback. Test signals: compare existing CRD versions before install, then server-side dry-run and snapshot smoke.
