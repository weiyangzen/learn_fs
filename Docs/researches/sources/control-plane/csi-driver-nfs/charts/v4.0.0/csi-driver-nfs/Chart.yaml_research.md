# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v4.0.0.

Important APIs/types/functions: Helm `apiVersion: v1`, `appVersion: v4.0.0`, `description`, `name`, and `version: v4.0.0`.

Control flow: Static metadata only.

State and persistence: Chart and Helm release metadata.

Dependencies and integration points: Marks the v4.0.0 template generation that introduces kubeletDir and FSGroup default changes.

Risks: Uses older chart API metadata while templates target modern Kubernetes APIs. Test signals: `helm lint`, package validation, and rendered manifest dry-run.
