<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-containerd -->
# sources/cloud-native/containerd/script/setup/config-containerd

- Purpose: Writes `/etc/containerd/config.toml` for integration/e2e environments.
- Important behavior: Detects SELinux availability with `getenforce`; writes config version 2, overlayfs `slow_chown = true`, and CRI `enable_selinux` matching host mode.
- Control flow: Set `enable_selinux=false`, enable it when SELinux exists and is not disabled, create `/etc/containerd`, then tee the generated TOML with sudo.
- State and persistence: Persists host-level containerd configuration under `/etc/containerd/config.toml`.
- Dependencies and integration: Used by setup pipelines before starting containerd; interacts with CRI plugin and overlayfs snapshotter.
- Risks: Overwrites existing config wholesale; assumes sudo is available for the `tee` path; config schema is containerd v2 style, not the newer `ConfigVersion = 4` Go constant.
- Test signals: Starting containerd and `crictl info` validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-containerd -->
