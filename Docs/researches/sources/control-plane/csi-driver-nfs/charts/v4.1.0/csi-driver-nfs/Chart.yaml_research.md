# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v4.1.0.

Important APIs/types/functions: Helm chart fields `apiVersion`, `appVersion: v4.1.0`, `description`, `name`, and `version`.

Control flow: Static packaging metadata.

State and persistence: Stored in chart packages and Helm release metadata.

Dependencies and integration points: Identifies the v4.1.0 templates that add node service-account creation and scheduling customization.

Risks: Metadata compatibility must be checked against rendered objects. Test signals: `helm lint`, package index check, and install dry-run.
