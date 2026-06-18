## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/Chart.yaml

Purpose: declares SMB CSI chart v0.6.0 metadata. It uses chart API v1 with appVersion and version `v0.6.0`.

State is historical Helm metadata referenced by the chart index and packaged archive. Dependencies are v0.6.0 templates, especially the adjusted Windows kubelet path value. Risks include legacy CSIDriver API and v-prefixed chart version handling. Test signal is Helm package/install success.
