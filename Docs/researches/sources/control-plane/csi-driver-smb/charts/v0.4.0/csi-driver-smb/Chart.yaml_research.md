## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/Chart.yaml

Purpose: declares SMB CSI chart v0.4.0 metadata. It maintains API v1, appVersion `v0.4.0`, description, name, and version.

State is historical Helm metadata. Dependencies are v0.4.0 chart templates, which begin adding a shared `node` values group. Risks include legacy Kubernetes API use and old chart version prefixing. Test signal is chart package/install behavior.
