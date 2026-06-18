# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart 4.11.0.

Important APIs/types/functions: Helm chart fields with `appVersion: 4.11.0` and `version: 4.11.0` without the earlier `v` prefix.

Control flow: Static metadata used by Helm.

State and persistence: Chart package and Helm release metadata.

Dependencies and integration points: Identifies the 4.11.0 chart content, which is largely identical to v4.10.0 except image/tag metadata.

Risks: Version string format changed from `v4.10.0`; automation expecting a leading `v` can break. Test signals: package/index validation and upgrade dry-run from v4.10.0.
