## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/Chart.yaml

Purpose: declares the v0.2.0 SMB CSI Helm chart release metadata. It uses API v1, appVersion `v0.2.0`, description, chart name, and matching version.

State is historical Helm metadata. Dependencies are v0.2.0 templates, including the newly added controller deployment and RBAC. Risks are legacy `v`-prefixed version handling and compatibility with modern Helm/Kubernetes. Test signal is chart package/index validation.
