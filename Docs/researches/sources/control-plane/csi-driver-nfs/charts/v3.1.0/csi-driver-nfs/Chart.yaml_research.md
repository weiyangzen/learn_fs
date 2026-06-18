# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v3.1.0.

Important APIs/types/functions: Static Helm chart fields `apiVersion: v1`, `appVersion: v3.1.0`, `description`, `name`, and `version`.

Control flow: No runtime control flow; consumed by Helm package/install/index commands.

State and persistence: Stored in packaged chart and Helm release metadata.

Dependencies and integration points: Identifies the v3.1.0 template/value set, which adds inline-volume and mount-permission options relative to prior versions.

Risks: Metadata does not express Kubernetes API compatibility. Test signals: chart lint/package and dry-run install against target clusters.
