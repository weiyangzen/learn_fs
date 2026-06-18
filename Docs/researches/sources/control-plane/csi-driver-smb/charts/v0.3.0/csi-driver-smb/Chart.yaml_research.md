## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/Chart.yaml

Purpose: declares chart metadata for SMB CSI v0.3.0. It keeps API v1, appVersion `v0.3.0`, chart name, description, and version.

State is historical release metadata. Dependencies are v0.3.0 templates, which mainly adjust health ports from v0.2.0. Risks are the same legacy version/API compatibility issues as earlier v0.x charts. Test signal is Helm packaging and historical install success.
