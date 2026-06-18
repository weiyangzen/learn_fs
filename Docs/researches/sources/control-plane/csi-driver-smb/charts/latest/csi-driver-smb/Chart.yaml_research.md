## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/Chart.yaml

Purpose: declares the mutable latest SMB CSI Helm chart. It uses chart API v1, chart name `csi-driver-smb`, description, appVersion `latest`, and version `v0.0.0`.

State is chart metadata read by Helm packaging, linting, and install commands. Dependencies include templates and values in the same chart directory. Risks include using a synthetic `v0.0.0` version for latest, which can confuse SemVer sorting and release workflow version validation, and appVersion `latest` tying deployments to mutable image tags when values are not overridden. Test signal is Helm lint/package/install behavior.
