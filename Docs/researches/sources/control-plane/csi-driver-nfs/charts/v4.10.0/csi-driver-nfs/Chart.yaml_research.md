# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v4.10.0.

Important APIs/types/functions: Helm v1 chart fields with `appVersion: v4.10.0` and `version: v4.10.0`.

Control flow: Static metadata used by Helm packaging and install history.

State and persistence: Chart/release metadata only.

Dependencies and integration points: Identifies the richer v4.10.0 chart set including resizer, snapshotter, snapshot CRDs, StorageClass, and VolumeSnapshotClass templates.

Risks: The `v` prefix differs from later v4.11.0/v4.12.0 metadata and may matter for tooling that parses semver strictly. Test signals: `helm lint`, package index validation, and dry-run install.
