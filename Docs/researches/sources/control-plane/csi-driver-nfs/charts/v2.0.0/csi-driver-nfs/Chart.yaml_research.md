# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/Chart.yaml

Purpose: Helm chart metadata for CSI NFS chart release v2.0.0.

Important APIs/types/functions: Helm v1 chart fields `apiVersion`, `appVersion`, `description`, `name`, and `version`.

Control flow: There is no runtime control flow; Helm uses this metadata for packaging, dependency resolution, install history, and repository indexes.

State and persistence: Persists only as chart package metadata and release metadata after install.

Dependencies and integration points: Links the template set under the v2.0.0 chart to application version `v2.0.0`.

Risks: v2 uses older Kubernetes manifests such as `storage.k8s.io/v1beta1` CSIDriver in its templates, so chart metadata alone may look installable on clusters where rendered APIs are removed. Test signals: `helm lint`, package index validation, and install dry-run against target Kubernetes versions.
